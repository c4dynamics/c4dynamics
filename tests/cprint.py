import unittest
import io
import sys
from contextlib import redirect_stdout
sys.path.append('.')
from c4dynamics import cprint 

class TestCPrint(unittest.TestCase):

    def setUp(self):
        """Set up a stream to capture stdout output."""
        self.output = io.StringIO()

    def test_default_color(self):
        """Test cprint with default color (white)."""
        with redirect_stdout(self.output):
            cprint("Test")
        expected = "\033[37mTest\033[0m\n"
        self.assertEqual(self.output.getvalue(), expected)

    def test_color_red(self):
        """Test cprint with red color."""
        with redirect_stdout(self.output):
            cprint("Test", color="r")
        expected = "\033[31mTest\033[0m\n"
        self.assertEqual(self.output.getvalue(), expected)

    def test_color_green(self):
        """Test cprint with green color."""
        with redirect_stdout(self.output):
            cprint("Test", color="g")
        expected = "\033[32mTest\033[0m\n"
        self.assertEqual(self.output.getvalue(), expected)

    def test_invalid_color(self):
        """Test cprint with an invalid color, expecting a KeyError."""
        with self.assertRaises(KeyError):
            cprint("Test", color="invalid_color")

    # def test_bold_text(self):
    #     """Test cprint with bold formatting."""
    #     with redirect_stdout(self.output):
    #         cprint("Test", color="g", bold=True)
    #     expected = "\033[1;32mTest\033[0m\n"
    #     self.assertEqual(self.output.getvalue(), expected)

    # def test_italic_text(self):
    #     """Test cprint with italic formatting."""
    #     with redirect_stdout(self.output):
    #         cprint("Test", color="b", italic=True)
    #     expected = "\033[3;34mTest\033[0m\n"
    #     self.assertEqual(self.output.getvalue(), expected)

    def tearDown(self):
        """Clean up the captured output."""
        self.output.close()


if __name__ == "__main__":
    unittest.main()
