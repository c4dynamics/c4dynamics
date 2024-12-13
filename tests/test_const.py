import unittest
import numpy as np
import sys 
sys.path.append('.')
from c4dynamics import pi, g_ms2, g_fts2, ft2m, lbft2tokgm2, r2d, d2r, kmh2ms, k2ms 
class TestC4DynamicsConstants(unittest.TestCase):

    def test_pi(self):
        self.assertAlmostEqual(pi, np.pi, places=10, msg="pi should match numpy's pi constant.")

    def test_gravity_constants(self):
        self.assertAlmostEqual(g_ms2, 9.80665, places=5, msg="g_ms2 should be 9.80665")
        self.assertAlmostEqual(g_fts2, 32.1740, places=4, msg="g_fts2 should be 32.1740")

    def test_conversion_constants(self):
        self.assertAlmostEqual(ft2m, 0.3048, places=4, msg="ft2m should be 0.3048")
        self.assertAlmostEqual(lbft2tokgm2, 4.88243, places=5, msg="lbft2tokgm2 should be 4.88243")
        self.assertAlmostEqual(r2d, 180 / np.pi, places=10, msg="r2d should be 180 / pi")
        self.assertAlmostEqual(d2r, np.pi / 180, places=10, msg="d2r should be pi / 180")
        self.assertAlmostEqual(kmh2ms, 1000 / 3600, places=10, msg="kmh2ms should be 1000 / 3600")
        self.assertAlmostEqual(k2ms, 1852 / 3600, places=10, msg="k2ms should be 1852 / 3600")

if __name__ == "__main__":
    unittest.main()
