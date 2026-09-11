# 📦 Mobile Shop ERP - Desktop Installer

## Overview

This project now includes a complete desktop application installer for Windows, built with Electron and Vite.

### Quick Links
- 🚀 **Quick Start:** [QUICK_START_INSTALLER.md](QUICK_START_INSTALLER.md)
- 📖 **Full Guide:** [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md)
- 🧪 **Test Report:** [TEST_REPORT.md](TEST_REPORT.md)

---

## What's Included

### Desktop Application
- ✅ Windows installer (.exe)
- ✅ Portable version (no installation)
- ✅ Auto-update ready
- ✅ Professional UI with Electron
- ✅ Native Windows integration (shortcuts, Start Menu)

### Package Contents
1. **Full Installer:** `Mobile Shop ERP-1.0.0.exe` (~180 MB)
   - Standard Windows installation
   - Desktop shortcut
   - Start Menu entry
   - Easy uninstall

2. **Portable Version:** `Mobile Shop ERP-1.0.0-portable.exe` (~180 MB)
   - No installation needed
   - USB-portable
   - No registry modifications

---

## Building the Installer

### Prerequisites
- Windows 7 or later
- Node.js 22.18+ or 24.12+
- 1 GB free disk space for build

### Quick Build
```bash
# Install dependencies (first time only)
npm install

# Build the installer
npm run electron-build
```

### Build Script
```bash
# Double-click: build-installer.bat
```

**Output:** Installers will be in `release/` folder

---

## Installation

### For End Users

1. **Download Installer**
   - Get `Mobile Shop ERP-1.0.0.exe`

2. **Run Installer**
   - Double-click the file
   - Follow the installation wizard
   - Takes 1-2 minutes

3. **Launch Application**
   - Click "Finish" to launch
   - Or find in Start Menu

### For Developers

```bash
# Development mode
npm run electron-dev

# Build web version
npm run build

# Build desktop app
npm run electron-build
```

---

## Project Structure

```
Mobile Shop ERP/
├── src/                          # Vue.js source code
│   ├── views/                    # Page components
│   ├── components/               # Reusable components
│   ├── stores/                   # Pinia stores
│   ├── api/                      # API clients
│   └── utils/                    # Utilities
├── electron/                     # Electron main process
│   ├── main.js                   # Main electron file
│   └── preload.js                # Security bridge
├── dist/                         # Built Vue app
├── public/                       # Static assets
├── assets/                       # Icons and images
├── build-installer.bat           # Build script
├── install-dependencies.bat      # Dependency installer
├── package.json                  # Project configuration
├── vite.config.js               # Vite configuration
└── README_INSTALLER.md          # This file
```

---

## NPM Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start web dev server (port 5174) |
| `npm run build` | Build web version to dist/ |
| `npm run preview` | Preview built web app |
| `npm run electron-dev` | Run app in electron (dev mode) |
| `npm run electron-build` | Build Windows installer |
| `npm run electron-pack` | Test package (no code sign) |
| `npm run dist` | Build for all platforms |

---

## Configuration

### Installer Settings
Edit `package.json` `build` section:

```json
{
  "build": {
    "appId": "com.mobileshop.erp",
    "productName": "Mobile Shop ERP",
    "win": {
      "target": ["nsis", "portable"]
    }
  }
}
```

### Custom Icon
1. Create 512x512 icon image
2. Save as `assets/icon.ico` (Windows)
3. Rebuild installer

### Installer Customization
Modify `package.json` → `build.nsis`:
```json
{
  "nsis": {
    "oneClick": false,
    "allowToChangeInstallationDirectory": true,
    "createDesktopShortcut": true
  }
}
```

---

## Features

### Core ERP System ✅
- **Dashboard** - Overview and analytics
- **Sales** - Invoice management and tracking
- **Inventory** - Product and stock management
- **Repairs** - Workshop job tracking
- **Customers** - Customer database
- **Reports** - Financial and business reports
- **Settings** - Configuration and admin panel

### Desktop-Specific Features ✅
- Native Windows integration
- System tray support (future)
- Local file access
- Offline functionality
- Print to PDF with professional templates
- Auto-updater ready

### Security ✅
- Context isolation enabled
- No node integration
- Sandbox mode enabled
- Secure IPC communication
- Data stored locally

---

## Troubleshooting

### Build Issues

**Error: "npm: command not found"**
- Install Node.js from nodejs.org
- Restart computer after installation

**Error: "Cannot find module 'electron'"**
```bash
npm install
npm install electron electron-builder --save-dev
```

**Build stuck or slow**
```bash
# Clear cache
npm cache clean --force

# Retry
npm install
npm run electron-build
```

### Installation Issues

**Windows Defender Warning**
- Click "More info"
- Click "Run anyway"
- This is normal for unsigned apps

**"Setup failed" error**
- Uninstall previous version
- Delete `C:\Program Files\Mobile Shop ERP\`
- Restart computer
- Reinstall

**Application won't launch**
- Uninstall completely
- Restart Windows
- Reinstall fresh

### Runtime Issues

**Slow performance**
- Close unnecessary apps
- Check available disk space
- Restart the application

**Data not saving**
- Check Windows permissions
- Ensure disk space available
- Check antivirus isn't blocking

---

## System Requirements

### Minimum
- OS: Windows 7 SP1+
- CPU: Intel Core 2 Duo
- RAM: 2 GB
- Disk: 500 MB free
- Display: 1024x768

### Recommended
- OS: Windows 10/11 (64-bit)
- CPU: Intel Core i5+
- RAM: 8 GB
- Disk: 1 GB free
- Display: 1920x1080

### No Additional Software Required
The installer includes everything needed - no Node.js, Python, or other runtime required!

---

## Distribution

### Sharing Your Installer

1. **Direct Download:**
   - Host on your website
   - Host on cloud storage
   - Share via USB drive

2. **Portable Version:**
   - Portable version can run from USB
   - No installation needed
   - Perfect for mobile deployment

3. **Update Strategy:**
   - Current: Manual updates
   - Future: Auto-update mechanism built-in

---

## Development Roadmap

### ✅ Completed
- [x] Desktop application setup
- [x] Windows installer
- [x] Portable version
- [x] Full ERP system
- [x] Invoice printing
- [x] Multi-user support

### 🔄 Planned
- [ ] Auto-update system
- [ ] Mac/Linux builds
- [ ] System tray integration
- [ ] Advanced offline sync
- [ ] Cloud backup integration
- [ ] Mobile app companion

---

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit pull request

### Development Setup
```bash
git clone <repository>
cd "Mobile Shop Inventry system"
npm install
npm run dev
```

---

## License

This project is licensed under the MIT License. See LICENSE file for details.

---

## Support & Feedback

### Getting Help
1. Check [INSTALLER_GUIDE.md](INSTALLER_GUIDE.md) for detailed help
2. Review [QUICK_START_INSTALLER.md](QUICK_START_INSTALLER.md) for quick setup
3. Check [TEST_REPORT.md](TEST_REPORT.md) for system status

### Reporting Issues
- Create an issue on GitHub
- Include error messages
- Describe steps to reproduce
- Mention your Windows version

### Feature Requests
- Open feature request issue
- Describe desired functionality
- Explain use case

---

## Version History

### Version 1.0.0 (Current)
- ✅ Initial desktop release
- ✅ Complete ERP system
- ✅ Windows installer & portable
- ✅ Professional UI/UX
- ✅ All core features

**Release Date:** September 10, 2026  
**Build Date:** September 10, 2026  
**Platform:** Windows 7+  

---

## Contact & Resources

- **Website:** https://mobileshop.local
- **Email:** support@mobileshop.local
- **Phone:** +92-XXX-XXXXXXX
- **Documentation:** See included .md files

---

## Acknowledgments

Built with:
- Vue.js 3
- Vite
- Electron
- Tailwind CSS
- Node.js

---

**Ready to deploy your ERP system? Follow the Quick Start guide above! 🚀**
