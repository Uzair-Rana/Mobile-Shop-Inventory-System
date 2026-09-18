@echo off
REM ===================================================================
REM  One-click build for the My Phone ERP Windows installer.
REM  Requires: Python 3.11+ and Inno Setup 6 (iscc on PATH or default dir).
REM ===================================================================
setlocal
cd /d "%~dp0backend"

echo [1/5] Installing Python dependencies...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt || goto :err

echo [2/5] Collecting static files...
set DJANGO_SETTINGS_MODULE=devnest.settings
python manage.py collectstatic --noinput || goto :err

echo [3/5] Building the app with PyInstaller...
python -m PyInstaller myphone.spec --noconfirm --clean || goto :err

echo [4/5] Building the installer with Inno Setup...
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% set ISCC=iscc
%ISCC% "..\installer\myphone_setup.iss" || goto :err

echo [5/5] Done.
echo Installer created in:  dist_installer\MyPhoneERP-Setup.exe
goto :eof

:err
echo.
echo BUILD FAILED. See the error above.
exit /b 1
