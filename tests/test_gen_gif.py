import unittest
from unittest.mock import patch, call
import os
import sys 
sys.path.append('.')
import c4dynamics as c4d  
from c4dynamics import gif 
import warnings


class TestGifFunction(unittest.TestCase):


    @patch("os.listdir")
    @patch("imageio.v2.imread")
    @patch("imageio.mimsave")
    @patch("os.path.join")
    def test_gif_creation_with_default_duration(self, mock_join, mock_mimsave, mock_imread, mock_listdir):
        """Test GIF creation with default duration and valid images in the directory."""
        
        # Mock the return value of os.listdir
        mock_listdir.return_value = ["image1.png", "image2.jpg", "image3.png", "image4.png"]
        
        # Mock what imread returns
        mock_imread.side_effect = lambda x: f"image data for {x}"

        # Mock os.path.join to return the correct file path
        mock_join.side_effect = lambda *args: "/".join(args)


        # Call the gif function
        gif("test_dir", "test_gif")

        # Verify that mimsave was called
        self.assertTrue(mock_mimsave.called)
        
        # Create expected calls wrapped in call()
        expected_calls = [
            call("test_dir/image1.png"),
            call("test_dir/image2.jpg"),
            call("test_dir/image3.png"),
            call("test_dir/image4.png"),
        ]
        
        # Verify that imread was called with the expected arguments
        mock_imread.assert_has_calls(expected_calls)



    @patch("os.listdir")
    @patch("imageio.v2.imread")  # Mock the image read function
    @patch("imageio.mimsave")
    def test_non_image_files_filtered(self, mock_mimsave, mock_imread, mock_listdir):
        """Test that non-image files are correctly filtered out."""
        # Directory contains mixed file types
        mock_listdir.return_value = ["image1.png", "document.pdf", "image2.jpg", "notes.txt"]

        # Mock imread to prevent reading from the filesystem
        mock_imread.side_effect = lambda x: f"image data for {x}"  # Just return a dummy response

        # Call the gif function
        gif("test_dir", "test_gif")

        # Confirm only 2 images are processed (png and jpg files)
        self.assertEqual(mock_imread.call_count, 2)





    @patch("os.listdir")
    @patch("imageio.mimsave")
    @patch("os.path.isfile")
    def test_empty_directory(self, mock_isfile, mock_mimsave, mock_listdir):
        """Test GIF creation with an empty directory."""
        mock_listdir.return_value = []  # Empty directory

        mock_isfile.return_value = True

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", c4d.c4warn)
            gif("test_dir", "test_gif")
            
        # mimsave should not be called since there are no images to process
        mock_mimsave.assert_not_called()


    @patch("os.listdir")
    @patch("imageio.v2.imread")  # Mock the image read function
    @patch("imageio.mimsave")
    def test_gif_name_auto_extension(self, mock_mimsave, mock_imread, mock_listdir):
        """Test GIF file name gets .gif extension if not provided."""
        
        # Mock the return value of os.listdir to simulate existing image files
        mock_listdir.return_value = ["image1.png", "image2.jpg"]

        # Mock what imread returns; you can return any placeholder data
        mock_imread.side_effect = lambda x: f"image data for {x}"

        # Call the gif function
        gif("test_dir", "test_gif_no_ext")

        # Verify that mimsave was called with the correct file name
        args, _ = mock_mimsave.call_args
        self.assertTrue(args[0].endswith("test_gif_no_ext.gif"))




    def tearDown(self):
        """Clean up any test artifacts if needed."""
        pass


if __name__ == "__main__":
    unittest.main()
