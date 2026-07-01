import customtkinter as ctk
from ..theme import BG_SURFACE, PRIMARY, TEXT_PRIMARY, TEXT_MUTED, get_font

class MetricCard(ctk.CTkFrame):
    def __init__(self, master, title, value, icon_name=None, **kwargs):
        # Extremely clean look. No border, just white background and spacing.
        super().__init__(master, fg_color="transparent", height=90, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        self.body = ctk.CTkFrame(self, fg_color=BG_SURFACE, corner_radius=18)
        self.base_rely = 0.05
        self.target_rely = self.base_rely
        self.current_rely = self.base_rely
        
        # We reserve space for a subtle lift (e.g. from 0.05 to 0.0)
        self.body.place(relx=0, rely=self.base_rely, relwidth=1.0, relheight=0.95)
        
        inner = ctk.CTkFrame(self.body, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=16)
        
        self.title_lbl = ctk.CTkLabel(inner, text=title, font=get_font("card_title"), text_color=TEXT_MUTED)
        self.title_lbl.pack(anchor="w")
        
        self.val_lbl = ctk.CTkLabel(inner, text=value, font=get_font("primary_number"), text_color=TEXT_PRIMARY)
        self.val_lbl.pack(anchor="w", pady=(4, 0))
        
        # Bind events for effortless lift animation
        def _on_enter(e):
            self.target_rely = 0.0
            self._animate_lift()
            
        def _on_leave(e):
            self.target_rely = self.base_rely
            self._animate_lift()
            
        self.body.bind("<Enter>", _on_enter)
        self.body.bind("<Leave>", _on_leave)
        inner.bind("<Enter>", _on_enter)
        self.title_lbl.bind("<Enter>", _on_enter)
        self.val_lbl.bind("<Enter>", _on_enter)
        
        self._anim_job = None
        
    def _animate_lift(self):
        if self._anim_job:
            self.after_cancel(self._anim_job)
            
        dist = self.target_rely - self.current_rely
        if abs(dist) > 0.001:
            self.current_rely += dist * 0.2
            self.body.place(relx=0, rely=self.current_rely, relwidth=1.0, relheight=0.95)
            self._anim_job = self.after(16, self._animate_lift)
        else:
            self.current_rely = self.target_rely
            self.body.place(relx=0, rely=self.current_rely, relwidth=1.0, relheight=0.95)

    def set_value(self, value):
        self.val_lbl.configure(text=value)

class PillTab(ctk.CTkButton):
    def __init__(self, master, text, command=None, **kwargs):
        super().__init__(
            master, 
            text=text, 
            command=command,
            fg_color="transparent",
            text_color=TEXT_MUTED,
            hover_color="#E9EDF7",
            corner_radius=20,
            font=get_font("body"),
            width=60,
            height=40,
            **kwargs
        )
        
    def set_active(self, active=True):
        if active:
            self.configure(fg_color=PRIMARY, text_color="#FFFFFF", hover_color="#4B49B8")
        else:
            self.configure(fg_color="transparent", text_color=TEXT_MUTED, hover_color="#E9EDF7")

class AnimatedButton(ctk.CTkFrame):
    def __init__(self, master, text, image=None, fg_color=None, hover_color=None, text_color=None, 
                 border_width=0, border_color=None, command=None, height=44, corner_radius=12, font=None, state="normal", **kwargs):
        super().__init__(master, fg_color="transparent", height=height + 4, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)
        
        self.base_y = 4
        self.target_y = self.base_y
        self.current_y = self.base_y
        
        self.btn = ctk.CTkButton(self, text=text, image=image, fg_color=fg_color, hover_color=hover_color, text_color=text_color, 
                                 border_width=border_width, border_color=border_color, command=command,
                                 corner_radius=corner_radius, height=height, font=font, state=state)
        self.btn.place(relx=0, y=self.base_y, relwidth=1.0)
        
        def _on_enter(e):
            if self.btn.cget("state") != "disabled":
                self.target_y = 0.0
                self._animate_lift()
            
        def _on_leave(e):
            self.after(10, self._check_pointer_leave)
            
        self.btn.bind("<Enter>", _on_enter)
        self.btn.bind("<Leave>", _on_leave)
        self.bind("<Enter>", _on_enter)
        self.bind("<Leave>", _on_leave)
        
        self._anim_job = None
        
    def _animate_lift(self):
        if self._anim_job:
            self.after_cancel(self._anim_job)
            
        dist = self.target_y - self.current_y
        if abs(dist) > 0.1:
            self.current_y += dist * 0.3
            self.btn.place(relx=0, y=self.current_y, relwidth=1.0)
            self._anim_job = self.after(16, self._animate_lift)
        else:
            self.current_y = self.target_y
            self.btn.place(relx=0, y=self.current_y, relwidth=1.0)

    def _pointer_in_area(self):
        try:
            x, y = self.winfo_pointerxy()
            wx, wy = self.winfo_rootx(), self.winfo_rooty()
            ww, wh = self.winfo_width(), self.winfo_height()
            return wx <= x <= wx + ww and wy <= y <= wy + wh
        except Exception:
            return False

    def _check_pointer_leave(self):
        if self._pointer_in_area():
            return
        self.target_y = self.base_y
        self._animate_lift()

    def configure(self, **kwargs):
        if hasattr(self, 'btn'):
            self.btn.configure(**kwargs)
            if kwargs.get("state") == "disabled":
                self.target_y = self.base_y
                self._animate_lift()
        else:
            super().configure(**kwargs)
        
    def cget(self, key):
        if hasattr(self, 'btn'):
            try:
                return self.btn.cget(key)
            except ValueError:
                return super().cget(key)
        return super().cget(key)
