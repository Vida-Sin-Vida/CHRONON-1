# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import numpy as np
from scipy import stats

class ResidualDiagnostics:
    """
    Statistical diagnostics for regression residuals.
    Implements tests for Normality, Autocorrelation, and Heteroscedasticity.
    """
    
    @staticmethod
    def run_diagnostics(residuals, X=None):
        """
        Runs a suite of diagnostic tests.
        """
        res = np.asarray(residuals)
        n = len(res)
        results = {}
        
        # 1. Normality (Shapiro-Wilk)
        if n > 3:
            s, p = stats.shapiro(res)
            results['Normality (Shapiro-Wilk)'] = {
                'stat': s, 'pval': p, 
                'verdict': 'FAIL' if p < 0.05 else 'PASS'
            }
        else:
            results['Normality'] = {'stat': 0, 'pval': 1.0, 'verdict': 'SKIP'}
            
        # 2. Autocorrelation (Ljung-Box)
        if n > 5:
            lags_h = min(10, n // 5)
            acf = []
            mean_res = np.mean(res)
            var_res = np.var(res)
            
            for lag in range(1, lags_h + 1):
                c = np.mean((res[:-lag] - mean_res) * (res[lag:] - mean_res)) / var_res
                acf.append(c)
            acf = np.array(acf)
            
            q_stat = 0
            for k in range(1, lags_h + 1):
                rho = acf[k-1]
                q_stat += (rho**2) / (n - k)
            q_stat *= n * (n + 2)
            
            pval_lb = 1 - stats.chi2.cdf(q_stat, lags_h)
            
            results['Autocorr (Ljung-Box)'] = {
                'stat': q_stat, 'pval': pval_lb,
                'verdict': 'FAIL' if pval_lb < 0.01 else 'PASS'
            }
        else:
             results['Autocorr (Ljung-Box)'] = {'stat': 0, 'pval': 1.0, 'verdict': 'SKIP'}
            
        # 3. Heteroscedasticity (LM Test / Breusch-Pagan simplified)
        if X is not None and len(X) == n and n > 2:
            e2 = res**2
            X_const = np.column_stack([np.ones(n), X])
            try:
                beta = np.linalg.pinv(X_const) @ e2
                y_hat = X_const @ beta
                ssr = np.sum((y_hat - np.mean(e2))**2)
                sse = np.sum((e2 - y_hat)**2)
                sst = ssr + sse
                if sst > 0:
                    r2 = ssr / sst
                    lm_stat = n * r2
                    pval_bp = 1 - stats.chi2.cdf(lm_stat, 1)
                    
                    results['Heteroscedasticity (LM)'] = {
                        'stat': lm_stat, 'pval': pval_bp,
                        'verdict': 'FAIL' if pval_bp < 0.05 else 'PASS'
                    }
                else:
                     results['Heteroscedasticity'] = {'stat':0, 'pval':1, 'verdict': 'SKIP'}
            except Exception:
                 results['Heteroscedasticity'] = {'stat':0, 'pval':1, 'verdict': 'ERROR'}
                 
        return results

    @staticmethod
    def get_plots_data(residuals):
        """
        Prepares data for diagnostic plotting.
        """
        res = np.sort(residuals)
        n = len(res)
        
        # QQ Plot
        theoretical_q = stats.norm.ppf((np.arange(1, n+1) - 0.5) / n)
        
        # ACF
        lags = range(min(20, n))
        acf = []
        mean_res = np.mean(residuals)
        var_res = np.var(residuals)
        for lag in lags:
            if lag == 0:
                c = 1.0
            else:
                c = np.mean((residuals[:-lag] - mean_res) * (residuals[lag:] - mean_res)) / var_res
            acf.append(c)
            
        return {
            'sorted_residuals': res,
            'theoretical_quantiles': theoretical_q,
            'acf': acf,
            'lags': list(lags)
        }

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
