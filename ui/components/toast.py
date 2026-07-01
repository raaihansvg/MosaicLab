import customtkinter as ctk

class ToastNotification(ctk.CTkFrame):
    def __init__(self, master, message, type="success", duration=3000, **kwargs):
        # Very light shadow simulation by having a very subtle border, or just clean white with a colored accent
        super().__init__(master, corner_radius=12, fg_color="#FFFFFF", border_width=1, border_color="#E9EDF7", **kwargs)
        
        self.message = message
        self.duration = duration
        
        colors = {
            "success": "#05CD99",
            "error": "#EE5D50",
            "info": "#4318FF",
            "warning": "#FFCE20"
        }
        accent = colors.get(type, colors["info"])
        
        # Accent dot instead of full bar for elegance
        dot = ctk.CTkFrame(self, width=10, height=10, corner_radius=5, fg_color=accent)
        dot.pack(side="left", padx=(16, 8), pady=12)
        
        self.lbl = ctk.CTkLabel(self, text=message, text_color="#2B3674", font=("Helvetica", 13, "bold"))
        self.lbl.pack(side="left", padx=(0, 24), pady=12)
        
        # Bottom Right positioning
        # We start off-screen to the right
        self.place(relx=1.2, rely=0.95, anchor="se")
        self.target_relx = 0.98
        self.current_relx = 1.2
        self.master = master

    def show(self):
        self.lift()
        self._animate_in()
        self.after(self.duration, self.hide)

    def _animate_in(self):
        dist = self.current_relx - self.target_relx
        if dist > 0.001:
            step = max(0.002, dist * 0.15)
            self.current_relx -= step
            self.place(relx=self.current_relx, rely=0.95, anchor="se")
            self.after(16, self._animate_in)
        else:
            self.place(relx=self.target_relx, rely=0.95, anchor="se")

    def hide(self):
        self._animate_out()

    def _animate_out(self):
        dist = 1.2 - self.current_relx
        if dist > 0.001:
            step = max(0.002, dist * 0.15)
            self.current_relx += step
            self.place(relx=self.current_relx, rely=0.95, anchor="se")
            self.after(16, self._animate_out)
        else:
            self.destroy()

def show_toast(master, message, type="success", duration=3000):
    toast = ToastNotification(master, message, type, duration)
    toast.show()
