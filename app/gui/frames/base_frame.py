import customtkinter as ctk

class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, manager=None, **kwargs):
        super().__init__(master, **kwargs)
        self.manager = manager
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def show(self):
        self.pack(fill="both", expand=True)

    def hide(self):
        self.pack_forget()
