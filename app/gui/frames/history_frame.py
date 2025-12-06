# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import json
import os
import csv
import pandas as pd
from .base_frame import BaseFrame
from .base_frame import BaseFrame
from app.gui.widgets.custom_notification import ChrononAlert, ChrononConfirm, ChrononSplash
from app.gui.translations import TRANSLATIONS

class HistoryFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if hasattr(self, "update_language"):
            self.after(100, self.update_language)
        
        self.label = ctk.CTkLabel(self, text="Historique des Expériences (Laboratoire)", 
                                font=ctk.CTkFont(size=20, weight="bold"), text_color="#0B1120")
        self.label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # History List (Treeview) - MAXIMIZED
        self.tree_frame = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#E0E0E0")
        self.tree_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.tree_frame.grid_columnconfigure(0, weight=1)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        
        # Style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30) 
        style.configure("Treeview", background="white", fieldbackground="white", foreground="#0B2240", bordercolor="#E5E7EB", font=("Segoe UI", 12))
        style.configure("Treeview.Heading", background="#0B2240", foreground="white", relief="flat", font=("Segoe UI", 13, "bold"))
        style.map("Treeview", background=[("selected", "#1F6AA5")], foreground=[("selected", "white")])
        
        # Updated Columns to match Ledger
        # header in ledger.py: ["timestamp", "run_id", "verdict", "hash_config", "hash_code", "json_row_path", "row_hash", "operator", "blinding_event"]
        # We display useful summary
        # Updated Columns to match ExperimentManager history.json
        columns = ("timestamp", "run_id", "delta_h", "n_points", "scenario")
        
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15, selectmode="extended")
        
        self.tree.heading("timestamp", text="Date/Time")
        self.tree.heading("run_id", text="Run ID")
        self.tree.heading("delta_h", text="Delta H (m)")
        self.tree.heading("n_points", text="N Points")
        self.tree.heading("scenario", text="Scénario")
        
        self.tree.column("timestamp", width=140)
        self.tree.column("run_id", width=140)
        self.tree.column("delta_h", width=80)
        self.tree.column("n_points", width=80)
        self.tree.column("scenario", width=100)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Actions
        self.btn_load = ctk.CTkButton(self, text="Charger la sélection", command=self.load_selection,
                                    fg_color="#0B1120", hover_color="#232D3F")
        self.btn_load.grid(row=2, column=0, padx=20, pady=20, sticky="e")
        
        self.btn_refresh = ctk.CTkButton(self, text="Actualiser", command=self.refresh_history,
                                       fg_color="#1F6AA5", hover_color="#155A8A")
        self.btn_refresh.grid(row=2, column=0, padx=20, pady=20, sticky="w")

        # Delete Button (Centered)
        self.btn_delete = ctk.CTkButton(self, text="Supprimer", command=self.delete_selection,
                                        fg_color="#EF4444", hover_color="#DC2626")
        self.btn_delete.grid(row=2, column=0, padx=20, pady=20)

        # Initial Load
        self.refresh_history()

    def refresh_history(self):
        # Clear
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # Read from history.json (ExperimentManager standard)
        hist_path = "history.json"
        
        # If manager exists, use its path or memory
        history_data = []
        if self.manager and hasattr(self.manager, 'history'):
            history_data = self.manager.history
        elif os.path.exists(hist_path):
             try:
                 with open(hist_path, 'r') as f:
                     history_data = json.load(f)
             except:
                 pass

        if not history_data:
            return

        # Sort by timestamp desc
        try:
            history_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        except:
            pass

        for run in history_data:
            ts = run.get("timestamp", "").replace("T", " ")[:19]
            rid = run.get("id", "Unknown")
            params = run.get("params", {})
            data_points = run.get("data", [])
            
            delta_h = params.get("delta_h", "N/A")
            scenario = params.get("scenario", "N/A")
            n_pts = len(data_points)
            
            # Insert
            self.tree.insert("", "end", values=(ts, rid, delta_h, n_pts, scenario))
            
        # Store for loading
        self.history_cache = history_data

    def load_selection(self):
        selected = self.tree.selection()
        if not selected: return
        
        # Get Run ID from tree
        item_vals = self.tree.item(selected[0])['values']
        run_id = item_vals[1] # ID is at index 1
        if hasattr(self, 'history_cache'):
            target_run = next((r for r in self.history_cache if str(r.get('id', '')) == str(run_id)), None)
            
            if target_run and self.manager:
                # Restore to Manager
                
                # Check data
                raw_data = target_run.get('data', [])
                if not raw_data:
                    ChrononAlert.show_info("Attention", "Ce run ne contient aucune donnée.")
                    return
                    
                # Push to Manager
                self.manager.data_log = raw_data
                self.manager.params = target_run.get('params', {})
                self.manager.current_run_index = len(raw_data) # Set index to end
                
                # Notify App
                # We trigger a 'complete' event to force Visualization update
                self.manager.notify_listeners("complete", raw_data)
                
                ChrononSplash.show("Run Chargé", f"Run {run_id}\n({len(raw_data)} points)")
            else:
                 ChrononAlert.show_error("Erreur", "Données non trouvées ou Manager déconnecté.")

    def delete_selection(self):
        selected = self.tree.selection()
        if not selected: return
        
        if not ChrononConfirm.ask_yes_no("Confirmation", f"Voulez-vous vraiment supprimer {len(selected)} élément(s) de l'historique ?"):
            return
            
        run_ids_to_delete = []
        for item_id in selected:
            vals = self.tree.item(item_id)['values']
            run_ids_to_delete.append(str(vals[1])) # ID is index 1
            
        if self.manager and hasattr(self.manager, 'delete_history_items'):
            self.manager.delete_history_items(run_ids_to_delete)
            self.refresh_history()
            ChrononAlert.show_success("Succès", "Éléments supprimés.")
        else:
            # Fallback direct file edit if manager not available (less robust)
            ChrononAlert.show_info("Attention", "Manager non disponible pour suppression.")

    def update_language(self):
        app = self.winfo_toplevel()
        lang = getattr(app, "language", "fr")
        
        t = TRANSLATIONS[lang]["HISTORY"]
        c = TRANSLATIONS[lang]["COMMON"]
        
        self.label.configure(text=t["TITLE"])
        self.btn_load.configure(text=t["BTN_LOAD"])
        self.btn_delete.configure(text=t["BTN_DELETE"])
        
        # Translate Tree Headings
        # Note: Treeview headings are configured via methods
        self.tree.heading("timestamp", text=t["COL_DATE"])
        self.tree.heading("run_id", text="Run ID") # Standard
        self.tree.heading("delta_h", text="Delta H")
        self.tree.heading("n_points", text=t["COL_SAMPLES"])
        self.tree.heading("scenario", text="Scenario" if lang == "en" else "Scénario")
