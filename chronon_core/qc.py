# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import numpy as np

class QualityControl:
    """
    Quality Control (QC) module for CHRONON runs.
    Enforces experimental standards on temperature, vibration, and data integrity.
    """
    
    DEFAULT_CONFIG = {
        'min_temp_C': 15.0,
        'max_temp_C': 30.0,
        'max_vibration_rms': 0.5,  # m/s^2
        'min_samples': 30,
        'max_jitter_dh': 0.05,     # meters
        'witness_dh_tol': 0.1      # meters, tolerance for null check
    }

    def __init__(self, config=None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

    def assess_run(self, df, run_metadata=None):
        """
        Assess a single run dataframe against configured QC thresholds.

        Parameters:
        -----------
        df : pandas.DataFrame
            Data for a single run. Must contain 'temp_C', 'a_rms_ms2', 'Delta_h_m' if available.
        run_metadata : dict, optional
            Metadata describing the run (e.g., 'is_witness').
        
        Returns:
        --------
        tuple
            (status, flags)
            status : str ("PASS", "WARN", or "FAIL")
            flags : list of strings describing failure reasons.
        """
        flags = []
        status = "PASS"
        
        # 1. Min Samples
        if len(df) < self.config['min_samples']:
            flags.append("N_SAMPLES_LOW")
            status = "FAIL"

        # 2. Environmental Checks
        if 'temp_C' in df.columns:
            mean_temp = df['temp_C'].mean()
            if not (self.config['min_temp_C'] <= mean_temp <= self.config['max_temp_C']):
                flags.append(f"TEMP_OUT_OF_BOUNDS: {mean_temp:.1f}")
                status = "FAIL"

        if 'a_rms_ms2' in df.columns:
            max_vib = df['a_rms_ms2'].max()
            if max_vib > self.config['max_vibration_rms']:
                flags.append(f"HIGH_VIBRATION: {max_vib:.2f}")
                status = "FAIL"

        # 3. Jitter on Delta h (stability)
        if 'Delta_h_m' in df.columns:
            dh_max = df['Delta_h_m'].max()
            dh_min = df['Delta_h_m'].min()
            dh_range = dh_max - dh_min
            
            # If range is large (>1m), it implies a SWEEP (Scan), so big std is expected.
            # If range is small, it implies STATIC mode, so we expect stability.
            if dh_range <= 1.0:
                dh_std = df['Delta_h_m'].std()
                if dh_std > self.config['max_jitter_dh']:
                    flags.append(f"UNSTABLE_HEIGHT: std={dh_std:.3f}")
                    status = "FAIL"
                
            # 4. Witness Check
            # Check if it is a witness run (Delta h ~ 0)
            is_witness = False
            if run_metadata and run_metadata.get('is_witness'):
                is_witness = True
            
            if is_witness:
                if abs(df['Delta_h_m'].mean()) > self.config['witness_dh_tol']:
                     flags.append("WITNESS_HEIGHT_NONZERO")
                     status = "FAIL"

        return status, flags

    def assess_batch(self, runs_list):
        """
        Assess a batch of runs.
        """
        results = {}
        for run_id, (df, meta) in runs_list.items():
            s, f = self.assess_run(df, meta)
            results[run_id] = {'status': s, 'flags': f}
        return results

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
