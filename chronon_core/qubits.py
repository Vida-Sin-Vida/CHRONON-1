# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import numpy as np
from scipy.optimize import curve_fit

class QubitAnalysis:
    """
    Analyzes T2 coherence times vs Chronon Field fluctuations.
    """
    
    def generate_mock_data(self, n=20):
        """Generates synthetic data for demonstration."""
        x = np.random.uniform(-5, 5, n)
        true_beta = -0.5
        intercept = 100.0
        noise = np.random.normal(0, 5, n)
        y = intercept + true_beta * x + noise
        y_err = np.random.uniform(1, 3, n)
        return x, y, y_err
        
    def analyze_t2_vs_phi(self, x, y, y_err=None, model_type="linear"):
        """
        Analyzes relationship between delta_ln_phi (x) and T2 (y).
        """
        if len(x) < 3:
            return {'valid': False, 'msg': "Insufficient data (N<3)"}
            
        x = np.array(x)
        y = np.array(y)
        if y_err is None: y_err = np.ones_like(y)
        
        results = {
            'valid': True,
            'n_samples': len(x),
            'model': model_type
        }
        
        def linear(x, t0, beta): return t0 + beta * x
        def exponential(x, t0, beta): return t0 * np.exp(beta * x)
        
        try:
            if model_type == "exponential":
                p0 = [np.mean(y), 0.0]
                try:
                    popt, pcov = curve_fit(exponential, x, y, sigma=y_err, p0=p0, maxfev=2000)
                except:
                     popt = [np.mean(y), 0.0]
                     pcov = np.diag([np.inf, np.inf])

                results.update({
                    'beta': popt[1],
                    'intercept': popt[0],
                    'slope_beta': popt[1],
                    'intercept_t2_0': popt[0],
                    'equation': "T2 = T0 * exp(beta * x)"
                })
            else:
                p0 = [np.mean(y), 0.0]
                popt, pcov = curve_fit(linear, x, y, sigma=y_err, p0=p0)
                results.update({
                    'beta': popt[1],
                    'intercept': popt[0],
                    'slope_beta': popt[1],
                    'intercept_t2_0': popt[0],
                    'equation': "T2 = T0 + beta * x"
                })
                
            results['std_error'] = np.sqrt(np.diag(pcov))[1]
            
            # Bootstrap CI for Beta
            betas = []
            for _ in range(100):
                idxs = np.random.choice(len(x), len(x), replace=True)
                try:
                    if model_type == "exponential":
                         pb, _ = curve_fit(exponential, x[idxs], y[idxs], maxfev=1000)
                    else:
                         pb, _ = curve_fit(linear, x[idxs], y[idxs])
                    betas.append(pb[1])
                except: pass
            
            if betas:
                results['ci_beta_95'] = np.percentile(betas, [2.5, 97.5])
            else:
                results['ci_beta_95'] = [0, 0]
                
        except Exception as e:
            return {'valid': False, 'msg': f"Fit failed: {e}"}
            
        return results

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
