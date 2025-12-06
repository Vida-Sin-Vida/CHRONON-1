
import unittest
import os
import shutil
import pandas as pd
import numpy as np
from chronon_core.qc import QualityControl
from chronon_core.stats import analyze_with_fallback
from chronon_core.ledger import Ledger

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_e2e"
        os.makedirs(self.test_dir, exist_ok=True)
        self.ledger_path = os.path.join(self.test_dir, "e2e_ledger.csv")
        self.ledger = Ledger(self.ledger_path)
        
    def tearDown(self):
        try:
            shutil.rmtree(self.test_dir)
        except:
            pass

    def test_full_pipeline_flow(self):
        """
        Simulate -> QC -> Compute -> Ledger.
        1. Create synthetic "Run" DF
        2. Filter via QC
        3. Analyze via Stats
        4. Record in Ledger
        """
        # 1. Simulate good run
        n = 50
        df = pd.DataFrame({
            'Delta_h_m': np.linspace(-10, 10, n),
            'temp_C': np.random.normal(20, 1, n), # Good temp
            'a_rms_ms2': np.random.uniform(0, 0.1, n) # Good vib
        })
        # y = 1e-5 * x
        df['y_frac'] = 1e-5 * df['Delta_h_m'] + np.random.normal(0, 1e-7, n)
        df['sigma_y'] = 1e-7
        
        # 2. QC
        # Use relaxed config for small test and Regression Data (varying Height)
        qc = QualityControl(config={'min_samples': 40, 'max_jitter_dh': 100.0})
        status, flags = qc.assess_run(df)
        self.assertEqual(status, "PASS", msg=f"QC Failed with: {flags}")
        
        # 3. Analyze
        # Assuming we extract arrays
        res = analyze_with_fallback(df['Delta_h_m'], df['y_frac'], df['sigma_y'])
        
        # 4. Ledger
        self.ledger.append_run(
            run_id="TEST_RUN_001",
            verdict="DETECTED" if res['pval'] < 0.05 else "NULL",
            config_hash="abc",
            code_hash="123",
            row_data={'slope': res['slope'], 'flags': flags}
        )
        
        # Verify file exists
        self.assertTrue(os.path.exists(self.ledger_path))
        with open(self.ledger_path, 'r') as f:
            content = f.read()
            self.assertIn("TEST_RUN_001", content)

    def test_bad_qc_flow(self):
        """Test that bad QC stops/flags correctly."""
        df = pd.DataFrame({
            'Delta_h_m': [1,2,3],
            'temp_C': [100, 100, 100] # Too hot
        })
        qc = QualityControl()
        status, flags = qc.assess_run(df)
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("TEMP" in f for f in flags))

if __name__ == '__main__':
    unittest.main()
