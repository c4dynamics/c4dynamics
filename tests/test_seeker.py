# type: ignore

import unittest
import numpy as np
from unittest.mock import MagicMock
import sys 
sys.path.append('.')
import c4dynamics as c4d
from c4dynamics.sensors import seeker

class TestSeeker(unittest.TestCase):

    def setUp(self):
        """Set up any necessary objects or parameters before each test."""
        self.origin = MagicMock(spec=c4d.rigidbody)
        self.origin.X = np.zeros(12)
        self.target = MagicMock(spec=c4d.state)
        self.target.Position = np.array([1, 1, 1])  # Arbitrary position
        self.target.cartesian.return_value = True  # Mock cartesian method to return True

    def test_initialization_with_origin(self):
        """Test seeker initialization with origin and default parameters."""
        seeker_instance = seeker(origin=self.origin)
        np.testing.assert_array_equal(seeker_instance.X, self.origin.X)
        self.assertIsInstance(seeker_instance, seeker)

    # def test_initialization_without_origin(self):
    #     """Test seeker initialization without origin parameter."""
    #     seeker_instance = seeker()
    #     self.assertIsNone(getattr(seeker_instance, 'X', None))

    def test_attributes(self):
        """Test that bias and scale factor properties are set and retrieved correctly."""
        seeker_instance = seeker()
        
        # Test setting and getting bias
        seeker_instance.bias = 0.5
        self.assertEqual(seeker_instance.bias, 0.5)

        # Test setting and getting scale_factor
        seeker_instance.scale_factor = 1.1
        self.assertEqual(seeker_instance.scale_factor, 1.1)

    def test_errors_model(self):
        """Test the errors model that modifies scale factor and bias."""
        seeker_instance = seeker()
        initial_scale_factor = seeker_instance._scale_factor
        initial_bias = seeker_instance._bias

        seeker_instance._errors_model()

        # Check that the scale factor and bias are updated (likely different due to randomness)
        self.assertNotEqual(seeker_instance._scale_factor, initial_scale_factor)
        self.assertNotEqual(seeker_instance._bias, initial_bias)

    def test_measure_method_with_valid_target(self):
        """Test the measure method with a valid target and default time."""
        seeker_instance = seeker(origin=self.origin, dt=1)

        az, el = seeker_instance.measure(target=self.target, t=0, store=True)

        # Assert az and el are within expected types and are floats
        self.assertIsInstance(az, float)
        self.assertIsInstance(el, float)

    def test_measure_method_invalid_target(self):
        """Test the measure method with an invalid target type."""
        seeker_instance = seeker(origin=self.origin)
        invalid_target = MagicMock()  # Does not have the required cartesian attribute
        invalid_target.cartesian.return_value = None  # or 0, depending on what's expected

        with self.assertRaises(TypeError):
            seeker_instance.measure(invalid_target)

    def test_warning_for_extra_kwargs(self):
        """Test that a warning is raised for invalid kwargs."""
        with self.assertWarns(UserWarning):
            seeker_instance = seeker(extra_kwarg=1)

    def test_measure_time_interval(self):
        """Test that measure does not update if time interval is less than dt."""
        seeker_instance = seeker(origin=self.origin, dt=1)
        
        # Initial measurement at t=0
        seeker_instance.measure(target=self.target, t=0)
        
        # Try measuring at t=0.5, should return None, None
        az, el = seeker_instance.measure(target=self.target, t=0.5)
        self.assertIsNone(az)
        self.assertIsNone(el)

    def test_measure_noise_effect(self):
        """Test that noise_std affects azimuth and elevation measurements."""
        seeker_instance = seeker(origin=self.origin, dt=1, noise_std=0.5)

        # Run measure several times to see effect of noise
        az_values = []
        el_values = []
        for _ in range(10):
            az, el = seeker_instance.measure(target=self.target, t=seeker_instance._lastsample + seeker_instance.dt)
            az_values.append(az)
            el_values.append(el)
        
        # Check that we have variability in az and el due to noise
        self.assertGreater(np.std(az_values), 0)
        self.assertGreater(np.std(el_values), 0)

if __name__ == "__main__":
    unittest.main()
