import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules


datas_sklearn,    binaries_sklearn,    hiddenimports_sklearn    = collect_all('sklearn')
datas_matplotlib, binaries_matplotlib, hiddenimports_matplotlib = collect_all('matplotlib')
datas_PIL,        binaries_PIL,        hiddenimports_PIL        = collect_all('PIL')
datas_pandas,     binaries_pandas,     hiddenimports_pandas     = collect_all('pandas')
datas_numpy,      binaries_numpy,      hiddenimports_numpy      = collect_all('numpy')

all_datas = (
    datas_sklearn
    + datas_matplotlib
    + datas_PIL
    + datas_pandas
    + datas_numpy
    + [('assets', 'assets')]
)

all_binaries = (
    binaries_sklearn
    + binaries_matplotlib
    + binaries_PIL
    + binaries_pandas
    + binaries_numpy
)

hidden = (
    hiddenimports_sklearn
    + hiddenimports_matplotlib
    + hiddenimports_PIL
    + hiddenimports_pandas
    + hiddenimports_numpy
    + collect_submodules('sklearn')
    + collect_submodules('sklearn.utils')
    + collect_submodules('sklearn.cluster')
    + [
        'sklearn',
        'sklearn.cluster',
        'sklearn.cluster._kmeans',
        'sklearn.utils._cython_blas',
        'sklearn.utils._weight_vector',
        'sklearn.utils._typedefs',
        'sklearn.neighbors._partition_nodes',
        'sklearn.neighbors._ball_tree',
        'sklearn.neighbors._kd_tree',
        'sklearn.utils.murmurhash',
        'sklearn.metrics._pairwise_distances_reduction._datasets_pair',
        'sklearn.metrics._pairwise_distances_reduction._middle_term_computer',
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.utils',
        'openpyxl.workbook',
        'openpyxl.writer.excel',
        'openpyxl.reader.excel',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.figure',
        'matplotlib.patches',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'pandas',
        'pandas._libs.tslibs.np_datetime',
        'pandas._libs.tslibs.nattype',
        'pandas._libs.tslibs.timedeltas',
        'pandas._libs.skiplist',
        'numpy',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'threading',
        'io',
        'warnings',
    ]
)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'streamlit',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'docutils',
        'setuptools',
        'pkg_resources',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ODM_Undip_2026_Mozaik',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,          
    onefile=True,       
)
