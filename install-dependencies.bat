@echo off
REM Mobile Shop ERP - Install Dependencies Script
REM This script installs all required Node.js dependencies

echo.
echo ======================================
echo Mobile Shop ERP - Dependency Installer
echo ======================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo [OK] Node.js is installed:
node --version

echo.
echo [INFO] Installing npm dependencies...
echo This may take a few minutes...
echo.

call npm install

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [SUCCESS] All dependencies installed successfully!
echo.
echo You can now:
echo   - Run development: npm run dev
echo   - Build web version: npm run build
echo   - Build desktop app: npm run electron-build
echo.
pause
