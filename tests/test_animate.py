# type: ignore

import unittest
import numpy as np
import os
import shutil
import sys 
sys.path.append('.')
from c4dynamics.rotmat import animate
from c4dynamics import rigidbody
import c4dynamics as c4d  


try: 
	import open3d as o3d
	o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)      
	OPEN3D_AVAILABLE = True
except ImportError: 
	OPEN3D_AVAILABLE = False 


class TestAnimateFunction(unittest.TestCase):

    def setUp(self):
        # Setup directories and test files
        self.test_dir = os.path.join('tests', '_out')
        os.makedirs(self.test_dir, exist_ok=True)
        self.model_file = os.path.join(self.test_dir, 'test_model.ply')
        
        # Create a mock model file
        with open(self.model_file, 'w') as f:
            f.write("Mock 3D model data")  # Simplified content for testing
        
        # Create a rigid body for testing
        self.rb = rigidbody()
        # Animate with directory path
        self.rb.theta = np.pi / 10
        self.rb.psi = np.pi / 10
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()
        self.rb.store()

    def tearDown(self):
        # Cleanup the test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)


    @unittest.skipUnless(OPEN3D_AVAILABLE, "Skipping Open3D tests because Open3D is not installed")
    def test_invalid_model_path(self):
        """Test if animate handles an invalid model path."""
        self.rb.store()
        self.rb.store()
        self.rb.store()
        with self.assertRaises(FileNotFoundError):
            animate(self.rb, 'invalid/path')

    @unittest.skipUnless(OPEN3D_AVAILABLE, "Skipping Open3D tests because Open3D is not installed")
    def test_empty_model_path(self):
        """Test if animate handles an empty model path."""
        self.rb.store()
        self.rb.store()
        self.rb.store()
        with self.assertRaises(FileNotFoundError):
            animate(self.rb, '')


    @unittest.skipUnless(OPEN3D_AVAILABLE, "Skipping Open3D tests because Open3D is not installed")
    @unittest.skipIf("DISPLAY" not in os.environ, "Skipping GUI test in headless mode")
    def test_single_model_file(self):
        """Test animate function with a single model file."""
        # Should run without errors
        animate(self.rb, self.model_file)


    @unittest.skipUnless(OPEN3D_AVAILABLE, "Skipping Open3D tests because Open3D is not installed")
    @unittest.skipIf("DISPLAY" not in os.environ, "Skipping GUI test in headless mode")
    def test_directory_of_models(self):
        """Test animate function with a directory of model files."""
        # Setup additional mock model files
        model_file2 = os.path.join(self.test_dir, 'test_model2.ply')
        with open(model_file2, 'w') as f:
            f.write("Mock 3D model data 2")

        animate(self.rb, self.test_dir)


    @unittest.skipUnless(OPEN3D_AVAILABLE, "Skipping Open3D tests because Open3D is not installed")
    def test_invalid_model_color(self):
        """Test animate function with invalid model color input."""
        self.rb.store()
        modelfile = c4d.datasets.d3_model('bunny')
        with self.assertRaises(ValueError):
            animate(self.rb, modelfile, modelcolor='invalid_color')


    @unittest.skipUnless(OPEN3D_AVAILABLE, "Skipping Open3D tests because Open3D is not installed")
    @unittest.skipIf("DISPLAY" not in os.environ, "Skipping GUI test in headless mode")
    def test_output_image_creation(self):
        """Test if output images are created when savedir is provided."""
        output_dir = os.path.join('tests', '_out', 'animate')
        animate(self.rb, self.model_file, savedir=output_dir)
        
        # Check if images are saved
        self.assertTrue(os.path.exists(output_dir))
        images = os.listdir(output_dir)
        self.assertTrue(any(img.endswith('.png') for img in images))
        
        # Cleanup
        shutil.rmtree(output_dir)

if __name__ == '__main__':
	unittest.main()
