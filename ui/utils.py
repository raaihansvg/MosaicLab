import subprocess
import os
from tkinter import filedialog

def modern_file_picker(title, filetypes_label="Image Files", filetypes_ext="*.jpg *.jpeg *.png *.webp"):
    """Uses native zenity on Linux if available, otherwise falls back to tkinter."""
    if os.name == "posix":
        try:
            cmd = [
                "zenity", "--file-selection", 
                f"--title={title}",
                f"--file-filter={filetypes_label} | {filetypes_ext}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return "" 
        except FileNotFoundError:
            pass
    ext_list = filetypes_ext.split()
    return filedialog.askopenfilename(title=title, filetypes=[(filetypes_label, " ".join(ext_list))])

def modern_save_picker(title, default_ext=".xlsx", filetypes_label="Excel Files", filetypes_ext="*.xlsx"):
    """Uses native zenity for save dialog if available, else tkinter."""
    if os.name == "posix":
        try:
            cmd = [
                "zenity", "--file-selection", "--save", "--confirm-overwrite",
                f"--title={title}",
                f"--file-filter={filetypes_label} | {filetypes_ext}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                path = result.stdout.strip()
                if not path.endswith(default_ext):
                    path += default_ext
                return path
            return ""
        except FileNotFoundError:
            pass
    ext_list = filetypes_ext.split()
    return filedialog.asksaveasfilename(title=title, defaultextension=default_ext, filetypes=[(filetypes_label, " ".join(ext_list))])

def interpolate_color(hex1, hex2, factor):
    hex1 = hex1.lstrip('#')
    hex2 = hex2.lstrip('#')
    if len(hex1) == 3: hex1 = ''.join([c*2 for c in hex1])
    if len(hex2) == 3: hex2 = ''.join([c*2 for c in hex2])
    
    r1, g1, b1 = int(hex1[0:2], 16), int(hex1[2:4], 16), int(hex1[4:6], 16)
    r2, g2, b2 = int(hex2[0:2], 16), int(hex2[2:4], 16), int(hex2[4:6], 16)
    
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return f"#{r:02x}{g:02x}{b:02x}"

def animate_widget_color(widget, prop, start_color, end_color, steps=15, current_step=0, delay=16):
    """Smoothly animates a color property (e.g. fg_color) of a widget using ease-out."""
    if current_step > steps:
        widget.configure(**{prop: end_color})
        return
    t = current_step / steps
    factor = 1 - pow(1 - t, 3)
    
    current_color = interpolate_color(start_color, end_color, factor)
    try:
        widget.configure(**{prop: current_color})
        widget.after(delay, animate_widget_color, widget, prop, start_color, end_color, steps, current_step + 1, delay)
    except:
        pass 

def animate_grid_pady(widget, base_top, base_bottom, lift_amount, steps=10, current_step=0, delay=16, direction="up"):
    if current_step > steps:
        return
        
    t = current_step / steps
    factor = 1 - pow(1 - t, 3) 
    
    shift = int(lift_amount * factor)
    
    if direction == "up":
        top = base_top - shift
        bottom = base_bottom + shift
    else:
        top = (base_top - lift_amount) + shift
        bottom = (base_bottom + lift_amount) - shift
        
    try:
        widget.grid_configure(pady=(top, bottom))
        widget.after(delay, animate_grid_pady, widget, base_top, base_bottom, lift_amount, steps, current_step + 1, delay, direction)
    except:
        pass
