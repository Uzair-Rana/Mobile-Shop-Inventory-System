@echo off
REM Mobile Shop ERP - Build Installer Script
REM This script builds the Windows installer (.exe)

setlocal enabledelayedexpansion

echo.
echo ======================================
echo Mobile Shop ERP - Installer Builder
echo ======================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if npm dependencies are installed
if not exist "node_modules" (
    echo [INFO] Dependencies not found. Installing...
    call npm install
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

echo [INFO] Building Vue.js application...
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build application
    pause
    exit /b 1
)

echo.
echo [INFO] Building Windows installer...
echo This may take several minutes...
echo.

call npm run electron-build
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build installer
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Installer built successfully!
echo.
echo The installer is located in: release\ folder
echo.
echo Files created:
echo   - Mobile Shop ERP-1.0.0.exe (Full installer)
echo   - Mobile Shop ERP-1.0.0-portable.exe (Portable version)
echo.
pause
