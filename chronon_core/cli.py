import argparse
import sys
import os
import logging
import pandas as pd
import numpy as np
from chronon_core import io, preprocess, windowing, stats, simulator, ablations, blinding, ledger

def load_config(config_path):
    try:
        import yaml
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except ImportError:
        logging.warning("PyYAML not found, using simple fallback parser.")
        return _fallback_parse(config_path)
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return {}

def _fallback_parse(path):
    config = {}
    with open(path, 'r') as f:
        for line in f:
            if ':' in line and not line.strip().startswith('#'):
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip().split('#')[0].strip()
                # Try infer type
                try:
                    if '.' in val:
                        config[key] = float(val)
                    else:
                        config[key] = int(val)
                except ValueError:
                    config[key] = val.replace('"', '').replace("'", "")
    return config

def cmd_ingest(args):
    print(f"Ingesting {args.input_file}...")
    df = io.load_raw_csv(args.input_file)
    io.save_processed(df, args.output)
    print(f"Saved processed file to {args.output}")

def cmd_preprocess(args):
    config = load_config(args.config)
    print(f"Preprocessing {args.input_file} with config {args.config}...")
    
    df = pd.read_csv(args.input_file)
    
    # 1. Discipline checks
    preprocess.check_discipline(df)
    
    # 2. Geodesy matches
    # (Assuming columns exist or we compute them here)
    
    # 3. Compute X, Y
    df = preprocess.compute_variables(df)
    
    # 4. Windowing
    w_sec = config.get('window_seconds', 120)
    df_windowed = windowing.compute_windows(df, window_sec=w_sec)
    
    io.save_processed(df_windowed, args.output)
    print(f"Preprocessed data saved to {args.output}")

def cmd_analyze(args):
    import pandas as pd # Ensure pandas is imported if not already in scope
    config = load_config(args.config)
    print(f"Analyzing {args.input_file}...")
    
    df = pd.read_csv(args.input_file)
    
    # Check blinding
    # If blinded, we might not see real Sigma_Y or Labels?
    # Assuming analysis runs on processed data.
    
    # Extract
    X = df['X_GR'].values
    Y = df['Y_res'].values
    sigma_Y = df['sigma_Y'].values
    
    # 1. Primary WLS
    res_wls = stats.fit_free_intercept_wls(X, Y, sigma_Y)
    print("Primary WLS Result:")
    print(res_wls)
    
    # 2. Bootstrap Check
    if args.bootstrap:
        bs_res = stats.wild_bootstrap(X, Y, sigma_Y, n_boot=config.get('bootstrap_n', 2000))
        print("Bootstrap Results:")
        print(bs_res)
        
    # 3. Deming Check
    # Ratio lambda = mean(sigY^2/sigX^2)
    # Filter valid sigmas
    valid = (df['sigma_X'] > 0) & (df['sigma_Y'] > 0)
    if valid.any():
        lam = np.mean(df.loc[valid, 'sigma_Y']**2 / df.loc[valid, 'sigma_X']**2)
        # Assuming fixed lambda Deming? Or WTLS.
        # Calling our WTLS function which assumes we pass arrays
        res_dem = stats.fit_deming_wtls(X, Y, df['sigma_X'].values, df['sigma_Y'].values)
        print("Deming Results:")
        print(res_dem)

def cmd_simulate(args):
    config = load_config(args.config)
    sim = simulator.Simulator(config)
    
    print(f"Simulating run with eps_phi={args.eps}...")
    df = sim.simulate_run(eps_phi=args.eps)
    
    out_path = args.output if args.output else "simulated_run.csv"
    io.save_processed(df, out_path)
    print(f"Simulated data saved to {out_path}")

def cmd_demo(args):
    """
    Runs the full pipeline end-to-end for demonstration.
    """
    print("\n=== CHRONON-1 PIPELINE DEMO ===\n")
    
    # 1. Simulate
    print("[1/4] Simulating Data...")
    sim_args = argparse.Namespace(config=args.config, eps=0.001, output='data/raw/demo_sim.csv')
    cmd_simulate(sim_args)
    
    # 2. Ingest
    print("\n[2/4] Ingesting Data...")
    ingest_args = argparse.Namespace(input_file='data/raw/demo_sim.csv', output='data/processed/demo_ingested.csv')
    cmd_ingest(ingest_args)
    
    # 3. Preprocess
    print("\n[3/4] Preprocessing Data...")
    pre_args = argparse.Namespace(config=args.config, input_file='data/processed/demo_ingested.csv', output='data/processed/demo_preprocessed.csv')
    cmd_preprocess(pre_args)
    
    # 4. Analyze
    print("\n[4/4] Analyzing Data...")
    ana_args = argparse.Namespace(config=args.config, input_file='data/processed/demo_preprocessed.csv', bootstrap=True)
    cmd_analyze(ana_args)
    
    print("\n=== DEMO COMPLETE ===")

def main():
    parser = argparse.ArgumentParser(description="CHRONON-1 Pipeline CLI")
    subparsers = parser.add_subparsers(dest='command')
    
    # ingest
    p_ingest = subparsers.add_parser('ingest')
    p_ingest.add_argument('input_file', help="Path to raw CSV")
    p_ingest.add_argument('--output', default='data/processed/ingested.csv')
    
    # preprocess
    p_pre = subparsers.add_parser('preprocess')
    p_pre.add_argument('--config', default='config.yml')
    p_pre.add_argument('--input_file', required=True)
    p_pre.add_argument('--output', required=True)
    
    # analyze
    p_ana = subparsers.add_parser('analyze')
    p_ana.add_argument('--config', default='config.yml')
    p_ana.add_argument('--input_file', required=True)
    p_ana.add_argument('--bootstrap', action='store_true')
    
    # simulate
    p_sim = subparsers.add_parser('simulate')
    p_sim.add_argument('--config', default='config.yml')
    p_sim.add_argument('--eps', type=float, default=0.0)
    p_sim.add_argument('--output')
    
    # demo
    p_demo = subparsers.add_parser('demo')
    p_demo.add_argument('--config', default='config.yml')
    
    args = parser.parse_args()
    
    if args.command == 'ingest':
        cmd_ingest(args)
    elif args.command == 'preprocess':
        cmd_preprocess(args)
    elif args.command == 'analyze':
        cmd_analyze(args)
    elif args.command == 'simulate':
        cmd_simulate(args)
    elif args.command == 'demo':
        cmd_demo(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
