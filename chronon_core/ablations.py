import numpy as np
import pandas as pd
from chronon_core import stats

def run_permutation_test(X, Y, sigma_Y, n_perms=2000):
    """
    Height-label permutation test.
    Shuffles X (heights) against Y (residuals).
    Returns p-value and histogram data.
    """
    # Base fit
    res_0 = stats.fit_free_intercept_wls(X, Y, sigma_Y)
    eps_0 = res_0['eps_phi']
    
    perm_eps = []
    
    X_perm = X.copy()
    for _ in range(n_perms):
        np.random.shuffle(X_perm)
        res_p = stats.fit_free_intercept_wls(X_perm, Y, sigma_Y)
        perm_eps.append(res_p['eps_phi'])
        
    perm_eps = np.array(perm_eps)
    # p-value: fraction where |eps_perm| >= |eps_0|
    p_val = np.mean(np.abs(perm_eps) >= np.abs(eps_0))
    
    return {
        'p_value': p_val,
        'dist': perm_eps,
        'nominal_eps': eps_0
    }

def run_desynchronization(df, lag_seconds):
    """
    Time desynchronization test.
    Shifts X by lag_seconds relative to Y.
    Requires timestamp checks.
    """
    # We shift Y relative to X.
    # Logic: Align Y(t) with X(t + lag)
    # This requires resampling or index shifting.
    # Assuming df is sorted and regular or we re-merge on time.
    
    df_shifted = df.copy()
    # If we shift the 'X_GR' column by lag
    # This assumes rows are time-ordered. 
    # Better: re-assign X values based on t + lag.
    # But X is computed from t. So we just recompute X at t+lag?
    # Or simplified: shift the vector if grids are uniform.
    
    # We'll implementation integer shift if step is uniform, else interpolation.
    # Simplest: shift vector by N bins.
    
    # For now, placeholder for specific shift logic
    pass

def run_sign_inversion(X, Y, sigma_Y):
    """
    Sign inversion test: Delta_h -> -Delta_h.
    """
    res = stats.fit_free_intercept_wls(-X, Y, sigma_Y)
    return res

def run_covariate_veto(Y, covariates_df, threshold=0.7):
    """
    Checks if any covariate explains >= threshold of variance.
    """
    # For each column in covariates, run linear regression Y ~ cov
    # Check R^2
    results = {}
    veto = False
    
    for col in covariates_df.columns:
        C = covariates_df[col].values
        # Simple OLS
        slope, intercept, r_value, p_value, std_err = stats.linregress(C, Y)
        r2 = r_value**2
        
        results[col] = r2
        if r2 >= threshold:
            veto = True
            
    return {'veto': veto, 'details': results}
