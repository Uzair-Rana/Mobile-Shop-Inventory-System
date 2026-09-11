# 🚀 Quick Start - Build Installer

## 60-Second Setup

### Step 1: Install Node.js (One Time)
1. Download from: https://nodejs.org/ (LTS version 22+)
2. Run installer and finish setup
3. Restart computer

### Step 2: Build Installer

**Windows Users - Easiest Method:**
```bash
# 1. Open Command Prompt in project folder
# 2. Run this file (double-click):
build-installer.bat
```

**Or use Terminal:**
```bash
# Install dependencies (first time only)
npm install

# Build installer
npm run electron-build
```

### Step 3: Find Your Installer
✅ Look in: `release/` folder

```
Mobile Shop ERP-1.0.0.exe          ← Full installer
Mobile Shop ERP-1.0.0-portable.exe ← Portable version
```

---

## What You Get

### Standard Installer
- ✅ Full installation with wizard
- ✅ Desktop shortcut
- ✅ Start Menu entry
- ✅ Easy uninstall via Control Panel
- Size: ~180 MB

### Portable Version
- ✅ No installation needed
- ✅ Run from USB
- ✅ No registry changes
- Size: ~180 MB

---

## Installation

1. **Download the installer**
   - `Mobile Shop ERP-1.0.0.exe`

2. **Run it**
   - Double-click the file

3. **Follow the wizard**
   - Accept license
   - Choose installation location
   - Create shortcuts

4. **Launch**
   - Click "Finish"
   - App starts automatically

---

## What's Inside

✅ **Complete ERP System**
- Dashboard with analytics
- Invoice management
- Inventory tracking
- Sales module
- Repair workshop
- Financial reports
- User management
- Print functionality

✅ **Features**
- Multi-user support
- Role-based access control
- Real-time data sync
- Offline mode support
- Invoice printing to PDF
- Professional UI/UX

✅ **Data**
- Sample invoices
- Sample products
- Sample customers
- Ready to use immediately

---

## Troubleshooting

### Windows Protected Message
- Click "More info"
- Click "Run anyway"
- Continue normally

### Build Fails
```bash
# 1. Delete node_modules
rmdir node_modules /s /q

# 2. Clear npm cache
npm cache clean --force

# 3. Reinstall
npm install

# 4. Build again
npm run electron-build
```

### File Not Found
- Ensure you're in the correct directory
- Check build-installer.bat is in project root
- Check Node.js is installed (run: node -v)

---

## Advanced Options

### Build Web Version Only
```bash
npm run build
# Output: dist/ folder
```

### Dev Mode (Testing)
```bash
npm run electron-dev
# Opens app in development mode with DevTools
```

### Build for Multiple Platforms
```bash
npm run dist
# Builds for Windows, Mac, Linux
```

---

## System Requirements

- **OS:** Windows 7+ (64-bit or 32-bit)
- **RAM:** 2 GB minimum
- **Disk:** 500 MB free space
- **Display:** 1024x768 minimum

---

## Next Steps

1. ✅ Install the application
2. ✅ Launch and explore dashboard
3. ✅ Configure settings (Company, Tax, Users)
4. ✅ Create your first invoice
5. ✅ Print and test invoice

---

## Support

📖 Full guide: See `INSTALLER_GUIDE.md`  
💬 Need help? Check troubleshooting section above

---

**That's it! You now have a professional ERP system installed and ready to use! 🎉**
