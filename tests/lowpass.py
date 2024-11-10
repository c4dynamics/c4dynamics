# type: ignore

import unittest
import numpy as np

import sys
sys.path.append('')
from c4dynamics.filters import lowpass 

class TestLowpassFilter(unittest.TestCase):

    def test_initialization_with_alpha(self):
        alpha = 0.5
        lp_filter = lowpass(alpha=alpha)
        self.assertEqual(lp_filter.alpha, alpha)
        self.assertEqual(lp_filter.y, 0)

    def test_initialization_with_dt_tau(self):
        dt = 0.1
        tau = 1.0
        lp_filter = lowpass(dt=dt, tau=tau)
        expected_alpha = dt / tau
        self.assertEqual(lp_filter.alpha, expected_alpha)
        self.assertEqual(lp_filter.y, 0)

    def test_initialization_with_y0(self):
        alpha = 0.5
        y0 = 10
        lp_filter = lowpass(alpha=alpha, y0=y0)
        self.assertEqual(lp_filter.alpha, alpha)
        self.assertEqual(lp_filter.y, y0)

    def test_initialization_without_parameters(self):
        with self.assertRaises(ValueError):
            lp_filter = lowpass()

    def test_sample(self):
        alpha = 0.5
        lp_filter = lowpass(alpha=alpha)
        x = 1.0
        y = lp_filter.sample(x)
        expected_y = (1 - alpha) * 0 + alpha * x
        self.assertEqual(y, expected_y)
        self.assertEqual(lp_filter.y, expected_y)

    def test_multiple_samples(self):
        alpha = 0.1
        lp_filter = lowpass(alpha=alpha)
        inputs = [1, 2, 3, 4, 5]
        expected_outputs = []
        y = 0
        for x in inputs:
            y = (1 - alpha) * y + alpha * x
            expected_outputs.append(y)
        for i, x in enumerate(inputs):
            output = lp_filter.sample(x)
            self.assertAlmostEqual(output, expected_outputs[i])

if __name__ == '__main__':
    unittest.main()
