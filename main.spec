# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data/pdfs/corpora', 'pdfs/corpora'),
        ('data/pdfs/tokenizers', 'pdfs/tokenizers'),
        ('data/pdfs/*.pdf', 'pdfs'),
        ('data/outputs/*.csv', 'outputs'),
        ('styles/main.qss', 'styles'),
        ('styles/flascard.qss', 'styles'),
    ],
    hiddenimports=[
        'PyMuPDF', 'pytesseract', 'pdf2image', 'nltk', 'pandas', 
        'wordfreq', 'eng-to-ipa', 'gTTS', 'Pillow', 'pyttsx3', 
        'playsound', 'PyQt6'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PyQt5'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
