import customtkinter as ctk
from ..tema import LATAR_PERMUKAAN, TEKS_UTAMA, TEKS_REDUP, ambil_font


class KartuMetrik(ctk.CTkFrame):
    def __init__(self, induk, judul, nilai, **kwargs):
        super().__init__(induk, fg_color="transparent", height=90, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.badanKartu = ctk.CTkFrame(self, fg_color=LATAR_PERMUKAAN, corner_radius=18)
        self.relyDasar = 0.05
        self.relyTarget = self.relyDasar
        self.relySaat = self.relyDasar

        self.badanKartu.place(relx=0, rely=self.relyDasar, relwidth=1.0, relheight=0.95)

        dalamKartu = ctk.CTkFrame(self.badanKartu, fg_color="transparent")
        dalamKartu.pack(fill="both", expand=True, padx=20, pady=16)

        self.labelJudul = ctk.CTkLabel(dalamKartu, text=judul, font=ambil_font("card_title"), text_color=TEKS_REDUP)
        self.labelJudul.pack(anchor="w")

        self.labelNilai = ctk.CTkLabel(dalamKartu, text=nilai, font=ambil_font("primary_number"), text_color=TEKS_UTAMA)
        self.labelNilai.pack(anchor="w", pady=(4, 0))

        def _saat_masuk(e):
            self.relyTarget = 0.0
            self._animasi_angkat()

        def _saat_keluar(e):
            self.relyTarget = self.relyDasar
            self._animasi_angkat()

        self.badanKartu.bind("<Enter>", _saat_masuk)
        self.badanKartu.bind("<Leave>", _saat_keluar)
        dalamKartu.bind("<Enter>", _saat_masuk)
        self.labelJudul.bind("<Enter>", _saat_masuk)
        self.labelNilai.bind("<Enter>", _saat_masuk)

        self._jobAnimasi = None

    def _animasi_angkat(self):
        if self._jobAnimasi:
            self.after_cancel(self._jobAnimasi)

        jarak = self.relyTarget - self.relySaat
        if abs(jarak) > 0.001:
            self.relySaat += jarak * 0.2
            self.badanKartu.place(relx=0, rely=self.relySaat, relwidth=1.0, relheight=0.95)
            self._jobAnimasi = self.after(16, self._animasi_angkat)
        else:
            self.relySaat = self.relyTarget
            self.badanKartu.place(relx=0, rely=self.relySaat, relwidth=1.0, relheight=0.95)

    def set_nilai(self, nilai):
        self.labelNilai.configure(text=nilai)


class TombolAnimasi(ctk.CTkFrame):
    def __init__(self, induk, teks, gambar=None, warnaTombol=None, warnaHover=None, warnaTeks=None,
                 lebarTepi=0, warnaTepi=None, perintah=None, tinggi=44, radiusSudut=12, font=None, kondisi="normal", **kwargs):
        super().__init__(induk, fg_color="transparent", height=tinggi + 4, **kwargs)
        self.pack_propagate(False)
        self.grid_propagate(False)

        self.posisiYDasar = 4
        self.posisiYTarget = self.posisiYDasar
        self.posisiYSaat = self.posisiYDasar

        self.tombol = ctk.CTkButton(
            self, text=teks, image=gambar,
            fg_color=warnaTombol, hover_color=warnaHover, text_color=warnaTeks,
            border_width=lebarTepi, border_color=warnaTepi, command=perintah,
            corner_radius=radiusSudut, height=tinggi, font=font, state=kondisi
        )
        self.tombol.place(relx=0, y=self.posisiYDasar, relwidth=1.0)

        def _saat_masuk(e):
            if self.tombol.cget("state") != "disabled":
                self.posisiYTarget = 0.0
                self._animasi_angkat()

        def _saat_keluar(e):
            self.after(10, self._cek_keluar_area)

        self.tombol.bind("<Enter>", _saat_masuk)
        self.tombol.bind("<Leave>", _saat_keluar)
        self.bind("<Enter>", _saat_masuk)
        self.bind("<Leave>", _saat_keluar)

        self._jobAnimasi = None

    def _animasi_angkat(self):
        if self._jobAnimasi:
            self.after_cancel(self._jobAnimasi)

        jarak = self.posisiYTarget - self.posisiYSaat
        if abs(jarak) > 0.1:
            self.posisiYSaat += jarak * 0.3
            self.tombol.place(relx=0, y=self.posisiYSaat, relwidth=1.0)
            self._jobAnimasi = self.after(16, self._animasi_angkat)
        else:
            self.posisiYSaat = self.posisiYTarget
            self.tombol.place(relx=0, y=self.posisiYSaat, relwidth=1.0)

    def _pointer_di_area(self):
        try:
            x, y = self.winfo_pointerxy()
            wx, wy = self.winfo_rootx(), self.winfo_rooty()
            ww, wh = self.winfo_width(), self.winfo_height()
            return wx <= x <= wx + ww and wy <= y <= wy + wh
        except Exception:
            return False

    def _cek_keluar_area(self):
        if self._pointer_di_area():
            return
        self.posisiYTarget = self.posisiYDasar
        self._animasi_angkat()

    def configure(self, **kwargs):
        if hasattr(self, 'tombol'):
            self.tombol.configure(**kwargs)
            if kwargs.get("state") == "disabled":
                self.posisiYTarget = self.posisiYDasar
                self._animasi_angkat()
        else:
            super().configure(**kwargs)

    def cget(self, kunci):
        if hasattr(self, 'tombol'):
            try:
                return self.tombol.cget(kunci)
            except ValueError:
                return super().cget(kunci)
        return super().cget(kunci)
