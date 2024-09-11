import unittest
import numpy as np
from scipy.linalg import solve_discrete_are, solve_continuous_are

# Assuming the kalman class is defined in a module named kalman_module
import sys
sys.path.append('')
# import c4dynamics as c4d 
from c4dynamics.filters import kalman

class TestKalmanFilter(unittest.TestCase):
    
    def setUp(self):
        self.dt = 0.1
        
        # Initial state covariance matrix (P0)
        self.P0 = np.array([[1, 0], [0, 1]])
        
        # Continuous system matrices
        self.A = np.array([[0, 1], [-1, 0]])
        self.c = np.array([[1, 0]])
        self.Q = np.array([[0.1, 0], [0, 0.1]])
        self.R = np.array([[0.1]])
        
        # Discrete system matrices
        self.F = np.array([[1, self.dt], [-self.dt, 1]])
        self.H = np.array([[1, 0]])
        self.Qk = np.array([[0.01, 0], [0, 0.01]])
        self.Rk = np.array([[0.1]])
        
    def test_initialization_continuous(self):
        kf = kalman(dt=self.dt, P0=self.P0, A=self.A, c=self.c, Q=self.Q, R=self.R)
        np.testing.assert_array_almost_equal(kf.F, np.eye(2) + self.A * self.dt)
        np.testing.assert_array_almost_equal(kf.H, self.c)
        np.testing.assert_array_almost_equal(kf.Qk, self.Q * self.dt)
        np.testing.assert_array_almost_equal(kf.Rk, self.R / self.dt)
        
    def test_initialization_discrete(self):
        kf = kalman(dt=self.dt, P0=self.P0, F=self.F, H=self.H, Qk=self.Qk, Rk=self.Rk)
        np.testing.assert_array_almost_equal(kf.F, self.F)
        np.testing.assert_array_almost_equal(kf.H, self.H)
        np.testing.assert_array_almost_equal(kf.Qk, self.Qk)
        np.testing.assert_array_almost_equal(kf.Rk, self.Rk)
        
    def test_initialization_steadystate(self):
        kf = kalman(dt=self.dt, P0=self.P0, steadystate=True, F=self.F, H=self.H, Qk=self.Qk, Rk=self.Rk)
        P_expected = solve_discrete_are(self.F.T, self.H.T, self.Qk, self.Rk)
        K_expected = P_expected @ self.H.T @ np.linalg.inv(self.H @ P_expected @ self.H.T + self.Rk)
        np.testing.assert_array_almost_equal(kf.P, P_expected)
        np.testing.assert_array_almost_equal(kf.Kinf, K_expected)
        
    def test_predict(self):
        kf = kalman(dt=self.dt, P0=self.P0, F=self.F, H=self.H, Qk=self.Qk, Rk=self.Rk)
        x = np.array([1, 0])
        x_pred = kf.predict(x)
        x_expected = self.F @ x
        np.testing.assert_array_almost_equal(x_pred, x_expected)
        
    def test_predict_with_control(self):
        kf = kalman(dt=self.dt, P0=self.P0, F=self.F, H=self.H, Qk=self.Qk, Rk=self.Rk, G=np.array([[0.5], [0.5]]))
        x = np.array([1, 0])
        u = 1
        x_pred = kf.predict(x, u)
        x_expected = self.F @ x + kf.G.reshape(x.shape) * u
        np.testing.assert_array_almost_equal(x_pred, x_expected)
        
    def test_update(self):
        kf = kalman(dt=self.dt, P0=self.P0, F=self.F, H=self.H, Qk=self.Qk, Rk=self.Rk)
        x = np.array([1, 0])
        z = np.array([1.1])
        x_pred = kf.predict(x)
        x_updated = kf.update(x_pred, z)
        K = kf.P @ kf.H.T @ np.linalg.inv(kf.H @ kf.P @ kf.H.T + kf.Rk)
        x_expected = x_pred + K @ (z - kf.H @ x_pred)
        np.testing.assert_array_almost_equal(x_updated, x_expected)

if __name__ == '__main__':
    unittest.main()
