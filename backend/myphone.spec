# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for My Phone ERP.

Build:  pyinstaller myphone.spec --noconfirm
Output: dist/MyPhoneERP/MyPhoneERP.exe
"""
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

LOCAL_APPS = [
    'apps.users', 'apps.branches', 'apps.inventory', 'apps.sales', 'apps.repairs',
    'apps.installments', 'apps.purchases', 'apps.customers', 'apps.suppliers',
    'apps.transfers', 'apps.cash', 'apps.reports', 'apps.settings_app', 'apps.audit',
    'apps.web', 'apps.spare_parts', 'apps.procurement', 'devnest',
]

THIRD_PARTY = [
    'django', 'rest_framework', 'corsheaders', 'django_filters', 'whitenoise',
    'waitress', 'decouple', 'dj_database_url', 'PIL', 'openpyxl', 'pystray',
]

hiddenimports = []
datas = []

# All submodules (incl. migrations, management commands) as hidden imports.
for pkg in LOCAL_APPS + THIRD_PARTY:
    hiddenimports += collect_submodules(pkg)

# Templates / static / locale and other data files for our apps + Django/DRF.
for pkg in ['apps.web', 'django', 'rest_framework']:
    datas += collect_data_files(pkg)

# Ship our app template & static source trees explicitly (belt-and-braces).
datas += [
    ('apps/web/templates', 'apps/web/templates'),
    ('apps/web/static', 'apps/web/static'),
]

block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'pytest', 'psycopg2'],
    cipher=block_cipher,
)

# PyInstaller's Django hook bundles the dev SQLite DB next to manage.py. Never
# ship it: the app creates a fresh DB in %LOCALAPPDATA%\MyPhoneERP instead.
a.datas = [d for d in a.datas if not d[0].lower().startswith('db.sqlite3')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='MyPhoneERP',
    debug=False,
    strip=False,
    upx=True,
    console=False,         # runs in the system tray, no console window
    icon='apps/web/static/web/logo.png',
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    strip=False, upx=True, name='MyPhoneERP',
)
