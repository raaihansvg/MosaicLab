import customtkinter as ctk
from ..components.cards import MetricCard, AnimatedButton
from ..theme import BG_BASE, PRIMARY, PRIMARY_HOVER, TEXT_MUTED, TEXT_PRIMARY, BORDER, get_font, get_icon
from core.constants import N_FORMATIONS, WARNA_DEFINISI

class Inspector(ctk.CTkScrollableFrame):
    def __init__(self, master, app_controller, **kwargs):
        # The inspector sits on the right, light background
        super().__init__(master, fg_color=BG_BASE, bg_color=BG_BASE, corner_radius=0, width=320, **kwargs)
        self.app = app_controller
        
        self.grid_columnconfigure(0, weight=1)
        
        self._build_header()
        self._build_metrics()
        self._build_distribution_area()
        self._build_export_area()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, sticky="ew", padx=24, pady=(32, 16))
        
        self.lbl_title = ctk.CTkLabel(hdr, text="Information", font=get_font("section_title"), text_color=TEXT_PRIMARY)
        self.lbl_title.pack(anchor="w")

    def _build_metrics(self):
        self.metrics = ctk.CTkFrame(self, fg_color="transparent")
        self.metrics.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 24))
        self.metrics.columnconfigure(0, weight=1)
        
        self.card_progress = MetricCard(self.metrics, "Progress", "0 / 10")
        self.card_progress.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        
        self.card_participants = MetricCard(self.metrics, "Peserta", "3,600")
        self.card_participants.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        
        self.card_grid = MetricCard(self.metrics, "Grid Size", "60 x 60")
        self.card_grid.grid(row=2, column=0, sticky="ew")

    def _build_distribution_area(self):
        self.dist_container = ctk.CTkFrame(self, fg_color="transparent")
        self.dist_container.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        
        ctk.CTkLabel(self.dist_container, text="Distribusi Warna", font=get_font("card_title"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 12))
        
        # This frame will hold the dynamic distribution bars
        self.dist_frame = ctk.CTkFrame(self.dist_container, fg_color="transparent")
        self.dist_frame.pack(fill="x")
        
        self.placeholder_lbl = ctk.CTkLabel(self.dist_frame, text="Belum ada data.\nProses gambar terlebih dahulu.", 
                                            font=get_font("body"), text_color=TEXT_MUTED, justify="left")
        self.placeholder_lbl.pack(anchor="w", pady=16)

    def _build_export_area(self):
        self.export = ctk.CTkFrame(self, fg_color="transparent")
        self.export.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 32))
        
        ctk.CTkLabel(self.export, text="Aksi", font=get_font("card_title"), text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 12))
        
        # Ghost button for Generate Excel
        self.btn_gen_excel = AnimatedButton(self.export, text="Generate Data", image=get_icon("file-spreadsheet", size=18, dark_mode=True),
                                            fg_color="transparent", border_width=1, border_color=BORDER, hover_color="#EAECEF", text_color=TEXT_PRIMARY,
                                            font=get_font("body"), corner_radius=12, height=44,
                                            command=self.app.generate_excel, state="disabled")
        self.btn_gen_excel.pack(fill="x", pady=(0, 12))
        
        # Primary accent for Download
        self.btn_dl_excel = AnimatedButton(self.export, text="Unduh Excel", image=get_icon("download", size=18, dark_mode=True),
                                           fg_color=PRIMARY, hover_color=PRIMARY_HOVER, text_color="#FFFFFF",
                                           font=get_font("body"), corner_radius=12, height=44,
                                           command=self.app.download_excel, state="disabled")
        self.btn_dl_excel.pack(fill="x")

    def update_metrics(self, processed_count):
        self.card_progress.set_value(f"{processed_count} / {N_FORMATIONS}")

    def render_distribution(self, data):
        for widget in self.dist_frame.winfo_children():
            widget.destroy()
            
        if not data:
            self.placeholder_lbl = ctk.CTkLabel(self.dist_frame, text="Belum ada data.\nProses gambar terlebih dahulu.", 
                                                font=get_font("body"), text_color=TEXT_MUTED, justify="left")
            self.placeholder_lbl.pack(anchor="w", pady=16)
            return

        total = sum(data["distribution"].values())
        if total == 0: total = 1
        
        for wkey, wdef in WARNA_DEFINISI.items():
            count = data["distribution"].get(wkey, 0)
            pct = (count / total) * 100
            
            f = ctk.CTkFrame(self.dist_frame, fg_color="transparent")
            f.pack(fill="x", pady=8)
            
            # Label
            ctk.CTkLabel(f, text=wdef["label"], font=get_font("caption"), text_color=TEXT_PRIMARY, width=60, anchor="w").pack(side="left")
            
            # Count (pack this before the expanding track so it doesn't get pushed off)
            ctk.CTkLabel(f, text=f"{count}", font=get_font("caption"), text_color=TEXT_MUTED).pack(side="right")
            
            # Track
            bar_bg = ctk.CTkFrame(f, fg_color=BG_BASE, border_width=1, border_color=BORDER, height=12, corner_radius=6)
            bar_bg.pack(side="left", fill="x", expand=True, padx=12)
            
            # Fill
            if count > 0:
                bar_fill = ctk.CTkFrame(bar_bg, fg_color=wdef["hex"], height=12, corner_radius=6)
                # Ensure visibility against white/light backgrounds for light colors (like white or yellow)
                if wdef["hex"].upper() in ["#FFFFFF", "#FFFF00"]:
                    bar_fill.configure(border_width=1, border_color="#EAECEF")
                bar_fill.place(relx=0, rely=0, relwidth=max(0.02, pct/100), relheight=1.0)
