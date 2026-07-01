import customtkinter as ctk
from ..tema import LATAR_SIDEBAR, WARNA_UTAMA, TEKS_REDUP, TEKS_UTAMA, ambil_ikon, ambil_font
from core.konstanta import JUMLAH_FORMASI


class Sidebar(ctk.CTkFrame):
    def __init__(self, induk, kontrolerAplikasi, **kwargs):
        super().__init__(induk, fg_color=LATAR_SIDEBAR, corner_radius=0, width=240, **kwargs)
        self.app = kontrolerAplikasi
        self.grid_propagate(False)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._bangun_header()
        self._bangun_slot()

    def _bangun_header(self):
        frameHeader = ctk.CTkFrame(self, fg_color="transparent")
        frameHeader.grid(row=0, column=0, sticky="ew", padx=24, pady=(40, 32))

        ctk.CTkLabel(frameHeader, text="Mozaik", font=ambil_font("section_title"), text_color=TEKS_UTAMA).pack(side="left")

    def _bangun_slot(self):
        frameKontainer = ctk.CTkFrame(self, fg_color="transparent")
        frameKontainer.grid(row=1, column=0, sticky="nsew", padx=16)
        frameKontainer.columnconfigure(0, weight=1)

        ctk.CTkLabel(frameKontainer, text="FORMASI", font=ambil_font("caption"), text_color=TEKS_REDUP, anchor="w").pack(fill="x", padx=12, pady=(0, 12))

        self.frameScroll = ctk.CTkFrame(frameKontainer, fg_color="transparent")
        self.frameScroll.pack(fill="both", expand=True)

        self.daftarSlot = {}
        for i in range(1, JUMLAH_FORMASI + 1):
            slot = SlotMenuFormasi(self.frameScroll, i, self.app)
            slot.pack(fill="x", pady=2)
            self.daftarSlot[i] = slot


class SlotMenuFormasi(ctk.CTkFrame):
    def __init__(self, induk, indeks, aplikasi, **kwargs):
        super().__init__(induk, fg_color="transparent", height=44, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.indeks = indeks
        self.app = aplikasi

        self.ikonKosong = ambil_ikon("circle", ukuran=16)
        self.ikonTerisi = ambil_ikon("image", ukuran=16, mode_gelap=False)
        self.ikonSelesai = ambil_ikon("check-circle-2", ukuran=16, mode_gelap=False)

        self._ikonAktif = self.ikonKosong

        self.indikator = ctk.CTkFrame(self, fg_color="transparent", width=3, corner_radius=1)
        self.indikator.place(relx=0, rely=0.2, relheight=0.6)

        self.relyDasar = 0.0
        self.relyTarget = self.relyDasar
        self.relySaat = self.relyDasar

        self.tombol = ctk.CTkButton(
            self, text=f"Formasi {indeks:02d}", image=self.ikonKosong, compound="left",
            fg_color="transparent", text_color=TEKS_REDUP, hover_color="#EAECEF",
            corner_radius=8, font=ambil_font("body"), anchor="w",
            command=self.saat_klik
        )
        self.tombol.place(relx=0.05, rely=self.relyDasar, relwidth=0.95, relheight=1.0)

        self.sedangAktif = False

        def _saat_masuk(e):
            if not self.sedangAktif:
                self.relyTarget = -0.08
                self._animasi_angkat()

        def _saat_keluar(e):
            self.relyTarget = self.relyDasar
            self._animasi_angkat()

        self.tombol.bind("<Enter>", _saat_masuk)
        self.tombol.bind("<Leave>", _saat_keluar)
        self._jobAnimasi = None

    def _animasi_angkat(self):
        if self._jobAnimasi:
            self.after_cancel(self._jobAnimasi)

        jarak = self.relyTarget - self.relySaat
        if abs(jarak) > 0.001:
            self.relySaat += jarak * 0.25
            self.tombol.place(relx=0.05, rely=self.relySaat, relwidth=0.95, relheight=1.0)
            self._jobAnimasi = self.after(16, self._animasi_angkat)
        else:
            self.relySaat = self.relyTarget
            self.tombol.place(relx=0.05, rely=self.relySaat, relwidth=0.95, relheight=1.0)

    def saat_klik(self):
        self.app.ganti_tab(self.indeks)

    def set_aktif(self, aktif=True):
        self.sedangAktif = aktif
        if aktif:
            self.tombol.configure(fg_color="#EAECEF", text_color=TEKS_UTAMA)
            self.indikator.configure(fg_color=WARNA_UTAMA)
            self.relyTarget = 0.0
            self._animasi_angkat()
        else:
            self.tombol.configure(fg_color="transparent", text_color=TEKS_REDUP)
            self.indikator.configure(fg_color="transparent")
            self.tombol.configure(image=self._ikonAktif)
            self.relyTarget = self.relyDasar
            self._animasi_angkat()

    def set_status(self, status):
        if status == "kosong":
            self._ikonAktif = self.ikonKosong
            if not self.sedangAktif:
                self.tombol.configure(text_color=TEKS_REDUP)
        elif status == "terupload":
            self._ikonAktif = self.ikonTerisi
            if not self.sedangAktif:
                self.tombol.configure(text_color=TEKS_UTAMA)
        elif status == "selesai":
            self._ikonAktif = self.ikonSelesai

        self.tombol.configure(image=self._ikonAktif)
