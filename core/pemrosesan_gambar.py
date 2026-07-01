import numpy as np
from PIL import Image, ImageFilter
from .konstanta import UKURAN_GRID, DAFTAR_WARNA, RGB_WARNA


def muat_gambar(jalurFile) -> np.ndarray:
    try:
        gambar = Image.open(jalurFile).convert("RGB")
        return np.array(gambar)
    except Exception as e:
        raise ValueError(f"Gagal memuat gambar: {e}")


def ubah_ukuran_ke_grid(arrayGambar: np.ndarray, ukuran: int = UKURAN_GRID) -> np.ndarray:
    gambarPil = Image.fromarray(arrayGambar)
    gambarResize = gambarPil.resize((ukuran, ukuran), Image.LANCZOS)
    return np.array(gambarResize)


def _piksel_ke_hsv(arrayRgb: np.ndarray) -> np.ndarray:
    rgb = arrayRgb.astype(np.float32) / 255.0
    r, g, b = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    nilaiMax = np.maximum(np.maximum(r, g), b)
    nilaiMin = np.minimum(np.minimum(r, g), b)
    delta = nilaiMax - nilaiMin

    h = np.zeros(len(r), dtype=np.float32)
    maskDelta = delta > 0
    m = maskDelta & (nilaiMax == r)
    h[m] = 60.0 * (((g[m] - b[m]) / delta[m]) % 6)
    m = maskDelta & (nilaiMax == g)
    h[m] = 60.0 * (((b[m] - r[m]) / delta[m]) + 2)
    m = maskDelta & (nilaiMax == b)
    h[m] = 60.0 * (((r[m] - g[m]) / delta[m]) + 4)
    h = h % 360.0

    s = np.zeros_like(nilaiMax)
    maskMax = nilaiMax > 0
    s[maskMax] = delta[maskMax] / nilaiMax[maskMax]

    v = nilaiMax
    return np.stack([h, s, v], axis=1)


def petakan_piksel_ke_warna(arrayRgb: np.ndarray) -> np.ndarray:
    hsv = _piksel_ke_hsv(arrayRgb)
    h, s, v = hsv[:, 0], hsv[:, 1], hsv[:, 2]
    n = len(h)

    indeksWarna = {k: i for i, k in enumerate(DAFTAR_WARNA)}
    hasilPeta = np.full(n, -1, dtype=np.int32)

    hasilPeta[v < 0.40] = indeksWarna["hitam"]

    mask = (hasilPeta == -1) & (v > 0.72) & (s < 0.40)
    hasilPeta[mask] = indeksWarna["putih"]

    mask = (hasilPeta == -1) & (s < 0.22)
    hasilPeta[mask & (v <= 0.55)] = indeksWarna["hitam"]
    hasilPeta[mask & (v > 0.55)] = indeksWarna["putih"]

    mask = (hasilPeta == -1) & (h >= 8) & (h < 35) & (s >= 0.55) & (v >= 0.50)
    hasilPeta[mask] = indeksWarna["oren"]

    mask = (hasilPeta == -1) & (h >= 35) & (h < 80) & (s >= 0.25) & (v >= 0.42)
    hasilPeta[mask] = indeksWarna["kuning"]

    mask = (hasilPeta == -1) & (h >= 180) & (h < 270) & (s >= 0.50) & (v >= 0.50)
    hasilPeta[mask] = indeksWarna["biru"]

    mask = (hasilPeta == -1) & ((h < 8) | (h >= 315)) & (s >= 0.55) & (v >= 0.50)
    hasilPeta[mask] = indeksWarna["merah"]

    mask = (hasilPeta == -1) & (h >= 270) & (h < 315) & (s >= 0.55) & (v >= 0.50)
    hasilPeta[mask] = indeksWarna["merah"]

    belumTerpetakan = hasilPeta == -1
    if belumTerpetakan.any():
        pikselBelum = arrayRgb[belumTerpetakan].astype(np.float32)
        selisih = pikselBelum[:, np.newaxis, :] - RGB_WARNA[np.newaxis, :, :]
        jarak = np.sum(selisih ** 2, axis=2)
        terbaik = np.argmin(jarak, axis=1)
        vBelum = v[belumTerpetakan]
        sBelum = s[belumTerpetakan]

        warnaKromatik = {indeksWarna["oren"], indeksWarna["merah"], indeksWarna["kuning"], indeksWarna["biru"]}
        hasilAkhir = terbaik.copy()
        for pi in range(len(pikselBelum)):
            if terbaik[pi] in warnaKromatik:
                jarakKromatik = jarak[pi, terbaik[pi]]
                jarakHitam = jarak[pi, indeksWarna["hitam"]]
                jarakPutih = jarak[pi, indeksWarna["putih"]]

                if vBelum[pi] < 0.55 and jarakHitam < 2.0 * jarakKromatik:
                    hasilAkhir[pi] = indeksWarna["hitam"]
                elif vBelum[pi] >= 0.50 and sBelum[pi] < 0.50 and jarakPutih < 2.5 * jarakKromatik:
                    hasilAkhir[pi] = indeksWarna["putih"]

        hasilPeta[belumTerpetakan] = hasilAkhir

    return hasilPeta


def praproses_gambar_untuk_grid(arrayGambar: np.ndarray) -> np.ndarray:
    UKURAN_ANTARA = 500
    gambarPil = Image.fromarray(arrayGambar)
    gambarTengah = gambarPil.resize((UKURAN_ANTARA, UKURAN_ANTARA), Image.LANCZOS)
    gambarTengah = gambarTengah.filter(ImageFilter.UnsharpMask(radius=2, percent=250, threshold=2))
    gambarFinal = gambarTengah.resize((UKURAN_GRID, UKURAN_GRID), Image.BOX)
    return np.array(gambarFinal)


def petakan_ke_warna_predefined(arrayGambar: np.ndarray) -> np.ndarray:
    piksel = arrayGambar.reshape(-1, 3)
    indeksWarna = petakan_piksel_ke_warna(piksel)
    return indeksWarna.reshape(UKURAN_GRID, UKURAN_GRID)


def proses_gambar_formasi(jalurFile) -> dict:
    arrayMentah = muat_gambar(jalurFile)
    arrayPraproses = praproses_gambar_untuk_grid(arrayMentah)
    gridWarna = petakan_ke_warna_predefined(arrayPraproses)

    arrayNamaWarna = np.array(DAFTAR_WARNA, dtype=object)[gridWarna]
    arrayPrevRgb = RGB_WARNA[gridWarna].astype(np.uint8)

    distribusi = {}
    for i, kunci in enumerate(DAFTAR_WARNA):
        distribusi[kunci] = int(np.sum(gridWarna == i))

    return {
        "grid_warna": gridWarna,
        "nama_warna": arrayNamaWarna,
        "prev_rgb": arrayPrevRgb,
        "distribusi": distribusi,
    }
