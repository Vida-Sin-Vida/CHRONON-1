# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import customtkinter as ctk
from .base_frame import BaseFrame
from app.gui.translations import TRANSLATIONS

class HelpFrame(BaseFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if hasattr(self, "update_language"):
            self.after(100, self.update_language)
        
        self.label = ctk.CTkLabel(self, text="Documentation & Théorie", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        # Documentation Content
        self.textbox = ctk.CTkTextbox(self, width=800, height=500, font=("Consolas", 14))
        self.textbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        self.textbox.insert("0.0", "Loading documentation...")
        self.textbox.configure(state="disabled")

    def update_language(self):
        app = self.winfo_toplevel()
        lang = getattr(app, "language", "fr")
        
        t = TRANSLATIONS[lang]["HELP"]
        self.label.configure(text=t["TITLE"])
        
        doc_content = t.get("TXT_DOC", "No documentation available.")
        
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", doc_content)
        self.textbox.configure(state="disabled")

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
