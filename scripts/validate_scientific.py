
import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chronon_core.stats import analyze_with_fallback
from chronon_core.ledger import Ledger

class ValidationSuite:
    def __init__(self, output_dir="validation_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.ledger = Ledger(os.path.join(output_dir, "validation_ledger.csv"))
        
    def generate_dataset(self, type_name="D1", n=100, slope=0.0, seed=None):
        """
        Generates synthetic datasets for validation.
        D1: Ideal (White noise, Homoscedastic)
        D2: Field (Larger noise, slight X uncertainty)
        D3: Autocorrelated (AR(1) noise) - Should trigger Ljung-Box
        D4: Heteroscedastic (Sigma ~ |X|) - Should trigger Breusch-Pagan
        """
        if seed is not None:
             np.random.seed(seed)
        
        
        X = np.linspace(-10, 10, n)
        sigma_Y_base = 0.01 # Reduced to improve power
        sigma_X = 0.0
        
        noise = np.random.normal(0, sigma_Y_base, n)
        
        if type_name == "D1":
            # Ideal
            pass
            
        elif type_name == "D2":
            # Field: X uncertainty
            # Make sigma_X large enough to be near threshold 0.1 relative to mean(X)=5 -> sigma=0.5
            sigma_X = 0.5 
            X_obs = X + np.random.normal(0, sigma_X, n)
            # Re-assign X to observed
            X = X_obs 
            noise = np.random.normal(0, sigma_Y_base * 2, n)
            
        elif type_name == "D3":
            # Autocorrelated (AR(1) with rho=0.6)
            ar_noise = np.zeros(n)
            rho = 0.8 # Stronger autocorr
            current = 0
            for i in range(1, n):
                current = rho * current + np.random.normal(0, sigma_Y_base)
                ar_noise[i] = current
            noise = ar_noise
            
        elif type_name == "D4":
            # Heteroscedastic
            # Sigma varies with X strongly
            sigmas = sigma_Y_base * (1 + 10.0 * np.abs(X))
            noise = np.random.normal(0, sigmas, n)
            
        Y = slope * X + noise
        
        # Sigma vector for WLS
        if type_name == "D4":
            sigma_vec = sigma_Y_base * (1 + 10.0 * np.abs(X))
        else:
            sigma_vec = np.ones(n) * sigma_Y_base
            
        if type_name == "D2":
            sigma_X_vec = np.ones(n) * sigma_X
        else:
            sigma_X_vec = None
            
        return X, Y, sigma_vec, sigma_X_vec

    def run_validation_loop(self):
        print("Starting Validation Loop...")
        results = []
        
        # Priority A: Validation Statistique
        # Scenarios
        datasets = ["D1", "D2", "D3", "D4"]
        injections = [
            ("S1 (Null)", 0.0), 
            ("S2 (Weak)", 1e-4), 
            ("S3 (Strong)", 1e-3)
        ]
        
        for ds_type in datasets:
            for scenarios_name, slope in injections:
                # Run N times to get statistics
                n_mc = 50 # 50 runs per scenario
                detected_count = 0
                
                for i in range(n_mc):
                    # Perturb seed slightly per iteration
                    np.random.seed(int(datetime.now().timestamp() * 1000) % 10000 + i)
                    
                    X, Y, sy, sx = self.generate_dataset(ds_type, n=400, slope=slope)
                    
                    # Run Analysis
                    res = analyze_with_fallback(X, Y, sy, sx)
                    
                    # Record
                    is_detected = res['pval'] < 0.05
                    if is_detected:
                        detected_count += 1
                        
                    # Ledger Entry
                    self.ledger.append_run(
                        run_id=f"{ds_type}_{scenarios_name}_{i}",
                        verdict="DETECTED" if is_detected else "NULL",
                        config_hash="TEST_CONFIG",
                        code_hash="TEST_CODE",
                        row_data={
                            'dataset': ds_type,
                            'scenario': scenarios_name,
                            'slope_true': slope,
                            'slope_est': res['slope'],
                            'pval': res['pval'],
                            'fallback': res.get('fallback_triggered', False),
                            'fallback_reasons': res.get('fallback_reasons', []),
                            'model': res['model_summary']
                        }
                    )
                    
                    results.append({
                        'dataset': ds_type,
                        'scenario': scenarios_name,
                        'slope_est': res['slope'],
                        'pval': res['pval'],
                        'detected': is_detected,
                        'fallback': res.get('fallback_triggered', False)
                    })
                    
        return pd.DataFrame(results)

    def run_sensitivity_analysis(self):
        print("\nStarting Sensitivity Analysis...")
        # Focus on D2 (Field) + S2 (Weak)
        X, Y, sy, sx = self.generate_dataset("D2", n=100, slope=1e-4)
        
        base_res = analyze_with_fallback(X, Y, sy, sx)
        base_slope = base_res['slope']
        
        sens_results = []
        
        # 1. Vary Deming Threshold
        for th in [0.05, 0.2]:
            res = analyze_with_fallback(X, Y, sy, sx, deming_threshold=th)
            change = abs(res['slope'] - base_slope) / abs(base_slope) if base_slope != 0 else 0
            sens_results.append({
                'param': 'deming_threshold',
                'val': th,
                'slope': res['slope'],
                'change_pct': change * 100
            })
            
        # 2. Vary NW Lag (approx via bandwidth override)
        # Base likely used auto L.
        # Try fixed L=2, L=10
        for bw in [2, 10]:
            res = analyze_with_fallback(X, Y, sy, sx, nw_bandwidth=bw)
            change = abs(res['slope'] - base_slope) / abs(base_slope) if base_slope != 0 else 0
            sens_results.append({
                'param': 'nw_bandwidth',
                'val': bw,
                'slope': res['slope'],
                'change_pct': change * 100
            })
            
        return pd.DataFrame(sens_results)

if __name__ == "__main__":
    suite = ValidationSuite()
    
    # 1. Validation Runs
    df_res = suite.run_validation_loop()
    
    # Report per Dataset/Scenario
    report = df_res.groupby(['dataset', 'scenario']).agg(
        Power=('detected', 'mean'),
        MeanSlope=('slope_est', 'mean'),
        FallbackRate=('fallback', 'mean')
    )
    
    print("\n=== Validation Report ===")
    print(report)
    
    # Save
    report.to_csv(os.path.join(suite.output_dir, "validation_summary.csv"))
    
    # 2. Sensitivity
    df_sens = suite.run_sensitivity_analysis()
    print("\n=== Sensitivity Report ===")
    print(df_sens)
    df_sens.to_csv(os.path.join(suite.output_dir, "sensitivity_summary.csv"))
    
    print("\nDone. Ledger and results saved to:", suite.output_dir)
