import customtkinter as ctk
import tkinter as tk
from ..components.cards import MetricCard
from ..theme import BG_BASE, BG_SURFACE, PRIMARY, PRIMARY_HOVER, TEXT_MUTED, TEXT_PRIMARY, get_icon
from core.constants import N_FORMATIONS
from ..utils import animate_widget_color, animate_grid_pady
class Dashboard(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, **kwargs):
        super().__init__(master, fg_color=BG_BASE, bg_color=BG_BASE, corner_radius=0, **kwargs)
        self.app = app_controller
        self.animating_scroll = False
        self.target_y = 0.0
        self.current_y = 0.0
        
        self.grid_columnconfigure(0, weight=1)
        
        self._build_topbar()
        self._build_metrics()
        # Tabs are removed in favor of sidebar navigation! 
        self._build_content_area()
        self._build_export_area()

    def _build_topbar(self):
        topbar = ctk.CTkFrame(self, fg_color="transparent", height=60)
        topbar.grid(row=0, column=0, sticky="ew", padx=40, pady=(40, 0))
        
        # We will use this to show the current selected formation
        self.lbl_title = ctk.CTkLabel(topbar, text="Pilih Formasi di Menu Kiri", font=("Helvetica", 28, "bold"), text_color=TEXT_PRIMARY)
        self.lbl_title.pack(side="left")
        
        # Process Button moved here for prominence
        icon_play = get_icon("play", size=18, dark_mode=True)
        self.btn_process_all = ctk.CTkButton(topbar, text="Proses Semua", image=icon_play, 
                                         font=("Helvetica", 14, "bold"), height=48, corner_radius=24,
                                         fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
                                         command=self.app.process_all)
        self.btn_process_all.pack(side="right")

    def _build_metrics(self):
        metrics = ctk.CTkFrame(self, fg_color="transparent")
        metrics.grid(row=1, column=0, sticky="ew", padx=40, pady=(32, 32))
        metrics.columnconfigure((0, 1, 2), weight=1, uniform="m")
        
        self.card_formations = MetricCard(metrics, "Formasi Diproses", "0 / 10")
        self.card_formations.grid(row=0, column=0, sticky="ew", padx=(0, 24))
        
        self.card_participants = MetricCard(metrics, "Total Peserta", "3,600")
        self.card_participants.grid(row=0, column=1, sticky="ew", padx=(0, 24))
        
        self.card_grid = MetricCard(metrics, "Ukuran Grid", "60 x 60")
        self.card_grid.grid(row=0, column=2, sticky="ew")

    def _build_content_area(self):
        # Huge card for the main content
        self.content = ctk.CTkFrame(self, fg_color=BG_SURFACE, corner_radius=24)
        self.content.grid(row=2, column=0, sticky="nsew", padx=40, pady=(10, 30))
        self.content.columnconfigure((0, 1), weight=1, uniform="c")
        
        # Lift hover effect for main content
        self._content_hovered = False
        def _content_on_enter(e):
            if not self._content_hovered:
                self._content_hovered = True
                animate_grid_pady(self.content, 10, 30, 8, direction="up")
                
        def _content_on_leave(e):
            x, y = self.winfo_pointerxy()
            wx, wy = self.content.winfo_rootx(), self.content.winfo_rooty()
            ww, wh = self.content.winfo_width(), self.content.winfo_height()
            if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
                if self._content_hovered:
                    self._content_hovered = False
                    animate_grid_pady(self.content, 10, 30, 8, direction="down")
                    
        self.content.bind("<Enter>", _content_on_enter)
        self.content.bind("<Leave>", _content_on_leave)
        
        # --- EMPTY STATE (Drag & Drop Zone) ---
        self.empty_state_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        # We don't pack it yet
        
        # Dashed-like box simulation via slightly darker bg and border
        self.drop_zone = ctk.CTkFrame(self.empty_state_frame, fg_color="#F4F7FE", 
                                       border_width=2, border_color="#E9EDF7", corner_radius=24, height=400)
        self.drop_zone.pack(fill="both", expand=True, padx=40, pady=40)
        self.drop_zone.pack_propagate(False)
        
        # Center content using pack inside the frame
        inner_empty = ctk.CTkFrame(self.drop_zone, fg_color="transparent")
        inner_empty.place(relx=0.5, rely=0.5, anchor="center")
        icon_up = get_icon("upload", size=48)
        
        lbl_icon = ctk.CTkLabel(inner_empty, text="", image=icon_up)
        if icon_up: lbl_icon.pack(pady=(0, 16))
        
        lbl_title = ctk.CTkLabel(inner_empty, text="Klik di sini untuk memilih gambar", font=("Helvetica", 18, "bold"), text_color=TEXT_PRIMARY)
        lbl_title.pack()
        
        lbl_subtitle = ctk.CTkLabel(inner_empty, text="atau Drag & Drop file ke dalam aplikasi", font=("Helvetica", 14), text_color=TEXT_MUTED)
        lbl_subtitle.pack(pady=(8, 0))
        
        # Bind clicks to everything in the drop zone
        def _trigger_click(e):
            self._on_dropzone_click()
            return "break"
            
        self.drop_zone.bind("<Button-1>", _trigger_click)
        inner_empty.bind("<Button-1>", _trigger_click)
        lbl_icon.bind("<Button-1>", _trigger_click)
        lbl_title.bind("<Button-1>", _trigger_click)
        lbl_subtitle.bind("<Button-1>", _trigger_click)
        
        # Add smooth hover effect
        def _on_enter(e):
            animate_widget_color(self.drop_zone, "fg_color", "#F4F7FE", "#E9EDF7", steps=10)
        def _on_leave(e):
            animate_widget_color(self.drop_zone, "fg_color", "#E9EDF7", "#F4F7FE", steps=10)
            
        self.drop_zone.bind("<Enter>", _on_enter)
        self.drop_zone.bind("<Leave>", _on_leave)
        
        # --- FULL STATE ---
        self.full_state_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        self.full_state_frame.columnconfigure((0, 1), weight=1, uniform="c")
        
        left = ctk.CTkFrame(self.full_state_frame, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=32, pady=32)
        left.columnconfigure(0, weight=1)
        
        # Top actions (Trash)
        actions = ctk.CTkFrame(left, fg_color="transparent")
        actions.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        
        self.btn_trash = ctk.CTkButton(actions, text="Hapus Formasi", image=get_icon("trash-2", size=16), 
                                       fg_color="#FEF2F2", hover_color="#FEE2E2", text_color="#DC2626", 
                                       font=("Helvetica", 13, "bold"), corner_radius=12, height=36,
                                       command=self._on_trash_click)
        self.btn_trash.pack(side="left")
        
        # Image
        self.lbl_image = ctk.CTkLabel(left, text="", fg_color="#F8FAFC", corner_radius=16, height=300)
        self.lbl_image.grid(row=1, column=0, sticky="ew", pady=(0, 32))
        
        # Distribution
        self.dist_frame = ctk.CTkFrame(left, fg_color="transparent")
        self.dist_frame.grid(row=2, column=0, sticky="ew")
        
        # Right (Plot)
        self.plot_frame = tk.Frame(self.full_state_frame, bg=BG_SURFACE)
        self.plot_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 32), pady=32)
        
        # Show initial placeholder
        self.placeholder_lbl = ctk.CTkLabel(self.content, text="Pilih slot formasi (F01-F10) di menu kiri untuk mulai.", 
                                            font=("Helvetica", 16), text_color=TEXT_MUTED, height=400)
        self.placeholder_lbl.grid(row=0, column=0, columnspan=2, pady=40)

    def _build_export_area(self):
        export = ctk.CTkFrame(self, fg_color=BG_SURFACE, corner_radius=24)
        export.grid(row=3, column=0, sticky="ew", padx=40, pady=(10, 30))
        
        self._export_hovered = False
        def _export_on_enter(e):
            if not self._export_hovered:
                self._export_hovered = True
                animate_grid_pady(export, 10, 30, 8, direction="up")
                
        def _export_on_leave(e):
            x, y = self.winfo_pointerxy()
            wx, wy = export.winfo_rootx(), export.winfo_rooty()
            ww, wh = export.winfo_width(), export.winfo_height()
            if not (wx <= x <= wx + ww and wy <= y <= wy + wh):
                if self._export_hovered:
                    self._export_hovered = False
                    animate_grid_pady(export, 10, 30, 8, direction="down")
                    
        export.bind("<Enter>", _export_on_enter)
        export.bind("<Leave>", _export_on_leave)
        
        info = ctk.CTkFrame(export, fg_color="transparent")
        info.pack(side="left", padx=32, pady=32)
        
        ctk.CTkLabel(info, text="Export Data Excel", font=("Helvetica", 18, "bold"), text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(info, text="Generate file Excel berisi koordinat, warna, posisi, dan komando.", 
                     font=("Helvetica", 14), text_color=TEXT_MUTED).pack(anchor="w", pady=(8, 0))
                     
        actions = ctk.CTkFrame(export, fg_color="transparent")
        actions.pack(side="right", padx=32, pady=32)
        
        self.btn_gen_excel = ctk.CTkButton(actions, text="Generate Excel", image=get_icon("file-spreadsheet", size=18),
                                           fg_color="#F8FAFC", hover_color="#F1F5F9", text_color=TEXT_PRIMARY,
                                           font=("Helvetica", 14, "bold"), corner_radius=16, height=48,
                                           command=self.app.generate_excel, state="disabled")
        self.btn_gen_excel.pack(side="left", padx=(0, 16))
        
        self.btn_dl_excel = ctk.CTkButton(actions, text="Unduh File", image=get_icon("download", size=18, dark_mode=True),
                                          fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#FFFFFF",
                                          font=("Helvetica", 14, "bold"), corner_radius=16, height=48,
                                          command=self.app.download_excel, state="disabled")
        self.btn_dl_excel.pack(side="left")

    def _on_dropzone_click(self):
        if self.app.active_tab:
            self.app.open_manual_upload_dialog()

    def _on_trash_click(self):
        if self.app.active_tab:
            self.app.handle_remove(self.app.active_tab)
    def _mouse_wheel_all(self, event):
        import sys
        if self._check_if_valid_scroll(event.widget):
            if not self._shift_pressed and self._parent_canvas.yview() != (0.0, 1.0):
                if sys.platform.startswith("win"):
                    delta = int(event.delta / 120)
                elif sys.platform == "darwin":
                    delta = int(event.delta)
                else:
                    delta = 1 if event.num == 4 else -1
                
                y1, y2 = self._parent_canvas.yview()
                if not self.animating_scroll:
                    self.current_y = y1
                    self.target_y = y1
                    
                self.target_y -= delta * 0.05
                self.target_y = max(0.0, min(1.0, self.target_y))
                
                if not self.animating_scroll:
                    self.animating_scroll = True
                    self._do_smooth_scroll()
                    
    def _do_smooth_scroll(self):
        dist = self.target_y - self.current_y
        if abs(dist) > 0.001:
            self.current_y += dist * 0.2
            self._parent_canvas.yview_moveto(self.current_y)
            self.after(16, self._do_smooth_scroll)
        else:
            self._parent_canvas.yview_moveto(self.target_y)
            self.animating_scroll = False
    def update_metrics(self, processed_count):
        self.card_formations.set_value(f"{processed_count} / {N_FORMATIONS}")

    def show_placeholder(self):
        self.lbl_title.configure(text="Dashboard")
        self.empty_state_frame.grid_forget()
        self.full_state_frame.grid_forget()
        self.placeholder_lbl.grid(row=0, column=0, columnspan=2, pady=40)

    def show_empty_state(self, index):
        self.lbl_title.configure(text=f"Formasi {index:02d}")
        self.placeholder_lbl.grid_forget()
        self.full_state_frame.grid_forget()
        self.empty_state_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def show_full_state(self, index):
        self.lbl_title.configure(text=f"Formasi {index:02d}")
        self.placeholder_lbl.grid_forget()
        self.empty_state_frame.grid_forget()
        self.full_state_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")
