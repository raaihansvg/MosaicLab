# MosaicLab

MosaicLab is a desktop application built to support the ODM Undip 2026 mosaic formation workflow. The application converts formation images into a 60 x 60 color grid, previews the mapped result, calculates color distribution, and exports participant data to an Excel file.

This project is built with Python, CustomTkinter, Pillow, NumPy, Pandas, Matplotlib, OpenPyXL, and PyInstaller.

## Features

### Formation Image Upload

MosaicLab provides formation slots from F01 to F10. Users can select a formation slot from the sidebar, then upload an image by clicking the upload area or dragging and dropping an image file into the application.

Supported image formats:

- JPG
- JPEG
- PNG
- WEBP

### Image Processing to Grid

Each uploaded image is processed into a 60 x 60 grid. The application resizes the image, applies sharpening, and maps pixels into predefined formation colors.

Available colors:

- Black
- White
- Orange
- Red
- Yellow
- Blue

### Formation Grid Preview

After processing, the application displays a color grid preview. This allows users to inspect the mapped formation before exporting the final Excel data.

Preview tools:

- Zoom in
- Zoom out
- Fit grid
- Toggle grid lines

### Color Distribution Summary

MosaicLab calculates the number of grid cells for each color in every formation. This helps users verify whether the color composition is suitable before the data is used.

### Excel Data Export

MosaicLab can generate an Excel file containing participant data based on grid coordinates and formation colors. The exported file includes:

- Participant coordinates
- Grid row and column
- Color per formation
- Participant position
- Up command
- Down command
- Color distribution summary per formation

Generated Excel sheets:

- `Data Peserta`
- `Ringkasan Distribusi`

### Windows EXE Build

This repository includes a GitHub Actions workflow that automatically builds a Windows `.exe` file. Every push to the `main` branch runs the build workflow and produces a downloadable Windows artifact.

## Requirements

To run the application from source, use Python 3.10 or newer. The GitHub Actions build uses Python 3.11.

Main dependencies:

- customtkinter
- tkinterdnd2
- Pillow
- numpy
- pandas
- scikit-learn
- openpyxl
- matplotlib
- pyinstaller

All required packages are listed in `requirements.txt`.

## Installation

Clone the repository:

```bash
git clone https://github.com/raaihansvg/MosaicLab.git
cd MosaicLab
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python3 main.py
```

Basic workflow:

1. Select a formation slot from the sidebar.
2. Upload a formation image by clicking the upload area or using drag and drop.
3. Click `Generate` to process the image into a color grid.
4. Review the preview and color distribution.
5. Click `Generate Data` to create the Excel data.
6. Click `Unduh Excel` to save the `.xlsx` file.

## Local Application Build

To build the desktop application from source using PyInstaller:

```bash
pyinstaller build.spec
```

The build output will be created in:

```text
dist/
```

Note: PyInstaller builds are most reliable when created on the target operating system. If you need a Windows `.exe`, build it on Windows or use the Windows runner provided by GitHub Actions.

## Windows EXE Build via GitHub Actions

This repository includes the following workflow:

```text
.github/workflows/build-windows.yml
```

How to download the generated `.exe`:

1. Push changes to the `main` branch.
2. Open the `Actions` tab on GitHub.
3. Select the `Build Windows EXE` workflow.
4. Open the latest successful run.
5. Download the `ODM_Undip_2026_Mozaik-Windows` artifact.
6. Extract the artifact file.
7. Run `ODM_Undip_2026_Mozaik.exe` on Windows.

### Windows Security and Drag-and-Drop Notes

Windows may show a SmartScreen warning such as "Windows protected your PC" before opening the generated `.exe`. This happens because the PyInstaller build is not code-signed yet. To remove this warning for normal users, the Windows executable needs to be signed with a trusted code-signing certificate.

If drag and drop does not work on Windows:

- Run the app normally, not with `Run as administrator`. Windows blocks drag and drop between Explorer and an app when they run at different privilege levels.
- Make sure the `.exe` is built from the latest `build.spec`, which bundles `tkinterdnd2` and its native `tkdnd` files.
- If the file was downloaded from the internet, right-click the `.exe`, choose `Properties`, then use `Unblock` if Windows shows that option.

## Project Structure

```text
MosaicLab/
├── main.py
├── build.spec
├── requirements.txt
├── core/
│   ├── konstanta.py
│   ├── pemrosesan_gambar.py
│   └── ekspor_excel.py
├── ui/
│   ├── jendela_utama.py
│   ├── tema.py
│   ├── utilitas.py
│   ├── components/
│   └── views/
├── assets/
│   └── icons/
└── .github/
    └── workflows/
```

## Core Modules

### `core/konstanta.py`

Stores the main application configuration, including grid size, formation count, color definitions, RGB values, and Excel styling colors.

### `core/pemrosesan_gambar.py`

Handles image loading, resizing, predefined color mapping, and color distribution data generation.

### `core/ekspor_excel.py`

Handles participant dataframe generation and Excel export using OpenPyXL, including sheet styling, headers, cell colors, participant positions, and distribution summary.

### `ui/jendela_utama.py`

Main application window module. It manages image upload, drag and drop, formation slot switching, image processing, grid preview, and Excel export.

## Asset Notes

The `assets/icons` folder is used for application interface icons. PNG files are required at runtime and are included in the PyInstaller build.

SVG files may be kept locally for design purposes, but they do not need to be tracked in the repository if the application does not use them directly.

## License

This project is licensed for internal use within the ODM Undip 2026 Mosaic Formation project. See the [LICENSE](LICENSE) file for details.
