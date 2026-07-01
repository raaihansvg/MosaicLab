import customtkinter as ctk
from ..components.kartu import KartuMetrik, TombolAnimasi
from ..tema import LATAR_DASAR, WARNA_UTAMA, WARNA_UTAMA_HOVER, TEKS_REDUP, TEKS_UTAMA, GARIS_TEPI, ambil_font, ambil_ikon
from core.konstanta import JUMLAH_FORMASI, DEFINISI_WARNA


class PanelInspeksi(ctk.CTkScrollableFrame):
    def __init__(self, induk, kontrolerAplikasi, **kwargs):
        super().__init__(induk, fg_color=LATAR_DASAR, bg_color=LATAR_DASAR, corner_radius=0, width=320, **kwargs)
        self.app = kontrolerAplikasi

        self.grid_columnconfigure(0, weight=1)

        self._bangun_header()
        self._bangun_metrik()
        self._bangun_area_distribusi()
        self._bangun_area_ekspor()

    def _bangun_header(self):
        frameHeader = ctk.CTkFrame(self, fg_color="transparent")
        frameHeader.grid(row=0, column=0, sticky="ew", padx=24, pady=(32, 16))

        self.labelJudul = ctk.CTkLabel(frameHeader, text="Informasi", font=ambil_font("section_title"), text_color=TEKS_UTAMA)
        self.labelJudul.pack(anchor="w")

    def _bangun_metrik(self):
        self.frameMetrik = ctk.CTkFrame(self, fg_color="transparent")
        self.frameMetrik.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 24))
        self.frameMetrik.columnconfigure(0, weight=1)

        self.kartuProgress = KartuMetrik(self.frameMetrik, "Progress", "0 / 10")
        self.kartuProgress.grid(row=0, column=0, sticky="ew", pady=(0, 16))

        self.kartuPeserta = KartuMetrik(self.frameMetrik, "Peserta", "3.600")
        self.kartuPeserta.grid(row=1, column=0, sticky="ew", pady=(0, 16))

        self.kartuGrid = KartuMetrik(self.frameMetrik, "Ukuran Grid", "60 x 60")
        self.kartuGrid.grid(row=2, column=0, sticky="ew")

    def _bangun_area_distribusi(self):
        self.frameDistribusi = ctk.CTkFrame(self, fg_color="transparent")
        self.frameDistribusi.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))

        ctk.CTkLabel(self.frameDistribusi, text="Distribusi Warna", font=ambil_font("card_title"), text_color=TEKS_REDUP).pack(anchor="w", pady=(0, 12))

        self.frameIsiDistribusi = ctk.CTkFrame(self.frameDistribusi, fg_color="transparent")
        self.frameIsiDistribusi.pack(fill="x")

        self.labelPlaceholder = ctk.CTkLabel(
            self.frameIsiDistribusi,
            text="Belum ada data.\nProses gambar terlebih dahulu.",
            font=ambil_font("body"), text_color=TEKS_REDUP, justify="left"
        )
        self.labelPlaceholder.pack(anchor="w", pady=16)

    def _bangun_area_ekspor(self):
        self.frameEkspor = ctk.CTkFrame(self, fg_color="transparent")
        self.frameEkspor.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 32))

        ctk.CTkLabel(self.frameEkspor, text="Aksi", font=ambil_font("card_title"), text_color=TEKS_REDUP).pack(anchor="w", pady=(0, 12))

        self.tombolGenerateData = TombolAnimasi(
            self.frameEkspor, teks="Generate Data",
            gambar=ambil_ikon("file-spreadsheet", ukuran=18, mode_gelap=True),
            warnaTombol="transparent", lebarTepi=1, warnaTepi=GARIS_TEPI,
            warnaHover="#EAECEF", warnaTeks=TEKS_UTAMA,
            font=ambil_font("body"), radiusSudut=12, tinggi=44,
            perintah=self.app.generate_excel, kondisi="disabled"
        )
        self.tombolGenerateData.pack(fill="x", pady=(0, 12))

        self.tombolUnduhExcel = TombolAnimasi(
            self.frameEkspor, teks="Unduh Excel",
            gambar=ambil_ikon("download", ukuran=18, mode_gelap=True),
            warnaTombol=WARNA_UTAMA, warnaHover=WARNA_UTAMA_HOVER, warnaTeks="#FFFFFF",
            font=ambil_font("body"), radiusSudut=12, tinggi=44,
            perintah=self.app.unduh_excel, kondisi="disabled"
        )
        self.tombolUnduhExcel.pack(fill="x")

    def perbarui_metrik(self, jumlahSelesai):
        self.kartuProgress.set_nilai(f"{jumlahSelesai} / {JUMLAH_FORMASI}")

    def render_distribusi(self, data):
        for widget in self.frameIsiDistribusi.winfo_children():
            widget.destroy()

        if not data:
            self.labelPlaceholder = ctk.CTkLabel(
                self.frameIsiDistribusi,
                text="Belum ada data.\nProses gambar terlebih dahulu.",
                font=ambil_font("body"), text_color=TEKS_REDUP, justify="left"
            )
            self.labelPlaceholder.pack(anchor="w", pady=16)
            return

        totalPiksel = sum(data["distribusi"].values())
        if totalPiksel == 0:
            totalPiksel = 1

        for kunciWarna, defWarna in DEFINISI_WARNA.items():
            jumlah = data["distribusi"].get(kunciWarna, 0)
            persentase = (jumlah / totalPiksel) * 100

            baris = ctk.CTkFrame(self.frameIsiDistribusi, fg_color="transparent")
            baris.pack(fill="x", pady=8)

            ctk.CTkLabel(baris, text=defWarna["label"], font=ambil_font("caption"), text_color=TEKS_UTAMA, width=60, anchor="w").pack(side="left")
            ctk.CTkLabel(baris, text=f"{jumlah}", font=ambil_font("caption"), text_color=TEKS_REDUP).pack(side="right")

            latarBar = ctk.CTkFrame(baris, fg_color=LATAR_DASAR, border_width=1, border_color=GARIS_TEPI, height=12, corner_radius=6)
            latarBar.pack(side="left", fill="x", expand=True, padx=12)

            if jumlah > 0:
                isiBar = ctk.CTkFrame(latarBar, fg_color=defWarna["hex"], height=12, corner_radius=6)
                if defWarna["hex"].upper() in ["#FFFFFF", "#FFD700"]:
                    isiBar.configure(border_width=1, border_color="#EAECEF")
                isiBar.place(relx=0, rely=0, relwidth=max(0.02, persentase / 100), relheight=1.0)
