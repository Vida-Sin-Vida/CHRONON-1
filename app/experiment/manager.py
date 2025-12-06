# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
import threading
import time
import random
import datetime
import json
import os

class ExperimentManager:
    def __init__(self):
        self.is_running = False
        self.params = {}
        self.data_log = []
        self.history_file = "history.json"
        self.history = self._load_history()
        self.current_run_index = 0
        self.listeners = [] # Observers for updates

    def _load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                return []
        return []

    def _save_history(self):
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {e}")

    def add_listener(self, listener):
        self.listeners.append(listener)

    def notify_listeners(self, event_type, data=None):
        for listener in self.listeners:
            listener(event_type, data)

    def start_experiment(self, n_runs, delta_h, duration, link_type, 
                         scenario="Standard", blinded=False, batch_mode=False,
                         alpha=0.01, beta=0.5, nu_sq=1.0, radius=100.0, gamma=0.0):
        if self.is_running:
            return
        
        self.params = {
            "n_runs": int(n_runs),
            "delta_h": float(delta_h),
            "duration": float(duration),
            "link_type": link_type,
            "scenario": scenario,
            "blinded": blinded,
            "batch_mode": batch_mode,
            "alpha": alpha,
            "beta": beta,
            "nu_sq": nu_sq,
            "radius": radius,
            "gamma": gamma # Recursivity Factor (0.0 - 0.99)
        }
        
        self.is_running = True
        self.current_run_index = 0
        self.data_log = []
        
        print(f"Starting experiment with {self.params}")
        self.notify_listeners("start", self.params)
        
        # Start background thread
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop_experiment(self):
        self.is_running = False
        self.notify_listeners("stop")

    def _run_loop(self):
        start_time = time.time()
        
        scenario = self.params.get("scenario", "Standard")
        blinded = self.params.get("blinded", False)
        
        # Sci Params
        alpha = self.params.get("alpha", 0.01)
        beta = self.params.get("beta", 0.5)
        gamma = self.params.get("gamma", 0.0) # Recursion
        batch = self.params.get("batch_mode", False)
        
        last_phi = 0 # Memory for recursion
        if gamma > 0:
            last_phi = random.gauss(0, 1) # Init seed
        
        while self.is_running and self.current_run_index < self.params["n_runs"]:
            try:
                # Simulate a run
                if not batch:
                    time.sleep(0.1) # Normal delay
                else:
                    pass # Max speed - UI updates throttled below
                
                # --- Demo Overrides ---
                # We override per-step or pre-calc? Pre-calc is better but doing here is safe.
                if "Demo" in scenario:
                    # Default Params for Demo
                    std_noise = 1.0
                    if "S1" in scenario: std_noise = 0.2
                    
                    if "Négatif" in scenario:
                        alpha = 0.0
                        beta = 0.0 # Flat
                    elif "Positif" in scenario:
                        # Estimate required slope for specific Sigma
                        # Z = slope * sqrt(N) * std_x / std_noise
                        # slope = Z * std_noise / (sqrt(N) * std_x)
                        
                        target_z = 3.0
                        if "5" in scenario: target_z = 5.5 # Strong
                        
                        # Approx Std(X) for linear sweep -dh to +dh is dh/sqrt(3)
                        # dh is stored in params
                        curr_dh = self.params.get("delta_h", 50.0)
                        std_x = curr_dh / 1.732 
                        n_total = self.params.get("n_runs", 100)
                        
                        import math
                        alpha = (target_z * std_noise) / (math.sqrt(n_total) * std_x)
                        beta = 0.0 # Clean center
                
                # --- Sweep Height Logic ---
                # To allow regression in a single run, we sweep height from -delta_h to +delta_h
                target_dh = self.params.get("delta_h", 50.0)
                if self.params["n_runs"] > 1:
                     # Linear interpolation: -dh to +dh
                     progress_fraction = self.current_run_index / (self.params["n_runs"] - 1)
                     current_h = -target_dh + 2 * target_dh * progress_fraction
                else:
                     current_h = target_dh
                     
                # --- Physics Calculation ---
                phi_val = self._calculate_physics_step(scenario, alpha, beta, gamma, last_phi, current_h)
                last_phi = phi_val # Update memory for recursion
                
                # --- Data Generation ---
                run_data = {
                    "id": self.current_run_index + 1,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "phi": phi_val,
                    "temperature": 20 + random.random(), # Mock Env
                    "status": "valid" if random.random() > 0.05 else "invalid",
                     # Scientific Columns for Visualization
                    "Delta_h_m": current_h,
                    "Delta_lnPhi": phi_val, # Identifying raw phi as observable
                    "sigma_Y": 0.01 if "S1" in scenario else 1.0, # Estimated error
                    "sigma_dh_m": 0.1 # Position uncertainty
                }
                
                self.data_log.append(run_data)
                self.current_run_index += 1
                
                # --- UI Updates (Optimized) ---
                # In batch mode, update only every 10 runs to save CPU
                should_update = True
                if batch and (self.current_run_index % 10 != 0) and (self.current_run_index != self.params["n_runs"]):
                    should_update = False

                if should_update:
                    progress = (self.current_run_index / self.params["n_runs"])
                    self.notify_listeners("progress", {"progress": progress, "run_data": run_data})
                    
                    # Log env data (Mask if blinded)
                    log_msg = f"Run {run_data['id']}: Temp={run_data['temperature']:.2f}C"
                    if not blinded:
                        log_msg += f", Phi={run_data['phi']:.4f}"
                    else:
                        log_msg += ", Phi=***BLINDED***"
                    self.notify_listeners("log", log_msg)

            except Exception as e:
                print(f"CRITICAL ERROR in Run {self.current_run_index}: {e}")
                self.notify_listeners("log", f"ERROR: {str(e)}")
                # Decide: Continue or Break? For robustness, we try to continue unless it's fatal
                pass

        self.is_running = False
        
        # Save to History
        experiment_record = {
            "id": f"RUN-{int(time.time())}",
            "timestamp": datetime.datetime.now().isoformat(),
            "params": self.params,
            "data": self.data_log
        }
        self.history.append(experiment_record)
        self._save_history() # Persist to disk
        
        self.notify_listeners("complete", self.data_log)

    def _calculate_physics_step(self, scenario, alpha, beta, gamma, last_phi, current_h):
        """
        Calculates the next Phi value based on scenario and parameters.
        Encapsulates the physics logic for clarity and reuse.
        """
        mean = 0.0
        std = 1.0
        
        # 1. Determine Scenario Baseline
        if "S1" in scenario:
            std = 0.2 # Low noise
        elif "S2" in scenario:
            mean = 2.0 # High shift
        elif "S3" in scenario:
            if random.random() > 0.8: mean = 5.0 # Anomalies

        # 2. Physics Formula: Phi = Gauss(mean, std) + (dh * alpha) + beta
        base_phi = random.gauss(mean, std) + (current_h * alpha) + beta
        
        # 3. Apply Recursivity (Gamma factor)
        # Phi_t = (1-g)*New + g*Old
        if gamma > 0:
            return (1 - gamma) * base_phi + gamma * last_phi
        
        return base_phi

    def delete_history_items(self, run_ids):
        """
        Deletes multiple history items by their IDs.
        """
        original_count = len(self.history)
        # Filter out items whose ID is in the run_ids list
        self.history = [r for r in self.history if r['id'] not in run_ids]
        
        if len(self.history) < original_count:
            self._save_history()

    def delete_history_item(self, run_id):
        # Wrapper for backward compatibility or single deletion
        self.delete_history_items([run_id])

    def _simulate_single_run(self, index, params):
        scenario = params.get("scenario", "Standard")
        alpha = params.get("alpha", 0.01)
        beta = params.get("beta", 0.5)
        dh = params.get("delta_h", 50.0)
        
        # Re-use logic if possible, or keep simple for single run sim
        # Currently _simulate_single_run is used by 'Simulateur' notebook likely, or independent tests
        # We will map it to the same logic for consistency
        
        # Construct args
        gamma = params.get("gamma", 0.0)
        # Use a dummy last_phi = 0 for single shot
        
        # Note: this method seems redundant if we have the main loop, 
        # but we'll clean it up to be consistent
        
        # ...Logic reproduced for standalone use...
        if "S1" in scenario: std = 0.2
        elif "S2" in scenario: mean = 2.0
        elif "S3" in scenario: 
            if random.random() > 0.8: mean = 5.0

        phi_val = random.gauss(mean, std) + (dh * alpha) + beta
        
        return {
            "id": index + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "phi": phi_val,
            "temperature": 20 + random.random(),
            "status": "valid" if random.random() > 0.05 else "invalid",
            "params": params # Store params for analysis
        }

    def get_results(self):
        return self.data_log
