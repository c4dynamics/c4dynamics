# type: ignore

import unittest
import numpy as np
import matplotlib.pyplot as plt
import cv2
import sys 
import tempfile
from unittest.mock import patch
sys.path.append('.')
import c4dynamics as c4d  # Assuming c4dynamics contains your functions

class TestPlotFunctions(unittest.TestCase):

    def setUp(self):
        self.fig, self.ax = c4d._figdef()

    def tearDown(self):
        plt.close(self.fig)

    def test_figdef(self):
        """Test _figdef creates a figure with correct properties."""
        self.assertEqual(self.fig.dpi, 200)
        self.assertAlmostEqual(self.fig.get_size_inches()[1] / self.fig.get_size_inches()[0], 1080 / 1920, places=5)

    def test_plotdefaults(self):
        """Test plotdefaults sets axis properties correctly."""
        c4d.plotdefaults(self.ax, title="Test Title", xlabel="X Axis", ylabel="Y Axis", fontsize=10)
        self.assertEqual(self.ax.get_title(), "Test Title")
        self.assertEqual(self.ax.get_xlabel(), "X Axis")
        self.assertEqual(self.ax.get_ylabel(), "Y Axis")
        self.assertTrue(self.ax.yaxis.get_major_formatter().get_useOffset() == False)


if __name__ == "__main__":
    unittest.main()
