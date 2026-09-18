# Building the My Phone ERP one-click installer

Produces `MyPhoneERP-Setup.exe` — a normal Windows installer. After installing,
the user double-clicks the desktop icon; the app starts a local server, opens the
browser, and (on first run) asks for the **installation key** `UFA_Dev_nest-123`.

## Prerequisites (build machine, Windows)
- **Python 3.11+** on PATH
- **Inno Setup 6** — https://jrsoftware.org/isdl.php (gives you `ISCC.exe`)

## Build (one command)
From the repo root:

```
build_installer.bat
```

This: installs deps → `collectstatic` → PyInstaller freeze (`backend/myphone.spec`)
→ Inno Setup (`installer/myphone_setup.iss`). Result:

```
dist_installer\MyPhoneERP-Setup.exe
```

## What ships / where data lives
- The frozen app goes to `C:\Program Files\MyPhoneERP\` (read-only).
- **All data is written to `%LOCALAPPDATA%\MyPhoneERP\`** — `db.sqlite3` (all records),
  `media\` (logo/uploads), `.activation` (install-key flag), `staticfiles\`.
  This survives uninstall/reinstall and is what the **Backup** feature zips.

## First run
1. Launch → browser opens `http://127.0.0.1:<port>/`.
2. **Activation** screen → enter `UFA_Dev_nest-123`.
3. Sign in with the seeded admin: **admin / admin123** (change it in Settings).

## Notes
- `.activation`, `db.sqlite3`, and build output are git-ignored and are **not**
  bundled, so every fresh install starts locked and demands the key.
- The app runs in the **system tray** (no console window). Right-click the tray
  icon for **Open My Phone ERP** / **Quit**. (Set `console=True` in `myphone.spec`
  if you want a visible server window for debugging.)
- Non-SQLite (Postgres) is still supported by setting a `DATABASE_URL` env var.
