# type: ignore

import unittest
import numpy as np
import sys 
sys.path.append('.')
from c4dynamics import state, rigidbody  # Adjust import according to your project structure
from c4dynamics.sensors.seeker import seeker
from c4dynamics.sensors.radar import radar  # Replace with the actual module where radar is defined

class TestRadar(unittest.TestCase):

    def setUp(self):
        """Set up for radar tests."""
        self.origin = rigidbody()
        self.target = state(x = 100)  # Replace with an appropriate initialization for target
        self.ideal_radar = radar(origin=self.origin, isideal=True)
        self.noisy_radar = radar(origin=self.origin, isideal=False, rng_noise_std=1.0)

    def test_initialization(self):
        """Test initialization of radar class."""
        self.assertEqual(self.ideal_radar.rng_noise_std, 0.0)
        self.assertEqual(self.noisy_radar.rng_noise_std, 1.0)
        self.assertEqual(self.ideal_radar.range, 0.0)
        self.assertEqual(self.noisy_radar.range, 0.0)

    def test_measure_ideal(self):
        """Test measure method in ideal conditions."""
        azimuth, elevation, range_ = self.ideal_radar.measure(self.target, store=False)
        self.assertEqual(azimuth, 0.0)  # Assuming that the measure method returns None for az if conditions aren't met
        self.assertEqual(elevation, 0.0)
        self.assertEqual(range_, 100.0)

    def test_measure_noisy(self):
        """Test measure method with noise."""
        # Set up a mock or fake target state to ensure az and el can be computed
        # self.target = ... # configure your target appropriately
        
        # Assuming P method of radar sets the azimuth and elevation for the target
        np.random.seed(111)
        azimuth, elevation, range_ = self.noisy_radar.measure(self.target, store=False)
        self.assertIsNotNone(azimuth)
        self.assertIsNotNone(elevation)
        self.assertIsNotNone(range_)
        self.assertEqual(range_, self.noisy_radar.P(self.target) + self.noisy_radar.rng_noise_std * 1.4965537763705212)

    def test_measure_storing_params(self):
        """Test the storing of parameters."""
        self.noisy_radar.measure(self.target, store=True)
        # Here you would check if the parameters were stored correctly.
        # For example, you could check a stored values list or a specific storage mechanism.
    
    def test_measure_invalid_target(self):
        """Test measure method with invalid target."""
        invalid_target = None  # Invalid state
        with self.assertRaises(TypeError):
            self.noisy_radar.measure(invalid_target)

    def test_noise_effect(self):
        """Test that noise is applied correctly."""
        # np.random.seed(0)  # for reproducibility
        measured_range = self.noisy_radar.measure(self.target)[2]
        self.assertAlmostEqual(measured_range, 100.0, delta=self.noisy_radar.rng_noise_std * 6)

if __name__ == '__main__':
    unittest.main()
