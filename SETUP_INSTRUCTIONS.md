# 🎯 Setup Instructions - Complete Guide

## Complete Setup & Build Process

---

## Table of Contents
1. [Pre-Installation](#pre-installation)
2. [Initial Setup](#initial-setup)
3. [Building Installer](#building-installer)
4. [Distribution](#distribution)
5. [Support](#support)

---

## Pre-Installation

### Check Your System

**Windows Version:**
```bash
# Press: Windows Key + R
# Type: winver
# Check: Windows 7 or later
```

**Storage Space:**
```bash
# You need at least:
- 2 GB for build process
- 500 MB for installed app
- 1 GB recommended free space
```

**Internet Connection:**
- Required for downloading dependencies
- Not needed for running the app

---

## Initial Setup

### Step 1: Install Node.js

1. **Download Node.js**
   - Go to: https://nodejs.org/
   - Download LTS version (22.18+ or 24.12+)
   - Choose Windows Installer (.msi)

2. **Run the Installer**
   - Double-click the `.msi` file
   - Click "Install"
   - Accept default settings
   - Click "Finish"

3. **Verify Installation**
   ```bash
   # Press: Windows Key + R
   # Type: cmd
   # Run this command:
   node -v
   # Should show: v22.x.x or higher
   ```

4. **Restart Computer**
   - Restart Windows to ensure PATH is updated

### Step 2: Prepare Project Folder

```bash
# Option A: If not already in project
# 1. Open File Explorer
# 2. Navigate to: D:\Projects\Mobile Shop Inventry system

# Option B: Using Command Prompt
cd "D:\Projects\Mobile Shop Inventry system"
```

### Step 3: Install Dependencies

**Method 1: Using Batch Script (Easiest)**
```bash
# Double-click: install-dependencies.bat
# Wait for it to complete
```

**Method 2: Using Command Prompt**
```bash
# Open Command Prompt in project folder
# Run:
npm install

# Wait (may take 5-10 minutes)
# Should end with "added X packages"
```

**Verify Installation:**
```bash
# Check if node_modules folder exists
# Should be ~500 MB in size
```

---

## Building Installer

### Method 1: Using Batch Script (Recommended)

1. **Open File Explorer**
   - Navigate to project folder
   - Find `build-installer.bat`

2. **Run the Script**
   - Double-click `build-installer.bat`
   - A Command Prompt window will open
   - Follow the prompts

3. **Wait for Completion**
   - Building takes 5-15 minutes
   - You'll see progress messages
   - Final message: "SUCCESS"

4. **Find Your Installers**
   - Open `release/` folder
   - You'll see:
     ```
     Mobile Shop ERP-1.0.0.exe (Standard)
     Mobile Shop ERP-1.0.0-portable.exe (Portable)
     ```

### Method 2: Using Command Prompt

```bash
# 1. Open Command Prompt
# Press: Windows Key + R
# Type: cmd
# Press: Enter

# 2. Navigate to project
cd "D:\Projects\Mobile Shop Inventry system"

# 3. Build the installer
npm run electron-build

# 4. Wait for completion (5-15 minutes)
# Success message will appear

# 5. Check release folder
dir release
```

### Method 3: Build Web-Only Version

```bash
# For web browser version only:
npm run build

# Output: dist/ folder
# Can be deployed to web server
```

---

## What Gets Built

### Standard Installer
- **File:** `Mobile Shop ERP-1.0.0.exe`
- **Size:** ~180 MB
- **Type:** Windows NSIS Installer
- **Features:**
  - Full installation wizard
  - Desktop shortcut creation
  - Start Menu entry
  - Easy uninstall via Control Panel
  - Registry entries
  - Windows integration

### Portable Version
- **File:** `Mobile Shop ERP-1.0.0-portable.exe`
- **Size:** ~180 MB
- **Type:** Self-extracting executable
- **Features:**
  - No installation required
  - Can run from USB drive
  - No registry changes
  - No Start Menu entry
  - Can delete app folder to uninstall

---

## Distribution

### Sharing the Installer

**Option 1: Direct Distribution**
```bash
# Copy these files:
- Mobile Shop ERP-1.0.0.exe
- Mobile Shop ERP-1.0.0-portable.exe

# Send via:
- Email (attachment or link)
- Cloud storage (Google Drive, Dropbox, OneDrive)
- USB drive
- FTP/Web server
```

**Option 2: Create Installation Media**
```bash
# USB Drive Installation:
1. Copy .exe file to USB drive
2. Give USB to end user
3. They plug in USB
4. Double-click .exe to install
```

**Option 3: Network Distribution**
```bash
# Company Network:
1. Place .exe on network share
2. Users run from \\server\software\
3. Installs to their local machines
```

### File Delivery Checklist
- [ ] Include installer (.exe)
- [ ] Include INSTALLER_GUIDE.md
- [ ] Include QUICK_START_INSTALLER.md
- [ ] Include support contact info
- [ ] Include system requirements

---

## Post-Installation

### For End Users

1. **After Installation**
   - Click "Finish" to launch app
   - Dashboard appears with sample data
   - Ready to use immediately

2. **Initial Configuration**
   - Go to Settings → Company
   - Enter your shop information
   - Configure tax settings
   - Create user accounts

3. **Start Using**
   - Create first invoice
   - Add products
   - Manage inventory
   - View reports

### For Administrators

1. **User Setup**
   - Settings → Users
   - Create staff accounts
   - Assign roles
   - Set permissions

2. **Data Configuration**
   - Import products
   - Set tax rates
   - Configure payment methods
   - Customize forms

3. **Backup Setup**
   - Regular data backups
   - Export important data
   - Document procedures

---

## Troubleshooting

### Build Fails

**"npm: command not found"**
```bash
# Node.js not installed
# Solution:
# 1. Download and install Node.js from nodejs.org
# 2. Restart computer
# 3. Try again
```

**"Cannot find module"**
```bash
# Dependencies not installed
# Solution:
cd "D:\Projects\Mobile Shop Inventry system"
npm install
npm run electron-build
```

**"NSIS error"**
```bash
# Windows installer creation failed
# Solution:
# 1. Delete dist folder: rmdir dist /s /q
# 2. Delete node_modules: rmdir node_modules /s /q
# 3. Clear cache: npm cache clean --force
# 4. Reinstall: npm install
# 5. Rebuild: npm run electron-build
```

**Build Takes Too Long**
- Normal: 5-15 minutes first time
- Check: Computer not overloaded
- Try: Close other applications
- Restart: Restart build process if stuck >30 min

### Installation Issues

**Windows Defender Blocks Installer**
- Click: "More info"
- Click: "Run anyway"
- Note: This is normal for unsigned apps

**Installation Hangs**
- Wait: Can take 2-3 minutes
- Restart: Close and retry
- Check: Disk space available

**App Won't Launch**
- Uninstall completely
- Delete: `C:\Program Files\Mobile Shop ERP\`
- Restart Windows
- Reinstall fresh

---

## Customization

### Change App Name
```json
// In package.json:
{
  "name": "your-app-name",
  "build": {
    "productName": "Your App Name"
  }
}
```

### Change App Icon
1. Create 512x512 PNG image
2. Convert to .ico format
3. Save as: `assets/icon.ico`
4. Rebuild installer

### Change Installer Settings
```json
// In package.json build.nsis:
{
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true
  }
}
```

---

## Advanced Options

### Build for Multiple Platforms
```bash
# Requires additional setup
# Builds Windows, Mac, Linux simultaneously:
npm run dist
```

### Build without Code Signing
```bash
# Faster build, no signing:
npm run electron-pack
```

### Clean Build
```bash
# Remove all build artifacts
rmdir dist /s /q
rmdir release /s /q
rmdir node_modules /s /q
npm cache clean --force

# Rebuild fresh
npm install
npm run electron-build
```

---

## Verification Checklist

After building, verify:

- [ ] Build completed without errors
- [ ] `release/` folder contains .exe files
- [ ] File size approximately 180 MB
- [ ] Installer runs without Windows Defender warning
- [ ] Installation completes successfully
- [ ] App launches and loads dashboard
- [ ] All menu items work
- [ ] Settings pages accessible
- [ ] Invoice printing works
- [ ] Data displays correctly

---

## System Performance

### Build System Requirements
- **Disk:** 2 GB free minimum
- **RAM:** 4 GB minimum
- **CPU:** Dual core or better
- **Time:** 5-15 minutes

### Runtime Requirements
- **Disk:** 500 MB installation
- **RAM:** 512 MB minimum (2 GB recommended)
- **Display:** 1024x768 minimum

---

## Getting Help

### Documentation
1. **Quick Start:** QUICK_START_INSTALLER.md
2. **Detailed Guide:** INSTALLER_GUIDE.md
3. **Test Report:** TEST_REPORT.md

### Support Resources
- Email: support@mobileshop.local
- Phone: +92-XXX-XXXXXXX
- Web: https://mobileshop.local/support

### Common Issues
- **Windows blocks installer:** Click "Run anyway"
- **Installation slow:** Normal, be patient
- **App won't start:** Uninstall and reinstall
- **Disk full:** Free up space and retry

---

## Next Steps

1. ✅ Install Node.js
2. ✅ Run install-dependencies.bat
3. ✅ Run build-installer.bat
4. ✅ Share installers with users
5. ✅ Guide users through installation
6. ✅ Help with configuration
7. ✅ Collect feedback
8. ✅ Plan updates

---

## Version Information

**Current Version:** 1.0.0  
**Build Date:** September 10, 2026  
**Platform:** Windows 7+  
**Architecture:** 32-bit & 64-bit  
**File Size:** ~180 MB  

---

**You're all set! Your ERP system is ready for deployment! 🎉**

For questions or issues, refer to the included documentation or contact support.
