import numpy as np
from PIL import Image, ImageFilter
from .constants import GRID_SIZE, WARNA_KEYS, WARNA_RGB

def load_image(uploaded_file) -> np.ndarray:
    try:
        img = Image.open(uploaded_file).convert("RGB")
        return np.array(img)
    except Exception as e:
        raise ValueError(f"Gagal memuat gambar: {e}")

def resize_to_grid(img_array: np.ndarray, size: int = GRID_SIZE) -> np.ndarray:
    pil_img = Image.fromarray(img_array)
    resized  = pil_img.resize((size, size), Image.LANCZOS)
    return np.array(resized)

def _pixels_to_hsv(rgb_array: np.ndarray) -> np.ndarray:
    rgb  = rgb_array.astype(np.float32) / 255.0
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    cmax  = np.maximum(np.maximum(r, g), b)
    cmin  = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin

    h = np.zeros(len(r), dtype=np.float32)
    mask = delta > 0
    m = mask & (cmax == r)
    h[m] = 60.0 * (((g[m] - b[m]) / delta[m]) % 6)
    m = mask & (cmax == g)
    h[m] = 60.0 * (((b[m] - r[m]) / delta[m]) + 2)
    m = mask & (cmax == b)
    h[m] = 60.0 * (((r[m] - g[m]) / delta[m]) + 4)
    h = h % 360.0

    s = np.zeros_like(cmax)
    mask_cmax = cmax > 0
    s[mask_cmax] = delta[mask_cmax] / cmax[mask_cmax]
    v = cmax
    return np.stack([h, s, v], axis=1)

def map_pixel_to_color_hsv(rgb_array: np.ndarray) -> np.ndarray:
    hsv     = _pixels_to_hsv(rgb_array)
    h, s, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    n       = len(h)

    IDX    = {k: i for i, k in enumerate(WARNA_KEYS)}
    result = np.full(n, -1, dtype=np.int32)

    result[v < 0.40] = IDX["hitam"]

    mask = (result == -1) & (v > 0.72) & (s < 0.40)
    result[mask] = IDX["putih"]

    mask = (result == -1) & (s < 0.22)
    result[mask & (v <= 0.55)] = IDX["hitam"]
    result[mask & (v >  0.55)] = IDX["putih"]

    mask = (result == -1) & (h >= 8) & (h < 35) & (s >= 0.55) & (v >= 0.50)
    result[mask] = IDX["oren"]

    mask = (result == -1) & (h >= 35) & (h < 80) & (s >= 0.25) & (v >= 0.42)
    result[mask] = IDX["kuning"]

    mask = (result == -1) & (h >= 180) & (h < 270) & (s >= 0.50) & (v >= 0.50)
    result[mask] = IDX["biru"]

    mask = (result == -1) & ((h < 8) | (h >= 315)) & (s >= 0.55) & (v >= 0.50)
    result[mask] = IDX["merah"]

    mask = (result == -1) & (h >= 270) & (h < 315) & (s >= 0.55) & (v >= 0.50)
    result[mask] = IDX["merah"]

    unresolved = result == -1
    if unresolved.any():
        px_u  = rgb_array[unresolved].astype(np.float32)
        diff  = px_u[:, np.newaxis, :] - WARNA_RGB[np.newaxis, :, :]
        dist  = np.sum(diff ** 2, axis=2)
        best  = np.argmin(dist, axis=1)
        v_u   = v[unresolved]
        s_u   = s[unresolved]

        CHROMATIC  = {IDX["oren"], IDX["merah"], IDX["kuning"], IDX["biru"]}
        final_best = best.copy()
        for pi in range(len(px_u)):
            if best[pi] in CHROMATIC:
                d_chroma = dist[pi, best[pi]]
                d_hitam  = dist[pi, IDX["hitam"]]
                d_putih  = dist[pi, IDX["putih"]]

                if v_u[pi] < 0.55 and d_hitam < 2.0 * d_chroma:
                    final_best[pi] = IDX["hitam"]
                elif v_u[pi] >= 0.50 and s_u[pi] < 0.50 and d_putih < 2.5 * d_chroma:
                    final_best[pi] = IDX["putih"]

        result[unresolved] = final_best

    return result

def preprocess_image_for_grid(img_array: np.ndarray) -> np.ndarray:
    INTER_SIZE = 500
    pil_img = Image.fromarray(img_array)
    mid = pil_img.resize((INTER_SIZE, INTER_SIZE), Image.LANCZOS)
    mid = mid.filter(ImageFilter.UnsharpMask(radius=2, percent=250, threshold=2))
    final = mid.resize((GRID_SIZE, GRID_SIZE), Image.BOX)
    return np.array(final)

def map_to_predefined_colors(img_array: np.ndarray) -> np.ndarray:
    pixels = img_array.reshape(-1, 3)
    color_indices = map_pixel_to_color_hsv(pixels)
    return color_indices.reshape(GRID_SIZE, GRID_SIZE)

def process_formation_image(uploaded_file) -> dict:
    raw        = load_image(uploaded_file)
    preprocessed = preprocess_image_for_grid(raw)
    color_grid   = map_to_predefined_colors(preprocessed)

    color_names = np.array(WARNA_KEYS, dtype=object)[color_grid]
    preview_rgb = WARNA_RGB[color_grid].astype(np.uint8)

    distribution = {}
    for i, key in enumerate(WARNA_KEYS):
        distribution[key] = int(np.sum(color_grid == i))

    return {
        "color_grid":   color_grid,
        "color_names":  color_names,
        "preview_rgb":  preview_rgb,
        "distribution": distribution,
    }
