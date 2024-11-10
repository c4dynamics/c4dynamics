# type: ignore

import unittest
import numpy as np
import sys 
sys.path.append('.')
from c4dynamics import state  # Adjust import based on your structure

class TestState(unittest.TestCase):

    def setUp(self):
        """Set up a default state instance for testing."""
        self.state_instance = state(x=1.0, y=2.0, z=3.0, vx=0.5, vy=1.5, vz=2.5)

    def test_initialization(self):
        """Test if the state instance is initialized correctly."""
        self.assertEqual(self.state_instance.X0.tolist(), [1.0, 2.0, 3.0, 0.5, 1.5, 2.5])
        self.assertEqual(self.state_instance._didx['x'], 1)
        self.assertEqual(self.state_instance._didx['y'], 2)
        self.assertEqual(self.state_instance._didx['z'], 3)

    def test_reserved_keys(self):
        """Test initialization with reserved keys raises ValueError."""
        with self.assertRaises(ValueError):
            state(X=1.0)

    def test_X_property(self):
        """Test the X property getter and setter."""
        self.assertTrue(np.array_equal(self.state_instance.X, np.array([1.0, 2.0, 3.0, 0.5, 1.5, 2.5])))
        
        self.state_instance.X = np.array([4.0, 5.0, 6.0, 0.6, 1.6, 2.6])
        self.assertTrue(np.array_equal(self.state_instance.X, np.array([4.0, 5.0, 6.0, 0.6, 1.6, 2.6])))

    def test_X_property_value_error(self):
        """Test the setter for X raises ValueError on incorrect length."""
        with self.assertRaises(ValueError):
            self.state_instance.X = np.array([1.0, 2.0])  # Shorter length

        with self.assertRaises(ValueError):
            self.state_instance.X = np.array([1.0, 2.0, 3.0, 4.0])  # Longer length

    def test_addvars(self):
        """Test adding new variables with addvars method."""
        self.state_instance.addvars(vx_new=1.0, vy_new=2.0)
        self.assertEqual(self.state_instance._didx['vx_new'], 7)  # It should be the next index
        self.assertTrue(np.array_equal(self.state_instance.X0, np.array([1.0, 2.0, 3.0, 0.5, 1.5, 2.5, 1.0, 2.0])))

    def test_store(self):
        """Test the store method."""
        self.state_instance.store(t=0)
        self.assertEqual(len(self.state_instance._data), 1)
        self.assertEqual(self.state_instance._data[0], [0] + self.state_instance.X.tolist())

    def test_plot(self):
        """Test the plot method (mocked for unit tests)."""
        import matplotlib.pyplot as plt
        ax = self.state_instance.plot('x', scale=1, darkmode=False)
        self.assertIsNone(ax)  # Ensure a valid axis is returned
        self.state_instance.store()
        self.state_instance.store()
        ax = self.state_instance.plot('x', scale=1, darkmode=False)
        self.assertIsNotNone(ax)  # Ensure a valid axis is returned


    def test_data(self):
        """Test the data method."""
        self.state_instance.store(t=0)
        data_t, data_x = self.state_instance.data('x')
        self.assertEqual(data_t.tolist(), [0])
        self.assertEqual(data_x.tolist(), [1.0])

    def test_timestate(self):
        """Test the timestate method."""
        self.state_instance.store(t=0)
        X_at_time = self.state_instance.timestate(0)
        self.assertTrue(np.array_equal(X_at_time, np.array([1.0, 2.0, 3.0, 0.5, 1.5, 2.5])))

    def test_position_property(self):
        """Test the position property."""
        position = self.state_instance.position
        self.assertTrue(np.array_equal(position, np.array([1.0, 2.0, 3.0])))

    def test_velocity_property(self):
        """Test the velocity property."""
        velocity = self.state_instance.velocity
        self.assertTrue(np.array_equal(velocity, np.array([0.5, 1.5, 2.5])))

    def test_norm_property(self):
        """Test the norm property."""
        norm_value = self.state_instance.norm
        self.assertAlmostEqual(norm_value, np.linalg.norm(self.state_instance.X))

    def test_normalize_property(self):
        """Test the normalize property."""
        normalized = self.state_instance.normalize
        norm_value = np.linalg.norm(normalized)
        self.assertAlmostEqual(norm_value, 1.0)

    def test_P_method(self):
        """Test the P method."""
        other_state = state(x=4.0, y=5.0, z=6.0)
        distance = self.state_instance.P(other_state)
        self.assertAlmostEqual(distance, np.sqrt((1.0 - 4.0) ** 2 + (2.0 - 5.0) ** 2 + (3.0 - 6.0) ** 2))

    def test_cartesian_method(self):
        """Test the cartesian method."""
        is_cartesian = self.state_instance.cartesian()
        self.assertTrue(is_cartesian)

if __name__ == '__main__':
    unittest.main()
