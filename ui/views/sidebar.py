import customtkinter as ctk
from ..theme import BG_SIDEBAR, PRIMARY, get_icon, TEXT_MUTED, TEXT_PRIMARY, get_font
from core.konstanta import N_FORMATIONS

class Sidebar(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        # Minimal sidebar
        super().__init__(master, fg_color=BG_SIDEBAR, corner_radius=0, width=240, **kwargs)
        self.app = app_controller
        self.grid_propagate(False)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self._build_header()
        self._build_slots()
        
    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(40, 32))
        
        ctk.CTkLabel(hdr, text="Mozaik", font=get_font("section_title"), text_color=TEXT_PRIMARY).pack(side="left")

    def _build_slots(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew", padx=16)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)
        
        ctk.CTkLabel(container, text="FORMASI", font=get_font("caption"), text_color=TEXT_MUTED, anchor="w").pack(fill="x", padx=12, pady=(0, 12))
        
        self.scroll = ctk.CTkFrame(container, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)
        
        self.slots = {}
        for i in range(1, N_FORMATIONS + 1):
            slot = FormationMenuItem(self.scroll, i, self.app)
            slot.pack(fill="x", pady=2)
            self.slots[i] = slot


class FormationMenuItem(ctk.CTkFrame):
    def __init__(self, master, index, app, **kwargs):
        super().__init__(master, fg_color="transparent", height=44, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.index = index
        self.app = app
        
        self.icon_empty = get_icon("circle", size=16)
        self.icon_uploaded = get_icon("image", size=16, dark_mode=False)
        self.icon_processed = get_icon("check-circle-2", size=16, dark_mode=False) 
        
        self._current_icon = self.icon_empty
        
        # Active indicator strip
        self.indicator = ctk.CTkFrame(self, fg_color="transparent", width=3, corner_radius=1.5)
        self.indicator.place(relx=0, rely=0.2, relheight=0.6)
        
        self.base_rely = 0.0
        self.target_rely = self.base_rely
        self.current_rely = self.base_rely
        
        self.btn = ctk.CTkButton(self, text=f"Formasi {index:02d}", image=self.icon_empty, compound="left",
                         fg_color="transparent", text_color=TEXT_MUTED, hover_color="#EAECEF",
                         corner_radius=8, font=get_font("body"), anchor="w",
                         command=self.on_click)
        self.btn.place(relx=0.05, rely=self.base_rely, relwidth=0.95, relheight=1.0)
        
        self.is_active = False
        
        def _on_enter(e):
            if not self.is_active:
                self.target_rely = -0.08
                self._animate_lift()
            
        def _on_leave(e):
            self.target_rely = self.base_rely
            self._animate_lift()
            
        self.btn.bind("<Enter>", _on_enter)
        self.btn.bind("<Leave>", _on_leave)
        self._anim_job = None
        
    def _animate_lift(self):
        if self._anim_job:
            self.after_cancel(self._anim_job)
            
        dist = self.target_rely - self.current_rely
        if abs(dist) > 0.001:
            self.current_rely += dist * 0.25
            self.btn.place(relx=0.05, rely=self.current_rely, relwidth=0.95, relheight=1.0)
            self._anim_job = self.after(16, self._animate_lift)
        else:
            self.current_rely = self.target_rely
            self.btn.place(relx=0.05, rely=self.current_rely, relwidth=0.95, relheight=1.0)
        
    def on_click(self):
        self.app.switch_tab(self.index)
        
    def set_active(self, active=True):
        self.is_active = active
        if active:
            self.btn.configure(fg_color="#EAECEF", text_color=TEXT_PRIMARY)
            self.indicator.configure(fg_color=PRIMARY)
            self.target_rely = 0.0
            self._animate_lift()
        else:
            self.btn.configure(fg_color="transparent", text_color=TEXT_MUTED)
            self.indicator.configure(fg_color="transparent")
            self.btn.configure(image=self._current_icon)
            self.target_rely = self.base_rely
            self._animate_lift()
                           
    def set_state(self, state):
        if state == "empty":
            self._current_icon = self.icon_empty
            if not self.is_active: self.btn.configure(text_color=TEXT_MUTED)
        elif state == "uploaded":
            self._current_icon = self.icon_uploaded
            if not self.is_active: self.btn.configure(text_color=TEXT_PRIMARY)
        elif state == "processed":
            self._current_icon = self.icon_processed
            # Primary color icon when processed? Or keep it neutral.
            # Using neutral text but different icon is cleaner.
            
        if not self.is_active:
            self.btn.configure(image=self._current_icon)
        else:
            self.btn.configure(image=self._current_icon) # Update icon even if active
