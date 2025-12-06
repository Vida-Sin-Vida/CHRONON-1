# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
import math
import tkinter as tk
import customtkinter as ctk
from .base_frame import BaseFrame
from app.gui.translations import TRANSLATIONS

class AcquisitionFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if hasattr(self, "update_language"):
            self.after(100, self.update_language)
        
        colors = self.master.colors if hasattr(self.master, "colors") else {}
        
        self.lbl_title = ctk.CTkLabel(self, text="Acquisition de Données", 
                                    font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
                                    text_color=colors.get("text_main", "black"))
        self.lbl_title.pack(pady=20, anchor="w")

        self.card_anim = ctk.CTkFrame(self, fg_color=colors.get("surface", "white"), corner_radius=20)
        self.card_anim.pack(fill="x", padx=0, pady=0)
        
        self.anim_height = 80
        self.canvas = tk.Canvas(self.card_anim, height=self.anim_height, bg=colors.get("surface", "white"), highlightthickness=0)
        self.canvas.pack(fill="x", padx=20, pady=20)
        
        self.anim_running = False
        self.scan_pos = 0
        self.scan_direction = 1
        
        self.grid_container = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_container.pack(fill="both", expand=True, pady=20)
        self.grid_container.grid_columnconfigure(0, weight=3)
        self.grid_container.grid_columnconfigure(1, weight=1)
        
        self.log_frame = ctk.CTkFrame(self.grid_container, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E7EB")
        self.log_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        
        self.log_widget = ctk.CTkTextbox(self.log_frame, fg_color="transparent", text_color="#0B2240", font=("Consolas", 13))
        self.log_widget.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_widget.insert("0.0", "> SYSTÈME PRÊT.\n")

        self.ctrl_frame = ctk.CTkFrame(self.grid_container, fg_color=colors.get("surface", "white"), corner_radius=15)
        self.ctrl_frame.grid(row=0, column=1, sticky="nsew")
        
        ctk.CTkLabel(self.ctrl_frame, text="Statut", font=("Segoe UI", 14, "bold"), text_color="gray").pack(pady=20)
        self.lbl_status = ctk.CTkLabel(self.ctrl_frame, text="EN ATTENTE", font=("Segoe UI", 20, "bold"), text_color=colors.get("primary", "blue"))
        self.lbl_status.pack()
        
        self.btn_stop = ctk.CTkButton(self.ctrl_frame, text="ARRÊT D'URGENCE", 
                                    fg_color="#EF4444", hover_color="#DC2626", 
                                    height=50, font=("Segoe UI", 12, "bold"), 
                                    command=self.stop_experiment)
        self.btn_stop.pack(side="bottom", fill="x", padx=20, pady=20)

        if self.manager:
            self.manager.add_listener(self.on_update)

    def start_animation(self):
        self.anim_running = True
        self.animate()

    def stop_animation(self):
        self.anim_running = False
        self.canvas.delete("wave")

    def animate(self):
        if not self.anim_running: return
        
        w = self.canvas.winfo_width()
        h = self.anim_height
        
        self.canvas.delete("all")
        
        self.scan_pos += 0.15
        
        points_main = []
        points_secondary = []
        step = 4
        
        for x in range(0, w + step, step):
            nx = x * 0.01
            y1 = math.sin(nx * 0.5 + self.scan_pos * 0.3) * 10
            y2 = math.sin(nx * 1.5 + self.scan_pos * 0.8) * 5
            y3 = math.sin(nx * 3.0 + self.scan_pos * 1.2) * 2
            
            y_final = h/2 + (y1 + y2 + y3)
            
            points_main.append(x)
            points_main.append(y_final)
            
            y_ghost = h/2 + (math.sin(nx * 0.5 + self.scan_pos * 0.3 - 0.5) * 10 + 
                             math.sin(nx * 1.5 + self.scan_pos * 0.8 - 0.5) * 5)
            points_secondary.append(x)
            points_secondary.append(y_ghost)
            
        if len(points_main) > 4:
            self.canvas.create_line(points_secondary, smooth=True, fill="#818CF8", width=2, stipple="gray50", tag="wave")
            self.canvas.create_line(points_main, smooth=True, fill="#1F6AA5", width=3, tag="wave")

        self.after(30, self.animate)

    def stop_experiment(self):
        if self.manager: self.manager.stop_experiment()

    def on_update(self, event, data):
        if event == "start":
            self.lbl_status.configure(text="ACQUISITION", text_color="#10B981")
            self.log_widget.delete("0.0", "end")
            self.log_widget.insert("end", "> DÉMARRAGE...\n")
            self.start_animation()
        elif event == "log":
            self.log_widget.insert("end", f"> {data}\n")
            self.log_widget.see("end")
        elif event == "stop" or event == "complete":
            self.lbl_status.configure(text="TERMINÉ", text_color="gray")
            self.log_widget.insert("end", "> FIN DE SESSION.\n")
            self.stop_animation()

    def update_language(self):
        lang = getattr(self.master, "language", "fr")
        t = TRANSLATIONS[lang]["ACQUISITION"]
        
        self.lbl_title.configure(text=t["TITLE"])
        self.btn_stop.configure(text=t["BTN_STOP"])
        
        # Status logic is dynamic, but we can update defaults
        curr_status = self.lbl_status._text
        if "ATTENTE" in curr_status or "READY" in curr_status:
             self.lbl_status.configure(text=t["STATUS_IDLE"])
        elif "COURS" in curr_status or "RUNNING" in curr_status:
             self.lbl_status.configure(text=t["STATUS_RUNNING"])

# ~ ~ ~ Φ(x) ~ ~ ~
# Benjamin Brécheteau | Chronon Field 2025
# ~ ~ ~ ~ ~ ~ ~ ~ ~
