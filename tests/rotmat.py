# type: ignore

import unittest
import numpy as np
import sys 
sys.path.append('.')
from c4dynamics.rotmat import rotx, roty, rotz, dcm321, dcm321euler

class TestRotationMatrices(unittest.TestCase):

    def test_rotx(self):
        """Test the rotx function."""
        # Test with phi = 0
        result = rotx(0)
        expected = np.eye(3)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

        # Test with phi = pi/2
        result = rotx(np.pi / 2)
        expected = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]])
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_roty(self):
        """Test the roty function."""
        # Test with theta = 0
        result = roty(0)
        expected = np.eye(3)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

        # Test with theta = pi/2
        result = roty(np.pi / 2)
        expected = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_rotz(self):
        """Test the rotz function."""
        # Test with psi = 0
        result = rotz(0)
        expected = np.eye(3)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

        # Test with psi = pi/2
        result = rotz(np.pi / 2)
        expected = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 1]])
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_dcm321(self):
        """Test the dcm321 function."""
        result = dcm321(np.pi / 2, 0, 0)  # Rotate 90 degrees around x-axis
        expected = rotx(np.pi / 2) @ roty(0) @ rotz(0)
        np.testing.assert_array_almost_equal(result, expected, decimal=6)

    def test_dcm321euler(self):
        """Test the dcm321euler function."""
        dcm = np.eye(3)  # Identity matrix should return (0, 0, 0)
        result = dcm321euler(dcm)
        expected = (0, 0, 0)
        self.assertEqual(result, expected)

        # Test with a known rotation matrix
        BI = np.array([[0.866, 0, -0.5],
                       [0, 1, 0],
                       [0.5, 0, 0.866]])
        result = dcm321euler(BI)
        expected = (0, 30, 0)  # Expected output
        self.assertAlmostEqual(result[0], expected[0], places=2)
        self.assertAlmostEqual(result[1], expected[1], places=2)
        self.assertAlmostEqual(result[2], expected[2], places=2)

if __name__ == '__main__':
    unittest.main()
