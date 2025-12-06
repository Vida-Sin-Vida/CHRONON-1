import os
import shutil
import hashlib
from chronon_core import ledger

def package_ledger(run_id, output_dir="replication_package"):
    """
    Packages the ledger, processed data, and code validation hashes.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy ledger
    if os.path.exists("ledger/runs_ledger.csv"):
        shutil.copy("ledger/runs_ledger.csv", os.path.join(output_dir, "runs_ledger.csv"))
        
    # Hash code
    code_hash = ledger.Ledger.hash_code("chronon_core")
    with open(os.path.join(output_dir, "code_hash.txt"), "w") as f:
        f.write(code_hash)
        
    print(f"Replication package created in {output_dir}")

if __name__ == "__main__":
    # Example usage
    package_ledger("latest")
