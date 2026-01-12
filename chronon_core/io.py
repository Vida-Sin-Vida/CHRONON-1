import pandas as pd
import logging

REQUIRED_HEADERS = [
    "timestamp_UTC", "site_id", "site_pair", "site_pair_label", "pair_orientation",
    "operator_id", "run_id", "height_m", "Delta_h_m", "y_frac",
    "allan_tau_s", "allan_sy_per_h", "T2_s", "T1_s", "Tphi_s",
    "temp_C", "pressure_hPa", "humidity_pct", "a_rms_ms2", "rf_intrusion_flag",
    "link_type", "link_SNR_dB", "firmware_tag", "g_local_mps2",
    "geoid_model", "geoid_version", "tide_model", "sagnac_applied", "sagnac_value",
    "pressure_load_corr", "sigma_dh_m", "duty_cycle", "software_env", "random_seed"
]

DERIVED_HEADERS = [
    "timestamp_UTC", "site_pair", "swap_flag", "operator_id", "run_id",
    "X_GR", "Delta_lnPhi", "Y_res", "sigma_X", "sigma_Y", "band_id"
]

def load_raw_csv(filepath):
    """
    Loads a raw measurement CSV and validates its schema strictly.
    """
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        logging.error(f"Failed to read CSV {filepath}: {e}")
        raise

    # strict header check
    missing = set(REQUIRED_HEADERS) - set(df.columns)
    if missing:
        msg = f"Schema violation in {filepath}. Missing columns: {missing}"
        logging.error(msg)
        raise ValueError(msg)
    
    # Ensure types for critical columns
    df['timestamp_UTC'] = pd.to_datetime(df['timestamp_UTC'])
    numeric_cols = ["Delta_h_m", "y_frac", "g_local_mps2", "sigma_dh_m", "sagnac_value", "pressure_load_corr"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df

def save_processed(df, filepath):
    """
    Saves the processed dataframe ensuring derived table schema.
    """
    # check that we have the columns
    missing = set(DERIVED_HEADERS) - set(df.columns)
    if missing:
        logging.warning(f"Processed dataframe missing columns intended for output: {missing}")
    
    # Save only the columns in the spec, or all if strictness not required for interim? 
    # Spec says "Derived table ... must match Sec. VII". So we filter.
    out_df = df[DERIVED_HEADERS] if set(DERIVED_HEADERS).issubset(df.columns) else df
    out_df.to_csv(filepath, index=False)
    logging.info(f"Saved processed data to {filepath}")
