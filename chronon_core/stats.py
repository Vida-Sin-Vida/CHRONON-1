# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import numpy as np
from scipy import stats, optimize
from .diagnostics import ResidualDiagnostics

def calculate_slope_epsilon_phi(X, Y, sigma_Y, sigma_X=None, **kwargs):
    """
    Central regression module for CHRONON.
    Computes the slope 'epsilon_phi' using Weighted Least Squares (WLS) or Deming Regression.

    Parameters:
    -----------
    X, Y, sigma_Y : array_like
        Data vectors and Y uncertainties.
    sigma_X : array_like, optional
        Uncertainties in X.
    **kwargs : dict
        deming_threshold : float (default 0.1)
        nw_bandwidth : int, optional

    Returns:
    --------
    dict containing regression results (slope, stderr, pval, ci, residuals, etc.)
    """
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    sigma_Y = np.asarray(sigma_Y, dtype=float)
    
    use_deming = False
    switch_reason = None
    
    # Check X uncertainty condition for Deming
    if sigma_X is not None:
        sigma_X = np.asarray(sigma_X, dtype=float)
        x_abs = np.abs(X)
        mask = x_abs > 1e-9
        if np.any(mask):
            rel_unc = np.mean(sigma_X[mask] / x_abs[mask])
        else:
            rel_unc = 0.0
            
        if rel_unc > kwargs.get('deming_threshold', 0.1):
            use_deming = True
            switch_reason = f"Relative X uncertainty {rel_unc:.2f} > {kwargs.get('deming_threshold', 0.1)}"

    if use_deming:
        # Perform Deming/WTLS with Bootstrap for robust Error estimation
        res_main = fit_deming_wtls(X, Y, sigma_X, sigma_Y)
        slope = res_main['eps_phi']
        alpha_val = res_main['alpha']
        
        # Bootstrap for errors
        boot_slopes = []
        n_boot = 200
        n_samples = len(Y)
        
        for _ in range(n_boot):
            indices = np.random.choice(n_samples, n_samples, replace=True)
            rx = fit_deming_wtls(X[indices], Y[indices], sigma_X[indices], sigma_Y[indices])
            if rx['success']:
                boot_slopes.append(rx['eps_phi'])
                
        boot_slopes = np.array(boot_slopes)
        stderr = np.std(boot_slopes)
        ci_low, ci_high = np.percentile(boot_slopes, [2.5, 97.5])
        
        if stderr > 0:
            z_score = slope / stderr
            pval = 2 * (1 - stats.norm.cdf(abs(z_score)))
        else:
            pval = 0.0
            
        return {
            'slope': slope,
            'stderr': stderr,
            'pval': pval,
            'ci_low': ci_low,
            'ci_high': ci_high,
            'model_summary': 'DEMING_WTLS',
            'switch_reason': switch_reason,
            'alpha': alpha_val,
            'residuals': Y - (alpha_val + slope * X)
        }

    else:
        # Standard WLS + HAC Errors
        res = fit_free_intercept_wls(X, Y, sigma_Y, nw_bandwidth=kwargs.get('nw_bandwidth'))
        slope = res['eps_phi']
        stderr = res['se_eps']
        alpha_val = res['alpha']
        
        dof = len(Y) - 2
        t_stat = slope / stderr if stderr > 0 else np.inf
        pval = 2 * (1 - stats.t.cdf(abs(t_stat), dof))
        
        t_crit = stats.t.ppf(0.975, dof)
        ci_low = slope - t_crit * stderr
        ci_high = slope + t_crit * stderr
        
        return {
            'slope': slope,
            'stderr': stderr,
            'pval': pval,
            'ci_low': ci_low,
            'ci_high': ci_high,
            'model_summary': 'WLS_HAC',
            'switch_reason': switch_reason,
            'alpha': alpha_val,
            'residuals': Y - (alpha_val + slope * X)
        }

def analyze_with_fallback(X, Y, sigma_Y, sigma_X=None, **kwargs):
    """
    Wrapper around calculate_slope_epsilon_phi that includes diagnostics and fallback logic.
    """
    # 1. Primary Analysis
    result = calculate_slope_epsilon_phi(X, Y, sigma_Y, sigma_X, **kwargs)
    
    # 2. Ensure Residuals
    residuals = result.get('residuals')
    if residuals is None:
        alpha = result.get('alpha', 0.0)
        slope = result['slope']
        residuals = Y - (alpha + slope * np.array(X))

    # 3. Diagnostics
    diag_res = ResidualDiagnostics.run_diagnostics(residuals, X)
    result['diagnostics'] = diag_res
    
    # 4. Fallback Checks
    needs_fallback = False
    fallback_reasons = []
    
    lb = diag_res.get('Autocorr (Ljung-Box)')
    if lb and lb['pval'] < 0.01:
        needs_fallback = True
        fallback_reasons.append("Ljung-Box p<0.01")
        
    bp = diag_res.get('Heteroscedasticity (LM)')
    if bp and bp['pval'] < 0.01:
        needs_fallback = True
        fallback_reasons.append("Breusch-Pagan p<0.01")
        
    if needs_fallback:
        result['fallback_triggered'] = True
        result['fallback_reasons'] = fallback_reasons
        
        # Robust Wild Bootstrap
        wb_res = wild_bootstrap(X, Y, sigma_Y, n_boot=1000)
        
        result['original_slope'] = result['slope']
        result['original_pval'] = result['pval']
        
        # Update with robust estimates
        result['slope'] = wb_res['boot_mean']
        result['stderr'] = wb_res['boot_std']
        result['ci_low'] = wb_res['ci_95'][0]
        result['ci_high'] = wb_res['ci_95'][1]
        
        if wb_res['boot_std'] > 0:
            z = result['slope'] / wb_res['boot_std']
            result['pval'] = 2 * (1 - stats.norm.cdf(abs(z)))
            
        result['model_summary'] += " + WILD_BOOTSTRAP"
    else:
        result['fallback_triggered'] = False
        
    return result

# --- Helper Functions ---

def compute_andrews_bandwidth(residuals):
    """Auto-bandwidth L for HAC."""
    T = len(residuals)
    if T == 0:
        return 0
    L = np.floor(4 * (T / 100)**(2/9))
    return int(L)

def newey_west_se(X, residuals, bandwidth):
    """Newey-West HAC standard errors."""
    XT_e = X.T * residuals
    S = XT_e @ XT_e.T
    
    for lag in range(1, bandwidth + 1):
        w_l = 1.0 - lag / (bandwidth + 1.0)
        Gamma_l = XT_e[:, lag:] @ XT_e[:, :-lag].T
        S += w_l * (Gamma_l + Gamma_l.T)
        
    try:
        XX_inv = np.linalg.inv(X.T @ X)
        V = XX_inv @ S @ XX_inv
        return np.sqrt(np.maximum(0, np.diag(V)))
    except np.linalg.LinAlgError:
        return np.zeros(X.shape[1])

def fit_free_intercept_wls(X_in, Y_in, sigma_Y_in, nw_bandwidth=None):
    """Weighted Least Squares with HAC errors."""
    X = np.array(X_in, dtype=float)
    Y = np.array(Y_in, dtype=float)
    sig = np.array(sigma_Y_in, dtype=float)
    
    weights = 1.0 / (sig**2 + 1e-12)
    sqrt_w = np.sqrt(weights)
    
    n = len(Y)
    X_mat = np.column_stack([np.ones(n), X])
    
    Y_star = Y * sqrt_w
    X_star = X_mat * sqrt_w[:, None]
    
    try:
        XTX_inv = np.linalg.inv(X_star.T @ X_star)
        beta = XTX_inv @ (X_star.T @ Y_star)
    except np.linalg.LinAlgError:
        return {'alpha':0, 'eps_phi':0, 'se_alpha':0, 'se_eps':0, 'bandwidth_L':0}
    
    res_star = Y_star - X_star @ beta
    
    if nw_bandwidth is not None:
        L = int(nw_bandwidth)
    else:
        L = compute_andrews_bandwidth(res_star)
    
    se = newey_west_se(X_star, res_star, L)
    
    return {
        'alpha': beta[0],
        'eps_phi': beta[1],
        'se_alpha': se[0],
        'se_eps': se[1],
        'bandwidth_L': L 
    }

def fit_deming_wtls(X, Y, sigma_X, sigma_Y):
    """Weighted Total Least Squares (Deming)."""
    def chi2(params):
        a, b = params
        denom = b**2 * sigma_X**2 + sigma_Y**2 + 1e-12
        numer = (Y - a - b*X)**2
        return np.sum(numer / denom)
        
    # Initial guess via OLS
    try:
        res_wls = np.polyfit(X, Y, 1) 
        init = [res_wls[1], res_wls[0]]
    except Exception:
        init = [0, 0]
    
    try:
        opt = optimize.minimize(chi2, init, method='L-BFGS-B')
        return {
            'alpha': opt.x[0],
            'eps_phi': opt.x[1],
            'success': opt.success
        }
    except Exception:
        return {'alpha': 0, 'eps_phi': 0, 'success': False}

def wild_bootstrap(X, Y, sigma_Y, n_boot=2000):
    """Studentized Wild Bootstrap."""
    res = fit_free_intercept_wls(X, Y, sigma_Y)
    y_hat = res['alpha'] + res['eps_phi'] * X
    residuals = Y - y_hat
    
    boot_betas = []
    
    sqrt5 = np.sqrt(5)
    v1 = -(sqrt5 - 1) / 2
    v2 = (sqrt5 + 1) / 2
    p = (sqrt5 + 1) / (2 * sqrt5)
    
    for _ in range(n_boot):
        rnd = np.random.rand(len(Y))
        v = np.where(rnd < p, v1, v2)
        y_boot = y_hat + residuals * v
        res_b = fit_free_intercept_wls(X, y_boot, sigma_Y)
        boot_betas.append(res_b['eps_phi'])
        
    boot_betas = np.array(boot_betas)
    
    return {
        'boot_mean': np.mean(boot_betas),
        'boot_std': np.std(boot_betas),
        'ci_95': np.percentile(boot_betas, [2.5, 97.5])
    }

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
