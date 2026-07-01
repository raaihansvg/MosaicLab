import numpy as np

GRID_SIZE    = 60
N_COLORS     = 6
N_FORMATIONS = 10

WARNA_DEFINISI = {
    "hitam":  {"rgb": (0,   0,   0),   "hex": "#000000", "label": "Hitam"},
    "putih":  {"rgb": (255, 255, 255), "hex": "#FFFFFF", "label": "Putih"},
    "oren":   {"rgb": (255, 140,  0),  "hex": "#FF8C00", "label": "Oren"},
    "merah":  {"rgb": (220,  20, 60),  "hex": "#DC143C", "label": "Merah"},
    "kuning": {"rgb": (255, 215,  0),  "hex": "#FFD700", "label": "Kuning"},
    "biru":   {"rgb": (30,  144, 255), "hex": "#1E90FF", "label": "Biru"},
}

WARNA_KEYS = list(WARNA_DEFINISI.keys())
WARNA_RGB  = np.array([v["rgb"] for v in WARNA_DEFINISI.values()], dtype=np.float32)

BACKGROUND_COLORS = {"putih", "hitam"}

EXCEL_FILLS = {
    "hitam":  "FF000000",
    "putih":  "FFFFFFFF",
    "oren":   "FFFF8C00",
    "merah":  "FFDC143C",
    "kuning": "FFFFD700",
    "biru":   "FF1E90FF",
}
