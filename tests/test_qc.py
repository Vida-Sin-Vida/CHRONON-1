
import unittest
import pandas as pd
from chronon_core.qc import QualityControl

class TestQC(unittest.TestCase):
    def setUp(self):
        self.qc = QualityControl()
        
    def test_pass_scenario(self):
        """Test a perfect run."""
        # Create dummy DF satisfying all rules
        # Min samples = 100
        N = 105
        data = {
            'temp_C': [20.0]*N,
            'vibration': [0.01]*N,
            'Delta_h_m': [0.5]*N,
            'phi': [0]*N,
            'sigma_Y': [0.1]*N
        }
        df = pd.DataFrame(data)
        
        status, flags = self.qc.assess_run(df)
        self.assertEqual(status, "PASS", f"Failed with flags: {flags}")
        self.assertEqual(len(flags), 0)
        
    def test_fail_temp(self):
        """Test failure on temperature check."""
        # Temp > MAX (30)
        N = 105
        data = {
            'temp_C': [40.0]*N, 
            'Delta_h_m': [1]*N, 
            'vibration': [0]*N
        } 
        df = pd.DataFrame(data)
        status, flags = self.qc.assess_run(df)
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("TEMP" in f for f in flags), f"Flags: {flags}")

    def test_min_samples(self):
        """Test failure on too few samples."""
        df = pd.DataFrame({'a': [1, 2]}) # 2 samples
        status, flags = self.qc.assess_run(df)
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("N_SAMPLES" in f for f in flags))

if __name__ == '__main__':
    unittest.main()
