# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

class ConsistencyIndex:
    """
    Calculates the Chronon Consistency Index (CCI).
    """
    
    def calculate_cci(self, residuals, pval_slope, bootstrap_ci, n_samples):
        """
        Calculates CCI score (0.0 - 1.0).
        """
        details = {}
        
        # 1. Normality Component (Max 0.3)
        try:
            from scipy.stats import skew, kurtosis
            s = abs(skew(residuals))
            k = abs(kurtosis(residuals))
            norm_penalty = min(0.3, (s/2.0 + k/5.0) * 0.1)
            score_norm = max(0.0, 0.3 - norm_penalty)
        except:
            score_norm = 0.15
            
        details['Normality'] = score_norm
        
        # 2. Stability Component (Max 0.3)
        ci_cross_zero = (bootstrap_ci[0] * bootstrap_ci[1] < 0)
        score_stab = 0.1 if ci_cross_zero else 0.3
        details['Stability'] = score_stab
        
        # 3. Sample Size (Max 0.2)
        score_n = min(0.2, (n_samples / 100.0) * 0.2)
        details['Sample Size'] = score_n
        
        # 4. Significance (Max 0.2)
        score_sig = 0.0
        if pval_slope < 0.001: score_sig = 0.2
        elif pval_slope < 0.01: score_sig = 0.15
        elif pval_slope < 0.05: score_sig = 0.1
        details['Significance'] = score_sig
        
        total_score = score_norm + score_stab + score_n + score_sig
        
        return round(total_score, 2), details

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
