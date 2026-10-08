# type: ignore

import unittest
import numpy as np

import sys

sys.path.append("")
import c4dynamics as c4d
from c4dynamics.controllers.quad_pid import (
    dynamics,
    position_reference,
    velocity_reference,
    InitializeControllers,
    ControlAllocator,
)
from c4dynamics.models.quad import default_quad_config
from c4dynamics.controllers.cascade_pid_config import default_controller_config


# Reference vehicle/gains, shared with the cascade-PID and EKF examples --
# see quad_config.py / controller_config.py. Not notebook-specific, so this
# uses the canonical defaults as-is (no per-example override).
QUAD_PARAMS = default_quad_config()
CONTROLLER_PARAMS = default_controller_config()


class TestQuadPid(unittest.TestCase):

    def setUp(self):
        self.quad = c4d.rigidbody()
        for k, v in QUAD_PARAMS.items():
            setattr(self.quad, k, v)
        self.controller_params = CONTROLLER_PARAMS
        self.A, self.B, self.omega, self.z_ref, self.t_sim = 4.0, 2.0, 0.1, 1.5, 90.0

    #
    # dynamics()
    #

    def test_dynamics_output_shape(self):
        x = np.zeros(12)
        rotor_speeds = np.array([600.0, 600.0, 600.0, 600.0])
        dx = dynamics(0.0, x, self.quad, rotor_speeds)
        self.assertEqual(dx.shape, (12,))
        self.assertTrue(np.all(np.isfinite(dx)))

    def test_dynamics_hover_equilibrium(self):
        # At zero velocity/attitude/rate and rotor speeds producing exactly
        # mg of total thrust, all accelerations must vanish.
        w_hover = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        rotor_speeds = np.array([w_hover] * 4)
        x = np.zeros(12)
        dx = dynamics(0.0, x, self.quad, rotor_speeds)
        np.testing.assert_array_almost_equal(dx[0:3], np.zeros(3))
        np.testing.assert_array_almost_equal(dx[3:6], np.zeros(3))
        np.testing.assert_array_almost_equal(dx[6:12], np.zeros(6))

    def test_dynamics_asymmetric_thrust_produces_roll(self):
        # X config: w3 = front-left CW, w4 = rear-right CW -- an imbalance
        # must produce a nonzero roll angular acceleration.
        w_hover = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        rotor_speeds = np.array([w_hover, w_hover, w_hover * 1.1, w_hover * 0.9])
        x = np.zeros(12)
        dx = dynamics(0.0, x, self.quad, rotor_speeds)
        self.assertGreater(abs(dx[9]), 1e-3)

    #
    # position_reference() / velocity_reference()
    #

    def test_takeoff_start_and_end(self):
        x0, y0, z0 = position_reference(0.0, self.A, self.B, self.omega, self.z_ref, t_sim=self.t_sim)
        self.assertEqual((x0, y0, z0), (0.0, 0.0, 0.0))
        # end of takeoff (t = t_takeoff = 8.0 by default): should have reached z_ref
        _, _, z_end = position_reference(8.0, self.A, self.B, self.omega, self.z_ref, t_sim=self.t_sim)
        self.assertAlmostEqual(z_end, self.z_ref, places=9)

    def test_landing_returns_to_origin(self):
        x_end, y_end, z_end = position_reference(
            self.t_sim, self.A, self.B, self.omega, self.z_ref, t_sim=self.t_sim
        )
        self.assertAlmostEqual(x_end, 0.0, places=6)
        self.assertAlmostEqual(y_end, 0.0, places=6)
        self.assertAlmostEqual(z_end, 0.0, places=6)

    def test_velocity_reference_matches_numerical_derivative(self):
        # velocity_reference() must be the analytical d/dt of position_reference().
        eps = 1e-5
        for t in (10.0, 25.0, 40.0, 60.0):
            xp, yp, _ = position_reference(t + eps, self.A, self.B, self.omega, self.z_ref, t_sim=self.t_sim)
            xm, ym, _ = position_reference(t - eps, self.A, self.B, self.omega, self.z_ref, t_sim=self.t_sim)
            vx_num = (xp - xm) / (2 * eps)
            vy_num = (yp - ym) / (2 * eps)
            vx, vy = velocity_reference(t, self.A, self.B, self.omega, t_sim=self.t_sim)
            self.assertAlmostEqual(vx, vx_num, places=4)
            self.assertAlmostEqual(vy, vy_num, places=4)

    #
    # ControlAllocator
    #

    def test_allocator_round_trip_recovers_commanded_wrench(self):
        allocator = ControlAllocator(self.quad.kT, self.quad.kQ, self.quad.l, omega_max=1000.0)
        T_cmd = self.quad.m * self.quad.g
        tau_phi_cmd, tau_theta_cmd, tau_psi_cmd = 0.02, -0.015, 0.01

        w1, w2, w3, w4 = allocator.allocate(T_cmd, tau_phi_cmd, tau_theta_cmd, tau_psi_cmd)
        F1, F2, F3, F4 = self.quad.kT * np.array([w1, w2, w3, w4]) ** 2
        gamma = self.quad.kQ / self.quad.kT

        T_out = F1 + F2 + F3 + F4
        tau_phi_out = self.quad.l * (-F1 + F2 + F3 - F4)
        tau_theta_out = self.quad.l * (-F1 + F2 - F3 + F4)
        tau_psi_out = gamma * (-F1 - F2 + F3 + F4)

        self.assertAlmostEqual(T_out, T_cmd, places=5)
        self.assertAlmostEqual(tau_phi_out, tau_phi_cmd, places=3)
        self.assertAlmostEqual(tau_theta_out, tau_theta_cmd, places=3)
        self.assertAlmostEqual(tau_psi_out, tau_psi_cmd, places=3)

    def test_allocator_rotor_speeds_are_nonnegative(self):
        allocator = ControlAllocator(self.quad.kT, self.quad.kQ, self.quad.l, omega_max=1000.0)
        # a deliberately unachievable, extreme torque demand
        w = allocator.allocate(0.0, 5.0, 5.0, 5.0)
        self.assertTrue(all(np.isfinite(w)))
        self.assertTrue(all(np.asarray(w) >= 0.0))

    #
    # InitializeControllers() / OuterPositionPID
    #

    def test_initialize_controllers_returns_four_objects(self):
        outer, mid, inner, allocator = InitializeControllers(self.controller_params, self.quad)
        self.assertEqual(outer.m, self.quad.m)
        self.assertEqual(outer.g, self.quad.g)
        self.assertEqual(allocator.kT, self.quad.kT)

    def test_outer_loop_tilt_compensates_thrust(self):
        # zero errors, tilted: the vertical part of the thrust, T cos(phi)
        # cos(theta), must still carry the weight.
        phi, theta = np.deg2rad(15.0), np.deg2rad(-10.0)
        outer, _, _, _ = InitializeControllers(self.controller_params, self.quad)
        tilted = c4d.state(x=0.0, y=0.0, z=1.5, vx=0.0, vy=0.0, vz=0.0,
                           phi=phi, theta=theta, psi=0.0)
        T_cmd, _, _, _ = outer.compute(
            Xd=0.0, Yd=0.0, Zd=1.5, Vxd=0.0, Vyd=0.0, Psi_sp=0.0,
            quad=tilted, Ts=1.0 / 50.0)
        self.assertAlmostEqual(T_cmd * np.cos(phi) * np.cos(theta),
                               self.quad.m * self.quad.g, places=9)

    def test_outer_loop_near_zero_error_gives_near_hover_thrust(self):
        outer, _, _, _ = InitializeControllers(self.controller_params, self.quad)
        hover_state = c4d.state(x=0.0, y=0.0, z=1.5, vx=0.0, vy=0.0, vz=0.0,
                                phi=0.0, theta=0.0, psi=0.0)
        T_cmd, phi_d, theta_d, psi_d = outer.compute(
            Xd=0.0, Yd=0.0, Zd=1.5, Vxd=0.0, Vyd=0.0, Psi_sp=0.0,
            quad=hover_state, Ts=1.0 / 50.0,
        )
        self.assertAlmostEqual(T_cmd, self.quad.m * self.quad.g,
                               delta=0.05 * self.quad.m * self.quad.g)
        self.assertLess(abs(phi_d), 1e-6)
        self.assertLess(abs(theta_d), 1e-6)

    #
    # FLU body frame sign conventions
    #

    def _rates_dot(self, rotor_speeds):
        dx = dynamics(0.0, np.zeros(12), self.quad, rotor_speeds)
        return dx[9:12]

    def test_flu_rear_heavy_thrust_pitches_nose_down(self):
        # rear motors (2, 4) stronger -> nose down -> positive pitch in FLU
        w = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        dp, dq, dr = self._rates_dot(np.array([w, 1.05 * w, w, 1.05 * w]))
        self.assertGreater(dq, 1e-3)

    def test_flu_left_heavy_thrust_rolls_right_side_down(self):
        # left motors (2, 3) stronger -> right side down -> positive roll
        w = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        dp, dq, dr = self._rates_dot(np.array([w, 1.05 * w, 1.05 * w, w]))
        self.assertGreater(dp, 1e-3)

    def test_flu_cw_rotors_faster_yaws_left(self):
        # CW rotors (3, 4) faster -> reaction torque CCW seen from above ->
        # positive yaw (nose left) in FLU
        w = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        dp, dq, dr = self._rates_dot(np.array([w, w, 1.05 * w, 1.05 * w]))
        self.assertGreater(dr, 1e-6)

    def test_flu_nose_down_accelerates_forward(self):
        # facing east (psi = 0), pitched nose down at hover thrust -> +x accel
        w = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        x = np.zeros(12); x[7] = 0.1
        dx = dynamics(0.0, x, self.quad, np.full(4, w))
        self.assertGreater(dx[3], 0.1)

    def test_flu_hover_thrust_balances_gravity(self):
        w = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        dx = dynamics(0.0, np.zeros(12), self.quad, np.full(4, w))
        self.assertAlmostEqual(dx[5], 0.0, places=9)

    def test_outer_loop_commands_follow_flu_signs(self):
        # facing east (psi = 0): body x = east, body y = north.
        outer, _, _, _ = InitializeControllers(self.controller_params, self.quad)
        hover = dict(x=0.0, y=0.0, z=1.5, vx=0.0, vy=0.0, vz=0.0,
                     phi=0.0, theta=0.0, psi=0.0)
        # target ahead (east) -> nose down -> theta_d > 0
        _, phi_d, theta_d, _ = outer.compute(
            Xd=1.0, Yd=0.0, Zd=1.5, Vxd=0.0, Vyd=0.0, Psi_sp=0.0,
            quad=c4d.state(**hover), Ts=1.0 / 50.0)
        self.assertGreater(theta_d, 0.0)
        # target to the right (south) -> right side down -> phi_d > 0
        outer, _, _, _ = InitializeControllers(self.controller_params, self.quad)
        _, phi_d, theta_d, _ = outer.compute(
            Xd=0.0, Yd=-1.0, Zd=1.5, Vxd=0.0, Vyd=0.0, Psi_sp=0.0,
            quad=c4d.state(**hover), Ts=1.0 / 50.0)
        self.assertGreater(phi_d, 0.0)

    def test_velocity_feedforward_tilts_toward_commanded_velocity(self):
        # zero position error, hovering, facing east. A commanded velocity
        # must tilt the thrust toward it on both axes, the same way the
        # position feedback does.
        # Kd also acts on (Vff - V); zero it so only the feedforward term is tested
        params = dict(self.controller_params, Kd_x=0.0, Kd_y=0.0)
        hover = dict(x=0.0, y=0.0, z=1.5, vx=0.0, vy=0.0, vz=0.0,
                     phi=0.0, theta=0.0, psi=0.0)
        # forward (east) -> nose down -> theta_d > 0
        outer, _, _, _ = InitializeControllers(params, self.quad)
        _, phi_d, theta_d, _ = outer.compute(
            Xd=0.0, Yd=0.0, Zd=1.5, Vxd=1.0, Vyd=0.0, Psi_sp=0.0,
            quad=c4d.state(**hover), Ts=1.0 / 50.0)
        self.assertGreater(theta_d, 0.0)
        # left (north) -> left side down -> phi_d < 0
        outer, _, _, _ = InitializeControllers(params, self.quad)
        _, phi_d, theta_d, _ = outer.compute(
            Xd=0.0, Yd=0.0, Zd=1.5, Vxd=0.0, Vyd=1.0, Psi_sp=0.0,
            quad=c4d.state(**hover), Ts=1.0 / 50.0)
        self.assertLess(phi_d, 0.0)


if __name__ == "__main__":
    unittest.main()
