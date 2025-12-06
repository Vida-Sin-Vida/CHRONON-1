import tkinter as tk
import customtkinter as ctk
import winsound

class ChrononAlert(ctk.CTkToplevel):
    """
    Custom Notification Window for CHRONON.
    Themed with application colors and plays a pleasant sound.
    """
    
    def __init__(self, title, message, level="info"):
        super().__init__()
        
        # Window Config
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        
        # Colors
        bg_color = "#0B2240" # Brand Dark
        btn_color = "#1F6AA5" # Brand Blue
        if level == "error":
            bg_color = "#450A0A" # Dark Red
            btn_color = "#DC2626"
            winsound.MessageBeep(winsound.MB_ICONHAND) # Error sound
        elif level == "success":
            bg_color = "#064E3B" # Dark Green
            btn_color = "#059669"
            winsound.MessageBeep(winsound.MB_ICONASTERISK) # Pleasant Ding
        else:
            winsound.MessageBeep(winsound.MB_ICONASTERISK) # Normal info
            
        self.configure(fg_color=bg_color)
        
        # Icon/Title
        icon = "ℹ️"
        if level == "success": icon = "✅"
        if level == "error": icon = "❌"
        if level == "warning": icon = "⚠️"
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text=f"{icon} {title}", font=("Roboto", 20, "bold"), text_color="white").pack(pady=(20, 10))
        
        msg_label = ctk.CTkLabel(self, text=message, font=("Roboto", 14), text_color="#E5E7EB", wraplength=350)
        msg_label.pack(pady=10, padx=20)
        
        ctk.CTkButton(self, text="OK", command=self.destroy, fg_color=btn_color, hover_color="white", text_color=bg_color).pack(pady=20)
        
        # Center Window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Modal behavior
        self.transient(self.master)
        self.grab_set()
        self.wait_window()

class ChrononConfirm(ctk.CTkToplevel):
    """
    Custom Confirmation Dialog (Yes/No).
    """
    def __init__(self, title, message):
        super().__init__()
        self.result = False
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0B2240")
        
        winsound.MessageBeep(winsound.MB_ICONQUESTION)
        
        # Center Window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        ctk.CTkLabel(self, text=f"❓ {title}", font=("Roboto", 18, "bold"), text_color="white").pack(pady=(20, 10))
        ctk.CTkLabel(self, text=message, font=("Roboto", 14), text_color="#E5E7EB", wraplength=350).pack(pady=10)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="Oui", command=self.on_yes, fg_color="#059669", width=80).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Non", command=self.on_no, fg_color="#DC2626", width=80).pack(side="left", padx=10)
        
        self.transient(self.master)
        self.grab_set()
        self.wait_window()

    def on_yes(self):
        self.result = True
        self.destroy()

    def on_no(self):
        self.result = False
        self.destroy()

    @staticmethod
    def ask_yes_no(title, message):
        dlg = ChrononConfirm(title, message)
        return dlg.result

class SoundEngine:
    """
    Plays high-quality synthesized sounds (Sine Waves) for a premium feel.
    Avoids '8-bit' square waves from standard Beep.
    """
    @staticmethod
    def _generate_bell_wav(freq_list, duration_ms=500):
        """Generates a soft bell-like sound (Sine wave with decay) in WAV format."""
        import math
        import struct
        import io
        
        sample_rate = 44100
        n_samples = int(sample_rate * (duration_ms / 1000.0))
        
        # WAV Header
        header = struct.pack('<4sI4s', b'RIFF', 36 + n_samples * 2, b'WAVE')
        fmt = struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16)
        data_header = struct.pack('<4sI', b'data', n_samples * 2)
        
        audio_data = bytearray()
        
        # simple additive synthesis
        for i in range(n_samples):
            t = float(i) / sample_rate
            
            # Mix frequencies (Major Chord)
            sample_val = 0
            for f in freq_list:
                # Sine wave
                osc = math.sin(2 * math.pi * f * t)
                sample_val += osc
            
            # Normalize
            sample_val /= len(freq_list)
            
            # Apply Envelope (Exponential Decay) for 'Bell' effect
            envelope = math.exp(-6 * t) 
            
            # Scale to 16-bit
            val = int(sample_val * envelope * 32767 * 0.8)
            audio_data.extend(struct.pack('<h', val))
            
        return header + fmt + data_header + audio_data

    @staticmethod
    def play_success():
        # Soft Major Chord (C5, E5, G5) - Chime Style
        try:
            import threading
            def _play():
                wav_data = SoundEngine._generate_bell_wav([523.25, 659.25, 783.99, 1046.50], duration_ms=600)
                winsound.PlaySound(wav_data, winsound.SND_MEMORY)
            threading.Thread(target=_play, daemon=True).start()
        except: pass

    @staticmethod
    def play_error():
        # Soft Low Chord (A3, C4) - Gentle Warning
        try:
            import threading
            def _play():
                wav_data = SoundEngine._generate_bell_wav([220.00, 277.18], duration_ms=400)
                winsound.PlaySound(wav_data, winsound.SND_MEMORY)
            threading.Thread(target=_play, daemon=True).start()
        except: pass


class ChrononSplash(ctk.CTkToplevel):
    """
    Non-blocking 'Splash' notification for quick success feedback.
    Auto-closes after a delay with a fade-out effect.
    """
    def __init__(self, title, message, duration=1500):
        super().__init__()
        
        # Window Setup
        self.overrideredirect(True) # No border
        self.attributes("-topmost", True)
        self.configure(fg_color="#064E3B") # Dark Green
        self.geometry("300x150")
        
        # Center
        self.update_idletasks()
        width = 300
        height = 150
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
        # Content
        # Big Icon
        ctk.CTkLabel(self, text="✅", font=("Arial", 40)).pack(pady=(15, 5))
        
        # Title
        ctk.CTkLabel(self, text=title, font=("Roboto", 16, "bold"), text_color="white").pack(pady=2)
        
        # Message
        ctk.CTkLabel(self, text=message, font=("Roboto", 12), text_color="#A7F3D0").pack(pady=5)
        
        # Sound
        SoundEngine.play_success()
        
        # Auto-close sequence
        self.after(duration, self.fade_out)

    def fade_out(self):
        """Gradually reduce alpha until close"""
        alpha = self.attributes("-alpha")
        if alpha > 0.05:
            alpha -= 0.1
            self.attributes("-alpha", alpha)
            self.after(50, self.fade_out)
        else:
            self.destroy()

    @staticmethod
    def show(title, message, duration=1500):
        ChrononSplash(title, message, duration)



    @staticmethod
    def show_info(title, message):
        ChrononAlert(title, message, level="info")

    @staticmethod
    def show_success(title, message):
        ChrononAlert(title, message, level="success")

    @staticmethod
    def show_error(title, message):
        ChrononAlert(title, message, level="error")
