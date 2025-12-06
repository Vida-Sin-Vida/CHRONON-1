# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import os
import json
import datetime
import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

from app.gui.translations import TRANSLATIONS
from .base_frame import BaseFrame
from chronon_core.stats import calculate_slope_epsilon_phi
from chronon_core.qc import QualityControl
from chronon_core.blinding import BlindingManager
from chronon_core.ledger import Ledger
from chronon_core.diagnostics import ResidualDiagnostics
from chronon_core.qubits import QubitAnalysis
from chronon_core.simulator import PowerSimulator
from app.backend.exporter import ReproducibleExporter
from chronon_core.interpretation import ScientificInterpreter
from chronon_core.cci import ConsistencyIndex
from chronon_core.sensitivity import SensitivityAnalyzer
from app.gui.widgets.custom_notification import ChrononAlert, ChrononSplash

class AnalysisFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.qc = QualityControl()
        self.blinder = BlindingManager(key_salt="chronon_lab_salt")
        self.ledger = Ledger(os.path.join(os.path.expanduser("~"), ".chronon_ledger.csv"))
        self.exporter = ReproducibleExporter(output_base_dir=os.path.join(os.path.expanduser("~"), "Desktop", "CHRONON_Exports"))
        self.diagnostics = ResidualDiagnostics()
        self.qubit_analyzer = QubitAnalysis()
        self.simulator = PowerSimulator()
        self.interpreter = ScientificInterpreter()
        self.cci_calc = ConsistencyIndex()
        self.sensitivity = SensitivityAnalyzer()

        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # Metrics
        self.metrics_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.lbl_epsilon = ctk.CTkLabel(self.metrics_frame, text="εΦ (pente): -- ± --", font=("Roboto", 16))
        self.lbl_epsilon.pack(side="left", padx=40, pady=20)

        self.lbl_beta = ctk.CTkLabel(self.metrics_frame, text="β (T2): --", font=("Roboto", 16))
        self.lbl_beta.pack(side="left", padx=40, pady=20)

        self.lbl_qc_status = ctk.CTkLabel(self.metrics_frame, text="Status: PENDING", font=("Roboto", 16, "bold"), text_color="gray")
        self.lbl_qc_status.pack(side="right", padx=10, pady=20)

        self.lbl_interp_badge = ctk.CTkLabel(self.metrics_frame, text="--", font=("Roboto", 14, "bold"), fg_color="gray", text_color="white", corner_radius=6)
        self.lbl_interp_badge.pack(side="right", padx=10, pady=20)

        # Actions
        self.actions_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.actions_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        btns = [
            ("Diagnostics / Drift", self.show_diagnostics),
            ("Analyse Qubits (T2)", self.show_qubit_analysis),
            ("Simulateur Power", self.show_simulation),
            ("Corrélation Matrix", self.show_correlations),
            ("Interprétation / CCI", self.show_interpretation),
            ("Limite Détection", self.show_detection_limit),
            ("Simulateur What-If", self.show_what_if)
        ]

        for i, (text, cmd) in enumerate(btns):
            r, c = divmod(i, 4)
            ctk.CTkButton(self.actions_frame, text=text, command=cmd, height=40,
                          fg_color="#3B8ED0", hover_color="#1F6AA5").grid(row=r, column=c, padx=5, pady=5, sticky="ew")

        # Insight Area
        self.lbl_details = ctk.CTkLabel(self, text="Insight & Analyse Automatisée", font=("Segoe UI", 16, "bold"))
        self.lbl_details.grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")

        self.stats_area = ctk.CTkTextbox(self, width=600, height=150, font=("Consolas", 12))
        self.stats_area.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.stats_area.insert("0.0", ">>> En attente d'exécution QC...")

        # Options
        self.options_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.options_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=5, sticky="w")
        self.check_trace = ctk.CTkCheckBox(self.options_frame, text="Trace Temporel")
        self.check_trace.pack(side="left", padx=10)
        self.check_trace.select()
        self.check_hist = ctk.CTkCheckBox(self.options_frame, text="Histogramme")
        self.check_hist.pack(side="left", padx=10)
        self.check_corr = ctk.CTkCheckBox(self.options_frame, text="Corrélation")
        self.check_corr.pack(side="left", padx=10)

        # Report Button
        self.btn_report = ctk.CTkButton(self, text="Générer Rapport PDF (Rapide)", fg_color="green", hover_color="darkgreen", command=self.generate_report)
        self.btn_report.grid(row=5, column=1, padx=20, pady=20, sticky="e")

        self.is_blinded = False
        self.current_mapping = None

        if self.manager:
            self.manager.add_listener(self.on_experiment_update)
            
        self.update_language()

    def update_language(self):
        lang = getattr(self.master, "language", "fr")
        t = TRANSLATIONS[lang]["ANALYSIS"]
        
        # Metrics
        curr_eps = self.lbl_epsilon._text.split(":")[1] if ":" in self.lbl_epsilon._text else "--"
        self.lbl_epsilon.configure(text=f"{t['METRICS_EPSILON']}:{curr_eps}")
        
        curr_beta = self.lbl_beta._text.split(":")[1] if ":" in self.lbl_beta._text else "--"
        self.lbl_beta.configure(text=f"{t['METRICS_BETA']}:{curr_beta}")
        
        # Update buttons
        btns_keys = [
            "BTN_DIAGNOSTICS", "BTN_QUBITS", "BTN_SIMULATION", "BTN_CORRELATION",
            "BTN_INTERPRETATION", "BTN_LIMIT", "BTN_WHATIF"
        ]
        children = self.actions_frame.winfo_children()
        for i, key in enumerate(btns_keys):
            if i < len(children):
                children[i].configure(text=t[key])

        self.lbl_details.configure(text=t["LBL_INSIGHT"])
        
        if "En attente" in self.stats_area.get("0.0", "end") or "Waiting" in self.stats_area.get("0.0", "end"):
             self.stats_area.delete("0.0", "end")
             self.stats_area.insert("0.0", t["TXT_WAITING"])
             
        self.check_trace.configure(text=t["CHK_TRACE"])
        self.check_hist.configure(text=t["CHK_HIST"])
        self.check_corr.configure(text=t["CHK_CORR"])
        self.btn_report.configure(text=t["BTN_REPORT"])
        
        if hasattr(self, 'btn_blind'):
             txt = t["LBL_BLIND_ON"] if self.is_blinded else t["LBL_BLIND_OFF"]
             self.btn_blind.configure(text=txt)

    def show(self):
        super().show()
        self.run_qc()

    def on_experiment_update(self, event_type, data):
        if event_type == "complete":
            self.run_qc()

    def run_qc(self):
        if not self.manager: return
        
        data = self.manager.get_results()
        if not data:
            self.lbl_qc_status.configure(text="Status: NO DATA", text_color="gray")
            return

        df = pd.DataFrame(data)
        qc_status, qc_flags = self.qc.assess_run(df)

        status_colors = {"PASS": "#10B981", "WARN": "#F59E0B", "FAIL": "#EF4444"}
        color = status_colors.get(qc_status, "gray")
        self.lbl_qc_status.configure(text=f"Status: {qc_status}", text_color=color)

        slope_val = 0.0
        beta_val = 0.0
        valid_reg = False
        pval = 1.0
        residuals = None
        x = None

        if 'Delta_h_m' in df.columns and len(df) > 2:
            try:
                x = pd.to_numeric(df['Delta_h_m'], errors='coerce')
                y = pd.to_numeric(df['phi'], errors='coerce')
                sy = pd.to_numeric(df.get('sigma_Y', [0.1]*len(df)), errors='coerce')

                reg = calculate_slope_epsilon_phi(x, y, sy)
                slope_val = reg['slope']
                valid_reg = True
                residuals = reg.get('residuals')
                pval = reg.get('pval', 1.0)
            except Exception as e:
                print(f"Regression Error: {e}")

        if 't2_time' in df.columns:
            beta_val = pd.to_numeric(df['t2_time'], errors='coerce').mean()

        stats = {
            'slope': slope_val,
            'pval': pval,
            'n': len(df)
        }
        
        if residuals is not None and valid_reg and x is not None:
             stats['diagnostics'] = self.diagnostics.run_diagnostics(residuals, x)
        else:
             stats['diagnostics'] = {}

        res_interp = self.interpreter.interpret(stats, qc_status)

        if self.is_blinded:
            self.lbl_epsilon.configure(text="εΦ (pente): *** BLINDED ***")
            self.lbl_beta.configure(text="β (T2): *** BLINDED ***")
            self.lbl_interp_badge.configure(text="BLIND", fg_color="gray")
            self.stats_area.delete("0.0", "end")
            self.stats_area.insert("0.0", ">>> ANALYSE MASQUÉE.\nProtocol de blinding actif.")
        else:
            self.lbl_epsilon.configure(text=f"εΦ (pente): {slope_val:.2e}")
            self.lbl_beta.configure(text=f"β (T2): {beta_val:.2f} ms")

            badge_txt = res_interp['conclusion_short']
            if badge_txt in ["SIGNAL DETECTED", "STRONG SIGNAL"]:
                 badge_col = "#10B981"
            elif badge_txt == "NO SIGNAL":
                 badge_col = "#EF4444"
            elif "POSSIBLE" in badge_txt:
                 badge_col = "#F59E0B"
            else:
                 badge_col = "gray"
            self.lbl_interp_badge.configure(text=badge_txt, fg_color=badge_col)

            full_text = f"--- RÉSULTATS AUTOMATIQUES ---\n{res_interp['summary_5_lines']}\n\n[QC: {qc_status}] [P-Val: {pval:.4f}]"
            self.stats_area.delete("0.0", "end")
            self.stats_area.insert("0.0", full_text)

    def toggle_blinding(self):
        if not self.is_blinded:
             self.is_blinded = True
             if hasattr(self, 'btn_blind'):
                 self.btn_blind.configure(text="Blinding (ON) 🔒", fg_color="black")
             
             current_text = self.lbl_epsilon._text
             if "εΦ" in current_text:
                 self.lbl_epsilon.configure(text="εΦ: *** BLINDED ***")
                 self.lbl_beta.configure(text="β: *** BLINDED ***")
                 
             ChrononAlert.show_info("Blinding 2.0", "Mode aveugle activé.")
        else:
            self.is_blinded = False
            if hasattr(self, 'btn_blind'):
                self.btn_blind.configure(text="Blinding (OFF)", fg_color="gray")
            ChrononAlert.show_info("Blinding", "Mode aveugle désactivé.")
            self.run_qc()

    def show_diagnostics(self):
        if not self.manager: return
        data = self.manager.get_results()
        if not data: return
        
        df = pd.DataFrame(data)
        if 'phi' not in df.columns: return
        
        if 'Delta_h_m' in df.columns and len(df)>2:
             x = pd.to_numeric(df['Delta_h_m'], errors='coerce')
             y = pd.to_numeric(df['phi'], errors='coerce')
             sy = pd.to_numeric(df.get('sigma_Y', [0.1]*len(df)), errors='coerce')
             
             try:
                 reg = calculate_slope_epsilon_phi(x, y, sy)
                 slope = reg['slope']
                 y_pred = y.mean() + slope * (x - x.mean()) 
                 residuals = y - y_pred
             except:
                 residuals = df['phi'] - df['phi'].mean()
                 x = None
        else:
             residuals = df['phi'] - df['phi'].mean()
             x = None
             
        results = self.diagnostics.run_diagnostics(residuals, x)
        plot_data = self.diagnostics.get_plots_data(residuals)
        
        top = ctk.CTkToplevel(self)
        top.title("Diagnostics Résiduels")
        top.geometry("900x700")
        
        txt_frame = ctk.CTkFrame(top)
        txt_frame.pack(side="top", fill="x", padx=10, pady=10)
        
        report_str = "--- DIAGNOSTICS STATISTIQUES ---\n"
        for k, v in results.items():
            pval = f"{v['pval']:.4f}" if v['pval'] is not None else "N/A"
            report_str += f"{k}: Stat={v['stat']:.3f}, p={pval} -> {v['verdict']}\n"
            
        lbl_rep = ctk.CTkLabel(txt_frame, text=report_str, justify="left", font=("Consolas", 14))
        lbl_rep.pack(padx=10, pady=10)
        
        btn_temp = ctk.CTkButton(txt_frame, text="Analyse Temporelle & Drift", fg_color="#F59E0B", hover_color="#D97706",
                                 command=lambda: self.show_temporal_analysis(residuals))
        btn_temp.pack(padx=10, pady=5)
        
        fig, axes = plt.subplots(2, 2, figsize=(8, 6))
        fig.patch.set_facecolor('#F0F0F0')
        fig.suptitle(f"Analyse des Résidus (N={len(residuals)})", fontsize=12)
        
        axes[0,0].hist(residuals, bins=15, color='#3B8ED0', alpha=0.7, edgecolor='black')
        axes[0,0].set_title("Histogramme Résidus")
        
        axes[0,1].scatter(plot_data['theoretical_quantiles'], plot_data['sorted_residuals'], color='#3B8ED0', alpha=0.7)
        model_line = plot_data['theoretical_quantiles'] * np.std(residuals) + np.mean(residuals)
        axes[0,1].plot(plot_data['theoretical_quantiles'], model_line, 'r--')
        axes[0,1].set_title("Q-Q Plot")
        axes[0,1].grid(True, linestyle=':', alpha=0.6)
        
        axes[1,0].plot(residuals, '-o', color='#3B8ED0', markersize=4, alpha=0.8)
        axes[1,0].axhline(0, color='r', linestyle='--')
        axes[1,0].set_title("Résidus vs Ordre")
        axes[1,0].grid(True, linestyle=':', alpha=0.6)
        
        axes[1,1].bar(plot_data['lags'], plot_data['acf'], color='#3B8ED0', edgecolor='black')
        axes[1,1].axhline(0, color='black', linewidth=0.5)
        conf_int = 1.96/np.sqrt(len(residuals))
        axes[1,1].axhline(conf_int, color='r', linestyle='--')
        axes[1,1].axhline(-conf_int, color='r', linestyle='--')
        axes[1,1].set_title("Autocorrélation (ACF)")
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def show_qubit_analysis(self):
        if not self.manager: return
        data = self.manager.get_results()
        if not data: return
        
        df = pd.DataFrame(data)
        
        if 'delta_ln_phi' in df.columns and 't2_time' in df.columns:
            x = df['delta_ln_phi']
            y = df['t2_time']
            y_err = df.get('t2_error', None)
        else:
            if len(data) > 0:
                tk.messagebox.showinfo("Demo Qubits", "Colonnes T2 manquantes. Utilisation données simulées.")
                x, y, y_err = self.qubit_analyzer.generate_mock_data(n=20)
            else:
                return

        top = ctk.CTkToplevel(self)
        top.title("Analyse Qubit T2 (Multi-Modèle)")
        top.geometry("900x700")
        
        ctrl = ctk.CTkFrame(top)
        ctrl.pack(side="top", fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ctrl, text="Modèle Décoherence:").pack(side="left", padx=10)
        combo_model = ctk.CTkComboBox(ctrl, values=["linear", "exponential"])
        combo_model.set("linear")
        combo_model.pack(side="left", padx=10)
        
        res_frame = ctk.CTkFrame(top)
        res_frame.pack(side="top", fill="x", padx=10)
        lbl_res = ctk.CTkLabel(res_frame, text="Résultats...", justify="left", font=("Consolas", 12))
        lbl_res.pack(padx=10, pady=10)
        
        fig = plt.figure(figsize=(7, 4))
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        def run_fit(model_name):
            res = self.qubit_analyzer.analyze_t2_vs_phi(x, y, y_err, model_type=model_name)
            
            if not res['valid']:
                 lbl_res.configure(text=f"Fit Failed: {res.get('msg')}")
                 return

            self.lbl_beta.configure(text=f"β (T2): {res['slope_beta']:.2f}")
            ci_low, ci_high = res['ci_beta_95']
            
            txt = (f"Modèle: {model_name.upper()}\n"
                   f"Equation: {res['equation']}\n"
                   f"Param Beta: {res['slope_beta']:.4f}  (StdErr: {res['std_error']:.4f})\n"
                   f"IC 95%: [{ci_low:.4f}, {ci_high:.4f}]\n"
                   f"Intercept T0: {res['intercept_t2_0']:.2f}")
            lbl_res.configure(text=txt)
            
            fig.clf()
            ax = fig.add_subplot(111)
            ax.errorbar(x, y, yerr=y_err, fmt='o', color='purple', alpha=0.5, label='Données Exp')
            
            x_fit = np.linspace(min(x), max(x), 100)
            if model_name == "exponential":
                y_fit = res['intercept_t2_0'] * np.exp(res['slope_beta'] * x_fit)
            else:
                y_fit = res['intercept_t2_0'] + res['slope_beta'] * x_fit
                
            ax.plot(x_fit, y_fit, 'k-', linewidth=2, label=f'Fit {model_name}')
            ax.set_title(f"Sensibilité Qubit ({model_name})")
            ax.set_xlabel("Delta ln(Phi)")
            ax.set_ylabel("T2 (ms)")
            ax.legend()
            ax.grid(True, alpha=0.3)
            canvas.draw()

        combo_model.configure(command=run_fit)
        run_fit("linear")

    def show_simulation(self):
        top = ctk.CTkToplevel(self)
        top.title("Simulateur Power / Injection")
        top.geometry("600x500")
        
        p_frame = ctk.CTkFrame(top)
        p_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(p_frame, text="True Slope (Injected):").grid(row=0, column=0, padx=5, pady=5)
        entry_slope = ctk.CTkEntry(p_frame)
        entry_slope.grid(row=0, column=1, padx=5, pady=5)
        entry_slope.insert(0, "0.0001")
        
        ctk.CTkLabel(p_frame, text="Sigma Noise (Y):").grid(row=1, column=0, padx=5, pady=5)
        entry_sigma = ctk.CTkEntry(p_frame)
        entry_sigma.grid(row=1, column=1, padx=5, pady=5)
        entry_sigma.insert(0, "0.1")
        
        ctk.CTkLabel(p_frame, text="N Simulations:").grid(row=2, column=0, padx=5, pady=5)
        entry_n = ctk.CTkEntry(p_frame)
        entry_n.grid(row=2, column=1, padx=5, pady=5)
        entry_n.insert(0, "200")
        
        res_label = ctk.CTkLabel(top, text="Résultats: ...", font=("Consolas", 14), justify="left")
        res_label.pack(padx=20, pady=20)
        
        def run_sim():
            try:
                s = float(entry_slope.get())
                sig = float(entry_sigma.get())
                n = int(entry_n.get())
                
                res = self.simulator.run_simulation(n_sims=n, true_slope=s, sigma_y=sig)
                
                txt = (f"--- RÉSULTATS (N={n}) ---\n"
                       f"Power (Detection Rate): {res['power']:.2%}\n"
                       f"Mean Slope Est: {res['mean_slope']:.2e}\n"
                       f"Bias: {res['bias']:.2e}\n")
                res_label.configure(text=txt)
                
            except Exception as e:
                res_label.configure(text=f"Erreur: {e}")
        
        btn_run = ctk.CTkButton(p_frame, text="Lancer Simulation", command=run_sim, fg_color="#DB2777")
        btn_run.grid(row=3, column=0, columnspan=2, pady=15)
        
        def run_scan():
             report = self.simulator.scan_scenarios()
             txt = "--- SCAN SCENARIOS ---\n"
             for name, r in report.items():
                 txt += f"{name}: Power={r['power']:.1%} Bias={r['bias']:.1e}\n"
             res_label.configure(text=txt)
             
        btn_scan = ctk.CTkButton(top, text="Scan Scenarios S1-S3", command=run_scan, fg_color="#4B5563")
        btn_scan.pack(pady=5)

    def show_correlations(self):
        if not self.manager: return
        data = self.manager.get_results()
        if not data: return
        
        df = pd.DataFrame(data)
        df_num = df.select_dtypes(include=[np.number])
        df_num = df_num.loc[:, (df_num != df_num.iloc[0]).any()]
        
        if df_num.empty or df_num.shape[1] < 2:
            tk.messagebox.showinfo("Info", "Pas assez de colonnes numériques pour corrélation.")
            return
            
        corr_matrix = df_num.corr()
        
        top = ctk.CTkToplevel(self)
        top.title("Matrice de Corrélation")
        top.geometry("800x700")
        
        fig = plt.figure(figsize=(8, 7))
        ax = fig.add_subplot(111)
        
        cax = ax.matshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)
        fig.colorbar(cax)
        
        ticks = np.arange(len(corr_matrix.columns))
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        ax.set_xticklabels(corr_matrix.columns, rotation=45, ha="left")
        ax.set_yticklabels(corr_matrix.columns)
        
        for i in range(len(corr_matrix.columns)):
            for j in range(len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", color="black" if abs(val)<0.7 else "white", fontsize=8)
                
        ax.set_title("Pearson Correlation Heatmap")
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def export_reproducible(self):
        if not self.manager: return
        data = self.manager.get_results()
        if not data: return
        df = pd.DataFrame(data)
        
        meta = {
            'run_id': "interactive_export",
            'timestamp': datetime.datetime.now().isoformat(),
            'notes': 'Export manual from GUI'
        }
        
        try:
            path = self.exporter.export_run(df, meta, self.ledger.path)
            ChrononSplash.show("Export Réussi", f"Dossier créé:\n{path}")
        except Exception as e:
            ChrononAlert.show_error("Erreur", f"Echec export: {e}")

    def generate_report(self):
        if not self.manager: return
        data = self.manager.get_results()
        if not data:
            tk.messagebox.showwarning("Rapport", "Aucune donnée disponible.")
            return

        export_dir = os.path.join(os.path.expanduser("~"), "Desktop", "CHRONON_Exports")
        os.makedirs(export_dir, exist_ok=True)
        
        timestamp_str = datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')
        filename = f"Chronon_Data-{timestamp_str}.pdf"
        file_path = os.path.join(export_dir, filename)

        try:
            df = pd.DataFrame(data)
            qc_status, qc_flags = self.qc.assess_run(df)
            
            stats_results = {
                'qc_status': qc_status,
                'qc_flags': qc_flags,
                'run_id': f"Run-{timestamp_str}"
            }
            
            residuals = None
            if 'Delta_h_m' in df.columns and len(df) > 2:
                x = pd.to_numeric(df['Delta_h_m'], errors='coerce')
                y = pd.to_numeric(df['phi'], errors='coerce')
                sy = pd.to_numeric(df.get('sigma_Y', [0.1]*len(df)), errors='coerce')
                sx = pd.to_numeric(df.get('sigma_dh_m', [0.0]*len(df)), errors='coerce')
                
                reg = calculate_slope_epsilon_phi(x, y, sy, sx)
                stats_results.update(reg)
                
                residuals = reg.get('residuals')
                if residuals is not None:
                    diag_res = self.diagnostics.run_diagnostics(residuals, x)
                    stats_results['diagnostics'] = diag_res
            else:
                stats_results.update({
                    'slope': 0.0, 'stderr': 0.0, 'pval': 1.0, 
                    'model_summary': "Data Insufficient",
                    'diagnostics': {}
                })
            
            if residuals is None:
                 tk.messagebox.showerror("Erreur", "Pas de résidus (Régression impossible)")
                 return

            fig_report = plt.figure(figsize=(10, 6))
            gs = fig_report.add_gridspec(2, 1)
            
            ax1 = fig_report.add_subplot(gs[0])
            if 'phi' in df.columns:
                ax1.plot(df['phi'], color='#1F6AA5', label='Phi Signal')
                ax1.set_title("Série Temporelle (Phi)")
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                
            ax2 = fig_report.add_subplot(gs[1])
            if 'Delta_h_m' in df.columns and len(df) > 2:
                x = pd.to_numeric(df['Delta_h_m'], errors='coerce')
                y = pd.to_numeric(df['phi'], errors='coerce')
                sy = pd.to_numeric(df.get('sigma_Y', [0.1]*len(df)), errors='coerce')
                
                ax2.errorbar(x, y, yerr=sy, fmt='o', color='black', alpha=0.5, label='Mesures')
                
                slope = stats_results.get('slope', 0)
                line_x = np.linspace(min(x), max(x), 100)
                line_y = y.mean() + slope * (line_x - x.mean())
                ax2.plot(line_x, line_y, 'r-', linewidth=2, label=f'Fit (εΦ={slope:.2e})')
                
                ax2.set_xlabel("Delta h (m)")
                ax2.set_ylabel("Phi")
                ax2.set_title("Régression Gravitationnelle")
                ax2.legend()
                ax2.grid(True, alpha=0.3)

            fig_report.tight_layout()

            from chronon_core.reporting import ReportGenerator
            
            meta = {
                'Operator': 'LabUser',
                'Software': 'CHRONON V1.0',
                'Export Path': export_dir
            }
            
            # Automated Description
            cci_score = 0.0
            if 'pval' in stats_results:
                 boot_ci = (stats_results.get('ci_low',0), stats_results.get('ci_high',0))
                 cci_score, _ = self.cci_calc.calculate_cci(residuals, stats_results['pval'], boot_ci, len(df))
            
            lang = getattr(self.master, "language", "fr")
            res_interp = self.interpreter.interpret(stats_results, qc_status, lang=lang)
            
            t_interp = TRANSLATIONS[lang]["INTERPRETATION"]
            desc_text = (f"{t_interp['CONCLUSION_LABEL']}: {res_interp['conclusion_short']}\n"
                         f"CCI Score: {cci_score:.2f}/1.0\n\n"
                         f"{t_interp['EVALUATION_LABEL']}:\n{res_interp['evaluation']}\n\n"
                         f"{t_interp['PUBLICATION_LABEL']}:\n{res_interp['publication_text']}")

            ReportGenerator.generate_pdf_report(file_path, fig_report, stats_results, metadata=meta, description_text=desc_text, lang=lang)
            plt.close(fig_report)
            
            ChrononSplash.show("Succès", f"Rapport PDF généré!")
            
        except Exception as e:
            ChrononAlert.show_error("Erreur", f"Echec génération rapport: {e}")

    def show_interpretation(self):
        if not self.manager: return
        data = self.manager.get_results()
        if not data: return
        df = pd.DataFrame(data)
        
        qc_status, qc_flags = self.qc.assess_run(df)
        
        stats = {'slope': 0.0, 'pval': 1.0, 'n': len(df)}
        cci_score = 0.0
        cci_details = {}
        
        if 'Delta_h_m' in df.columns and len(df)>2:
             x = pd.to_numeric(df['Delta_h_m'], errors='coerce')
             y = pd.to_numeric(df['phi'], errors='coerce')
             sy = pd.to_numeric(df.get('sigma_Y', [0.1]*len(df)), errors='coerce')
             reg = calculate_slope_epsilon_phi(x, y, sy)
             stats.update(reg)
             
             residuals = reg.get('residuals')
             if residuals is not None:
                 stats['diagnostics'] = self.diagnostics.run_diagnostics(residuals, x)
                 boot_ci = (reg.get('ci_low',0), reg.get('ci_high',0))
                 cci_score, cci_details = self.cci_calc.calculate_cci(
                     residuals, reg['pval'], boot_ci, len(df)
                 )

        lang = getattr(self.master, "language", "fr")
        res_interp = self.interpreter.interpret(stats, qc_status, lang=lang)
        t = TRANSLATIONS[lang]["INTERPRETATION"]
        
        top = ctk.CTkToplevel(self)
        top.title("Interpretation / CCI")
        top.geometry("800x700")
        
        sf = ctk.CTkScrollableFrame(top, width=780, height=680)
        sf.pack(padx=10, pady=10, fill="both", expand=True)
        
        color_sig = "#10B981" if res_interp['signal_strength'] in ["STRONG", "WEAK"] else "#EF4444"
        ctk.CTkLabel(sf, text=f"{t['CONCLUSION_LABEL']}: {res_interp['conclusion_short']}", font=("Roboto", 24, "bold"), text_color=color_sig).pack(pady=20)
        
        f_cci = ctk.CTkFrame(sf, fg_color="white", corner_radius=10)
        f_cci.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_cci, text="Chronon Consistency Index (CCI)", text_color="black", font=("Arial", 16, "bold")).pack(pady=10)
        
        canvas = tk.Canvas(f_cci, width=600, height=50, bg="white", highlightthickness=0)
        canvas.pack(pady=10)
        
        w_bar = 600 * cci_score
        color_cci = "#EF4444" 
        if cci_score > 0.5: color_cci = "#F59E0B"
        if cci_score > 0.8: color_cci = "#10B981"
        
        canvas.create_rectangle(0, 10, 600, 40, fill="#E5E7EB", outline="")
        canvas.create_rectangle(0, 10, w_bar, 40, fill=color_cci, outline="")
        canvas.create_text(300, 25, text=f"{cci_score}/1.0", font=("Arial", 12, "bold"), fill="black")
        
        det_txt = " | ".join([f"{k}: {v:.2f}" for k, v in cci_details.items()])
        ctk.CTkLabel(f_cci, text=det_txt, text_color="gray").pack(pady=5)
        
        f_eval = ctk.CTkFrame(sf)
        f_eval.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_eval, text=t["EVALUATION_LABEL"], font=("Roboto", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(f_eval, text=res_interp['evaluation'], font=("Roboto", 14), text_color="#1F6AA5").pack(anchor="w", padx=10)
        
        f_pub = ctk.CTkFrame(sf)
        f_pub.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(f_pub, text=t["PUBLICATION_LABEL"], font=("Roboto", 16, "bold")).pack(anchor="w", padx=10, pady=5)
        tb_pub = ctk.CTkTextbox(f_pub, width=700, height=100)
        tb_pub.pack(padx=10, pady=10)
        tb_pub.insert("0.0", res_interp['publication_text'])

    def show_detection_limit(self):
        if not self.manager: return
        data = self.manager.get_results()
        if not data: return
        df = pd.DataFrame(data)
        
        n = len(df)
        if 'Delta_h_m' in df.columns:
            x = pd.to_numeric(df['Delta_h_m'], errors='coerce')
            x_std = x.std()
        else:
            x_std = 100
            
        sigma_y = df['sigma_Y'].mean() if 'sigma_Y' in df.columns else 0.1
        mdp = self.sensitivity.calculate_mdp(sigma_y, n, x_std)
        
        msg = (f"=== LIMITE DE DÉTECTION ===\n\n"
               f"Paramètres Actuels: N = {n}, Sigma Y = {sigma_y:.4f}\n"
               f"Pente Minimale Détectable (MDP): εΦ > {mdp:.2e}\n"
               f"(Power=80%, Alpha=5%)")
               
        ChrononAlert.show_info("Sensibilité Setup", msg)

    def show_what_if(self):
        top = ctk.CTkToplevel(self)
        top.title("Simulateur What-If Interactif")
        top.geometry("900x700")
        
        ctrl_frame = ctk.CTkFrame(top)
        ctrl_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(ctrl_frame, text="Nombre d'échantillons (N)").grid(row=0, column=0, padx=10)
        slider_n = ctk.CTkSlider(ctrl_frame, from_=10, to=1000, number_of_steps=99)
        slider_n.set(100)
        slider_n.grid(row=0, column=1, padx=10, sticky="ew")
        lbl_n = ctk.CTkLabel(ctrl_frame, text="100")
        lbl_n.grid(row=0, column=2, padx=10)
        
        ctk.CTkLabel(ctrl_frame, text="Bruit (Sigma Y)").grid(row=1, column=0, padx=10)
        slider_sig = ctk.CTkSlider(ctrl_frame, from_=0.01, to=2.0, number_of_steps=199)
        slider_sig.set(0.1)
        slider_sig.grid(row=1, column=1, padx=10, sticky="ew")
        lbl_sig = ctk.CTkLabel(ctrl_frame, text="0.10")
        lbl_sig.grid(row=1, column=2, padx=10)
        
        ctk.CTkLabel(ctrl_frame, text="Pente Réelle (Simulée)").grid(row=2, column=0, padx=10)
        slider_slope = ctk.CTkSlider(ctrl_frame, from_=0, to=5e-4, number_of_steps=100)
        slider_slope.set(1e-4)
        slider_slope.grid(row=2, column=1, padx=10, sticky="ew")
        lbl_slope = ctk.CTkLabel(ctrl_frame, text="1.0e-4")
        lbl_slope.grid(row=2, column=2, padx=10)
        
        chart_frame = ctk.CTkFrame(top)
        chart_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        fig, ax = plt.subplots(figsize=(5, 4))
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def update_plot(val=None):
            n = int(slider_n.get())
            sig = float(slider_sig.get())
            slope_true = float(slider_slope.get())
            
            lbl_n.configure(text=str(n))
            lbl_sig.configure(text=f"{sig:.2f}")
            lbl_slope.configure(text=f"{slope_true:.2e}")
            
            x_std = 100.0
            ns = np.linspace(10, 1000, 50)
            powers = [self.sensitivity.get_power_for_slope(slope_true, sig, ni, x_std) for ni in ns]
            
            ax.clear()
            ax.plot(ns, powers, 'b-', linewidth=2, label='Power Curve')
            ax.axvline(n, color='r', linestyle='--', label=f'Current N={n}')
            
            curr_poul = self.sensitivity.get_power_for_slope(slope_true, sig, n, x_std)
            ax.plot(n, curr_poul, 'fo', markersize=8)
            
            ax.set_ylim(-0.05, 1.05)
            ax.set_xlabel("Nombre d'échantillons (N)")
            ax.set_ylabel("Puissance Statistique (1-β)")
            ax.set_title(f"Simulation: Power = {curr_poul:.1%}")
            ax.grid(True, alpha=0.3)
            ax.legend()
            canvas.draw()
            
        slider_n.configure(command=update_plot)
        slider_sig.configure(command=update_plot)
        slider_slope.configure(command=update_plot)
        
        update_plot()

    def show_temporal_analysis(self, residuals):
        if len(residuals) < 10:
             ChrononAlert.show_info("Info", "Pas assez de points pour analyse temporelle (>10 requis).")
             return
             
        top = ctk.CTkToplevel(self)
        top.title("Analyse Dynamique des Résidus")
        top.geometry("800x600")
        
        window = max(5, int(len(residuals)/10))
        roll_mean = pd.Series(residuals).rolling(window=window).mean()
        roll_std = pd.Series(residuals).rolling(window=window).std()
        
        fig = plt.figure(figsize=(8, 6))
        gs = fig.add_gridspec(2, 2)
        
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(residuals, 'o', color='gray', alpha=0.3, label='Résidus bruts')
        ax1.plot(roll_mean, 'r-', linewidth=2, label=f'Moyenne Mobile (w={window})')
        ax1.fill_between(range(len(residuals)), roll_mean - 2*roll_std, roll_mean + 2*roll_std, color='orange', alpha=0.2, label='±2σ')
        ax1.axhline(0, color='black', linestyle='--')
        ax1.set_title("Stabilité Temporelle (Drift)")
        ax1.legend()
        
        ax2 = fig.add_subplot(gs[1, 0])
        x_indices = np.arange(len(residuals))
        h, xedges, yedges = np.histogram2d(x_indices, residuals, bins=[min(20, len(residuals)//2), 20])
        ax2.imshow(h.T, origin='lower', aspect='auto', cmap='inferno', interpolation='nearest',
                   extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
        ax2.set_title("Densité Spectrale (Heatmap)")
        
        ax3 = fig.add_subplot(gs[1, 1])
        abs_res = np.abs(residuals)
        fit_coef = np.polyfit(np.arange(len(residuals)), abs_res, 1)
        fit_line = np.polyval(fit_coef, np.arange(len(residuals)))
        
        ax3.scatter(np.arange(len(residuals)), abs_res, alpha=0.5, s=10)
        ax3.plot(fit_line, 'g-', linewidth=2)
        drift_slope = fit_coef[0]
        status = "STABLE" if abs(drift_slope) < 1e-5 else "DRIFTING"
        
        ax3.set_title(f"Homoscédasticité: {status}")
        ax3.set_ylabel("|Residus|")
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
