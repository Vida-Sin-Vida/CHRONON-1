# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import numpy as np
import pandas as pd
from .stats import calculate_slope_epsilon_phi

class PowerSimulator:
    """
    Monte Carlo Simulator for Injection Tests and Power Analysis.
    """
    
    def run_simulation(self, n_sims=500, n_samples=50, true_slope=1e-5, sigma_y=0.1, sigma_x=0.0):
        """
        Runs Monte Carlo simulation to estimate detection power.
        """
        results = []
        detected_count = 0
        alpha = 0.05
        
        for i in range(n_sims):
            x_true = np.random.uniform(-10, 10, n_samples)
            x_obs = x_true + np.random.normal(0, sigma_x, n_samples) if sigma_x > 0 else x_true
            
            noise = np.random.normal(0, sigma_y, n_samples)
            y_obs = true_slope * x_true + noise
            
            sy_vec = np.ones(n_samples) * sigma_y
            sx_val = sigma_x if sigma_x > 0 else None
            
            try:
                reg = calculate_slope_epsilon_phi(x_obs, y_obs, sy_vec, sx_val)
                pval = reg['pval']
                detected = pval < alpha
                
                results.append({
                    'sim_id': i,
                    'slope_est': reg['slope'],
                    'pval': pval,
                    'detected': detected
                })
                
                if detected:
                    detected_count += 1
            except:
                pass
                
        df_res = pd.DataFrame(results)
        power = detected_count / len(df_res) if len(df_res) > 0 else 0
        mean_slope = df_res['slope_est'].mean() if len(df_res) > 0 else 0
        bias = mean_slope - true_slope
        
        return {
            'power': power,
            'mean_slope': mean_slope,
            'bias': bias,
            'n_sims': n_sims
        }
    
    def scan_scenarios(self):
        """
        Runs scenarios S1, S2, S3 (Low, Med, High signal).
        """
        scenarios = {
            'S1 (Null)': 0.0,
            'S2 (Weak)': 1e-4,
            'S3 (Strong)': 1e-3
        }
        
        report = {}
        for name, slope in scenarios.items():
            res = self.run_simulation(n_sims=200, n_samples=50, true_slope=slope, sigma_y=0.1)
            report[name] = res
            
        return report

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
