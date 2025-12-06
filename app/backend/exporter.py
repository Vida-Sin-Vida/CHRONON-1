
import os
import json
import pandas as pd
import datetime
import shutil
import subprocess
import hashlib
import logging

class ReproducibleExporter:
    """
    Handles the creation of a fully reproducible export package.
    """
    
    def __init__(self, output_base_dir="exports"):
        self.base_dir = output_base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
    def export_run(self, data_df, metadata, ledger_path, figures=None):
        """
        Creates a timestamped folder with all artifacts.
        
        Args:
            data_df (pd.DataFrame): The processed data.
            metadata (dict): Analysis results, QC verdict, config, RNG seed.
            ledger_path (str): Path to the master ledger file.
            figures (list): List of matplotlib figures to save (optional).
            
        Returns:
            str: Path to the created export directory.
        """
        
        # 1. Create Timestamped Directory
        ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        run_id = metadata.get("run_id", "unknown_run")
        export_dir = os.path.join(self.base_dir, f"export_{ts}_{run_id}")
        os.makedirs(export_dir, exist_ok=True)
        
        try:
            # 2. Save Data
            data_path = os.path.join(export_dir, "data_processed.csv")
            data_df.to_csv(data_path, index=False)
            
            # Compute data hash
            with open(data_path, "rb") as f:
                data_hash = hashlib.sha256(f.read()).hexdigest()
            metadata["export_data_hash"] = data_hash
            
            # 3. Save Metadata (Config + QC + Stats)
            meta_path = os.path.join(export_dir, "metadata.json")
            with open(meta_path, "w") as f:
                json.dump(metadata, f, indent=4)
                
            # 4. Snapshot Environment (requirements.txt)
            req_path = os.path.join(export_dir, "requirements.txt")
            try:
                # Capture pip freeze
                subprocess.check_call([pd.sys.executable, "-m", "pip", "freeze"], stdout=open(req_path, "w"))
            except Exception as e:
                logging.warning(f"Failed to snapshot pip freeze: {e}")
                with open(req_path, "w") as f:
                    f.write(f"Error capturing constraints: {e}")

            # 5. Ledger Copy
            if ledger_path and os.path.exists(ledger_path):
                shutil.copy2(ledger_path, os.path.join(export_dir, "ledger_snapshot.csv"))
                
                # Also copy related JSON rows if possible? 
                # For simplicity, we just copy the summary CSV.
                
            # 6. Latex Snippet
            self.generate_latex_snippet(metadata, export_dir)

            # 7. Save Figures
            if figures:
                figs_dir = os.path.join(export_dir, "figures")
                os.makedirs(figs_dir, exist_ok=True)
                for i, fig in enumerate(figures):
                    fig.savefig(os.path.join(figs_dir, f"figure_{i}.svg"))
                    fig.savefig(os.path.join(figs_dir, f"figure_{i}.png"))
                    
            logging.info(f"Export successful: {export_dir}")
            return export_dir
            
        except Exception as e:
            logging.error(f"Export failed: {e}")
            raise

    def generate_latex_snippet(self, metadata, export_dir):
        """
        Generates a LaTeX snippet with the key results.
        Equation: \epsilon\Phi = (slope \pm error) \times 10^X \quad (p < pval)
        """
        try:
            reg = metadata.get('regression', {})
            if not reg or 'slope' not in reg:
                return
                
            slope = reg['slope']
            error = reg['stderr']
            pval = reg['pval']
            
            # Formatting to scientific notation
            # We want (A +/- B) * 10^K
            import math
            if slope == 0: 
                exponent = 0
            else:
                exponent = int(math.floor(math.log10(abs(slope))))
            
            mantissa_s = slope / (10**exponent)
            mantissa_e = error / (10**exponent)
            
            # Format p-value
            if pval < 0.001:
                p_str = "p < 10^{-3}"
            else:
                p_str = f"p = {pval:.3f}"
            
            latex_content = (
                r"% Auto-generated result by CHRONON" + "\n"
                r"\begin{equation}" + "\n"
                rf"  \epsilon\Phi = ({mantissa_s:.2f} \pm {mantissa_e:.2f}) \times 10^{{{exponent}}} \quad ({p_str})" + "\n"
                r"\end{equation}" + "\n"
            )
            
            with open(os.path.join(export_dir, "result_snippet.tex"), "w") as f:
                f.write(latex_content)
                
        except Exception as e:
            logging.warning(f"Could not generate LaTeX: {e}")

