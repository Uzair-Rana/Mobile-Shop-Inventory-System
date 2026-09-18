# My Phone ERP

Inventory, sales, repairs and procurement system for a mobile phone shop.
A Django server-rendered web app (`backend/`), shipped to Windows as a
one-click installer.

## Run for development

```sh
cd backend
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open http://127.0.0.1:8000/. On first launch the app asks for the installation
key, then you sign in (create a user with `python manage.py createsuperuser`).

## Project layout

- `backend/apps/web/` — the web UI (views, templates, static files)
- `backend/apps/*` — domain apps (inventory, sales, procurement, repairs, ...);
  `procurement` is the source of truth for stock
- `backend/devnest/` — Django settings and URLs
- `backend/launcher.py` — desktop launcher used by the packaged app
- `installer/` — Inno Setup script and build notes

## Build the Windows installer

Requires Python 3.11+ and [Inno Setup 6](https://jrsoftware.org/isdl.php).
From the repo root:

```
build_installer.bat
```

The installer is written to `dist_installer\MyPhoneERP-Setup.exe` — that single
file is what you send to users. See `installer/BUILD_INSTALLER.md` for details.
