# type: ignore

import unittest
import numpy as np

import sys
sys.path.append('')
from c4dynamics.filters import ekf 



class TestEKF(unittest.TestCase):


    def setUp(self):
        self.X = {'x': 0., 'y': 0.}
        self.P0 = np.array([[1, 0], [0, 1]])
        self.dt = 0.1
        self.G = np.array([1, 1])
        self.ekf_filter = ekf(self.X, self.P0, G = self.G)


    def test_initialization(self):
        # self.assertEqual(self.ekf_filter.dt, self.dt)
        np.testing.assert_array_equal(self.ekf_filter.P, self.P0)
        self.assertIsNotNone(self.ekf_filter.G)
        self.assertEqual(self.ekf_filter.x, 0)
        self.assertEqual(self.ekf_filter.y, 0)


    def test_initialization_with_invalid_X(self):
        with self.assertRaises(TypeError):
            ekf([0, 0], self.P0)


    def test_predict(self):
        F = np.array([[1, self.dt], [0, 1]])
        Qk = np.array([[0.1, 0], [0, 0.1]])
        self.ekf_filter.predict(F = F, Q = Qk)
        expected_P = F @ self.P0 @ F.T + Qk
        np.testing.assert_array_equal(self.ekf_filter.P, expected_P)
        expected_X = F @ np.array([0, 0])
        np.testing.assert_array_equal(self.ekf_filter.X, expected_X)


    def test_predict_with_fx(self):

        F = np.array([[1, self.dt], [0, 1]])
        Qk = np.array([[0.1, 0], [0, 0.1]])
        fx = np.array([1, 1])

        expected_X = self.ekf_filter.X.copy() 

        self.ekf_filter.predict(F = F, Q = Qk, fx = fx, dt = self.dt)
        expected_P = F @ self.P0 @ F.T + Qk
        expected_X = expected_X + fx * self.dt

        np.testing.assert_array_equal(self.ekf_filter.P, expected_P)
        np.testing.assert_array_equal(self.ekf_filter.X, expected_X)


    def test_update(self):

        # F = np.array([[1, self.dt], [0, 1]])
        # Qk = np.array([[0.1, 0], [0, 0.1]])
        H = np.array([[1, 0], [0, 1]])
        Rk = np.array([[0.1, 0], [0, 0.1]])
        z = np.array([1, 1])


        # self.ekf_filter.predict(F = F, Q = Qk)
        Xprev = self.ekf_filter.X.copy() 
        Pprev = self.ekf_filter.P.copy()
        kout = self.ekf_filter.update(z, H = H, R = Rk)


        K = Pprev @ H.T @ np.linalg.inv(H @ Pprev @ H.T + Rk)
        
        expected_X = Xprev + K @ (z - H @ Xprev)
        expected_P = (np.eye(2) - K @ H) @ Pprev

        np.testing.assert_array_almost_equal(self.ekf_filter.X, expected_X)
        np.testing.assert_array_almost_equal(self.ekf_filter.P, expected_P)


    # def test_update_without_predict(self):
    #     H = np.array([[1, 0], [0, 1]])
    #     Rk = np.array([[0.1, 0], [0, 0.1]])
    #     z = np.array([1, 1])
    #     with self.assertRaises(ValueError):
    #         self.ekf_filter.update(z, H = H, R = Rk)


    def test_store(self):
        F = np.array([[1, self.dt], [0, 1]])
        Qk = np.array([[0.1, 0], [0, 0.1]])
        self.ekf_filter.predict(F = F, Q = Qk)
        self.ekf_filter.store()
        self.assertTrue(hasattr(self.ekf_filter, 'P00'))
        self.assertTrue(hasattr(self.ekf_filter, 'P11'))


if __name__ == '__main__':
    unittest.main()
