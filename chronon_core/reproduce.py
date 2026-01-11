import os
import sys
import json
import platform
import hashlib
import subprocess
from datetime import datetime
from datetime import timezone
import numpy as np
import yaml
import pandas as pd
import scipy
try:
    import statsmodels
    STATSMODELS_VERSION = statsmodels.__version__
except ImportError:
    STATSMODELS_VERSION = "not_installed"

# Internal modules
from chronon_core import preprocess, windowing, stats, io

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()

def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

def git_rev() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

def run_reproduce(config_path: str):
    print(f"Loading config from {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()
    
    config_hash = sha256_string(config_content)
    cfg = yaml.safe_load(config_content)

    # 1. Setup Environment
    seed = int(cfg.get("seed", 0))
    # Enforce global seeding for deterministic behavior in analysis steps
    np.random.seed(seed)
    
    out_dir = cfg.get("out_dir", "reports")
    os.makedirs(out_dir, exist_ok=True)
    
    # 2. Data Acquisition
    dataset_cfg = cfg.get("dataset", {})
    kind = dataset_cfg.get("kind", "toy")
    
    df = None
    dataset_source_hash = "unknown"
    dataset_actual_path = "unknown"
    
    if kind == "toy":
        # Run external script to generate data
        print("Generating toy dataset using scripts/generate_toy.py...")
        script_path = os.path.join("scripts", "generate_toy.py")
        if not os.path.exists(script_path):
             raise FileNotFoundError(f"Generation script not found at {script_path}. Please run from project root.")
        
        toy_output = os.path.join("data", "raw", "toy_run_auto.csv")
        dataset_actual_path = toy_output
        
        # Call subprocess
        cmd = [sys.executable, script_path, "--config", config_path, "--output", toy_output]
        subprocess.check_call(cmd)
        
        print(f"Loading generated dataset from {toy_output}...")
        df = io.load_raw_csv(toy_output)
        dataset_source_hash = sha256_file(toy_output)
        
    elif kind == "external":
        path = dataset_cfg.get("path")
        dataset_actual_path = path
        print(f"Loading external dataset from {path}...")
        df = io.load_raw_csv(path)
        if os.path.exists(path):
            dataset_source_hash = sha256_file(path)
    else:
        raise ValueError(f"Unknown dataset kind: {kind}")

    # 3. Preprocessing
    print("Preprocessing...")
    
    try:
        preprocess.check_discipline(df)
    except Exception as e:
        print(f"Warning: Discipline check failed: {e}")

    df = preprocess.compute_variables(df)
    
    # Windowing
    w_sec = cfg.get("window_seconds", 120)
    df_windowed = windowing.compute_windows(df, window_sec=w_sec)
    
    # 4. Analysis
    print("Analyzing...")
    analysis_cfg = cfg.get("analysis", {})
    
    X = df_windowed['X_GR'].values
    Y = df_windowed['Y_res'].values
    sigma_Y = df_windowed['sigma_Y'].values
    
    results = {
        "status": "ok", 
        "seed": seed,
        "config": cfg,
        "metrics": {}
    }

    # Primary WLS
    res_wls = stats.fit_free_intercept_wls(X, Y, sigma_Y)
    results["metrics"]["wls"] = res_wls
    
    print("WLS Results:", res_wls)

    # Bootstrap
    if analysis_cfg.get("bootstrap", False):
        print("Running bootstrap...")
        bs_res = stats.wild_bootstrap(X, Y, sigma_Y, n_boot=analysis_cfg.get("n_boot", 2000))
        results["metrics"]["bootstrap"] = bs_res

    # 5. Output Generation
    results_path = os.path.join(out_dir, "results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        # Use Custom Encoder and sort_keys for strict reproducibility
        json.dump(results, f, indent=2, cls=NumpyEncoder, sort_keys=True)

    # checksums
    checksum_path = os.path.join(out_dir, "checksums.sha256")
    with open(checksum_path, "w", encoding="utf-8") as f:
        f.write(f"{sha256_file(results_path)}  results.json\n")

    # run report
    report_path = os.path.join(out_dir, "RUN_REPORT.md")
    timestamp_utc = datetime.now(timezone.utc).isoformat()
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# CHRONON-1 RUN REPORT\n\n")
        f.write(f"- datetime_utc: {timestamp_utc}\n")
        f.write(f"- git_commit: {git_rev()}\n")
        f.write(f"- python: {platform.python_version()}\n")
        f.write(f"- platform: {platform.platform()}\n")
        f.write(f"- numpy: {np.__version__}\n")
        f.write(f"- pandas: {pd.__version__}\n")
        f.write(f"- scipy: {scipy.__version__}\n")
        f.write(f"- statsmodels: {STATSMODELS_VERSION}\n")
        f.write(f"- seed: {seed}\n")
        f.write(f"- config_file: {config_path}\n")
        f.write(f"- config_sha256: {config_hash}\n")
        f.write(f"- dataset_path: {dataset_actual_path}\n")
        f.write(f"- dataset_sha256: {dataset_source_hash}\n")
        f.write(f"- output_dir: {out_dir}\n")
        f.write("\n## Key Results\n")
        f.write("### WLS Fit\n")
        
        wls_dict = results["metrics"]["wls"]
        for k in sorted(wls_dict.keys()): 
            f.write(f"- **{k}**: {wls_dict[k]}\n")
            
    print(f"Reproduction complete. Results in {out_dir}")
