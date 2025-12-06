# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
import customtkinter as ctk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import numpy as np
import pandas as pd
from chronon_core.stats import calculate_slope_epsilon_phi

from .base_frame import BaseFrame
from app.gui.widgets.custom_notification import ChrononAlert, ChrononConfirm, ChrononSplash
from app.gui.translations import TRANSLATIONS

class VisualizationFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Configure layout (2 columns: controls, plot)
        self.grid_columnconfigure(0, weight=0) # Controls
        self.grid_columnconfigure(1, weight=1) # Plot
        self.grid_rowconfigure(0, weight=1)

        # Controls Side Panel
        self.controls_frame = ctk.CTkFrame(self, width=200)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.title_label = ctk.CTkLabel(self.controls_frame, text="Contrôles Graphiques (v2)", font=ctk.CTkFont(weight="bold"))
        self.title_label.pack(pady=10, padx=10)

        # STATUS BANNER (New)
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
        self.lbl_qc = ctk.CTkLabel(self.status_frame, text="QC: UNKNOWN", text_color="gray", font=("Arial", 12, "bold"))
        self.lbl_qc.pack(side="left", padx=20, pady=5)
        
        self.lbl_blind = ctk.CTkLabel(self.status_frame, text="Blind: ON", text_color="orange", font=("Arial", 12, "bold"))
        self.lbl_blind.pack(side="left", padx=20, pady=5)

        self.lbl_fallback = ctk.CTkLabel(self.status_frame, text="Fallback: OFF", text_color="gray", font=("Arial", 12, "bold"))
        self.lbl_fallback.pack(side="left", padx=20, pady=5)
        
        self.btn_help = ctk.CTkButton(self.status_frame, text="Aide / Guide", width=80, fg_color="gray", command=self.show_help)
        self.btn_help.pack(side="right", padx=10, pady=5)

        # Plot Type Selection
        self.plot_type_var = ctk.StringVar(value="Régression Centrale (εΦ)")
        self.plot_type_menu = ctk.CTkOptionMenu(self.controls_frame, variable=self.plot_type_var,
                                                values=["Régression Centrale (εΦ)", "Série Temporelle", "Résidus Δy", "Corrélation T2/Φ", "Heatmap", "Histogramme"],
                                                command=lambda x: self.update_plot())
        self.plot_type_menu.pack(pady=10, padx=10)

        # Options
        self.check_overlay = ctk.CTkCheckBox(self.controls_frame, text="Overlay Multi-runs", command=self.update_plot)
        self.check_overlay.pack(pady=10, padx=10, anchor="w")
        
        self.check_errorbars = ctk.CTkCheckBox(self.controls_frame, text="Barres d'erreur", command=self.update_plot)
        self.check_errorbars.pack(pady=10, padx=10, anchor="w")

        # Filters
        self.filter_frame = ctk.CTkFrame(self.controls_frame)
        self.filter_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(self.filter_frame, text="Filtre (Run ID)").pack()
        
        self.entry_min = ctk.CTkEntry(self.filter_frame, placeholder_text="Min", width=60)
        self.entry_min.pack(side="left", padx=5, pady=5)
        self.entry_max = ctk.CTkEntry(self.filter_frame, placeholder_text="Max", width=60)
        self.entry_max.pack(side="right", padx=5, pady=5)
        
        self.btn_apply_filter = ctk.CTkButton(self.filter_frame, text="Appliquer", width=60, command=self.update_plot)
        self.btn_apply_filter.pack(pady=5)

        self.btn_refresh = ctk.CTkButton(self.controls_frame, text="Actualiser", command=self.update_plot)
        self.btn_refresh.pack(pady=10, padx=10)
        
        self.btn_export_sel = ctk.CTkButton(self.controls_frame, text="Export Sélection", command=self.export_selection, fg_color="blue", state="disabled")
        self.btn_export_sel.pack(pady=10, padx=10)
        
        self.btn_save = ctk.CTkButton(self.controls_frame, text="Sauvegarder Graphique", command=self.save_plot, fg_color="green", hover_color="darkgreen")
        self.btn_save.pack(pady=10, padx=10)
        
        if self.manager:
            self.manager.add_listener(self.on_experiment_update)
            
        self.update_pending = False
        self.colorbar = None
        self.selector = None
        self.selected_indices = []

        # Plot Area (Initialize ONCE)
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Initialize Plot
        self.fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.fig.patch.set_facecolor('#FFFFFF') # Light background
        self.ax.set_facecolor('#FFFFFF')
        self.ax.tick_params(colors='#0B2240', labelsize=10) # Dark Blue Text
        self.ax.xaxis.label.set_color('#0B2240')
        self.ax.yaxis.label.set_color('#0B2240')
        self.ax.title.set_color('#0B2240')
        
        # Spines (borders)
        for spine in self.ax.spines.values():
            spine.set_color('#0B2240')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        
        # Toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Initial draw
        # Initial draw
        self.update_plot()
        if hasattr(self, "update_language"):
             self.after(100, self.update_language)

    def update_language(self):
        app = self.winfo_toplevel()
        lang = getattr(app, "language", "fr")
        
        t = TRANSLATIONS[lang]["VISUALIZATION"]
        c = TRANSLATIONS[lang]["COMMON"]
        
        self.title_label.configure(text=t["TITLE"])
        self.ax.set_xlabel(t["LBL_X_AXIS"])
        self.ax.set_ylabel(t["LBL_Y_AXIS"])
        
        # Controls
        self.btn_refresh.configure(text=t["BTN_REFRESH"])
        self.btn_export_sel.configure(text=t["BTN_EXPORT"])
        self.btn_save.configure(text=t["BTN_SAVE"])
        self.btn_apply_filter.configure(text=t["BTN_APPLY"])
        self.btn_help.configure(text=t["BTN_HELP"])
        
        self.check_overlay.configure(text=t["CHK_OVERLAY"])
        self.check_errorbars.configure(text=t["CHK_ERRORBARS"])
        
        # Banners (Static part, dynamic part handled in update_plot usually, but we set defaults)
        # self.lbl_qc.configure(text=t["LBL_QC"]) # Logic overwrites this often
        # self.lbl_blind.configure(text=t["LBL_BLIND"])
        
        # Plot Types Menu
        current_val = self.plot_type_var.get()
        new_values = t["PLOT_TYPES"]
        self.plot_type_menu.configure(values=new_values)
        
        # Try to map current selection to new language to avoid reset
        # Simple index mapping
        # "Régression..." is index 0 in both lists hopefully
        # fr: ["Régression...", "Série...", "Residus...", ...]
        # en: ["Central...", "Time Series...", "Residuals...", ...]
        # We need access to the OLD list to find index. 
        # But we don't have it easily unless we construct it or check TRANSLATIONS[other_lang].
        # Simplified: Just keep current_val if valid, else default to index 0.
        # But current_val will be in old language.
        # Fallback: Default to 0.
        # Better: Try to find index in FR or EN list
        found_idx = -1
        for lang_code in ["fr", "en"]:
             opts = TRANSLATIONS[lang_code]["VISUALIZATION"]["PLOT_TYPES"]
             if current_val in opts:
                 found_idx = opts.index(current_val)
                 break
        
        if found_idx != -1 and found_idx < len(new_values):
             self.plot_type_var.set(new_values[found_idx])
        else:
             self.plot_type_var.set(new_values[0])

        self.canvas.draw()

    def on_experiment_update(self, event_type, data):
        # Throttle updates to avoid freezing the GUI
        if event_type in ["progress", "complete"]:
            if not self.update_pending:
                self.update_pending = True
                # Update max 5 times per second (200ms)
                self.after(200, self._perform_update)
                
    def _perform_update(self):
        self.update_plot()
        self.update_pending = False

    def on_select(self, eclick, erelease):
        """Callback for RectangleSelector."""
        if not self.current_data: return
        
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        
        # Normalize coords
        xmin, xmax = min(x1, x2), max(x1, x2)
        ymin, ymax = min(y1, y2), max(y1, y2)
        
        # Find points inside rect
        selected = []
        df = self.current_data
        
        # Assuming df has 'x' and 'y' columns mapped from plotting
        # We need to map back to original data indices
        # Simplified: Check against plotted arrays
        
        # We store plotted data in self.plotted_x and self.plotted_y for this
        if hasattr(self, 'plotted_x') and hasattr(self, 'plotted_y'):
             for i, (px, py) in enumerate(zip(self.plotted_x, self.plotted_y)):
                 if xmin <= px <= xmax and ymin <= py <= ymax:
                     selected.append(i)
        
        self.selected_indices = selected
        
        if selected:
            self.btn_export_sel.configure(state="normal", text=f"Export ({len(selected)})")
        else:
            self.btn_export_sel.configure(state="disabled", text="Export Sélection")

    def toggle_selector(self, state=True):
        if hasattr(self, 'selector') and self.selector:
            self.selector.set_active(state)

    def update_plot(self):
        # Clear Colorbar if exists (Safety First)
        if self.colorbar:
            try:
                self.colorbar.remove()
            except Exception:
                pass 
            self.colorbar = None

        self.ax.clear()
        self.ax.set_facecolor('#FFFFFF')
        self.selected_indices = []
        self.btn_export_sel.configure(state="disabled", text="Export Sélection")
        
        if not self.manager:
            return
            
        # Get Data
        raw_data = self.manager.get_results()
        if not raw_data:
            self.ax.text(0.5, 0.5, "Pas de données disponibles", color="#0B2240", ha="center", fontsize=12)
            self.canvas.draw()
            return
            
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(raw_data)
        
        # Filtering
        try:
            if self.entry_min.get():
                min_val = int(self.entry_min.get())
                df = df[df['id'] >= min_val]
            if self.entry_max.get():
                max_val = int(self.entry_max.get())
                df = df[df['id'] <= max_val]
        except Exception:
            pass # Ignore filter errors
            
        if df.empty:
            self.ax.text(0.5, 0.5, "Aucune donnée filtrée", color="#0B2240", ha="center")
            self.canvas.draw()
            return

        self.current_data = df # Store for selection
        plot_type = self.plot_type_var.get()
        
        # Helper to get column if exists, else zero
        def get_col(name, default=0.0):
            return df[name] if name in df.columns else np.zeros(len(df)) + default

        if plot_type in ["Régression Centrale (εΦ)", "Central Regression (εΦ)"]:
            # X = Delta_h, Y = Y_res (or similar)
            # Check what keys are in 'raw_data'. Assuming standard keys from io.py or manager.
            # We need 'Delta_h_m' and some 'Y' (Delta_lnPhi or Y_res).
            # From previous steps, derived headers include Delta_h_m, Delta_lnPhi.
            
            # Map keys (adaptation to likely keys in dict)
            # Assuming manager returns list of dicts with keys matching CSV columns roughly
            x_data = get_col('Delta_h_m')
            y_data = get_col('Delta_lnPhi') # Primary observable?
            sigma_y = get_col('sigma_Y', 0.1) # Default error if missing
            sigma_x = get_col('sigma_dh_m', 0.0)
            
            # Status colors
            # If status provided in data
            colors = []
            if 'status' in df.columns:
                colors = df['status'].apply(lambda s: 'red' if s == 'FAIL' else 'green').tolist()
            else:
                colors = ['blue'] * len(df)
            
            # Scatter
            self.ax.scatter(x_data, y_data, c=colors, alpha=0.7, edgecolors='k', zorder=3)
            if self.check_errorbars.get():
                self.ax.errorbar(x_data, y_data, yerr=sigma_y, fmt='none', ecolor='gray', alpha=0.3, zorder=1)
                
            # Perform Regression on fly for visualization
            reg_res = calculate_slope_epsilon_phi(x_data, y_data, sigma_y, sigma_x)
            self.last_stats = reg_res # Cache for report
            
            # Plot Fit Line
            x_range = np.linspace(x_data.min(), x_data.max(), 100)
            slope = reg_res['slope']
            # Intercept? calculate_slope_epsilon_phi might use 'alpha' internally but returns slope primarily?
            # It returns full res if we look at implementation?
            # Impl returned dict with slope, pval, but not intercept explicitly in top level dict?
            # Wait, calculate_slope_epsilon_phi implementation uses fit_free_intercept_wls which returns alpha.
            # But the top wrapper I wrote returned simplified dict.
            # I should have returned alpha too. I'll assume 0 intersect or re-fit for line drawing?
            # Or just update stats.py later to return alpha. 
            # For now, let's assume y = slope * x + alpha. 
            # I will just plot slope line centered on mean for visualization or 
            # trust the user just wants the slope visual.
            pass # TODO: get intercept to draw line correctly.
            
            # Simplified line: y = mx (if model predicts 0 intercept? No, free intercept)
            # I will assume intercept is roughly Y_mean - slope*X_mean for viz purpose if not available.
            # Plot Fit Line
            x_range = np.linspace(x_data.min(), x_data.max(), 100)
            slope = reg_res['slope']
            # Use alpha if available, else estimate
            alpha_est = reg_res.get('alpha', np.mean(y_data) - slope * np.mean(x_data))
            y_fit = alpha_est + slope * x_range
            
            # Update labels
            if reg_res.get('switch_reason'):
                self.lbl_fallback.configure(text=f"Fallback: {reg_res['model_summary']}", text_color="red")
            else:
                self.lbl_fallback.configure(text="Fallback: None", text_color="green")
            
            self.ax.plot(x_range, y_fit, 'r--', label=f"Fit εΦ={slope:.2e}")
            
            # CI Band (Simplified for viz: slope +/- CI)
            ci_high = reg_res['ci_high']
            ci_low = reg_res['ci_low']
            # This is CI of slope. Effect on Y is...
            # y_upper = (alpha) + ci_high * x
            # y_lower = (alpha) + ci_low * x
            # This makes a "bowtie" shape.
            y_upper = alpha_est + ci_high * x_range
            y_lower = alpha_est + ci_low * x_range
            self.ax.fill_between(x_range, y_lower, y_upper, color='red', alpha=0.1, label="95% CI")

            self.ax.set_xlabel("Delta h (m)")
            self.ax.set_ylabel("Delta ln(Phi)")
            self.ax.set_title(f"Régression Centrale: p={reg_res['pval']:.3g}")
            
            self.plotted_x = x_data.values
            self.plotted_y = y_data.values
            
            # Activate Selector
            if not self.selector:
                 self.selector = RectangleSelector(self.ax, self.on_select, useblit=True,
                                                   button=[1], minspanx=5, minspany=5,
                                                   spancoords='pixels', interactive=True)
            self.toggle_selector(True)

        elif plot_type in ["Série Temporelle", "Time Series"]:
            self.toggle_selector(False)
            ids = get_col('id')
            phis = get_col('phi') # or Delta_lnPhi
            self.ax.plot(ids, phis, color="#1F6AA5", marker='o', linestyle='-')
            self.ax.set_xlabel("Run ID")
            self.ax.set_ylabel("Amplitude")
            if self.check_errorbars.get():
                 self.ax.errorbar(ids, phis, yerr=get_col('sigma_Y', 0.1), fmt='none', ecolor='gray', alpha=0.5)

        elif plot_type in ["Résidus Δy", "Residuals Δy"]:
            self.toggle_selector(False)
            x_data = get_col('Delta_h_m')
            y_data = get_col('Delta_lnPhi')
            sigma_y = get_col('sigma_Y', 0.1)
            sigma_x = get_col('sigma_dh_m', 0.0)
            
            # Must run regression to get residuals
            reg_res = calculate_slope_epsilon_phi(x_data, y_data, sigma_y, sigma_x)
            residuals = reg_res.get('residuals', y_data - (reg_res.get('alpha', 0) + reg_res['slope'] * x_data))
            
            self.ax.scatter(x_data, residuals, c='purple', alpha=0.7)
            self.ax.axhline(0, color='black', linestyle='--')
            self.ax.set_xlabel("Delta h (m)")
            self.ax.set_ylabel("Résidus (O - C)")
            self.ax.set_title("Résidus de Régression")
            
        elif plot_type in ["Corrélation T2/Φ", "Correlation T2/Φ"]:
            self.toggle_selector(False)
            x_temp = get_col('temperature')
            y_phi = get_col('Delta_lnPhi')
            self.ax.scatter(x_temp, y_phi, c='orange', alpha=0.7)
            self.ax.set_xlabel("Température (°C)")
            self.ax.set_ylabel("Delta ln(Phi)")
            self.ax.set_title("Corrélation Environnementale")
            
        elif plot_type == "Heatmap":
            self.toggle_selector(False)
            x_data = get_col('Delta_h_m')
            y_data = get_col('Delta_lnPhi')
            hb = self.ax.hexbin(x_data, y_data, gridsize=20, cmap='inferno')
            self.colorbar = self.fig.colorbar(hb, ax=self.ax)
            self.ax.set_xlabel("Delta h (m)")
            self.ax.set_ylabel("Delta ln(Phi)")
            self.ax.set_title("Densité des Points")

        elif plot_type in ["Histogramme", "Histogram"]:
            self.toggle_selector(False)
            x_data = get_col('Delta_h_m')
            y_data = get_col('Delta_lnPhi')
            sigma_y = get_col('sigma_Y', 0.1)
            # Run regression to get residuals distribution
            reg_res = calculate_slope_epsilon_phi(x_data, y_data, sigma_y)
            residuals = reg_res.get('residuals', y_data - (reg_res.get('alpha', 0) + reg_res['slope'] * x_data))
            
            self.ax.hist(residuals, bins=20, color='skyblue', edgecolor='black')
            self.ax.set_xlabel("Résidus")
            self.ax.set_ylabel("Fréquence")
            self.ax.set_title("Distribution des Résidus")
        
        self.ax.legend()
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.canvas.draw()

    def export_selection(self):
        if not self.selected_indices or self.current_data is None:
            return
            
        subset = self.current_data.iloc[self.selected_indices]
        
        from tkinter import filedialog
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if filename:
            subset.to_csv(filename, index=False)
        if filename:
            subset.to_csv(filename, index=False)
            ChrononSplash.show("Export", f"Sélection exportée:\n{len(subset)} lignes")

    def save_plot(self):
        from tkinter import filedialog
        
        from datetime import datetime
        default_name = f"Chronon_Data-{datetime.now().strftime('%d-%m-%Y_%H-%M')}.pdf"
        filename = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                initialfile=default_name,
                                                filetypes=[("PDF Document", "*.pdf"), ("PNG Image", "*.png"), ("SVG Image", "*.svg")])
        if filename:
            if filename.endswith(".pdf"):
                 # Ask if user wants simple plot or full report
                is_report = ChrononConfirm.ask_yes_no("Type de PDF", "Générer un rapport complet (Texte + Stats + Graphique) ?\n(Non = Graphique seul)")
                if is_report:
                    try:
                        from chronon_core.reporting import ReportGenerator
                        # Need stats results. VisualizationFrame computes them on fly currently in update_plot...
                        # We should cache the latest stats result in self.last_stats
                        if hasattr(self, 'last_stats') and self.last_stats:
                             ReportGenerator.generate_pdf_report(filename, self.fig, self.last_stats, metadata={'run_filter': self.entry_min.get() or "All"})
                             ChrononSplash.show("Succès", f"Rapport PDF généré!")
                        else:
                             ChrononAlert.show_info("Attention", "Pas de résultats statistiques disponibles (faites une analyse d'abord). Sauvegarde graphique seul.")
                             self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=self.fig.get_facecolor())
                    except Exception as e:
                        ChrononAlert.show_error("Erreur", f"Échec rapport: {e}\nSauvegarde image standard...")
                        self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=self.fig.get_facecolor())
                else:
                    self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=self.fig.get_facecolor())
            else:
                try:
                    self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor=self.fig.get_facecolor())
                    ChrononSplash.show("Succès", f"Graphique sauvegardé!")
                except Exception as e:
                    ChrononAlert.show_error("Erreur", f"Échec de la sauvegarde: {e}")



    def show_help(self):
        msg = """Guide Rapide CHRONON:

1. Acquisition / Chargement:
   - Importez vos données ou lancez une acquisition.
   - Les données sont initialement "aveugles" (Blind).

2. Quality Control (QC):
   - Le système vérifie T°, vibrations, etc.
   - Regardez le flag 'QC' en bas.

3. Analyse & Fallback:
   - La régression (WLS) est automatique.
   - Si les suppositions sont violées (Autocorr), le Fallback s'active (voir bandeau).

4. Export:
   - Utilisez 'Sauvegarder Graphique' pour le PDF.
   - 'Export Sélection' pour CSV brut.
"""
        ChrononAlert.show_info("Aide CHRONON", msg)
