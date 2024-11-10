# type: ignore

import unittest
from unittest.mock import patch, MagicMock
import numpy as np
import cv2
import os 

import sys 
sys.path.append('.')
from c4dynamics.detectors import yolov3  # replace 'yolov3_module' with your actual module name
from c4dynamics import pixelpoint  # replace 'yolov3_module' with your actual module name

MODEL_SIZE = (416, 416, 3)

class TestYoloV3(unittest.TestCase):

    @patch("c4dynamics.datasets.nn_model")
    @patch("os.path.exists")
    @patch("cv2.dnn.readNetFromDarknet")  # Add this line
    def setUp(self, mock_readNet, mock_exists, mock_nn_model):
        # Mock the path to weights for initialization
        home_folder = os.path.expanduser("~")
        mock_nn_model.return_value = os.path.join(home_folder, 'AppData\\Local\\c4data\\yolov3.weights')
        mock_exists.return_value = True

        # Create a MagicMock instance for net
        mock_net = MagicMock()
        mock_net.getLayerNames.return_value = ['layer1', 'layer2', 'layer3']  # Example layer names
        mock_net.getUnconnectedOutLayers.return_value = [1, 2, 3]  # Example indices for unconnected layers
        mock_readNet.return_value = mock_net  # Return the mocked net

        self.yolo = yolov3()
        self.sample_frame = np.zeros((MODEL_SIZE[0], MODEL_SIZE[1], 3), dtype=np.uint8)
    
    def test_initialization_default_weights(self):
        # Check if initialization sets up the network
        self.assertGreater(len(self.yolo.ln), 0)  # This should now pass since ln has layers

        self.assertIsInstance(self.yolo.net, MagicMock)
        self.assertTrue(hasattr(self.yolo, 'ln'))
        self.assertGreater(len(self.yolo.ln), 0)
    
    def test_initialization_invalid_weights_path(self):
        # Check if FileNotFoundError is raised for a non-existent weights path
        with self.assertRaises(FileNotFoundError):
            yolov3(weights_path="invalid/path/to/weights")

    def test_threshold_getters_setters(self):
        # Test NMS threshold getter and setter
        self.yolo.nms_th = 0.6
        self.assertEqual(self.yolo.nms_th, 0.6)
        
        # Test confidence threshold getter and setter
        self.yolo.confidence_th = 0.7
        self.assertEqual(self.yolo.confidence_th, 0.7)
    
    @patch("cv2.dnn.blobFromImage")
    @patch("cv2.dnn_Net.forward")
    def test_detect(self, mock_forward, mock_blobFromImage):
        # Prepare mock forward pass output
        mock_forward.return_value = [np.random.rand(1, 85)]  # mock detection output
        mock_blobFromImage.return_value = np.zeros((1, 416, 416, 3), dtype=np.float32)

        # Mock detection: (confidence > threshold and valid bounding box)
        points = self.yolo.detect(self.sample_frame)
        
        # Check if points output is a list of `pixelpoint`
        self.assertIsInstance(points, list)
        for point in points:
            self.assertIsInstance(point, pixelpoint)
            self.assertTrue(hasattr(point, 'class_id'))
            self.assertTrue(hasattr(point, 'fsize'))
    
    def test_detect_empty_frame(self):
        # Test detect method with an empty frame, expecting no detections
        points = self.yolo.detect(self.sample_frame)
        self.assertEqual(points, [])  # No detections should be returned

if __name__ == "__main__":
    unittest.main(failfast = True)
