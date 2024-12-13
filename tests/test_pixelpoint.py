# type: ignore

import unittest
import numpy as np
import sys 
sys.path.append('.')
from c4dynamics import pixelpoint  # Adjust import as necessary

class TestPixelPoint(unittest.TestCase):

    def setUp(self):
        """Set up a pixelpoint instance for testing."""
        self.pp = pixelpoint(x=10, y=20, w=30, h=40)

    def test_initialization(self):
        """Test the initialization of pixelpoint."""
        self.assertEqual(self.pp.x, 10)
        self.assertEqual(self.pp.y, 20)
        self.assertEqual(self.pp.w, 30)
        self.assertEqual(self.pp.h, 40)

    def test_fsize_property(self):
        """Test the fsize property."""
        self.pp.fsize = (800, 600)
        self.assertEqual(self.pp.fsize, (800, 600))

        with self.assertRaises(ValueError):
            self.pp.fsize = (800,)  # Should raise ValueError

    def test_class_id_property(self):
        """Test the class_id property."""
        self.pp.class_id = 'car'
        self.assertEqual(self.pp.class_id, 'car')

        with self.assertRaises(TypeError):
            self.pp.class_id = 123  # Should raise TypeError

    def test_box_property(self):
        """Test the box property."""
        expected_box = [(10 - 30 / 2, 20 - 40 / 2), (10 + 30 / 2, 20 + 40 / 2)]
        self.assertEqual(self.pp.box, expected_box)

    def test_Xpixels_property(self):
        """Test the Xpixels property."""
        self.pp.fsize = (800, 600)  # Set frame size
        expected_Xpixels = np.array([
            10 * 800,  # x
            20 * 600,  # y
            30 * 800,  # w
            40 * 600   # h
        ], dtype=np.int32)
        np.testing.assert_array_equal(self.pp.Xpixels, expected_Xpixels)

    def test_boxcenter_static_method(self):
        """Test the boxcenter static method."""
        box = [(0, 0, 10, 10)]
        expected_center = np.array([[5.0, 5.0]])
        np.testing.assert_array_equal(pixelpoint.boxcenter(box), expected_center)

    def test_video_detections_method(self):
        """Test the video_detections method."""
        # Assuming you have a video file for testing, you would provide a valid path here.
        # vidpath = 'path_to_test_video.mp4'
        # detections = pixelpoint.video_detections(vidpath, tf=10, storepath=None)
        # self.assertIsInstance(detections, dict)  # Check if detections are returned as a dict
        pass  # Uncomment and complete when a suitable video is available

if __name__ == '__main__':
    unittest.main()
