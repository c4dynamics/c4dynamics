# type: ignore

import unittest
import numpy as np
import sys
sys.path.append('.')
from c4dynamics.utils.math import *
from c4dynamics.states.lib.datapoint import datapoint
from c4dynamics.states.lib.rigidbody import rigidbody
from c4dynamics.eqm import eqm3, eqm6

class TestEquationsOfMotion(unittest.TestCase):

    def setUp(self):
        # Create sample instances for tests
        self.dp = datapoint()
        self.dp.mass = 10  # 10 kg mass

        self.rb = rigidbody()
        self.rb.mass = 0.5
        self.rb.I = np.array([0.5, 0.4, 0.6])  # Inertia for x, y, z axes

    def test_eqm3_free_fall(self):
        """Test eqm3 under free-fall conditions with no initial velocity."""
        F = np.array([0, 0, -9.8 * self.dp.mass])  # gravity
        self.dp.vx, self.dp.vy, self.dp.vz = 0, 0, 0  # initial velocity
        
        result = eqm3(self.dp, F)
        expected = np.array([0, 0, 0, 0, 0, -9.8])  # zero initial velocity, acceleration -9.8 m/s²

        np.testing.assert_almost_equal(result, expected, decimal=5)

    def test_eqm6_rotational_motion(self):
        """Test eqm6 under torque on y-axis with no initial angular velocity."""
        F = np.array([0, 0, 0])  # No translational force
        M = np.array([0, 1.0, 0])  # Torque on y-axis
        
        # No initial angular or linear velocity
        self.rb.vx, self.rb.vy, self.rb.vz = 0, 0, 0
        self.rb.p, self.rb.q, self.rb.r = 0, 0, 0  # angular velocities

        result = eqm6(self.rb, F, M)
        expected_rotational_derivatives = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2.5, 0])

        np.testing.assert_almost_equal(result, expected_rotational_derivatives, decimal=5)

    def test_eqm3_constant_velocity(self):
        """Test eqm3 with constant velocity and zero force."""
        F = np.array([0, 0, 0])  # No force
        self.dp.vx, self.dp.vy, self.dp.vz = 5, 5, 5  # constant velocity in each axis

        result = eqm3(self.dp, F)
        expected = np.array([5, 5, 5, 0, 0, 0])  # Constant velocity, no acceleration

        np.testing.assert_almost_equal(result, expected, decimal=5)

if __name__ == "__main__":
    unittest.main()
