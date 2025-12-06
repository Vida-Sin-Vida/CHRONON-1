import pandas as pd
import numpy as np
# import allantools # Removed to avoid dependency

def compute_windows(df, window_sec=120):
    """
    Downsamples the dataframe by non-overlapping block averaging.
    window_sec: size of the window in seconds.
    The spec says: "Window averages: apply non-overlapping windows of user config (60–300 s)."
    """
    if df.empty:
        return df
        
    df = df.sort_values('timestamp_UTC')
    
    # Resample
    # Ensure index is datetime
    if not np.issubdtype(df['timestamp_UTC'].dtype, np.datetime64):
        df['timestamp_UTC'] = pd.to_datetime(df['timestamp_UTC'])
        
    df = df.set_index('timestamp_UTC')
    
    # Columns to average
    # We take mean of numeric columns
    # First, handle numeric only
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Resample rule
    rule = f'{window_sec}S'
    
    # Use 'mean' for signals, 'sum' for counts? Spec implies averages.
    # Note: X_GR, Y_res, Sigma_X should be averaged properly.
    # Sigma aggregation: 
    # If samples are independent, sigma_mean = sigma_sq / sqrt(N). 
    # But usually we re-evaluate sigma from the spread or assume 1/sqrt(N).
    # Spec: "produce σ_Δh per window". If we map from raw, we strictly average the sigmas (conservative)? 
    # Or quadrature?
    # Standard practice: variance of the mean = var_population / N.
    # We will average the values and effectively reduce sigma by sqrt(N) *if* we trust N is effective count.
    # Safer: calculate standard error of the mean of the points in the bin.
    
    resampled = df[numeric_cols].resample(rule).mean()
    
    # Also need counts to scale sigma
    counts = df[numeric_cols].resample(rule).count()
    
    # Adjust sigmas
    if 'sigma_X' in resampled.columns:
        # sigma_new = sigma_avg / sqrt(count)
        # assuming sigma_X column holds per-point uncertainty
        resampled['sigma_X'] = resampled['sigma_X'] / np.sqrt(counts['sigma_X'])
        
    if 'sigma_Y' in resampled.columns:
        resampled['sigma_Y'] = resampled['sigma_Y'] / np.sqrt(counts['sigma_Y'])
        
    # Drop empty bins
    resampled = resampled.dropna()
    
    # Restore non-numeric meta-data (take first or mode)
    # site_pair, operator_id etc.
    # We can join back scalar columns
    meta_cols = list(set(df.columns) - set(numeric_cols))
    if meta_cols:
        meta = df[meta_cols].resample(rule).first() # Take first value for metadata
        resampled = resampled.join(meta)
        
    return resampled.reset_index()

def calc_allan_stats(df, rate=1.0):
    """
    Computes Allan deviation diagnostics.
    df: dataframe with 'Y_res' (residuals) or 'y_frac'.
    rate: sample rate in Hz.
    """
    # Assuming equidistant data after filling gaps or raw data?
    # Spec: "Window averages... Store Allan stats." 
    # Likely meaning we compute ADEV of the residuals to check noise type.
    
    if 'Y_res' not in df.columns:
        return {}
        
    data = df['Y_res'].values
    
    # Simple Overlapping Allan Deviation Implementation
    # to avoid external dependency
    
    def _simple_oadev(y, rate, taus):
        # y: frequency data
        # rate: sample rate
        # taus: array of tau values (in seconds)
        ad = []
        for tau in taus:
            m = int(tau * rate)
            if m < 1 or m >= len(y):
                ad.append(np.nan)
                continue
            
            # Create overlapping sums
            # Avg of y over tau: y_bar(t)
            # Efficient moving average
            # But standard formula for OADEV:
            # sigma^2(tau) = 1/(2*(N-2m)*tau^2) * sum_{i=1}^{N-2m} (x_{i+2m} - 2x_{i+m} + x_i)^2 ... 
            # if x is phase.
            # For freq y:
            # sigma^2 = 1/(2m^2(N-2m+1)) * sum (sum(y[i+m:i+2m]) - sum(y[i:i+m]))^2
            
            N = len(y)
            if N < 2*m + 1:
                ad.append(np.nan)
                continue
                
            # Compute moving sums
            cs = np.cumsum(np.insert(y, 0, 0))
            # sum[i:i+m] = cs[i+m] - cs[i]
            
            # We want diff of averages:
            # y_bar_k+1 - y_bar_k
            # y_bar(i, m) = (cs[i+m] - cs[i]) / m
            # We want sum over overlapping blocks
            
            # Vectors of moving sums
            # s1 = y[i]...y[i+m-1] -> cs[i+m] - cs[i] for i=0..N-2m
            end_idx = N - 2*m
            s1 = cs[m : m+end_idx+1] - cs[0 : end_idx+1]
            s2 = cs[2*m : 2*m+end_idx+1] - cs[m : m+end_idx+1]
            
            diffs = (s2 - s1) / m
            
            # sigma^2 = 0.5 * mean(diffs^2)
            sigma2 = 0.5 * np.mean(diffs**2)
            ad.append(np.sqrt(sigma2))
            
        return ad

    taus = np.logspace(0, int(np.log10(len(data)/3)), 5)
    adevs = _simple_oadev(data, rate, taus)
    
    return {
        'taus': taus,
        'adevs': adevs
    }

def prewhiten(df, phi=0.0):
    """
    Prewhiten for HAC if required?
    Spec: "Prewhiten if required" -> usually AR(1) filter.
    y_t* = y_t - phi * y_{t-1}
    x_t* = x_t - phi * x_{t-1}
    
    Actually HAC handles autocorrelation, but prewhitening can improve small sample performance.
    If phi is not provided, we might estimate it.
    Spec says "Use HAC ... Prewhiten if required".
    We'll leave this hooks for now.
    """
    if phi == 0.0:
        return df
        
    # Apply AR(1) filter
    # ... implementation skipped for now, relying on HAC
    return df
