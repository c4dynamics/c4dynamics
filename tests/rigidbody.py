# type: ignore

import unittest
import numpy as np
import sys
sys.path.append('.')
from c4dynamics import rigidbody 
import c4dynamics as c4d 

class TestRigidbody(unittest.TestCase):

    def setUp(self):
        """Set up a basic rigidbody instance for testing."""
        self.rb = rigidbody(x=1.0, y=2.0, z=3.0, vx=4.0, vy=5.0, vz=6.0, 
                            phi=0.1, theta=0.2, psi=0.3, p=0.4, q=0.5, r=0.6)

    def test_initialization(self):
        """Test initialization of rigidbody with given parameters."""
        self.assertEqual(self.rb.x, 1.0)
        self.assertEqual(self.rb.y, 2.0)
        self.assertEqual(self.rb.z, 3.0)
        self.assertEqual(self.rb.vx, 4.0)
        self.assertEqual(self.rb.vy, 5.0)
        self.assertEqual(self.rb.vz, 6.0)
        self.assertEqual(self.rb.phi, 0.1)
        self.assertEqual(self.rb.theta, 0.2)
        self.assertEqual(self.rb.psi, 0.3)
        self.assertEqual(self.rb.p, 0.4)
        self.assertEqual(self.rb.q, 0.5)
        self.assertEqual(self.rb.r, 0.6)

    def test_inertia_tensor_property(self):
        """Test inertia tensor property."""
        self.rb.I = [1, 2, 3]
        np.testing.assert_array_equal(self.rb.I, np.array([1, 2, 3]))

    def test_angles_property(self):
        """Test angles property returns correct values."""
        expected_angles = np.array([self.rb.phi, self.rb.theta, self.rb.psi])
        np.testing.assert_array_equal(self.rb.angles, expected_angles)

    def test_ang_rates_property(self):
        """Test angular rates property returns correct values."""
        expected_rates = np.array([self.rb.p, self.rb.q, self.rb.r])
        np.testing.assert_array_equal(self.rb.ang_rates, expected_rates)

    def test_rotation_matrix(self):
        """Test rotation matrix property."""
        br = self.rb.BR
        self.assertIsInstance(br, np.ndarray)  # Check if BR is an ndarray

    def test_transpose_rotation_matrix(self):
        """Test transpose of rotation matrix."""
        rb = self.rb.RB
        self.assertIsInstance(rb, np.ndarray)  # Check if RB is an ndarray
        np.testing.assert_array_equal(rb, np.transpose(self.rb.BR))

    def test_integration_method(self):
        """Test the integration method (mock behavior for testing)."""
        forces = np.array([0.0, 0.0, 0.0])  # Mock forces
        moments = np.array([0.0, 0.0, 0.0])  # Mock moments
        dt = 0.1  # Time step
        acc = self.rb.inteqm(forces, moments, dt)
        self.assertIsInstance(acc, np.ndarray)  # Check if acceleration is returned as numpy array

    def test_animate_method(self):
        """Test the animate method."""
        modelpath = c4d.datasets.d3_model('bunny') # "path/to/model"  # Mock model path
        angle0 = [0, 0, 0]
        modelcolor = None
        dt = 1e-3
        savedir = None
        cbackground = [1, 1, 1]
        self.rb.theta = np.pi / 10
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        # Here we would typically check if animate doesn't raise errors
        try:
            self.rb.animate(modelpath, angle0, modelcolor, dt, savedir, cbackground)
        except Exception as e:
            self.fail(f"animate() raised an exception: {e}")

    # def test_repr(self):
    #     """Test the __repr__ method."""
    #     expected_repr = "rigidbody(x=1.0, y=2.0, z=3.0, vx=4.0, vy=5.0, vz=6.0, phi=0.1, theta=0.2, psi=0.3, p=0.4, q=0.5, r=0.6)"
    #     self.assertEqual(repr(self.rb), expected_repr)

if __name__ == '__main__':
    unittest.main()
