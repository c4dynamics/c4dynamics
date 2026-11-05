# type: ignore

import unittest
import numpy as np
from scipy.linalg import solve_discrete_are
from scipy.linalg import expm

# Assuming the kalman class is defined in a module named kalman_module
import sys

sys.path.append("")
import c4dynamics as c4d

import warnings

warnings.simplefilter("ignore", c4d.c4warn)


# first order systems
# https://eng.libretexts.org/Bookshelves/Industrial_and_Systems_Engineering/Introduction_to_Control_Systems_(Iqbal)/01%3A_Mathematical_Models_of_Physical_Systems/1.02%3A_First-Order_ODE_Models
# https://cocalc.com/share/public_paths/7557a5ac1c870f1ec8f01271959b16b49df9d087/07-Kalman-Filter-Math.ipynb


class TestKalman(unittest.TestCase):

    def setUp(self):
        self.X = {"x": 0, "y": 0}
        self.dt = 0.1

        # Initial state covariance matrix (P0)
        self.P0 = np.array([[1, 0], [0, 1]])

        # Discrete system matrices
        self.F = np.array([[1, self.dt], [-self.dt, 1]])
        self.H = np.array([[1, 0]])

        self.Q = np.diag([1, 1])
        self.R = 1

        """Set up a default Kalman filter with steady state"""
        self.dt = 0.1
        self.process_noise = 0.01
        self.measure_noise = 0.1
        self.kf = c4d.filters.kalman.velocitymodel(self.dt, self.process_noise, self.measure_noise)

    def test_initialization_discrete(self):
        kf = c4d.filters.kalman(self.X, P0=self.P0, F=self.F, H=self.H, Q=self.Q, R=self.R)
        np.testing.assert_array_almost_equal(kf.F, self.F)
        np.testing.assert_array_almost_equal(kf.H, self.H)
        np.testing.assert_array_almost_equal(kf.Q, self.Q)
        np.testing.assert_array_almost_equal(kf.R, self.R)

        """Test Kalman filter initialization with a discrete model"""
        # self.assertTrue(self.kf.isdiscrete, "Expected system to be discrete")
        F = np.zeros((6, 6))
        F[0, 4] = 1
        F[1, 5] = 1
        F = expm(F * self.dt)
        np.testing.assert_array_almost_equal(self.kf.F, F, decimal=5)
        self.assertEqual(self.kf.H.shape, (4, 6), "Unexpected measurement matrix shape")

    def test_initialization_steadystate(self):
        kf = c4d.filters.kalman(
            self.X, P0=self.P0, steadystate=True, F=self.F, H=self.H, Q=self.Q, R=self.R
        )
        P_expected = solve_discrete_are(self.F.T, self.H.T, self.Q, self.R)
        K_expected = P_expected @ self.H.T @ np.linalg.inv(self.H @ P_expected @ self.H.T + self.R)
        np.testing.assert_array_almost_equal(kf.P, P_expected)
        np.testing.assert_array_almost_equal(kf._Kinf, K_expected)

    def test_predict(self):
        kf = c4d.filters.kalman(self.X, P0=self.P0, F=self.F, H=self.H, Q=self.Q, R=self.R)
        x = np.array([1, 0])
        kf.X = x
        x_expected = self.F @ x
        kf.predict()
        x_pred = kf.X
        np.testing.assert_array_almost_equal(x_pred, x_expected)

    def test_predict_with_control(self):
        kf = c4d.filters.kalman(
            self.X, P0=self.P0, F=self.F, H=self.H, Q=self.Q, R=self.R, G=np.array([[0.5], [0.5]])
        )
        x = np.array([1, 0])
        kf.X = x
        u = 1
        x_expected = self.F @ x + kf.G.reshape(x.shape) * u
        kf.predict(u=u)
        x_pred = kf.X
        np.testing.assert_array_almost_equal(x_pred, x_expected)

    def test_update(self):

        kf = c4d.filters.kalman(self.X, P0=self.P0, F=self.F, H=self.H, Q=self.Q, R=self.R)

        kf.predict()
        x_pred = kf.X

        K = kf.P @ kf.H.T @ np.linalg.inv(kf.H @ kf.P @ kf.H.T + kf.R)
        z = np.array([1.1])
        x_expected = x_pred + K @ (z - kf.H @ x_pred)
        kf.update(z)
        x_updated = kf.X

        np.testing.assert_array_almost_equal(x_updated, x_expected)

        """Test update with measurement"""
        z = np.array([1.0, 1.0, 1.0, 1.0])
        self.kf.update(z)
        self.assertEqual(self.kf.X.shape[0], 6, "Expected state dimension mismatch after update")

    def test_update_covariance_joseph_form(self):
        """P is updated in the Joseph form (I-KH) P (I-KH)' + K R K'."""
        kf = c4d.filters.kalman(self.X, P0=self.P0, F=self.F, H=self.H, Q=self.Q, R=self.R)
        kf.predict()
        Pprev = kf.P.copy()

        K = kf.update(z=1.1)

        IKH = np.eye(2) - K @ kf.H
        P_expected = IKH @ Pprev @ IKH.T + K @ kf.R @ K.T
        np.testing.assert_allclose(kf.P, P_expected, rtol=1e-12, atol=0)

    def test_update_covariance_matches_short_form_when_well_conditioned(self):
        """For the optimal gain the Joseph form equals (I-KH) P."""
        H = np.array([[1.0, 0.0], [0.5, 1.0]])
        R = np.diag([0.3, 0.7])
        kf = c4d.filters.kalman(self.X, P0=self.P0, F=self.F, H=H, Q=self.Q, R=R)
        kf.predict()
        Pprev = kf.P.copy()

        K = kf.update(z=[1.0, -0.5])

        np.testing.assert_allclose(kf.P, (np.eye(2) - K @ H) @ Pprev, rtol=1e-10, atol=1e-14)

    def test_update_covariance_with_runtime_R(self):
        """The R passed to update() is the one used in the K R K' term."""
        kf = c4d.filters.kalman(self.X, P0=self.P0, F=self.F, H=self.H, Q=self.Q, R=self.R)
        Pprev = kf.P.copy()
        R_new = np.array([[4.0]])

        K = kf.update(z=1.0, R=R_new)

        IKH = np.eye(2) - K @ self.H
        np.testing.assert_allclose(kf.P, IKH @ Pprev @ IKH.T + K @ R_new @ K.T, rtol=1e-12)

    def test_update_covariance_stays_symmetric_when_ill_conditioned(self):
        """Large initial uncertainty with a precise sensor: P stays symmetric.

        With P0 = 1e8 I and R = 1e-6, the short form P - KHP leaves P
        asymmetric by ~1e-4 relative to its magnitude after a few steps.
        """
        F = np.array([[1.0, 1.0], [0.0, 1.0]])
        H = np.array([[1.0, 0.0]])
        kf = c4d.filters.kalman(self.X, P0=[1e4, 1e4], F=F, H=H, Q=np.zeros((2, 2)), R=1e-6)

        for _ in range(50):
            kf.predict()
            kf.update(z=0.0)
            asym = np.abs(kf.P - kf.P.T).max() / np.abs(kf.P).max()
            self.assertLess(asym, 1e-12)
            self.assertGreaterEqual(np.linalg.eigvalsh(kf.P).min(), -1e-12 * np.abs(kf.P).max())

    def test_update_covariance_does_not_collapse_when_ill_conditioned(self):
        """Extreme conditioning: P stays a positive covariance.

        With P0 = 1e12 I and R = 1e-8, the short form P - KHP rounds P to
        exactly zero, after which the filter ignores every measurement.
        """
        F = np.array([[1.0, 1.0], [0.0, 1.0]])
        H = np.array([[1.0, 0.0]])
        kf = c4d.filters.kalman(self.X, P0=[1e6, 1e6], F=F, H=H, Q=np.zeros((2, 2)), R=1e-8)

        for _ in range(50):
            kf.predict()
            kf.update(z=0.0)
            self.assertTrue(np.all(np.isfinite(kf.P)))
            self.assertTrue(np.all(np.diag(kf.P) > 0))
            self.assertGreaterEqual(np.linalg.eigvalsh(kf.P).min(), -1e-12 * np.abs(kf.P).max())

    def test_update_steadystate_keeps_P_constant(self):
        """In steady-state mode update() does not touch P."""
        P_before = self.kf.P.copy()
        self.kf.update(np.array([1.0, 1.0, 1.0, 1.0]))
        np.testing.assert_array_equal(self.kf.P, P_before)

    def test_update_gate_rejection_keeps_P(self):
        """A gated-out measurement leaves X and P unchanged."""
        kf = c4d.filters.kalman(self.X, P0=self.P0, F=self.F, H=self.H, Q=self.Q, R=self.R)
        X_before, P_before = kf.X.copy(), kf.P.copy()

        K = kf.update(z=100.0, gate=9.0)

        self.assertIsNone(K)
        np.testing.assert_array_equal(kf.X, X_before)
        np.testing.assert_array_equal(kf.P, P_before)

    def test_steady_state_gain(self):
        """Test if steady-state Kalman gain is correctly computed"""
        self.assertIsNotNone(self.kf._Kinf, "Kalman gain should be defined in steady-state mode")
        np.testing.assert_array_almost_equal(
            self.kf._Kinf,
            self.kf.P
            @ self.kf.H.T
            @ np.linalg.inv(self.kf.H @ self.kf.P @ self.kf.H.T + self.kf.R),
            decimal=5,
        )

    def test_invalid_initial_conditions(self):
        """Test invalid initialization arguments"""
        with self.assertRaises(TypeError):
            c4d.filters.kalman(X=[0, 0, 0], dt=0.1)  # X should be a dict

        with self.assertRaises(ValueError):
            c4d.filters.kalman({"x": 0, "y": 0}, F=np.eye(2), H=None)  # H is missing

    def test_store_state(self):
        """Test state storage functionality"""
        self.kf.store(t=0)
        self.assertTrue(
            hasattr(self.kf, "P00"), "P00 attribute should be stored after calling store"
        )
        self.assertEqual(
            self.kf.P00,
            np.diag(self.kf.P)[0],
            "Stored P00 should match the first diagonal element of P",
        )


if __name__ == "__main__":
    unittest.main()
