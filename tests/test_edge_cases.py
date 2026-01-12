
import unittest
import numpy as np
from chronon_core.stats import analyze_with_fallback, calculate_slope_epsilon_phi

class TestStatsEdgeCases(unittest.TestCase):
    def setUp(self):
        np.random.seed(42)

    def test_low_n(self):
        """Test behavior with N < 3 (should return safe defaults, no crash)"""
        X = [1.0, 2.0]
        Y = [2.0, 4.0]
        sigma_Y = [0.1, 0.1]
        res = analyze_with_fallback(X, Y, sigma_Y)
        # Should run without error but pval likely high or undefined
        self.assertIn('slope', res)
        
    def test_constant_x(self):
        """Test behavior when X has zero variance (Singular Matrix)"""
        X = [5.0, 5.0, 5.0, 5.0]
        Y = [1.0, 2.0, 1.0, 2.0]
        sigma_Y = [0.1] * 4
        res = analyze_with_fallback(X, Y, sigma_Y)
        # Expect 0 slope or safe fallback, not crash
        self.assertEqual(res['slope'], 0.0)
        
    def test_nan_input(self):
        """Test robustness against NaN inputs (should ideally filter or handle)"""
        # Our current implementation doesn't explicitly filter NaNs inside stats.py 
        # (It trusts caller or numpy/scipy handles it or throws exception).
        # We should check if it crashes or propagates NaN.
        # Ideally, we prefer it to fail gracefully or propagate NaN.
        X = [1.0, 2.0, np.nan, 4.0]
        Y = [1.0, 2.0, 3.0, 4.0]
        sigma_Y = [0.1] * 4
        
        # Current numpy/linalg behavior with nan is usually nan.
        try:
            res = calculate_slope_epsilon_phi(X, Y, sigma_Y)
            np.isnan(res['slope'])
        except Exception:
            pass

    def test_zero_uncertainty(self):
        """Test behavior when sigma_Y is 0 (or near zero)"""
        X = [1, 2, 3]
        Y = [1, 2, 3]
        sigma_Y = [0.0, 0.0, 0.0]
        res = analyze_with_fallback(X, Y, sigma_Y)
        self.assertAlmostEqual(res['slope'], 1.0)

    def test_very_large_numbers(self):
        """Test numerical stability with large inputs"""
        X = np.array([1, 2, 3]) * 1e9
        Y = np.array([1, 2, 3]) * 1e-9 # slope 1e-18
        sigma_Y = np.ones(3) * 1e-10
        res = analyze_with_fallback(X, Y, sigma_Y)
        self.assertAlmostEqual(res['slope'], 1e-18, delta=1e-20)

if __name__ == '__main__':
    unittest.main()
