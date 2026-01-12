# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import csv
import hashlib
import json
import os
import datetime

class Ledger:
    def __init__(self, ledger_path):
        self.path = ledger_path
        self._ensure_header()
        
    def _ensure_header(self):
        header = ["timestamp", "run_id", "verdict", "hash_config", "hash_code", "json_row_path", "row_hash", "operator", "blinding_event"]
        
        if not os.path.exists(self.path):
            with open(self.path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                
    def append_run(self, run_id, verdict, config_hash, code_hash, row_data, operator="Unknown", blinding_event=None):
        """
        Appends a run to the ledger with full traceability.
        """
        ts = datetime.datetime.utcnow().isoformat()
        
        row_data['meta_timestamp'] = ts
        row_data['operator'] = operator
        row_data['blinding_event'] = blinding_event
        row_data['config_hash'] = config_hash
        row_data['code_hash'] = code_hash
        row_data['run_verdict'] = verdict

        json_filename = f"ledger_row_{run_id}_{ts.replace(':','').replace('.','')}.json"
        json_path = os.path.join(os.path.dirname(self.path), json_filename)
        
        json_bytes = json.dumps(row_data, sort_keys=True, indent=2).encode('utf-8')
        row_hash = hashlib.sha256(json_bytes).hexdigest()
        
        with open(json_path, 'wb') as f:
            f.write(json_bytes)
            
        with open(self.path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ts, run_id, verdict, config_hash, code_hash, json_filename, row_hash, operator, blinding_event])
            
    @staticmethod
    def hash_code(directory):
        """
        Hashes all .py files in the directory for code freezing.
        """
        sha = hashlib.sha256()
        for root, dirs, files in os.walk(directory):
            for name in sorted(files):
                if name.endswith('.py'):
                    filepath = os.path.join(root, name)
                    with open(filepath, 'rb') as f:
                        while True:
                            data = f.read(65536)
                            if not data:
                                break
                            sha.update(data)
        return sha.hexdigest()

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
