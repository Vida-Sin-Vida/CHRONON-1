# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
import threading
import time
import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

from app.experiment.manager import ExperimentManager

from .frames.setup_frame import SetupFrame
from .frames.acquisition_frame import AcquisitionFrame
from .frames.visualization_frame import VisualizationFrame
from .frames.analysis_frame import AnalysisFrame
from app.gui.translations import TRANSLATIONS

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CHRONON V1.0 - Interface Scientifique")
        self.geometry("1200x800")
        
        # 1. Window Identity
        # 1. Window Identity
        # 1. Window Identity
        try:
            # WINDOWS: Use .ico for best transparency support in title bar
            self.iconbitmap("logo_zenodo_v2.ico")
        except Exception as e:
            print(f"Icon error: {e}")

        # 2. Visual Theme (Scientific Modern)
        # 2. Visual Theme (Professional Light)
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue") 
        
        # Colors: Extracted from "Chronon Field" Image
        # THEME PALETTE (User Light Theme)
        self.colors = {
            "bg": "#F7F6F3",        # Off-White (Main BG)
            "surface": "#FFFFFF",   # White (Cards/Sidebar/High Vis)
            "primary": "#1F6AA5",   # Medium Blue (Action) - Adjusted for contrast
            "primary_hover": "#155A8A", # Darker Blue
            "text_main": "#0B2240", # Dark Blue (Global Text)
            "text_sub": "#4B5563",  # Gray 600
            "border": "#E5E7EB",    # Gray 200
            "success": "#10B981",   # Emerald
            "error": "#EF4444",     # Red
            "warning": "#F59E0B",   # Amber
            "nav_hover": "#EEF2FF", # Indigo 50
            "nav_active": "#DBEAFE" # Blue 100
        }
        
        # Backward compatibility for any old code not yet updated (though we are updating frames)
        self.color_bg = self.colors["bg"]
        self.color_panel = self.colors["surface"] 
        self.color_primary = self.colors["text_main"] 
        
        self.configure(fg_color=self.color_bg)

        # Initialize Logic
        self.manager = ExperimentManager()

        # Configure grid layout (1x2)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create Navigation Frame (Sidebar) - White
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.color_panel, width=220)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(6, weight=1) 

        # Logo: Image
        try:
            from PIL import Image
            logo_img = ctk.CTkImage(light_image=Image.open("logo/logo_sidebar.png"),
                                  dark_image=Image.open("logo/logo_sidebar.png"),
                                  size=(100, 100)) # Square to prevent distortion
            self.logo_label = ctk.CTkLabel(self.navigation_frame, text="", image=logo_img)
            self.logo_label.grid(row=0, column=0, padx=20, pady=20)
        except Exception as e:
            print(f"Logo load error: {e}")
            self.logo_label = ctk.CTkLabel(self.navigation_frame, text="CHRONON", 
                                         font=ctk.CTkFont(family="Roboto", size=24, weight="bold"),
                                         text_color=self.color_primary)
            self.logo_label.grid(row=0, column=0, padx=20, pady=40)

        # Navigation Buttons
        self.setup_button = self._create_nav_button("SETUP", "setup", 1)
        self.acquisition_button = self._create_nav_button("ACQUISITION", "acquisition", 2)
        self.viz_button = self._create_nav_button("VISUALISATION", "visualization", 3)
        self.analysis_button = self._create_nav_button("ANALYSE", "analysis", 4)
        self.history_button = self._create_nav_button("HISTORIQUE", "history", 5)
        self.help_button = self._create_nav_button("AIDE / THÉORIE", "help", 6)

        # Spacer to push signature to bottom
        self.navigation_frame.grid_rowconfigure(6, weight=0) # Reset previous weight
        self.navigation_frame.grid_rowconfigure(7, weight=1) # Spacer row

        # Language Switcher
        self.language = "fr"
        self.lang_switch = ctk.CTkSegmentedButton(self.navigation_frame, values=["FR", "EN"], 
                                                  command=self.change_language,
                                                  width=100, height=24)
        self.lang_switch.grid(row=7, column=0, pady=(10, 5))
        self.lang_switch.set("FR")

        # Signature (Bottom Left)
        self.lbl_signature = ctk.CTkLabel(self.navigation_frame, text="Dev : Brécheteau.B",
                                        font=ctk.CTkFont(family="Garamond", size=13, weight="bold"),
                                        text_color="#1F6AA5") # Blue like buttons
        self.lbl_signature.grid(row=8, column=0, pady=5, sticky="s")

        # Main Content Frames
        self.frames = {}
        self.current_frame_name = None

        # Initialize Frames with Manager
        from .frames.history_frame import HistoryFrame 
        from .frames.help_frame import HelpFrame
        
        for F, name in [
            (SetupFrame, "setup"),
            (AcquisitionFrame, "acquisition"),
            (VisualizationFrame, "visualization"),
            (AnalysisFrame, "analysis"),
            (HistoryFrame, "history"),
            (HelpFrame, "help")
        ]:
            # Frames are containers. We keep them transparent so the Main Black BG shows through.
            # Inside each frame, we will add 'Cards'.
            frame = F(master=self, manager=self.manager, corner_radius=0, fg_color="transparent")
            self.frames[name] = frame
            # Do not grid here. select_frame will handle it.

        # Select default frame
        self.select_frame("setup")

    def _create_nav_button(self, text, name, row):
        btn = ctk.CTkButton(self.navigation_frame, corner_radius=8, height=45, border_spacing=15, text=text,
                            font=ctk.CTkFont(family="Roboto", size=15, weight="bold"),
                            fg_color="transparent", text_color="#555555", 
                            hover_color="#F0F0F0", anchor="w", 
                            command=lambda: self.select_frame(name))
        btn.grid(row=row, column=0, sticky="ew", padx=15, pady=5) 
        return btn

    def select_frame(self, name):
        # Reset button colors
        for btn in [self.setup_button, self.acquisition_button, self.viz_button, 
                    self.analysis_button, self.history_button, self.help_button]:
            btn.configure(fg_color="transparent", text_color="#555555")

        # Highlight selected button - Minimalist Style
        active_btn = None
        if name == "setup": active_btn = self.setup_button
        elif name == "acquisition": active_btn = self.acquisition_button
        elif name == "visualization": active_btn = self.viz_button
        elif name == "analysis": active_btn = self.analysis_button
        elif name == "history": active_btn = self.history_button
        elif name == "help": active_btn = self.help_button
        
        if active_btn:
            # Active State: Light Blue bg + Dark Blue Text
            active_btn.configure(fg_color="#E6F0FA", text_color="#1F6AA5") 

        # Show frame
        if self.current_frame_name:
            self.frames[self.current_frame_name].grid_forget()
        
        self.frames[name].grid(row=0, column=1, sticky="nsew")
        self.current_frame_name = name

        # Update language for the new frame if supported
        if hasattr(self.frames[name], 'update_language'):
            self.frames[name].update_language()

    def change_language(self, new_lang):
        self.language = new_lang.lower()
        
        # Update Sidebar
        t_side = TRANSLATIONS[self.language]["SIDEBAR"]
        self.setup_button.configure(text=t_side["SETUP"])
        self.acquisition_button.configure(text=t_side["ACQUISITION"])
        self.viz_button.configure(text=t_side["VISUALIZATION"])
        self.analysis_button.configure(text=t_side["ANALYSIS"])
        self.history_button.configure(text=t_side["HISTORY"])
        self.help_button.configure(text=t_side["HELP"])
        
        # Update Current Frame
        if self.current_frame_name and hasattr(self.frames[self.current_frame_name], 'update_language'):
            self.frames[self.current_frame_name].update_language()

