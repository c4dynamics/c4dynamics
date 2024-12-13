import unittest
import numpy as np
from scipy.special import erfinv
from math import isclose
import sys 
sys.path.append('.')
import c4dynamics as c4d  # Import your custom module that contains the aliased functions

class TestC4DynamicsMathFunctions(unittest.TestCase):

    def test_sind_cosd_tand(self):
        """Test sind, cosd, and tand degree-based trigonometric functions."""
        self.assertAlmostEqual(c4d.sind(90), 1.0, places=5)
        self.assertAlmostEqual(c4d.cosd(0), 1.0, places=5)
        self.assertAlmostEqual(c4d.tand(45), 1.0, places=5)

    def test_asind_acosd_atand(self):
        """Test asind, acosd, and atand inverse trigonometric functions in degrees."""
        self.assertAlmostEqual(c4d.asind(1), 90.0, places=5)
        self.assertAlmostEqual(c4d.acosd(1), 0.0, places=5)
        self.assertAlmostEqual(c4d.atand(1), 45.0, places=5)

    def test_atan2d(self):
        """Test atan2d, a degree-based version of arctan2."""
        self.assertAlmostEqual(c4d.atan2d(1, 1), 45.0, places=5)
        self.assertAlmostEqual(c4d.atan2d(0, -1), 180.0, places=5)

    def test_sqrt(self):
        """Test sqrt function alias."""
        self.assertEqual(c4d.sqrt(4), 2.0)
        self.assertEqual(c4d.sqrt(0), 0.0)

    def test_norm(self):
        """Test norm function alias."""
        vector = np.array([3, 4])
        self.assertEqual(c4d.norm(vector), 5.0)

    # def test_mrandn(self):
    #     """Test mrandn to check that it generates approximately normal distributed values."""
    #     n = 1000000  # Use a large sample for a statistically meaningful mean
    #     sample = c4d.mrandn(n)
    #     mean = np.mean(sample)
    #     stddev = np.std(sample)
    #     # Expect mean around 0 and stddev around sqrt(2), based on the implementation
    #     self.assertTrue(isclose(mean, 0, abs_tol=0.01))
    #     self.assertTrue(isclose(stddev, np.sqrt(2), rel_tol=0.01))

    def test_basic_trig_aliases(self):
        """Test basic trigonometric function aliases (sin, cos, tan)."""
        self.assertAlmostEqual(c4d.sin(np.pi / 2), 1.0, places=5)
        self.assertAlmostEqual(c4d.cos(0), 1.0, places=5)
        self.assertAlmostEqual(c4d.tan(np.pi / 4), 1.0, places=5)

    def test_basic_arctrig_aliases(self):
        """Test basic inverse trigonometric function aliases (asin, acos, atan)."""
        self.assertAlmostEqual(c4d.asin(1), np.pi / 2, places=5)
        self.assertAlmostEqual(c4d.acos(1), 0, places=5)
        self.assertAlmostEqual(c4d.atan(1), np.pi / 4, places=5)

    def tearDown(self):
        """Clean up resources if needed after tests."""
        pass


if __name__ == "__main__":
    unittest.main()
