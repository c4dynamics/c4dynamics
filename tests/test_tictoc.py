import unittest
import time
import sys 
sys.path.append('.')
import c4dynamics as c4d  # Assuming your functions are in c4dynamics
from unittest.mock import patch
import io


class TestTimingFunctions(unittest.TestCase):

    def test_tic_toc_basic(self):
        """Test basic functionality of tic and toc."""
        start = c4d.tic()
        time.sleep(0.1)
        elapsed = c4d.toc(show=False)
        self.assertAlmostEqual(elapsed, 0.1, places=0)

    def test_toc_output(self):
      """Test that toc prints output correctly."""
      c4d.tic()  # Start the timer
      time.sleep(0.0001)
      # Capture printed output from toc()
      with patch('sys.stdout', new=io.StringIO()) as fake_stdout:
        elapsed = c4d.toc()  # Stop the timer and print elapsed time
        output = fake_stdout.getvalue().strip()
        
        # Verify that output contains a non-zero elapsed time
        self.assertTrue(output)
        # self.assertIn("Elapsed time:", output)  # Customize this based on expected output format
        
        # Additionally, check the return value if toc() returns elapsed time
        self.assertGreater(elapsed, 0, "Elapsed time should be positive.")


if __name__ == "__main__":
    unittest.main()
