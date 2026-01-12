import numpy as np
from scipy import stats

class RunComparator:
    """
    Compares two independent runs of the CHRONON experiment.
    Calculates delta epsilon, significance of difference, and overlaps.
    """
    
    def compare_runs(self, run_a, run_b):
        """
        run_a, run_b: dicts or DataFrames containing 'slope', 'stderr', 'n', etc.
        Ideally these are specific result dicts from the manager/ledger.
        """
        results = {}
        
        # Extract basic stats
        # If passed as 'row_data' from ledger, it is nested in 'regression'
        r1 = self._extract_reg(run_a)
        r2 = self._extract_reg(run_b)
        
        slope1, err1 = r1.get('slope', 0), r1.get('stderr', 1e-9)
        slope2, err2 = r2.get('slope', 0), r2.get('stderr', 1e-9)
        
        # 1. Delta Epsilon
        delta_slope = slope2 - slope1
        results['delta_slope'] = delta_slope
        
        # 2. Z-Test for difference
        # Z = (b1 - b2) / sqrt(SE1^2 + SE2^2)
        pooled_se = np.sqrt(err1**2 + err2**2)
        z_score = delta_slope / pooled_se
        pval_diff = 2 * (1 - stats.norm.cdf(abs(z_score))) # Two-tailed
        
        results['z_score_diff'] = z_score
        results['pval_diff'] = pval_diff
        results['significant_diff'] = pval_diff < 0.05
        
        # 3. Overlap check
        # Do 95% CIs overlap?
        ci1 = (r1.get('ci_low', -np.inf), r1.get('ci_high', np.inf))
        ci2 = (r2.get('ci_low', -np.inf), r2.get('ci_high', np.inf))
        
        overlap_range = max(0, min(ci1[1], ci2[1]) - max(ci1[0], ci2[0]))
        results['ci_overlap'] = overlap_range > 0
        
        return results

    def _extract_reg(self, run_data):
        # Helper to find regression dict
        if 'regression' in run_data:
            return run_data['regression']
        if 'slope' in run_data:
            return run_data
        return {}
