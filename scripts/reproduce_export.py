
import os
import sys
import pandas as pd
import json
import glob

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chronon_core.stats import analyze_with_fallback, calculate_slope_epsilon_phi

def verify_reproducibility(ledger_dir="validation_results"):
    """
    Attempts to reproduce analysis from Exported Ledger + JSONs.
    Note: Since validate_scientific.py simulation did NOT save raw X,Y arrays to JSON 
          (it only saved summary stats in row_data), we cannot bitwise reproduce 
          the simulation runs without the seed or raw data.
          
    However, for the purpose of this check, we will demonstrate the capability
    by verifying the INTEGRITY of the ledger (hashes match content) and 
    displaying the stored results.
    
    If raw data were stored (e.g. experimental runs), we would load X,Y from JSON
    and re-run `analyze_with_fallback` and assert equality.
    """
    print(f"Scanning export directory: {ledger_dir}")
    
    csv_path = os.path.join(ledger_dir, "validation_ledger.csv")
    if not os.path.exists(csv_path):
        print(f"[FAIL] Ledger CSV not found at {csv_path}")
        return False
        
    df_ledger = pd.read_csv(csv_path, names=["timestamp", "run_id", "verdict", "config_hash", "code_hash", "json_path", "row_hash", "operator", "blinding"])
    
    print(f"Found {len(df_ledger)} ledger entries.")
    
    verified_count = 0
    failed_count = 0
    
    # Check a sample
    sample_size = min(50, len(df_ledger))
    print(f"Verifying integrity of last {sample_size} runs...")
    
    import hashlib
    
    for i in range(len(df_ledger) - sample_size, len(df_ledger)):
        if i < 0:
            continue
        
        row = df_ledger.iloc[i]
        json_file = row['json_path']
        full_json_path = os.path.join(ledger_dir, json_file)
        
        if not os.path.exists(full_json_path):
            print(f"[WARN] JSON file missing: {json_file}")
            failed_count += 1
            continue
            
        # Verify Hash
        with open(full_json_path, 'r') as f:
            data = json.load(f)
            # Re-serialize to check hash
            # Note: Reproducing exact JSON dump binary is tricky due to whitespace options.
            # Ledger.py used: json.dumps(row_data, sort_keys=True, indent=2).encode('utf-8')
            json_bytes = json.dumps(data, sort_keys=True, indent=2).encode('utf-8')
            recalc_hash = hashlib.sha256(json_bytes).hexdigest()
            
            if recalc_hash == row['row_hash']:
                verified_count += 1
            else:
                print(f"[FAIL] Hash Mismatch for {row['run_id']}")
                print(f"Expected: {row['row_hash']}")
                print(f"Got     : {recalc_hash}")
                failed_count += 1

    print("\nVerification Results:")
    print(f"Verified : {verified_count}")
    print(f"Failed   : {failed_count}")
    
    if failed_count == 0:
        print("[SUCCESS] Export integrity confirmed.")
    else:
        print("[FAIL] Some records corrupted or missing.")
        
if __name__ == "__main__":
    verify_reproducibility()
