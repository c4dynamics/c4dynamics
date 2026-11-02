# type: ignore

import unittest
import numpy as np
import sys

sys.path.append(".")
from c4dynamics.rotmat import rotx, roty, rotz, dcm321, dcm321euler
from c4dynamics.rotmat import euler2quat, quat2dcm, quat2euler


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
        BI = np.array([[0.866, 0, -0.5], [0, 1, 0], [0.5, 0, 0.866]])
        result = dcm321euler(BI)
        expected = (0, 30, 0)  # Expected output
        self.assertAlmostEqual(result[0], expected[0], places=2)
        self.assertAlmostEqual(result[1], expected[1], places=2)
        self.assertAlmostEqual(result[2], expected[2], places=2)

    def test_euler2quat(self):
        """Test the euler2quat function."""
        np.testing.assert_array_almost_equal(euler2quat(0, 0, 0), [1, 0, 0, 0])
        np.testing.assert_array_almost_equal(
            euler2quat(psi=np.pi / 2), [np.sqrt(0.5), 0, 0, np.sqrt(0.5)]
        )
        self.assertAlmostEqual(np.linalg.norm(euler2quat(0.3, -0.2, 1.1)), 1)

    def test_quat2dcm(self):
        """Test quat2dcm against dcm321 for random attitudes."""
        rng = np.random.default_rng(0)
        for _ in range(100):
            angles = rng.uniform([-np.pi, -np.pi / 2, -np.pi], [np.pi, np.pi / 2, np.pi])
            np.testing.assert_array_almost_equal(quat2dcm(euler2quat(*angles)), dcm321(*angles))
        # non unit quaternion is normalized
        np.testing.assert_array_almost_equal(quat2dcm([2, 0, 0, 0]), np.eye(3))

    def test_quat2euler(self):
        """Test quat2euler round trip, and array input."""
        rng = np.random.default_rng(1)
        angles = rng.uniform([-np.pi, -np.pi / 2, -np.pi], [np.pi, np.pi / 2, np.pi], (50, 3))
        quats = np.array([euler2quat(*a) for a in angles])
        for a, q in zip(angles, quats):
            np.testing.assert_array_almost_equal(quat2euler(q), a)
        np.testing.assert_array_almost_equal(quat2euler(quats), angles)
        # the sign of the quaternion doesn't change the attitude
        np.testing.assert_array_almost_equal(quat2euler(-quats), angles)

if __name__ == "__main__":
    unittest.main()
