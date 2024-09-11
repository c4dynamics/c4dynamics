import unittest
import os, sys
import hashlib
from unittest.mock import patch, mock_open
import pooch
sys.path.append('.')
from c4dynamics.data._manager import (CACHE_DIR, sha256, clear_cache, image, video, nn_model, d3_model)


class TestDatasetFunctions(unittest.TestCase):

  def setUp(self):
    # Ensure cache directory exists
    os.makedirs(CACHE_DIR, exist_ok=True)

  def tearDown(self):
    # Clear the cache after each test
    clear_cache()

  def test_sha256(self):
    # Mock a file and its content
    mock_content = b"Test content"
    with patch("builtins.open", mock_open(read_data=mock_content)):
      with patch("os.path.isfile", return_value=True):
        with patch("os.path.exists", return_value=True):
          # Write mock content to a file
          test_file = os.path.join(CACHE_DIR, "testfile.txt")
          with open(test_file, "wb") as f:
            f.write(mock_content)

          # Calculate the sha256 hash
          expected_hash = hashlib.sha256(mock_content).hexdigest()
          self.assertEqual(sha256(test_file), expected_hash)

  def test_clear_cache(self):
    # Create a dummy file in cache directory
    dummy_file = os.path.join(CACHE_DIR, "dummy.txt")
    with open(dummy_file, "w") as f:
      f.write("dummy data")

    # Ensure the file exists
    self.assertTrue(os.path.exists(dummy_file))

    # Clear cache
    clear_cache()

    # Check if the cache is empty
    self.assertFalse(os.path.exists(dummy_file))

  def test_clear_cache_specific_file(self):
    # Create dummy files for testing
    dummy_file_f16 = os.path.join(CACHE_DIR, 'f16', 'dummy.txt')
    dummy_file_yolov3 = os.path.join(CACHE_DIR, 'yolov3.cfg')
    os.makedirs(os.path.dirname(dummy_file_f16), exist_ok = True)
    with open(dummy_file_f16, "w") as f:
      f.write("dummy data for f16")
    with open(dummy_file_yolov3, "w") as f:
      f.write("dummy data for yolov3")

    # Ensure the files exist
    self.assertTrue(os.path.exists(dummy_file_f16))
    self.assertTrue(os.path.exists(dummy_file_yolov3))

    # Clear specific cache
    clear_cache('f16')
    clear_cache('yolov3')

    # Check if the files were removed
    self.assertFalse(os.path.exists(dummy_file_f16))
    self.assertFalse(os.path.exists(dummy_file_yolov3))

  @patch("pooch.create.fetch", return_value=os.path.join(CACHE_DIR, "planes.png"))
  def test_image_fetch(self, mock_fetch):
    # Test image fetch
    image_file = image('planes')
    self.assertEqual(image_file, os.path.join(CACHE_DIR, "planes.png"))
    mock_fetch.assert_called_once_with("planes.png")

  @patch("pooch.create.fetch", return_value=os.path.join(CACHE_DIR, "aerobatics.mp4"))
  def test_video_fetch(self, mock_fetch):
    # Test video fetch
    video_file = video('aerobatics')
    self.assertEqual(video_file, os.path.join(CACHE_DIR, "aerobatics.mp4"))
    mock_fetch.assert_called_once_with("aerobatics.mp4")

  @patch("pooch.create.fetch", return_value=os.path.join(CACHE_DIR, "yolov3.cfg"))
  def test_nn_model_fetch(self, mock_fetch):
    # Test neural network model fetch
    nn_file = nn_model('yolov3')
    self.assertEqual(nn_file, CACHE_DIR)
    self.assertEqual(mock_fetch.call_count, 3)

  @patch("pooch.create.fetch", return_value=os.path.join(CACHE_DIR, 'f16', 'Aileron_A_F16.stl'))
  def test_d3_model_fetch_f16(self, mock_fetch):
    # Test 3D model fetch for F16
    d3_file = d3_model('f16')
    self.assertTrue(d3_file.endswith('f16'))
    self.assertEqual(mock_fetch.call_count, 9)

  @patch("pooch.create.fetch", return_value=os.path.join(CACHE_DIR, "bunny.pcd"))
  def test_d3_model_fetch_bunny(self, mock_fetch):
    # Test 3D model fetch for bunny
    d3_file = d3_model('bunny')
    self.assertEqual(d3_file, os.path.join(CACHE_DIR, "bunny.pcd"))
    mock_fetch.assert_called_once_with("bunny.pcd")

  @patch("pooch.create.fetch", return_value=os.path.join(CACHE_DIR, "bunny_mesh.ply"))
  def test_d3_model_fetch_bunnymesh(self, mock_fetch):
    # Test 3D model fetch for bunny mesh
    d3_file = d3_model('bunnymesh')
    self.assertEqual(d3_file, os.path.join(CACHE_DIR, "bunny_mesh.ply"))
    mock_fetch.assert_called_once_with("bunny_mesh.ply")


if __name__ == '__main__':
  unittest.main()



