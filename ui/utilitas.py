import subprocess
import os
from tkinter import filedialog


def pilih_file(judul, labelTipe="File Gambar", ekstensiTipe="*.jpg *.jpeg *.png *.webp"):
    if os.name == "posix":
        try:
            cmd = [
                "zenity", "--file-selection", 
                f"--title={judul}",
                f"--file-filter={labelTipe} | {ekstensiTipe}"
            ]
            hasil = subprocess.run(cmd, capture_output=True, text=True)
            if hasil.returncode == 0:
                return hasil.stdout.strip()
            return ""
        except FileNotFoundError:
            pass

    ekstensiList = ekstensiTipe.split()
    return filedialog.askopenfilename(
        title=judul,
        filetypes=[(labelTipe, " ".join(ekstensiList))]
    )


def simpan_file(judul, ekstensiDefault=".xlsx", labelTipe="File Excel", ekstensiTipe="*.xlsx"):
    if os.name == "posix":
        try:
            cmd = [
                "zenity", "--file-selection", "--save", "--confirm-overwrite",
                f"--title={judul}",
                f"--file-filter={labelTipe} | {ekstensiTipe}"
            ]
            hasil = subprocess.run(cmd, capture_output=True, text=True)
            if hasil.returncode == 0:
                jalur = hasil.stdout.strip()
                if not jalur.endswith(ekstensiDefault):
                    jalur += ekstensiDefault
                return jalur
            return ""
        except FileNotFoundError:
            pass

    ekstensiList = ekstensiTipe.split()
    return filedialog.asksaveasfilename(
        title=judul,
        defaultextension=ekstensiDefault,
        filetypes=[(labelTipe, " ".join(ekstensiList))]
    )


def interpolasi_warna(hex1, hex2, faktor):
    hex1 = hex1.lstrip('#')
    hex2 = hex2.lstrip('#')

    if len(hex1) == 3:
        hex1 = ''.join([c * 2 for c in hex1])
    if len(hex2) == 3:
        hex2 = ''.join([c * 2 for c in hex2])

    r1, g1, b1 = int(hex1[0:2], 16), int(hex1[2:4], 16), int(hex1[4:6], 16)
    r2, g2, b2 = int(hex2[0:2], 16), int(hex2[2:4], 16), int(hex2[4:6], 16)

    r = int(r1 + (r2 - r1) * faktor)
    g = int(g1 + (g2 - g1) * faktor)
    b = int(b1 + (b2 - b1) * faktor)

    return f"#{r:02x}{g:02x}{b:02x}"


def animasi_warna_widget(widget, properti, warnaAwal, warnaAkhir, langkah=15, langkahSaat=0, jeda=16):
    if langkahSaat > langkah:
        try:
            widget.configure(**{properti: warnaAkhir})
        except Exception:
            pass
        return

    t = langkahSaat / langkah
    faktor = 1 - pow(1 - t, 3)

    warnaSekarang = interpolasi_warna(warnaAwal, warnaAkhir, faktor)
    try:
        widget.configure(**{properti: warnaSekarang})
        widget.after(jeda, animasi_warna_widget, widget, properti, warnaAwal, warnaAkhir, langkah, langkahSaat + 1, jeda)
    except Exception:
        pass
