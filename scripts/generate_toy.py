import argparse
import os
import sys
import yaml
import numpy as np
import pandas as pd

C_LIGHT = 299792458.0

# Full list of required headers from chronon_core.io
REQUIRED_HEADERS = [
    "timestamp_UTC", "site_id", "site_pair", "site_pair_label", "pair_orientation",
    "operator_id", "run_id", "height_m", "Delta_h_m", "y_frac",
    "allan_tau_s", "allan_sy_per_h", "T2_s", "T1_s", "Tphi_s",
    "temp_C", "pressure_hPa", "humidity_pct", "a_rms_ms2", "rf_intrusion_flag",
    "link_type", "link_SNR_dB", "firmware_tag", "g_local_mps2",
    "geoid_model", "geoid_version", "tide_model", "sagnac_applied", "sagnac_value",
    "pressure_load_corr", "sigma_dh_m", "duty_cycle", "software_env", "random_seed"
]

def simulate_data(n_samples=500, eps_phi=0.0, seed=0, output="toy.csv"):
    np.random.seed(seed)
    
    # 1. Physics Generation
    t_s = np.arange(n_samples, dtype=float)
    start_time = pd.Timestamp("2024-01-01 12:00:00")
    timestamps = start_time + pd.to_timedelta(t_s, unit='s')
    
    tidal_freq = 2 * np.pi / 43200.0
    avg_h = 500.0
    delta_h = avg_h + 0.5 * np.sin(tidal_freq * t_s)
    g = 9.81
    X_GR = g * delta_h / (C_LIGHT**2)
    
    sigma_y = 1e-15
    noise = np.random.normal(0, sigma_y, n_samples)
    y_meas = X_GR * (1.0 + eps_phi) + noise
    
    # 2. DataFrame Construction
    df = pd.DataFrame()
    df['timestamp_UTC'] = timestamps
    
    # Physics columns
    df['Delta_h_m'] = delta_h
    df['g_local_mps2'] = g
    df['y_frac'] = y_meas
    df['sagnac_value'] = 0.0
    df['sagnac_applied'] = 1 # True
    df['pressure_load_corr'] = 0.0
    df['sigma_dh_m'] = 0.01
    df['allan_sy_per_h'] = 1e-16
    
    # Dummy Metadata to satisfy Schema
    df['site_id'] = "TOY_SITE"
    df['site_pair'] = "TOY_A-TOY_B"
    df['site_pair_label'] = "Laboratory Test"
    df['pair_orientation'] = "V"
    df['operator_id'] = "AUTO_BOT"
    df['run_id'] = "TOY_001"
    df['height_m'] = 500.0
    df['allan_tau_s'] = 1.0
    df['T2_s'] = 60.0
    df['T1_s'] = 60.0
    df['Tphi_s'] = 60.0
    df['temp_C'] = 20.0
    df['pressure_hPa'] = 1013.0
    df['humidity_pct'] = 50.0
    df['a_rms_ms2'] = 0.0
    df['rf_intrusion_flag'] = 0
    df['link_type'] = "FIBER"
    df['link_SNR_dB'] = 100.0
    df['firmware_tag'] = "v1.0"
    df['geoid_model'] = "EGM2008"
    df['geoid_version'] = "1.0"
    df['tide_model'] = "NONE"
    df['duty_cycle'] = 1.0
    df['software_env'] = "Python 3.11"
    df['random_seed'] = seed
    
    # Reorder to match if needed, or just ensure existence
    # We will write all required headers
    for col in REQUIRED_HEADERS:
        if col not in df.columns:
            df[col] = 0 # Safety net
            
    os.makedirs(os.path.dirname(output), exist_ok=True)
    df.to_csv(output, index=False)
    print(f"Generated toy dataset at {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    
    with open(args.config) as f:
        cfg = yaml.safe_load(f)
        
    ds = cfg.get("dataset", {})
    simulate_data(
        n_samples=ds.get("n", 500),
        eps_phi=ds.get("eps", 0.0),
        seed=cfg.get("seed", 0),
        output=args.output
    )
