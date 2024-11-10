# type: ignore

import unittest
import numpy as np
import sys 
sys.path.append('.')
from c4dynamics.eqm import int3, int6

class TestIntMethods(unittest.TestCase):

    def setUp(self):
        # Mock datapoint and rigidbody with minimal attributes for testing
        self.dp = type('datapoint', (object,)   
                        , {'X': np.zeros(6), 'mass': 1
                            , 'x': 0, 'y': 0, 'z': 0, 'vx': 0, 'vy': 0, 'vz': 0 
                                , 'update': lambda x: None})()
        self.rb = type('rigidbody', (object,)
                       , {'X': np.zeros(12), 'mass': 1, 'I': np.ones(3)
                            , 'x': 0, 'y': 0, 'z': 0, 'vx': 0, 'vy': 0, 'vz': 0 
                                , 'phi': 0, 'theta': 0, 'psi': 0, 'p': 0, 'q': 0, 'r': 0  
                                    , 'update': lambda x: None})()
        # Forces and moments for tests
        self.forces = np.array([1.0, -9.81, 0.0])
        self.moments = np.array([0.1, 0.0, 0.0])
        self.dt = 0.01  # Small time step for integration

    def test_int3_without_derivs(self):
        # Test int3 without returning derivatives
        X = int3(self.dp, self.forces, self.dt)
        self.assertIsInstance(X, np.ndarray)
        self.assertEqual(X.shape, (6,))
    
    def test_int3_with_derivs(self):
        # Test int3 with returning derivatives
        X, dxdt4 = int3(self.dp, self.forces, self.dt, derivs_out=True)
        self.assertIsInstance(X, np.ndarray)  # Expect X to be an ndarray, not float64
        self.assertEqual(X.shape, (6,))       # Expect shape to be (3,) for a 3D vector
        self.assertEqual(dxdt4.shape, (3,))
        

    def test_int6_without_derivs(self):
        # Test int6 without returning derivatives
        X = int6(self.rb, self.forces, self.moments, self.dt)
        self.assertIsInstance(X, np.ndarray)
        self.assertEqual(X.shape, (12,))
    
    def test_int6_with_derivs(self):
        # Test int6 with returning derivatives
        X, dxdt4 = int6(self.rb, self.forces, self.moments, self.dt, derivs_out=True)
        self.assertIsInstance(X, np.ndarray)
        self.assertEqual(X.shape, (12,))
        self.assertEqual(dxdt4.shape, (6,))

    def test_int3_invalid_inputs(self):
        # Test int3 with invalid inputs
        with self.assertRaises(TypeError):
            int3(self.dp, "invalid_forces", self.dt)  # Forces should be array-like

    def test_int6_invalid_inputs(self):
        # Test int6 with invalid inputs
        with self.assertRaises(TypeError):
            int6(self.rb, self.forces, "invalid_moments", self.dt)  # Moments should be array-like

if __name__ == '__main__':
    unittest.main()
