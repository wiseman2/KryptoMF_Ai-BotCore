# Building Executables

This guide explains how to build standalone executables for non-technical users who don't have Python installed.

## 📦 What Gets Built

### CLI Executable (Open Source)
- **File**: `KryptoMF-Bot.exe` (Windows) or `KryptoMF-Bot` (Mac/Linux)
- **Size**: ~50-80 MB
- **Includes**: Core bot engine, all strategies, exchange connectors
- **Excludes**: GUI components
- **Mode**: Console application

### GUI Executable (Premium)
- **File**: `KryptoMF-Bot-GUI.exe` (Windows) or `KryptoMF-Bot-GUI` (Mac/Linux)
- **Size**: ~100-150 MB
- **Includes**: Everything in CLI + Premium GUI
- **Mode**: Windowed application (no console)

## 🛠️ Prerequisites

Install PyInstaller:
```bash
pip install pyinstaller
```

## 🏗️ Building

### Build CLI Executable (Open Source)

```bash
cd Public/KryptoMF_Ai-BotCore
pyinstaller build.spec
```

Output: `dist/KryptoMF-Bot.exe`

### Build GUI Executable (Premium)

```bash
cd Public/KryptoMF_Ai-BotDashboard
pyinstaller build_gui.spec
```

Output: `dist/KryptoMF-Bot-GUI.exe`

## 📋 Build Options

### One-File vs One-Folder

**Current**: One-file (easier distribution)
- ✅ Single executable
- ✅ Easy to distribute
- ❌ Slower startup (extracts to temp)

**Alternative**: One-folder (faster startup)
```python
# In .spec file, change EXE() to:
exe = EXE(
    pyz,
    a.scripts,
    [],  # Don't bundle everything
    exclude_binaries=True,  # Keep separate
    ...
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KryptoMF-Bot',
)
```

### UPX Compression

**Current**: Enabled (smaller file size)
- ✅ Smaller executable (~30% reduction)
- ❌ Slower startup
- ❌ May trigger antivirus

**Disable** for faster startup:
```python
# In .spec file:
upx=False,
```

## 🎨 Adding an Icon

1. Create icon files:
   - Windows: `icon.ico` (256x256)
   - Mac: `icon.icns`
   - Linux: `icon.png`

2. Update `.spec` file:
   ```python
   exe = EXE(
       ...
       icon='path/to/icon.ico',
   )
   ```

## 🔐 Code Signing (Recommended for Distribution)

### Windows

```bash
# Get a code signing certificate
# Then sign the executable:
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist/KryptoMF-Bot-GUI.exe
```

### macOS

```bash
# Sign with Apple Developer certificate
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/KryptoMF-Bot-GUI.app

# Notarize for Gatekeeper
xcrun altool --notarize-app --primary-bundle-id "com.kryptomf.bot" --username "your@email.com" --password "@keychain:AC_PASSWORD" --file dist/KryptoMF-Bot-GUI.zip
```

## 📦 Distribution

### Windows

**Option 1**: Standalone EXE
- Upload `KryptoMF-Bot-GUI.exe` to website
- Users download and run

**Option 2**: Installer (NSIS/Inno Setup)
```nsis
; installer.nsi
!define APP_NAME "KryptoMF Bot"
!define APP_VERSION "1.0.0"

OutFile "KryptoMF-Bot-Setup.exe"
InstallDir "$PROGRAMFILES\KryptoMF Bot"

Section "Install"
    SetOutPath $INSTDIR
    File "dist\KryptoMF-Bot-GUI.exe"
    CreateShortcut "$DESKTOP\KryptoMF Bot.lnk" "$INSTDIR\KryptoMF-Bot-GUI.exe"
SectionEnd
```

### macOS

**Option 1**: DMG Image
```bash
# Create .app bundle
pyinstaller build_gui.spec --windowed

# Create DMG
hdiutil create -volname "KryptoMF Bot" -srcfolder dist/KryptoMF-Bot-GUI.app -ov -format UDZO KryptoMF-Bot-GUI.dmg
```

**Option 2**: PKG Installer
```bash
pkgbuild --root dist/KryptoMF-Bot-GUI.app --identifier com.kryptomf.bot --version 1.0.0 --install-location /Applications KryptoMF-Bot-GUI.pkg
```

### Linux

**Option 1**: AppImage
```bash
# Use appimagetool
appimagetool dist/KryptoMF-Bot-GUI KryptoMF-Bot-GUI.AppImage
```

**Option 2**: DEB Package
```bash
# Create debian package structure
mkdir -p kryptomf-bot_1.0.0/usr/bin
cp dist/KryptoMF-Bot-GUI kryptomf-bot_1.0.0/usr/bin/
dpkg-deb --build kryptomf-bot_1.0.0
```

## 🚀 Automated Builds (CI/CD)

### GitHub Actions

Create `.github/workflows/build.yml`:

```yaml
name: Build Executables

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller build_gui.spec
      - uses: actions/upload-artifact@v3
        with:
          name: KryptoMF-Bot-Windows
          path: dist/KryptoMF-Bot-GUI.exe

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller build_gui.spec
      - run: hdiutil create -volname "KryptoMF Bot" -srcfolder dist/KryptoMF-Bot-GUI.app -ov -format UDZO KryptoMF-Bot-GUI.dmg
      - uses: actions/upload-artifact@v3
        with:
          name: KryptoMF-Bot-macOS
          path: KryptoMF-Bot-GUI.dmg

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller build_gui.spec
      - uses: actions/upload-artifact@v3
        with:
          name: KryptoMF-Bot-Linux
          path: dist/KryptoMF-Bot-GUI
```

## 🧪 Testing Executables

### Before Distribution

1. **Test on clean machine** (no Python installed)
2. **Test all features**:
   - Bot creation
   - Exchange connection
   - Strategy execution
   - Paper trading
   - Configuration save/load
3. **Test antivirus compatibility**:
   - Upload to VirusTotal
   - Test with Windows Defender
   - Test with common AV software
4. **Test on different OS versions**:
   - Windows 10, 11
   - macOS 11, 12, 13
   - Ubuntu 20.04, 22.04

## 📊 File Sizes (Approximate)

| Build | Windows | macOS | Linux |
|-------|---------|-------|-------|
| CLI | 60 MB | 65 MB | 70 MB |
| GUI | 120 MB | 130 MB | 125 MB |

## 🐛 Troubleshooting

### "Failed to execute script"
- Missing hidden imports
- Add to `hiddenimports` in `.spec` file

### "DLL load failed"
- Missing binary dependencies
- Add to `binaries` in `.spec` file

### Antivirus false positive
- Code sign the executable
- Submit to antivirus vendors for whitelisting
- Disable UPX compression

### Large file size
- Enable UPX compression
- Exclude unnecessary modules
- Use one-folder mode

## 📝 Release Checklist

- [ ] Update version number in code
- [ ] Build executables for all platforms
- [ ] Code sign executables
- [ ] Test on clean machines
- [ ] Create release notes
- [ ] Upload to website/GitHub releases
- [ ] Update download links
- [ ] Announce release

## 🔗 Resources

- [PyInstaller Documentation](https://pyinstaller.org/)
- [Code Signing Guide](https://pyinstaller.org/en/stable/usage.html#code-signing)
- [NSIS Installer](https://nsis.sourceforge.io/)
- [Inno Setup](https://jrsoftware.org/isinfo.php)

