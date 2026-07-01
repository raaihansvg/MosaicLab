import customtkinter as ctk
import tkinter as tk
from ..tema import LATAR_PERMUKAAN, LATAR_DASAR, WARNA_UTAMA, WARNA_UTAMA_HOVER, TEKS_REDUP, TEKS_UTAMA, GARIS_TEPI, ambil_font, ambil_ikon
from ..utilitas import animasi_warna_widget
from ..components.kartu import TombolAnimasi


class AreaKanvas(ctk.CTkFrame):
    def __init__(self, induk, kontrolerAplikasi, **kwargs):
        super().__init__(induk, fg_color=LATAR_PERMUKAAN, corner_radius=0, **kwargs)
        self.app = kontrolerAplikasi

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._bangun_topbar()
        self._bangun_area_konten()

    def _bangun_topbar(self):
        self.frameTopbar = ctk.CTkFrame(self, fg_color="transparent", height=72)
        self.frameTopbar.grid(row=0, column=0, sticky="ew", padx=40, pady=(32, 0))

        self.labelJudul = ctk.CTkLabel(self.frameTopbar, text="Workspace", font=ambil_font("page_title"), text_color=TEKS_UTAMA)
        self.labelJudul.pack(side="left")

        self.frameAksi = ctk.CTkFrame(self.frameTopbar, fg_color="transparent")
        self.frameAksi.pack(side="right")

        self.tombolGenerate = TombolAnimasi(
            self.frameAksi, teks="Generate", gambar=ambil_ikon("play", ukuran=16, mode_gelap=True),
            warnaTombol=WARNA_UTAMA, warnaHover=WARNA_UTAMA_HOVER, warnaTeks="#FFFFFF",
            font=ambil_font("body"), radiusSudut=12, tinggi=44, width=140,
            perintah=self.app.proses_semua
        )
        self.tombolGenerate.pack(side="left")

        self.tombolHapus = TombolAnimasi(
            self.frameAksi, teks="Hapus", gambar=ambil_ikon("trash-2", ukuran=16),
            warnaTombol="transparent", warnaHover="#FFECEB", warnaTeks="#FF3B30",
            font=ambil_font("body"), radiusSudut=12, tinggi=44, width=100,
            perintah=self._saat_hapus_klik
        )
        self.tombolHapus.pack(side="left", padx=(20, 0))
        self.tombolHapus.pack_forget()

    def _bangun_area_konten(self):
        self.frameKontainer = ctk.CTkFrame(self, fg_color="transparent")
        self.frameKontainer.grid(row=1, column=0, sticky="nsew", padx=40, pady=(24, 40))
        self.frameKontainer.grid_columnconfigure(0, weight=1)
        self.frameKontainer.grid_rowconfigure(0, weight=1)

        self.frameKosong = ctk.CTkFrame(self.frameKontainer, fg_color="transparent")

        self._zonaUploadRelyDasar = 0.5
        self._zonaUploadRelyTarget = self._zonaUploadRelyDasar
        self._zonaUploadRelySaat = self._zonaUploadRelyDasar
        self._zonaUploadHover = False
        self._jobAnimasiZonaUpload = None

        self.zonaUpload = ctk.CTkFrame(
            self.frameKosong, fg_color=LATAR_DASAR,
            corner_radius=24, border_width=1, border_color=GARIS_TEPI
        )
        self.zonaUpload.place(relx=0.5, rely=self._zonaUploadRelyDasar, anchor="center", relwidth=0.8, relheight=0.6)

        self.frameIsiKosong = ctk.CTkFrame(self.zonaUpload, fg_color="transparent")
        self.frameIsiKosong.place(relx=0.5, rely=0.5, anchor="center")

        ikonUpload = ambil_ikon("upload", ukuran=48)
        self.labelIkonUpload = ctk.CTkLabel(self.frameIsiKosong, text="", image=ikonUpload)
        if ikonUpload:
            self.labelIkonUpload.pack(pady=(0, 24))

        self.labelUploadJudul = ctk.CTkLabel(self.frameIsiKosong, text="Klik untuk memilih gambar", font=ambil_font("section_title"), text_color=TEKS_UTAMA)
        self.labelUploadJudul.pack()
        self.labelUploadSubjudul = ctk.CTkLabel(self.frameIsiKosong, text="atau Drag & Drop file ke sini", font=ambil_font("body"), text_color=TEKS_REDUP)
        self.labelUploadSubjudul.pack(pady=(8, 0))

        def _saat_klik(e):
            if self.app.tabAktif:
                self.app.buka_dialog_upload_manual()
            return "break"

        semuaWidget = [self.zonaUpload, self.frameIsiKosong, self.labelIkonUpload] + self.frameIsiKosong.winfo_children()
        for w in semuaWidget:
            w.bind("<Button-1>", _saat_klik)

        def _saat_masuk_zona(e):
            if self._zonaUploadHover:
                return
            self._zonaUploadHover = True
            self._zonaUploadRelyTarget = 0.485
            self._animasi_angkat_zona_upload()
            animasi_warna_widget(self.zonaUpload, "fg_color", LATAR_DASAR, "#F0F1F5", langkah=10)

        def _saat_keluar_zona(e):
            self.after(10, self._cek_keluar_zona_upload)

        for w in semuaWidget:
            w.bind("<Enter>", _saat_masuk_zona)
            w.bind("<Leave>", _saat_keluar_zona)

        self.frameTerisi = ctk.CTkFrame(self.frameKontainer, fg_color="transparent")
        self.frameTerisi.grid_columnconfigure((0, 1), weight=1, uniform="split")
        self.frameTerisi.grid_rowconfigure(0, weight=1)

        self.frameGambarAsli = ctk.CTkFrame(self.frameTerisi, fg_color=LATAR_DASAR, corner_radius=24, border_width=1, border_color=GARIS_TEPI)
        self.frameGambarAsli.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.labelGambar = ctk.CTkLabel(self.frameGambarAsli, text="", fg_color="transparent")
        self.labelGambar.place(relx=0.5, rely=0.5, anchor="center")

        self.frameGridHasil = ctk.CTkFrame(self.frameTerisi, fg_color=LATAR_DASAR, corner_radius=24, border_width=1, border_color=GARIS_TEPI)
        self.frameGridHasil.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self.framePlot = tk.Frame(self.frameGridHasil, bg=LATAR_DASAR)
        self.framePlot.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

        self.frameToolbar = ctk.CTkFrame(
            self.frameGridHasil, fg_color=LATAR_PERMUKAAN,
            corner_radius=16, border_width=1, border_color=GARIS_TEPI, height=48
        )
        self.frameToolbar.place(relx=0.5, rely=0.95, anchor="s")

        daftarAlat = [
            ("zoom-in", self._zoom_masuk),
            ("zoom-out", self._zoom_keluar),
            ("maximize", self._pas_grid),
            ("grid", self._toggle_grid)
        ]

        for namaIkon, perintah in daftarAlat:
            tombol = ctk.CTkButton(
                self.frameToolbar, text="", image=ambil_ikon(namaIkon, ukuran=18, mode_gelap=False),
                width=40, height=40, fg_color="transparent", hover_color="#F6F7FB", corner_radius=12,
                command=perintah
            )
            tombol.pack(side="left", padx=4, pady=4)

        self.labelPlaceholder = ctk.CTkLabel(
            self.frameKontainer, text="Pilih formasi dari menu kiri.",
            font=ambil_font("body"), text_color=TEKS_REDUP
        )
        self.tampilkan_placeholder()

    def _saat_hapus_klik(self):
        if self.app.tabAktif:
            self.app.tangani_hapus(self.app.tabAktif)

    def tampilkan_placeholder(self):
        self.labelJudul.configure(text="Workspace")
        self.tombolHapus.pack_forget()
        self.frameKosong.grid_forget()
        self.frameTerisi.grid_forget()
        self.labelPlaceholder.place(relx=0.5, rely=0.5, anchor="center")

    def tampilkan_state_kosong(self, indeks):
        self.labelJudul.configure(text=f"Formasi {indeks:02d}")
        self.tombolHapus.pack_forget()
        try:
            self.labelPlaceholder.place_forget()
        except Exception:
            pass
        self.frameKosong.grid(row=0, column=0, sticky="nsew")
        self.frameTerisi.grid(row=0, column=0, sticky="nsew")
        self.frameKosong.tkraise()

    def tampilkan_state_terisi(self, indeks):
        self.labelJudul.configure(text=f"Formasi {indeks:02d}")
        self.tombolHapus.pack(side="left", padx=(20, 0))
        try:
            self.labelPlaceholder.place_forget()
        except Exception:
            pass
        self.frameKosong.grid(row=0, column=0, sticky="nsew")
        self.frameTerisi.grid(row=0, column=0, sticky="nsew")
        
        # Add opaque background to frameTerisi so it hides frameKosong underneath
        self.frameTerisi.configure(fg_color=LATAR_PERMUKAAN)
        self.frameTerisi.tkraise()

    def set_gambar(self, gambarCtk):
        self.labelGambar.configure(image=gambarCtk, text="")

    def bersihkan_plot(self):
        for widget in self.framePlot.winfo_children():
            widget.destroy()

    def pasang_kanvas_plot(self, widgetTk):
        widgetTk.pack(fill="both", expand=True)
        if hasattr(self.app, "daftarkan_target_drop"):
            self.app.daftarkan_target_drop(widgetTk)

    def ambil_target_drop(self):
        return [
            self,
            self.frameKontainer,
            self.frameKosong,
            self.zonaUpload,
            self.frameIsiKosong,
            self.labelIkonUpload,
            self.labelUploadJudul,
            self.labelUploadSubjudul,
            self.frameTerisi,
            self.frameGambarAsli,
            self.labelGambar,
            self.frameGridHasil,
            self.framePlot,
        ]

    def _pointer_di_zona_upload(self):
        try:
            x, y = self.winfo_pointerxy()
            wx, wy = self.zonaUpload.winfo_rootx(), self.zonaUpload.winfo_rooty()
            ww, wh = self.zonaUpload.winfo_width(), self.zonaUpload.winfo_height()
            return wx <= x <= wx + ww and wy <= y <= wy + wh
        except Exception:
            return False

    def _cek_keluar_zona_upload(self):
        if self._pointer_di_zona_upload():
            return
        self._zonaUploadHover = False
        self._zonaUploadRelyTarget = self._zonaUploadRelyDasar
        self._animasi_angkat_zona_upload()
        animasi_warna_widget(self.zonaUpload, "fg_color", "#F0F1F5", LATAR_DASAR, langkah=10)

    def _animasi_angkat_zona_upload(self):
        if self._jobAnimasiZonaUpload:
            self.after_cancel(self._jobAnimasiZonaUpload)

        jarak = self._zonaUploadRelyTarget - self._zonaUploadRelySaat
        if abs(jarak) > 0.0005:
            self._zonaUploadRelySaat += jarak * 0.22
            self.zonaUpload.place_configure(rely=self._zonaUploadRelySaat)
            self._jobAnimasiZonaUpload = self.after(16, self._animasi_angkat_zona_upload)
        else:
            self._zonaUploadRelySaat = self._zonaUploadRelyTarget
            self.zonaUpload.place_configure(rely=self._zonaUploadRelySaat)

    def _zoom_masuk(self):
        if hasattr(self.app, 'zoom_grid'):
            self.app.zoom_grid(0.8)

    def _zoom_keluar(self):
        if hasattr(self.app, 'zoom_grid'):
            self.app.zoom_grid(1.2)

    def _pas_grid(self):
        if hasattr(self.app, 'pas_grid'):
            self.app.pas_grid()

    def _toggle_grid(self):
        if hasattr(self.app, 'toggle_garis_grid'):
            self.app.toggle_garis_grid()
