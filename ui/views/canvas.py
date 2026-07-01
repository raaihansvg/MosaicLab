import customtkinter as ctk
import tkinter as tk
from ..theme import BG_SURFACE, BG_BASE, PRIMARY, PRIMARY_HOVER, TEXT_MUTED, TEXT_PRIMARY, BORDER, get_font, get_icon
from ..utils import animate_widget_color
from ..components.cards import AnimatedButton

class CanvasArea(ctk.CTkFrame):
    def __init__(self, master, app_controller, **kwargs):
        # White background for the main canvas area
        super().__init__(master, fg_color=BG_SURFACE, corner_radius=0, **kwargs)
        self.app = app_controller
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_topbar()
        self._build_content_area()
        
    def _build_topbar(self):
        self.topbar = ctk.CTkFrame(self, fg_color="transparent", height=72)
        self.topbar.grid(row=0, column=0, sticky="ew", padx=40, pady=(32, 0))
        
        self.lbl_title = ctk.CTkLabel(self.topbar, text="Workspace", font=get_font("page_title"), text_color=TEXT_PRIMARY)
        self.lbl_title.pack(side="left")
        
        # Action Buttons
        self.actions_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        self.actions_frame.pack(side="right")
        
        self.btn_process = AnimatedButton(
            self.actions_frame, text="Generate", image=get_icon("play", size=16, dark_mode=True),
            fg_color=PRIMARY, text_color="#FFFFFF", hover_color=PRIMARY_HOVER,
            font=get_font("body"), corner_radius=12, height=44, width=140,
            command=self.app.process_all
        )
        self.btn_process.pack(side="left")

        self.btn_delete = AnimatedButton(
            self.actions_frame, text="Delete", image=get_icon("trash-2", size=16),
            fg_color="transparent", text_color="#FF3B30", hover_color="#FFECEB",
            font=get_font("body"), corner_radius=12, height=44, width=100,
            command=self._on_trash_click
        )
        self.btn_delete.pack(side="left", padx=(20, 0))
        self.btn_delete.pack_forget() # Hide initially

    def _build_content_area(self):
        self.content_container = ctk.CTkFrame(self, fg_color="transparent")
        self.content_container.grid(row=1, column=0, sticky="nsew", padx=40, pady=(24, 40))
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)
        
        # --- EMPTY STATE ---
        self.empty_state = ctk.CTkFrame(self.content_container, fg_color="transparent")
        
        self._drop_zone_base_rely = 0.5
        self._drop_zone_target_rely = self._drop_zone_base_rely
        self._drop_zone_current_rely = self._drop_zone_base_rely
        self._drop_zone_hovered = False
        self._drop_zone_anim_job = None

        self.drop_zone = ctk.CTkFrame(self.empty_state, fg_color=BG_BASE, corner_radius=24, border_width=1, border_color=BORDER)
        self.drop_zone.place(relx=0.5, rely=self._drop_zone_base_rely, anchor="center", relwidth=0.8, relheight=0.6)
        
        self.inner_empty = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        self.inner_empty.place(relx=0.5, rely=0.5, anchor="center")
        
        icon_up = get_icon("upload", size=48)
        self.lbl_upload_icon = ctk.CTkLabel(self.inner_empty, text="", image=icon_up)
        if icon_up: self.lbl_upload_icon.pack(pady=(0, 24))
        
        self.lbl_upload_title = ctk.CTkLabel(self.inner_empty, text="Klik untuk memilih gambar", font=get_font("section_title"), text_color=TEXT_PRIMARY)
        self.lbl_upload_title.pack()
        self.lbl_upload_subtitle = ctk.CTkLabel(self.inner_empty, text="atau Drag & Drop file ke sini", font=get_font("body"), text_color=TEXT_MUTED)
        self.lbl_upload_subtitle.pack(pady=(8, 0))
        
        def _trigger_click(e):
            if self.app.active_tab:
                self.app.open_manual_upload_dialog()
            return "break"
                    
        for w in [self.drop_zone, self.inner_empty, self.lbl_upload_icon] + self.inner_empty.winfo_children():
            w.bind("<Button-1>", _trigger_click)
            
        def _on_enter(e):
            if self._drop_zone_hovered:
                return
            self._drop_zone_hovered = True
            self._drop_zone_target_rely = 0.485
            self._animate_drop_zone_lift()
            animate_widget_color(self.drop_zone, "fg_color", BG_BASE, "#F0F1F5", steps=10)

        def _on_leave(e):
            self.after(10, self._check_drop_zone_leave)

        for w in [self.drop_zone, self.inner_empty, self.lbl_upload_icon] + self.inner_empty.winfo_children():
            w.bind("<Enter>", _on_enter)
            w.bind("<Leave>", _on_leave)
        
        # --- FULL STATE (Split View) ---
        self.full_state = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.full_state.grid_columnconfigure((0, 1), weight=1, uniform="split")
        self.full_state.grid_rowconfigure(0, weight=1)
        
        # Left: Original Image
        self.img_container = ctk.CTkFrame(self.full_state, fg_color=BG_BASE, corner_radius=24, border_width=1, border_color=BORDER)
        self.img_container.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.lbl_image = ctk.CTkLabel(self.img_container, text="", fg_color="transparent")
        self.lbl_image.place(relx=0.5, rely=0.5, anchor="center")
        
        # Right: Grid View
        self.grid_container = ctk.CTkFrame(self.full_state, fg_color=BG_BASE, corner_radius=24, border_width=1, border_color=BORDER)
        self.grid_container.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        
        self.plot_frame = tk.Frame(self.grid_container, bg=BG_BASE)
        self.plot_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
        
        # Toolbar for Grid (Floating at bottom center of grid_container)
        self.grid_toolbar = ctk.CTkFrame(self.grid_container, fg_color=BG_SURFACE, corner_radius=16, border_width=1, border_color=BORDER, height=48)
        self.grid_toolbar.place(relx=0.5, rely=0.95, anchor="s")
        
        # Add basic tools: Zoom In, Zoom Out, Fit, Grid Toggle
        tools = [
            ("zoom-in", self._zoom_in),
            ("zoom-out", self._zoom_out),
            ("maximize", self._fit_grid),
            ("grid", self._toggle_grid)
        ]
        
        for icon_name, cmd in tools:
            btn = ctk.CTkButton(self.grid_toolbar, text="", image=get_icon(icon_name, size=18, dark_mode=False),
                                width=40, height=40, fg_color="transparent", hover_color="#F6F7FB", corner_radius=12,
                                command=cmd)
            btn.pack(side="left", padx=4, pady=4)

        self.placeholder = ctk.CTkLabel(self.content_container, text="Pilih formasi dari menu kiri.", 
                                        font=get_font("body"), text_color=TEXT_MUTED)
        self.show_placeholder()

    def _on_trash_click(self):
        if self.app.active_tab:
            self.app.handle_remove(self.app.active_tab)

    def show_placeholder(self):
        self.lbl_title.configure(text="Workspace")
        self.btn_delete.pack_forget()
        self.empty_state.grid_forget()
        self.full_state.grid_forget()
        self.placeholder.place(relx=0.5, rely=0.5, anchor="center")

    def show_empty_state(self, index):
        self.lbl_title.configure(text=f"Formasi {index:02d}")
        self.btn_delete.pack_forget()
        try: self.placeholder.place_forget()
        except: pass
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.full_state.grid(row=0, column=0, sticky="nsew")
        self.empty_state.tkraise()

    def show_full_state(self, index):
        self.lbl_title.configure(text=f"Formasi {index:02d}")
        self.btn_delete.pack(side="left", padx=(20, 0))
        try: self.placeholder.place_forget()
        except: pass
        self.empty_state.grid(row=0, column=0, sticky="nsew")
        self.full_state.grid(row=0, column=0, sticky="nsew")
        
        # Add opaque background to hide empty_state underneath
        self.full_state.configure(fg_color=BG_SURFACE)
        self.full_state.tkraise()

    def set_image(self, ctk_img):
        self.lbl_image.configure(image=ctk_img, text="")
        
    def clear_plot(self):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()
            
    def attach_canvas(self, tk_widget):
        tk_widget.pack(fill="both", expand=True)
        if hasattr(self.app, "register_drop_targets"):
            self.app.register_drop_targets(tk_widget)

    def drop_target_widgets(self):
        return [
            self,
            self.content_container,
            self.empty_state,
            self.drop_zone,
            self.inner_empty,
            self.lbl_upload_icon,
            self.lbl_upload_title,
            self.lbl_upload_subtitle,
            self.full_state,
            self.img_container,
            self.lbl_image,
            self.grid_container,
            self.plot_frame,
        ]

    def _pointer_in_drop_zone(self):
        try:
            x, y = self.winfo_pointerxy()
            wx, wy = self.drop_zone.winfo_rootx(), self.drop_zone.winfo_rooty()
            ww, wh = self.drop_zone.winfo_width(), self.drop_zone.winfo_height()
            return wx <= x <= wx + ww and wy <= y <= wy + wh
        except Exception:
            return False

    def _check_drop_zone_leave(self):
        if self._pointer_in_drop_zone():
            return
        self._drop_zone_hovered = False
        self._drop_zone_target_rely = self._drop_zone_base_rely
        self._animate_drop_zone_lift()
        animate_widget_color(self.drop_zone, "fg_color", "#F0F1F5", BG_BASE, steps=10)

    def _animate_drop_zone_lift(self):
        if self._drop_zone_anim_job:
            self.after_cancel(self._drop_zone_anim_job)

        dist = self._drop_zone_target_rely - self._drop_zone_current_rely
        if abs(dist) > 0.0005:
            self._drop_zone_current_rely += dist * 0.22
            self.drop_zone.place_configure(rely=self._drop_zone_current_rely)
            self._drop_zone_anim_job = self.after(16, self._animate_drop_zone_lift)
        else:
            self._drop_zone_current_rely = self._drop_zone_target_rely
            self.drop_zone.place_configure(rely=self._drop_zone_current_rely)

    # Basic tool functions that defer to app
    def _zoom_in(self):
        if hasattr(self.app, 'zoom_grid'): self.app.zoom_grid(0.8)
    def _zoom_out(self):
        if hasattr(self.app, 'zoom_grid'): self.app.zoom_grid(1.2)
    def _fit_grid(self):
        if hasattr(self.app, 'fit_grid'): self.app.fit_grid()
    def _toggle_grid(self):
        if hasattr(self.app, 'toggle_grid_lines'): self.app.toggle_grid_lines()
