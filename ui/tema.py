import customtkinter as ctk
import os
from PIL import Image
import platform

WARNA_UTAMA = "#5E5CE6"
WARNA_UTAMA_HOVER = "#4B49B8"
LATAR_DASAR = "#F6F7FB"
LATAR_PERMUKAAN = "#FFFFFF"
LATAR_SIDEBAR = "#F6F7FB"
GARIS_TEPI = "#EAECEF"
TEKS_UTAMA = "#111827"
TEKS_REDUP = "#6B7280"
TEKS_TERBALIK = "#FFFFFF"

WARNA_SUKSES = "#34C759"
WARNA_PERINGATAN = "#FFCC00"
WARNA_ERROR = "#FF3B30"

def ambil_font(tipe="body"):
    famili_display = "SF Pro Display" if platform.system() == "Darwin" else "Inter"
    famili_teks = "SF Pro Text" if platform.system() == "Darwin" else "Inter"

    if tipe == "page_title":
        return (famili_display, 32, "bold")
    elif tipe == "section_title":
        return (famili_display, 22, "bold")
    elif tipe == "card_title":
        return (famili_teks, 15, "normal")
    elif tipe == "primary_number":
        return (famili_display, 24, "bold")
    elif tipe == "body":
        return (famili_teks, 15, "normal")
    elif tipe == "caption":
        return (famili_teks, 13, "normal")
    return (famili_teks, 15, "normal")

def atur_tema():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

def ambil_ikon(nama, ukuran=20, mode_gelap=False):
    direktoriAset = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
    jalurTerang = os.path.join(direktoriAset, f"{nama}_light.png")
    jalurGelap = os.path.join(direktoriAset, f"{nama}_dark.png")

    if os.path.exists(jalurTerang) and os.path.exists(jalurGelap):
        return ctk.CTkImage(
            light_image=Image.open(jalurTerang),
            dark_image=Image.open(jalurGelap),
            size=(ukuran, ukuran)
        )
    return None
