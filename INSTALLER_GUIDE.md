# 📦 Mobile Shop ERP - Installer Guide

## Complete Setup & Installation Instructions

---

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Installation Options](#installation-options)
3. [Building the Installer](#building-the-installer)
4. [Installation Steps](#installation-steps)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 7 or later (32-bit or 64-bit)
- **Processor:** Intel Core 2 Duo or equivalent
- **RAM:** 2 GB minimum (4 GB recommended)
- **Disk Space:** 500 MB for installation
- **Display:** 1024x768 minimum resolution

### Recommended Requirements
- **OS:** Windows 10 or Windows 11 (64-bit)
- **Processor:** Intel Core i5 or better
- **RAM:** 8 GB or more
- **Disk Space:** 1 GB available
- **Display:** 1920x1080 or higher
- **Internet:** For updates and online features

### Software Requirements
- None! The application is self-contained and doesn't require Node.js, Python, or any external runtime.

---

## Installation Options

### Option 1: Standard Installer (Recommended)
- **File:** `Mobile Shop ERP-1.0.0.exe`
- **Size:** ~180 MB
- **Features:**
  - Full installation with setup wizard
  - Desktop shortcut creation
  - Start Menu entry
  - Easy uninstallation via Control Panel
  - Automatic updates support

### Option 2: Portable Version
- **File:** `Mobile Shop ERP-1.0.0-portable.exe`
- **Size:** ~180 MB
- **Features:**
  - No installation required
  - Run directly from USB drive
  - No registry modifications
  - Portable folder-based configuration

---

## Building the Installer

### Step 1: Install Node.js
1. Download Node.js from: https://nodejs.org/
2. Choose LTS version (22.18+ or 24.12+)
3. Run the installer and follow the prompts
4. Restart your computer

### Step 2: Prepare the Project
```bash
# Navigate to project directory
cd "D:\Projects\Mobile Shop Inventry system"

# Install all dependencies
npm install
```

### Step 3: Build the Installer

**Option A: Using Batch Script (Easiest)**
```bash
# Double-click: build-installer.bat
```

**Option B: Using NPM Commands**
```bash
# Build web version
npm run build

# Build installer
npm run electron-build

# Or build for all platforms
npm run dist
```

### Step 4: Locate the Installer
The compiled installers will be in: `release/` folder

```
release/
├── Mobile Shop ERP-1.0.0.exe          (Standard installer)
├── Mobile Shop ERP-1.0.0-portable.exe (Portable version)
└── Mobile Shop ERP-1.0.0.exe.blockmap
```

---

## Installation Steps

### For Standard Installer (.exe)

1. **Download/Locate the Installer**
   - Find `Mobile Shop ERP-1.0.0.exe`
   - Verify file size (~180 MB)

2. **Run the Installer**
   - Double-click the `.exe` file
   - If prompted by Windows Defender, click "More info" → "Run anyway"

3. **Welcome Screen**
   - Review application information
   - Click "Next" to continue

4. **License Agreement**
   - Read the license terms
   - Click "I Agree" to accept
   - Click "Next"

5. **Installation Location**
   - Default: `C:\Program Files\Mobile Shop ERP`
   - Change location if desired (optional)
   - Click "Next"

6. **Additional Tasks**
   - ✓ Create a desktop shortcut
   - ✓ Create Start Menu folder
   - Click "Next"

7. **Installation Progress**
   - Wait for installation to complete
   - This typically takes 1-2 minutes

8. **Completion**
   - Check "Launch Mobile Shop ERP"
   - Click "Finish"

9. **First Launch**
   - Application will open automatically
   - Dashboard will load with sample data
   - You're ready to use!

### For Portable Version

1. **Extract the File**
   - Right-click `Mobile Shop ERP-1.0.0-portable.exe`
   - Select "Extract here" (if archive tool available)
   - Or simply run the `.exe` directly

2. **Run the Application**
   - Double-click the executable
   - No installation required
   - Application launches immediately

3. **Optional: Create Shortcut**
   - Right-click the `.exe` → "Create shortcut"
   - Place shortcut on Desktop or Start Menu
   - Double-click to launch anytime

---

## Configuration

### Initial Setup

1. **Company Settings**
   - Go to Settings → Company
   - Enter your shop name
   - Add contact information
   - Set default currency (PKR)
   - Save changes

2. **Tax Settings**
   - Go to Settings → Tax
   - Configure tax rates for products
   - Set default tax calculation method
   - Save configuration

3. **User Management** (Admin only)
   - Go to Settings → Users
   - Create staff accounts
   - Assign roles and permissions
   - Set user passwords

4. **Role Configuration** (Admin only)
   - Go to Settings → Roles
   - Define user roles (Admin, Manager, Staff)
   - Set permissions for each role
   - Apply role-based access control

### Data Import/Export

**Backup Your Data:**
```bash
# Data is stored in: C:\Users\[Username]\AppData\Local\Mobile Shop ERP\
# Location varies by Windows version
```

**Export Data:**
- Use Export feature in each module (Sales, Inventory, etc.)
- Save to CSV or Excel format
- Keep regular backups

---

## Troubleshooting

### Issue: "Windows protected your PC"

**Solution:**
1. Click "More info"
2. Click "Run anyway"
3. App will launch normally

This is normal for unsigned applications. To remove this warning, sign the executable (requires code signing certificate).

### Issue: Application Won't Start

**Solution:**
1. Uninstall the application
2. Restart your computer
3. Reinstall using the installer

### Issue: Slow Performance

**Solution:**
- Close unnecessary applications
- Increase available RAM
- Check disk space (ensure at least 500 MB free)
- Restart the application

### Issue: Data Not Saving

**Solution:**
1. Check disk permissions
2. Ensure enough disk space
3. Try restarting the application
4. Reinstall if problem persists

### Issue: Installer Download Corrupted

**Solution:**
1. Delete the downloaded file
2. Re-download from source
3. Verify file size matches expected (~180 MB)
4. Use checksum verification if available

### Getting Help

1. **Check the Help Menu**
   - App Menu → Help → About
   - Review built-in documentation

2. **Online Documentation**
   - Visit project wiki
   - Check troubleshooting guide

3. **Support Contact**
   - Email: support@mobileshop.local
   - Phone: +92-XXX-XXXXXXX

---

## Uninstallation

### Remove from Windows

1. **Using Control Panel:**
   - Press `Win + R`
   - Type `control panel`
   - Go to Programs → Programs and Features
   - Find "Mobile Shop ERP"
   - Click "Uninstall"
   - Follow the uninstall wizard

2. **Using Settings:**
   - Press `Win + I` to open Settings
   - Go to Apps → Apps & features
   - Search for "Mobile Shop ERP"
   - Click and select "Uninstall"

### Remove Application Data

**Important:** This will delete all stored data!

1. **Locate data folder:**
   ```
   C:\Users\[YourUsername]\AppData\Local\Mobile Shop ERP\
   ```

2. **Delete the folder:**
   - Right-click the folder
   - Select "Delete"
   - Confirm deletion

3. **Clear Start Menu:**
   - Right-click "Mobile Shop ERP" in Start Menu
   - Click "Uninstall"

4. **Remove Desktop Shortcut:**
   - Right-click the desktop shortcut
   - Select "Delete"

---

## Upgrading to New Versions

### Automatic Updates (Future Versions)
1. Application will notify you of available updates
2. Click "Update" when prompted
3. Application will download and install
4. Restart to apply updates

### Manual Updates
1. Download new installer version
2. Run the installer
3. Select "Upgrade existing installation"
4. Application will update preserving your data

---

## System Integration

### Desktop Shortcut
- Automatically created during installation
- Located on your Desktop
- Double-click to launch anytime

### Start Menu
- Automatically added to Start Menu
- Search for "Mobile Shop ERP" in Windows Search
- Pin to taskbar for quick access

### Command Line Launch
```bash
# If installed in default location:
"C:\Program Files\Mobile Shop ERP\Mobile Shop ERP.exe"
```

---

## Performance Optimization

### For Optimal Performance:

1. **System Level:**
   - Keep Windows updated
   - Disable unnecessary background apps
   - Ensure adequate disk space (>500 MB free)

2. **Application Level:**
   - Regular data backups
   - Clear cache periodically
   - Restart application daily
   - Update to latest version

3. **Network (Optional):**
   - Ensure stable internet connection
   - For offline use, use mock API mode
   - Sync data when connection available

---

## Version Information

**Current Version:** 1.0.0  
**Release Date:** September 10, 2026  
**Platform:** Windows (7, 8, 10, 11)  
**Architecture:** 64-bit and 32-bit support  

### Changelog
- ✅ Initial Release
- ✅ Complete ERP System
- ✅ Invoice Management
- ✅ Inventory Tracking
- ✅ Sales Management
- ✅ Repair Workshop
- ✅ Financial Reports
- ✅ Multi-user Support
- ✅ Role-based Access Control
- ✅ Invoice Printing

---

## License & Legal

**License:** MIT License  
**Copyright:** 2026 DEVNEST Dev  

This software is provided "as-is" without any warranty. Users are responsible for maintaining backups of their data.

---

## Support & Feedback

For issues, feature requests, or feedback:
- **Email:** support@mobileshop.local
- **Web:** https://mobileshop.local/support
- **Phone:** +92-XXX-XXXXXXX

---

## FAQ

**Q: Can I use this on Mac or Linux?**  
A: Currently Windows only. Mac and Linux versions may be added in future releases.

**Q: Is internet required?**  
A: No. The application works completely offline with mock API.

**Q: Where is my data stored?**  
A: Local storage in `AppData\Local\Mobile Shop ERP\`

**Q: Can I run multiple instances?**  
A: Yes, but not simultaneously on the same user account.

**Q: How do I backup my data?**  
A: Use Export feature or copy the AppData folder.

**Q: Is my data secure?**  
A: Data is stored locally. Ensure your Windows user account is password protected.

---

**Happy invoicing! 🎉**

For the latest updates and support, visit our website or contact support.
