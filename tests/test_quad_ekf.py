# type: ignore

import unittest
import numpy as np

import sys

sys.path.append("")
import c4dynamics as c4d
from c4dynamics.controllers.quad_pid import dynamics
from c4dynamics.models.quad import default_quad_config
from c4dynamics.sensors.navigation import imu
from c4dynamics.utils.use_cases.quad_ekf import accel_h, accel_H


def make_quad():
    quad = c4d.rigidbody()
    for k, v in default_quad_config().items():
        setattr(quad, k, v)
    return quad


class TestAccelModelMatchesSensor(unittest.TestCase):
    """The EKF's accelerometer model must predict what the simulated IMU
    measures. A frame mismatch between the two (e.g. the sensor in one body
    convention and accel_h in another) makes the filter diverge."""

    def setUp(self):
        self.quad = make_quad()
        w = np.sqrt(self.quad.m * self.quad.g / (4 * self.quad.kT))
        # unequal rotor speeds: net thrust off hover and nonzero torques
        self.rotor_speeds = np.array([1.04 * w, 0.98 * w, 1.01 * w, 1.03 * w])
        # tilted, yawed and moving, so every term of [BI] and the drag matters
        self.x = np.array([1.0, -2.0, 3.0,           # position
                           1.5, -0.8, 0.4,           # velocity
                           0.20, -0.15, 0.70,        # phi, theta, psi
                           0.0, 0.0, 0.0])           # body rates

    def _imu_measurement(self, dt=1e-6):
        # two samples one dt apart along dynamics(): the second carries the
        # finite-difference acceleration. Zero body rates keep the attitude
        # (and so [BI]) fixed across the step.
        sensor = imu(isideal=True, g=self.quad.g, frame='ENU')
        rb = c4d.rigidbody()
        rb.X = self.x
        sensor.measure(rb, t=0.0)
        rb.X = self.x + dt * dynamics(0.0, self.x, self.quad, self.rotor_speeds)
        return np.array(sensor.measure(rb, t=dt)[:2])

    def test_accel_h_predicts_imu_measurement(self):
        np.testing.assert_allclose(
            accel_h(self.x, self.quad, self.rotor_speeds),
            self._imu_measurement(), atol=1e-6)

    def test_gravity_only_model_matches_imu_at_rest(self):
        # no quad / rotor speeds: accel_h falls back to the gravity
        # projection, which is what an IMU reads on a body at rest
        x = np.zeros(12)
        x[6:9] = [0.2, -0.15, 0.7]
        rb = c4d.rigidbody()
        rb.X = x
        z = imu(isideal=True, g=c4d.g_ms2, frame='ENU').measure(rb)[:2]
        np.testing.assert_allclose(accel_h(x), z, atol=1e-12)

    def test_gravity_only_jacobian_matches_numeric(self):
        x = np.zeros(12)
        x[6:9] = [0.2, -0.15, 0.7]
        H = accel_H(x)
        eps = 1e-6
        for i in (6, 7):
            xp, xm = x.copy(), x.copy()
            xp[i] += eps
            xm[i] -= eps
            np.testing.assert_allclose(
                H[:, i], (accel_h(xp) - accel_h(xm)) / (2 * eps), atol=1e-6)


if __name__ == "__main__":
    unittest.main()
