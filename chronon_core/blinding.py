import hashlib
import json
import os
import pandas as pd
import uuid

class BlindingManager:
    def __init__(self, key_salt):
        self.salt = key_salt
        self._mapping = {} # Internal storage for active session
        
    def blind_labels(self, df):
        """
        Blinds Delta_h labels and link types.
        Returns: blinded_df, mapping_id
        """
        blinded = df.copy()
        
        # New mapping for this session
        mapping_id = str(uuid.uuid4())
        current_map = {}
        
        cols_to_blind = ['site_pair_label', 'link_type']
        
        for col in cols_to_blind:
            if col in blinded.columns:
                # Create unique map for each unique value
                unique_vals = blinded[col].unique()
                col_map = {}
                for val in unique_vals:
                    # Deterministic hash but salted
                    blind_val = self._hash_val(val)[:8] # Short hash
                    col_map[blind_val] = val
                    
                # Apply map (invert it for apply)
                # We need val -> blind_val
                val_to_blind = {v: k for k, v in col_map.items()}
                blinded[col] = blinded[col].map(val_to_blind)
                
                current_map[col] = col_map
                
        self._mapping[mapping_id] = current_map
        return blinded, mapping_id

    def unblind_labels(self, blinded_df, mapping_id):
        """
        Restores original labels using the mapping_id.
        """
        if mapping_id not in self._mapping:
            raise ValueError("Invalid or expired mapping ID")
            
        unblinded = blinded_df.copy()
        mapping = self._mapping[mapping_id]
        
        for col, col_map in mapping.items():
            if col in unblinded.columns:
                # col_map is blind -> original
                unblinded[col] = unblinded[col].map(col_map)
                
        return unblinded

    def _hash_val(self, val):
        s = f"{val}{self.salt}"
        return hashlib.sha256(s.encode()).hexdigest()

    def freeze_config(self, config_dict):
        """
        Computes SHA-256 of the configuration.
        """
        s = json.dumps(config_dict, sort_keys=True)
        return hashlib.sha256(s.encode()).hexdigest()

