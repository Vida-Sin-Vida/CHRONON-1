import numpy as np
from scipy import stats

class SensitivityAnalyzer:
    """
    Analyzes the sensitivity and detection limits of the experimental setup.
    Focuses on Simple Linear Regression power analysis.
    """
    
    def calculate_mdp(self, sigma_y, n, x_spread, alpha=0.05, power=0.8):
        """
        Calculates Minimum Detectable Slope (MDP).
        MDP = (sigma_y / (sqrt(Sxx))) * (t_alpha + t_beta)
        Sxx = sum((x - mean(x))^2) approx N * var(x)
        x_spread: Standard deviation of X (Delta_h) or roughly (Max-Min)/sqr(12)
        """
        if n <= 2: return float('inf')
        
        # Degrees of freedom
        df = n - 2
        
        # t-statistics
        # Two-sided alpha
        t_alpha = stats.t.ppf(1 - alpha/2, df)
        # One-sided beta (Power = 1 - beta)
        t_beta = stats.t.ppf(power, df)
        
        # Standard Error of Slope
        # SE_beta = sigma_y / sqrt(Sxx)
        # Sxx = (n-1) * var(x) if x_spread is std deviation
        # Let's assume x_spread is the standard deviation of x
        sxx = (n - 1) * (x_spread ** 2)
        se_slope = sigma_y / np.sqrt(sxx)
        
        mdp = se_slope * (t_alpha + t_beta)
        return mdp

    def get_power_for_slope(self, slope, sigma_y, n, x_spread, alpha=0.05):
        """
        Calculates statistical power for a specific true slope.
        """
        if n <= 2: return 0.0
        
        df = n - 2
        sxx = (n - 1) * (x_spread ** 2)
        se_slope = sigma_y / np.sqrt(sxx)
        
        # Non-centrality parameter approximation
        # t_stat = slope / se_slope
        delta = abs(slope) / se_slope
        
        # Critical t
        t_crit = stats.t.ppf(1 - alpha/2, df)
        
        # Power = P(t > t_crit | delta) + P(t < -t_crit | delta)
        # Approx using normal if N large, or non-central t
        # Using non-central t distribution 'nct'
        try:
            power = 1 - stats.nct.cdf(t_crit, df, nc=delta) + stats.nct.cdf(-t_crit, df, nc=delta)
        except:
            # Fallback to normal approx
            power = 1 - stats.norm.cdf(t_crit - delta) + stats.norm.cdf(-t_crit - delta)
            
        return power

    def get_power_curve(self, sigma_y, n, x_spread, slope_max):
        """
        Generates X, Y arrays for a power curve plot (Power vs True Slope).
        """
        slopes = np.linspace(0, slope_max, 50)
        powers = [self.get_power_for_slope(s, sigma_y, n, x_spread) for s in slopes]
        return slopes, powers
