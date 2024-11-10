# type: ignore

import unittest
import numpy as np
import sys 
sys.path.append('.')
from c4dynamics import datapoint, c4warn  # Update with the correct import path

class TestDatapoint(unittest.TestCase):

    def setUp(self):
        """Set up a basic datapoint instance for testing."""
        self.dp = datapoint(x=1.0, y=2.0, z=3.0, vx=4.0, vy=5.0, vz=6.0)

    def test_initialization(self):
        """Test initialization of datapoint with given coordinates."""
        self.assertEqual(self.dp.x, 1.0)
        self.assertEqual(self.dp.y, 2.0)
        self.assertEqual(self.dp.z, 3.0)
        self.assertEqual(self.dp.vx, 4.0)
        self.assertEqual(self.dp.vy, 5.0)
        self.assertEqual(self.dp.vz, 6.0)

    def test_mass_property(self):
        """Test mass property of the datapoint."""
        self.assertEqual(self.dp.mass, 1)  # Default mass
        self.dp.mass = 10
        self.assertEqual(self.dp.mass, 10)

    def test_data_method(self):
        """Test the data method for accessing stored state."""
        self.dp.store(t=0)
        self.dp.store(t=1)
        self.assertEqual(self.dp.data('t').tolist(), [0, 1])
        self.assertTrue(np.array_equal(self.dp.data('x')[1], np.array([1.0, 1.0])))

    def test_integration_method(self):
        """Test the integration method (mock behavior for testing)."""
        forces = np.array([0.0, 0.0, 0.0])  # Mock forces
        dt = 0.1  # Time step
        acc = self.dp.inteqm(forces, dt)
        self.assertIsInstance(acc, np.ndarray)  # Check if acceleration is returned as numpy array

    def test_plot_function(self):
        """Test the plotting functionality."""
        import matplotlib.pyplot as plt
        
        self.dp.store(t=0)
        self.dp.store(t=1)
        self.dp.plot('x')  # Should not raise errors and produce a plot
        plt.close()  # Close the plot after testing to avoid displaying

    def test_invalid_plot_variable(self):
        """Test that an error is raised for an invalid plot variable."""
        with self.assertWarns(c4warn):
            self.dp.plot('invalid_var')

    def test_plot_with_custom_ax(self):
        """Test the plot function with a custom Axes object."""
        import matplotlib.pyplot as plt
        
        fig, ax = plt.subplots()
        self.dp.store(t=0)
        self.dp.store(t=1)
        self.dp.plot('x', ax=ax)
        plt.close(fig)  # Close the plot after testing to avoid displaying

    def test_storeparams(self):
        """Test the storeparams method."""
        self.dp.storeparams('mass', t=0)
        self.assertIn(0, self.dp._prmdata['mass'][0])  # Check that time is stored

    def test_timestate(self):
        """Test the timestate method for retrieving state at a specific time."""
        self.dp.store(t=0)
        self.dp.store(t=1)
        X = self.dp.timestate(0)
        self.assertTrue(np.array_equal(X, np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])))

    # def test_repr(self):
    #     """Test the __repr__ method."""
    #     expected_repr = "datapoint(x=1.0, y=2.0, z=3.0, vx=4.0, vy=5.0, vz=6.0)"
    #     self.assertEqual(repr(self.dp), expected_repr)

if __name__ == '__main__':
    unittest.main()
