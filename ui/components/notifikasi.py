import customtkinter as ctk


class NotifikasiToast(ctk.CTkFrame):
    def __init__(self, induk, pesan, tipe="success", durasi=3000, **kwargs):
        super().__init__(induk, corner_radius=12, fg_color="#FFFFFF", border_width=1, border_color="#E9EDF7", **kwargs)

        self.pesan = pesan
        self.durasi = durasi

        paletWarna = {
            "success": "#05CD99",
            "error": "#EE5D50",
            "info": "#4318FF",
            "warning": "#FFCE20"
        }
        aksen = paletWarna.get(tipe, paletWarna["info"])

        titikAksen = ctk.CTkFrame(self, width=10, height=10, corner_radius=5, fg_color=aksen)
        titikAksen.pack(side="left", padx=(16, 8), pady=12)

        self.labelPesan = ctk.CTkLabel(self, text=pesan, text_color="#2B3674", font=("Inter", 13, "bold"))
        self.labelPesan.pack(side="left", padx=(0, 24), pady=12)

        self.place(relx=1.2, rely=0.95, anchor="se")
        self.relxTarget = 0.98
        self.relxSaat = 1.2

    def tampilkan(self):
        self.lift()
        self._animasi_masuk()
        self.after(self.durasi, self.sembunyikan)

    def _animasi_masuk(self):
        jarak = self.relxSaat - self.relxTarget
        if jarak > 0.001:
            langkah = max(0.002, jarak * 0.15)
            self.relxSaat -= langkah
            self.place(relx=self.relxSaat, rely=0.95, anchor="se")
            self.after(16, self._animasi_masuk)
        else:
            self.place(relx=self.relxTarget, rely=0.95, anchor="se")

    def sembunyikan(self):
        self._animasi_keluar()

    def _animasi_keluar(self):
        jarak = 1.2 - self.relxSaat
        if jarak > 0.001:
            langkah = max(0.002, jarak * 0.15)
            self.relxSaat += langkah
            try:
                self.place(relx=self.relxSaat, rely=0.95, anchor="se")
                self.after(16, self._animasi_keluar)
            except Exception:
                pass
        else:
            try:
                self.destroy()
            except Exception:
                pass


def tampilkan_toast(induk, pesan, tipe="success", durasi=3000):
    toast = NotifikasiToast(induk, pesan, tipe, durasi)
    toast.tampilkan()
