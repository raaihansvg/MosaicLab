import customtkinter as ctk
import os
from PIL import Image
import platform


PRIMARY = "#5E5CE6"
PRIMARY_HOVER = "#4B49B8"
BG_BASE = "#F6F7FB"
BG_SURFACE = "#FFFFFF"
BG_SIDEBAR = "#F6F7FB"
BORDER = "#EAECEF"
TEXT_PRIMARY = "#111827"
TEXT_MUTED = "#6B7280"
TEXT_INVERSE = "#FFFFFF"

CLR_SUCCESS = "#34C759"
CLR_WARNING = "#FFCC00"
CLR_ERROR = "#FF3B30"

def get_font(type="body"):
    """Returns the appropriate font tuple matching Apple's hierarchy."""
    family_display = "SF Pro Display" if platform.system() == "Darwin" else "Inter"
    family_text = "SF Pro Text" if platform.system() == "Darwin" else "Inter"
    
    if type == "page_title":
        return (family_display, 32, "bold")
    elif type == "section_title":
        return (family_display, 22, "bold")
    elif type == "card_title":
        return (family_text, 15, "normal")
    elif type == "primary_number":
        return (family_display, 24, "bold")
    elif type == "body":
        return (family_text, 15, "normal")
    elif type == "caption":
        return (family_text, 13, "normal")
    return (family_text, 15, "normal")

def setup_theme():
    ctk.set_appearance_mode("Light")
    ctk.set_default_color_theme("blue")

def get_icon(name, size=20, dark_mode=False):
    light_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", f"{name}_light.png")
    dark_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", f"{name}_dark.png")
    
    if os.path.exists(light_path) and os.path.exists(dark_path):
        return ctk.CTkImage(
            light_image=Image.open(light_path),
            dark_image=Image.open(dark_path),
            size=(size, size)
        )
    return None
