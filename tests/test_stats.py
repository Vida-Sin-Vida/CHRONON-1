
import unittest
import numpy as np
from chronon_core.stats import calculate_slope_epsilon_phi

class TestStats(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)
        
    def test_wls_linear_fit(self):
        """Test standard WLS fit on clean data."""
        # Y = 2*X + 1 + small noise
        X = np.linspace(0, 10, 20)
        sigma_Y = np.ones(20) * 0.1
        noise = np.random.normal(0, 0.1, 20)
        Y = 2.0 * X + 1.0 + noise
        
        res = calculate_slope_epsilon_phi(X, Y, sigma_Y)
        
        self.assertAlmostEqual(res['slope'], 2.0, delta=0.1)
        self.assertTrue(res['pval'] < 0.05)
        self.assertEqual(res['model_summary'], "WLS_HAC")
        self.assertIsNone(res['switch_reason'])
        
    def test_deming_trigger(self):
        """Test that Deming is triggered when X uncertainty is high."""
        X = np.linspace(0, 10, 20)
        Y = 2.0 * X 
        sigma_Y = np.ones(20) * 0.1
        sigma_X = np.ones(20) * 2.0 
        
        res = calculate_slope_epsilon_phi(X, Y, sigma_Y, sigma_X)
        
        # Check if it switched
        self.assertEqual(res['model_summary'], 'DEMING_WTLS')
        self.assertIn("uncertainty", res['switch_reason'])

    def test_empty_input(self):
        """Test robustness against empty input."""
        res = calculate_slope_epsilon_phi([], [], [])
        # If empty, stats code might raise or return 0/NaN depending on linalg
        # Current stats.py fit_free handles linalg error -> returns 0.
        # Let's just ensure it doesn't crash and returns valid dict structure
        self.assertIn('slope', res)

if __name__ == '__main__':
    unittest.main()
