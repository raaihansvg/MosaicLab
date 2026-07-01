import customtkinter as ctk
from tkinterdnd2 import TkinterDnD, DND_FILES, DND_ALL, COPY, REFUSE_DROP
from PIL import Image
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import threading
from urllib.parse import unquote, urlparse

from .tema import atur_tema, LATAR_DASAR, TEKS_UTAMA, TEKS_REDUP, GARIS_TEPI
from .views.sidebar_baru import Sidebar
from .views.kanvas import AreaKanvas
from .views.inspeksi import PanelInspeksi
from .components.notifikasi import tampilkan_toast
from core.pemrosesan_gambar import proses_gambar_formasi
from core.ekspor_excel import bangun_dataframe_peserta, ekspor_ke_excel


class JendelaUtama(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self):
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        atur_tema()
        self.title("ODM Undip 2026")
        self.geometry("1440x900")
        self.minsize(1280, 800)
        self.configure(fg_color=LATAR_DASAR)

        self.jalurTerUpload = {}
        self.dataFormasi = {}
        self.bytesExcel = None
        self.tampilkanGrid = True
        self.warnaBg = "putih"

        self.tabAktif = None
        self._refKanvas = None
        self._refFoto = {}
        self._sedangDragDrop = False
        self._dialogUploadManualTerbuka = False

        self._bangun_layout()
        self._daftarkan_dnd()

        self.areaKanvas.tampilkan_placeholder()

    def _bangun_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=240)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0, minsize=320)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(self, self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.areaKanvas = AreaKanvas(self, self)
        self.areaKanvas.grid(row=0, column=1, sticky="nsew")

        self.panelInspeksi = PanelInspeksi(self, self)
        self.panelInspeksi.grid(row=0, column=2, sticky="nsew")

    def _daftarkan_dnd(self):
        self.daftarkan_target_drop(self)
        self.daftarkan_target_drop(*self.areaKanvas.ambil_target_drop())

    def daftarkan_target_drop(self, *widgets):
        for widget in widgets:
            if not widget:
                continue
            try:
                widget.drop_target_register(DND_FILES, DND_ALL)
                widget.dnd_bind('<<DropEnter>>', self._izinkan_drop)
                widget.dnd_bind('<<DropPosition>>', self._izinkan_drop)
                widget.dnd_bind('<<Drop:DND_Files>>', self._tangani_drop)
                widget.dnd_bind('<<Drop>>', self._tangani_drop)
            except Exception:
                pass

    def _izinkan_drop(self, event):
        if not self.tabAktif:
            return REFUSE_DROP
        return COPY

    def _pecah_data_drop(self, data):
        try:
            kandidat = list(self.tk.splitlist(data))
        except Exception:
            kandidat = [data]

        hasil = []
        for item in kandidat:
            teks = str(item).replace("\r", "\n")
            baris = [b.strip() for b in teks.splitlines() if b.strip()]
            if len(baris) > 1:
                hasil.extend(baris)
            else:
                hasil.append(str(item).strip())
        return hasil

    def _normalisasi_jalur_drop(self, data):
        hasil = []
        for jalur in self._pecah_data_drop(data):
            if not jalur or jalur.startswith("#"):
                continue
            parsed = urlparse(jalur)
            if parsed.scheme == "file":
                jalur = unquote(parsed.path)
            elif parsed.scheme:
                continue
            hasil.append(jalur)
        return hasil

    def _tangani_drop(self, event):
        if self._sedangDragDrop:
            return COPY
        self._sedangDragDrop = True

        daftarFile = self._normalisasi_jalur_drop(event.data)

        if not daftarFile:
            self._sedangDragDrop = False
            return REFUSE_DROP

        if self.tabAktif:
            jalur = daftarFile[0]
            ekstensi = os.path.splitext(jalur)[1].lower()
            if ekstensi in [".jpg", ".jpeg", ".png", ".webp"]:
                self.after(100, lambda t=self.tabAktif, f=jalur: self._selesai_drop(t, f))
            else:
                self.after(100, lambda: self._selesai_drop_error())
            return COPY
        else:
            self._sedangDragDrop = False
            return REFUSE_DROP

    def _selesai_drop(self, tabIndeks, jalurFile):
        self._sedangDragDrop = False
        self.tangani_upload(tabIndeks, jalurFile)

    def _selesai_drop_error(self):
        self._sedangDragDrop = False
        tampilkan_toast(self, "Format file tidak didukung", tipe="error")

    def buka_dialog_upload_manual(self):
        if self._dialogUploadManualTerbuka or not self.tabAktif:
            return

        tabIndeks = self.tabAktif
        self._dialogUploadManualTerbuka = True
        self.after(50, lambda i=tabIndeks: self._jalankan_dialog_upload_manual(i))

    def _jalankan_dialog_upload_manual(self, tabIndeks):
        try:
            from .utilitas import pilih_file
            jalur = pilih_file(judul=f"Pilih Formasi {tabIndeks:02d}")
            if jalur:
                self.tangani_upload(tabIndeks, jalur)
        except Exception as e:
            tampilkan_toast(self, f"Gagal membuka file: {e}", tipe="error")
        finally:
            self._dialogUploadManualTerbuka = False

    def tangani_upload(self, indeks, jalur):
        self.jalurTerUpload[indeks] = jalur
        if indeks in self.dataFormasi:
            del self.dataFormasi[indeks]

        self.sidebar.daftarSlot[indeks].set_status("terupload")
        self._periksa_status_ekspor()

        if self.tabAktif == indeks:
            self.ganti_tab(indeks)

    def tangani_hapus(self, indeks):
        if indeks in self.jalurTerUpload:
            del self.jalurTerUpload[indeks]
        if indeks in self.dataFormasi:
            del self.dataFormasi[indeks]

        self.sidebar.daftarSlot[indeks].set_status("kosong")
        self.panelInspeksi.perbarui_metrik(len(self.dataFormasi))
        self._periksa_status_ekspor()

        if self.tabAktif == indeks:
            self.ganti_tab(indeks)

    def proses_semua(self):
        if not self.jalurTerUpload:
            tampilkan_toast(self, "Upload minimal 1 gambar", tipe="warning")
            return

        self.areaKanvas.tombolGenerate.configure(state="disabled", text="Memproses...")

        def _tugas():
            jumlahBerhasil = 0
            for idx, jalur in list(self.jalurTerUpload.items()):
                try:
                    hasil = proses_gambar_formasi(jalur)
                    self.dataFormasi[idx] = hasil
                    self.after(0, lambda i=idx: self.sidebar.daftarSlot[i].set_status("selesai"))
                    jumlahBerhasil += 1
                except Exception as e:
                    print(f"Error F{idx}: {e}")

            self.after(0, lambda: self._pasca_proses(jumlahBerhasil))

        threading.Thread(target=_tugas, daemon=True).start()

    def _pasca_proses(self, jumlahBerhasil):
        self.areaKanvas.tombolGenerate.configure(state="normal", text="Generate")
        self.panelInspeksi.perbarui_metrik(len(self.dataFormasi))
        self._periksa_status_ekspor()

        if jumlahBerhasil > 0:
            tampilkan_toast(self, f"Berhasil memproses {jumlahBerhasil} formasi", tipe="success")
            indeksAkhir = max(self.dataFormasi.keys())
            self.ganti_tab(indeksAkhir)

    def ganti_tab(self, indeks):
        self.tabAktif = indeks

        for idx, slot in self.sidebar.daftarSlot.items():
            slot.set_aktif(idx == indeks)

        if indeks not in self.jalurTerUpload:
            self.areaKanvas.tampilkan_state_kosong(indeks)
            self.panelInspeksi.render_distribusi(None)
        else:
            self.areaKanvas.tampilkan_state_terisi(indeks)
            if indeks in self.dataFormasi:
                self._render_preview(indeks)
            else:
                self._render_belum_diproses(indeks)

    def _render_belum_diproses(self, indeks):
        jalur = self.jalurTerUpload[indeks]
        if self._refKanvas:
            try:
                self._refKanvas.get_tk_widget().destroy()
            except Exception:
                pass
            self._refKanvas = None

        try:
            gambarPil = Image.open(jalur)
            gambarPil.thumbnail((600, 600), Image.LANCZOS)
            gambarCtk = ctk.CTkImage(light_image=gambarPil, size=gambarPil.size)
            self._refFoto[indeks] = gambarCtk
            self.areaKanvas.set_gambar(gambarCtk)
        except Exception:
            self.areaKanvas.labelGambar.configure(image="", text="Gagal memuat gambar")

        self.areaKanvas.bersihkan_plot()
        ctk.CTkLabel(
            self.areaKanvas.framePlot,
            text="Belum diproses.\nKlik 'Generate' untuk memproses.",
            font=("Inter", 14), text_color=TEKS_REDUP
        ).place(relx=0.5, rely=0.5, anchor="center")

        self.panelInspeksi.render_distribusi(None)

    def _render_preview(self, indeks):
        data = self.dataFormasi[indeks]
        jalur = self.jalurTerUpload[indeks]

        try:
            gambarPil = Image.open(jalur)
            gambarPil.thumbnail((600, 600), Image.LANCZOS)
            gambarCtk = ctk.CTkImage(light_image=gambarPil, size=gambarPil.size)
            self._refFoto[indeks] = gambarCtk
            self.areaKanvas.set_gambar(gambarCtk)
        except Exception:
            pass

        self.areaKanvas.bersihkan_plot()

        if self._refKanvas:
            try:
                self._refKanvas.get_tk_widget().destroy()
            except Exception:
                pass
            self._refKanvas = None

        fig = self._buat_figure(data, f"F{indeks}")
        self._refKanvas = FigureCanvasTkAgg(fig, master=self.areaKanvas.framePlot)
        self._refKanvas.draw()
        self.areaKanvas.pasang_kanvas_plot(self._refKanvas.get_tk_widget())

        self.panelInspeksi.render_distribusi(data)

    def _buat_figure(self, data, label):
        prevRgb = data["prev_rgb"]
        fig, ax = plt.subplots(1, 1, figsize=(6, 6), facecolor=LATAR_DASAR)
        ax.set_facecolor(LATAR_DASAR)
        ax.imshow(prevRgb, interpolation="nearest", aspect="equal")

        ax.set_title("Grid Preview", color=TEKS_UTAMA, fontsize=14, fontweight="bold", pad=12)
        ax.tick_params(colors=TEKS_REDUP, labelsize=9)

        for spine in ax.spines.values():
            spine.set_edgecolor(GARIS_TEPI)

        if self.tampilkanGrid:
            for i in range(0, 60 + 1, 1):
                ax.axhline(i - 0.5, color=GARIS_TEPI, linewidth=0.5)
                ax.axvline(i - 0.5, color=GARIS_TEPI, linewidth=0.5)

        daftarTick = list(range(0, 60, 5))
        ax.set_xticks(daftarTick)
        ax.set_xticklabels([t + 1 for t in daftarTick])
        ax.set_yticks(daftarTick)
        ax.set_yticklabels([t + 1 for t in daftarTick])
        plt.tight_layout(pad=1)
        return fig

    def zoom_grid(self, faktor):
        if self._refKanvas:
            ax = self._refKanvas.figure.axes[0]
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            cx = (xlim[0] + xlim[1]) / 2
            cy = (ylim[0] + ylim[1]) / 2
            lx = (xlim[1] - xlim[0]) * faktor
            ly = (ylim[1] - ylim[0]) * faktor
            ax.set_xlim(cx - lx / 2, cx + lx / 2)
            ax.set_ylim(cy - ly / 2, cy + ly / 2)
            self._refKanvas.draw()

    def pas_grid(self):
        if self._refKanvas:
            ax = self._refKanvas.figure.axes[0]
            ax.set_xlim(-0.5, 60 - 0.5)
            ax.set_ylim(60 - 0.5, -0.5)
            self._refKanvas.draw()

    def toggle_garis_grid(self):
        self.tampilkanGrid = not self.tampilkanGrid
        if self.tabAktif and self.tabAktif in self.dataFormasi:
            self._render_preview(self.tabAktif)

    def _periksa_status_ekspor(self):
        if not self.dataFormasi:
            self.panelInspeksi.tombolGenerateData.configure(state="disabled", text="Generate Data")
            self.panelInspeksi.tombolUnduhExcel.configure(state="disabled")
            self.bytesExcel = None
        else:
            self.panelInspeksi.tombolGenerateData.configure(state="normal", text="Generate Data")

    def generate_excel(self):
        if not self.dataFormasi:
            return
        self.panelInspeksi.tombolGenerateData.configure(state="disabled", text="Generating...")

        def _tugas():
            try:
                kunciUrut = sorted(self.dataFormasi.keys())
                daftarFormasi = [self.dataFormasi[k] for k in kunciUrut]

                df = bangun_dataframe_peserta(daftarFormasi, warnaBg=self.warnaBg)
                self.bytesExcel = ekspor_ke_excel(df, daftarFormasi)

                self.after(0, self._saat_generate_berhasil)
            except Exception as e:
                pesan = str(e)
                self.after(0, lambda p=pesan: self._saat_generate_gagal(p))

        threading.Thread(target=_tugas, daemon=True).start()

    def _saat_generate_berhasil(self):
        self.panelInspeksi.tombolGenerateData.configure(state="normal", text="Generate Data")
        self.panelInspeksi.tombolUnduhExcel.configure(state="normal")
        tampilkan_toast(self, "Data Excel siap diunduh!", tipe="success")

    def _saat_generate_gagal(self, pesan):
        self.panelInspeksi.tombolGenerateData.configure(state="normal", text="Generate Data")
        tampilkan_toast(self, f"Gagal: {pesan}", tipe="error")

    def unduh_excel(self):
        if not self.bytesExcel:
            return

        from .utilitas import simpan_file
        jalur = simpan_file(judul="Simpan File Excel")
        if jalur:
            try:
                with open(jalur, "wb") as f:
                    f.write(self.bytesExcel)
                tampilkan_toast(self, "Excel berhasil disimpan!", tipe="success")
            except Exception as e:
                tampilkan_toast(self, f"Gagal: {e}", tipe="error")
