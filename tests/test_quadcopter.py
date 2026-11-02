# type: ignore

import unittest
import numpy as np

import sys

sys.path.append("")
import c4dynamics as c4d
from c4dynamics.eqm import quadeqm, quadforces
from c4dynamics.models.quad import default_quad_config
from c4dynamics.rotmat import dcm321, dcm321euler, euler2quat

# v_ENU = M v_NED (swap x, y and flip z), body FLU = D body FRD
M = np.array([[0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, -1.0]])
D = np.diag([1.0, -1.0, -1.0])


def make_quad(**kw):
    return c4d.struct(**dict(default_quad_config(), **kw))


def random_state(rng):
    return rng.normal(size=12) * [5, 5, 5, 2, 2, 2, 0.5, 0.5, 3, 1, 1, 1]


def to_quaternion(X):
    return np.concatenate([X[:6], euler2quat(*X[6:9]), X[9:]])


def ned_to_enu(X):
    # the same physical state in ENU / FLU
    BI = D @ dcm321(*X[6:9]) @ M.T
    return np.concatenate([M @ X[0:3], M @ X[3:6],
                           np.deg2rad(dcm321euler(BI)), D @ X[9:12]])


class TestQuadEqm(unittest.TestCase):

    def setUp(self):
        self.quad = make_quad()
        self.w_hover = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        self.rng = np.random.default_rng(7)

    def test_hover_equilibrium(self):
        for frame in ('ENU', 'NED'):
            np.testing.assert_allclose(
                quadeqm(0, np.zeros(12), self.quad, [self.w_hover] * 4, frame),
                np.zeros(12), atol=1e-12)
            Xq = np.zeros(13)
            Xq[6] = 1.0
            np.testing.assert_allclose(
                quadeqm(0, Xq, self.quad, [self.w_hover] * 4, frame),
                np.zeros(13), atol=1e-12)

    def test_reference_enu_flu_model(self):
        # the model quad_pid.dynamics was written as before moving to eqm
        q = self.quad
        for _ in range(50):
            X = random_state(self.rng)
            w = self.rng.uniform(300, 900, 4)
            _, _, _, vx, vy, vz, phi, theta, psi, p, qr, r = X
            F1, F2, F3, F4 = q.kT * w**2
            T = F1 + F2 + F3 + F4
            tau = [q.l * (-F1 + F2 + F3 - F4), q.l * (-F1 + F2 - F3 + F4),
                   q.kQ / q.kT * (-F1 - F2 + F3 + F4)]
            Om = w[0] + w[1] - w[2] - w[3]
            Mx = tau[0] - q.Ar * p - q.IR * qr * Om
            My = tau[1] - q.Ar * qr + q.IR * p * Om
            Mz = tau[2] - q.Ar * r
            BI = dcm321(phi, theta, psi)
            u, v, ww = BI @ [vx, vy, vz]
            dv = BI.T @ [-q.Ax * u, -q.Ay * v, T - q.Az * ww] / q.m - [0, 0, q.g]
            expected = np.array([
                vx, vy, vz, *dv,
                p + np.sin(phi) * np.tan(theta) * qr + np.cos(phi) * np.tan(theta) * r,
                np.cos(phi) * qr - np.sin(phi) * r,
                (np.sin(phi) * qr + np.cos(phi) * r) / np.cos(theta),
                (Mx - (q.Izz - q.Iyy) * qr * r) / q.Ixx,
                (My - (q.Ixx - q.Izz) * p * r) / q.Iyy,
                (Mz - (q.Iyy - q.Ixx) * p * qr) / q.Izz])
            np.testing.assert_allclose(quadeqm(0, X, q, w, 'ENU'), expected,
                                       rtol=1e-12, atol=1e-12)

    def test_ned_frd_and_enu_flu_describe_the_same_motion(self):
        for _ in range(50):
            X_ned = random_state(self.rng)
            X_ned[7] = np.clip(X_ned[7], -1.2, 1.2)
            X_enu = ned_to_enu(X_ned)
            w = self.rng.uniform(300, 900, 4)
            d_ned = quadeqm(0, X_ned, self.quad, w, 'NED')
            d_enu = quadeqm(0, X_enu, self.quad, w, 'ENU')
            np.testing.assert_allclose(d_enu[3:6], M @ d_ned[3:6], atol=1e-9)
            np.testing.assert_allclose(d_enu[9:12], D @ d_ned[9:12], atol=1e-9)

    def test_quaternion_and_euler_bodies_agree(self):
        for frame in ('ENU', 'NED'):
            for _ in range(50):
                X = random_state(self.rng)
                w = self.rng.uniform(300, 900, 4)
                de = quadeqm(0, X, self.quad, w, frame)
                dq = quadeqm(0, to_quaternion(X), self.quad, w, frame)
                np.testing.assert_allclose(dq[:6], de[:6], atol=1e-10)
                np.testing.assert_allclose(dq[10:], de[9:], atol=1e-10)

    def test_explicit_rotor_geometry_matches_x_layout(self):
        l = self.quad.l
        X = random_state(self.rng)
        w = self.rng.uniform(300, 900, 4)
        flu = make_quad(rotor_pos=[[l, -l], [-l, l], [l, l], [-l, -l]],
                        rotor_dir=[1, 1, -1, -1])
        np.testing.assert_allclose(quadeqm(0, X, flu, w, 'ENU'),
                                   quadeqm(0, X, self.quad, w, 'ENU'), atol=1e-12)
        frd = make_quad(rotor_pos=[[l, l], [-l, -l], [l, -l], [-l, l]])
        np.testing.assert_allclose(quadeqm(0, X, frd, w, 'NED'),
                                   quadeqm(0, X, self.quad, w, 'NED'), atol=1e-12)

    def test_moving_with_the_wind_has_no_drag(self):
        X = np.zeros(12)
        X[3:6] = [2.0, -1.0, 0.5]
        still = quadforces(X, self.quad, [self.w_hover] * 4, 'NED')[0]
        self.assertGreater(np.abs(still[:2]).max(), 0.1)
        windy = quadforces(X, make_quad(wind=X[3:6]), [self.w_hover] * 4, 'NED')[0]
        np.testing.assert_allclose(windy, [0, 0, -self.quad.m * self.quad.g], atol=1e-12)

    def test_specific_force_matches_imu(self):
        # quadforces F_b / m is what an IMU at the center of mass reads
        for frame in ('ENU', 'NED'):
            X = random_state(self.rng)
            X[9:12] = 0.0   # fixed attitude across the finite-difference step
            w = self.rng.uniform(300, 900, 4)
            sensor = c4d.sensors.imu(isideal=True, g=self.quad.g, frame=frame)
            rb = c4d.rigidbody()
            rb.X = X
            sensor.measure(rb, t=0.0)
            dt = 1e-6
            rb.X = X + dt * quadeqm(0, X, self.quad, w, frame)
            np.testing.assert_allclose(
                np.array(sensor.measure(rb, t=dt)[:3]),
                quadforces(X, self.quad, w, frame)[0] / self.quad.m, atol=1e-5)

    def test_invalid_inputs_raise(self):
        with self.assertRaises(ValueError):
            quadeqm(0, np.zeros(12), self.quad, [0] * 4, 'XYZ')
        with self.assertRaises(ValueError):
            quadeqm(0, np.zeros(10), self.quad, [0] * 4, 'NED')


if __name__ == "__main__":
    unittest.main()
