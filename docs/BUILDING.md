# Building SoPDF Executable

This guide explains how to create a standalone .exe file for SoPDF on Windows.

## Quick Build (Recommended)

### Option 1: Using Batch File (Easiest)
1. Double-click `build.bat`
2. Wait for the build process to complete
3. Find your `SoPDF.exe` in the `dist/` folder

### Option 2: Using Python Script
```bash
# Install build dependencies
pip install -r requirements-build.txt

# Run build script
python build.py
```

## Manual Build (Advanced)

If you prefer to run PyInstaller manually:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed --name=SoPDF --icon=assets/SoPDF_icon.ico --add-data=assets;assets --add-data=docs;docs --hidden-import=customtkinter --hidden-import=PIL --hidden-import=pdf2image --hidden-import=PyPDF2 run.py
```

## Build Optimization

### Size Optimization
The build script automatically applies several optimizations:
- Excludes unnecessary modules (`test`, `unittest`, `pydoc`, etc.)
- Uses Python optimization level 2
- Strips debug symbols
- Creates a single-file executable

### UPX Compression (Optional)
For even smaller executables, install UPX:

1. Download UPX from https://upx.github.io/
2. Extract to a folder in your PATH
3. Run the build script again - it will automatically detect and use UPX

UPX can reduce file size by 50-70% with minimal performance impact.

## Build Outputs

After building, you'll find:
- `dist/SoPDF.exe` - Your standalone executable
- `build/` - Temporary build files (can be deleted)
- `SoPDF.spec` - PyInstaller specification file

## Distribution

### What to Include
When distributing your application:
- `SoPDF.exe` (required)
- `docs/INSTALL_POPPLER.md` (recommended for PDF preview functionality)
- Any custom documentation

### System Requirements for End Users
- Windows 10 or later
- No Python installation required
- Poppler (optional, for PDF previews)

## Troubleshooting

### Common Build Issues

**"Module not found" errors during build:**
```bash
pip install -r requirements-build.txt
```

**Missing icon error:**
- Ensure `assets/SoPDF_icon.ico` exists
- Or remove the `--icon` parameter from the build command

**Large executable size:**
- Install UPX for compression
- Review the exclude list in `build.py`
- Consider using `--onedir` instead of `--onefile` for faster startup

**Application won't start after building:**
- Test with `--onedir` first to isolate issues
- Check for missing hidden imports
- Ensure all data files are included with `--add-data`

### Size Comparison
- **Basic build**: ~15-25 MB
- **With UPX compression**: ~8-15 MB
- **One-directory mode**: Larger total size but faster startup

## Advanced Configuration

### Custom Build Settings
Edit `build.py` to customize:
- Add more `--exclude-module` entries
- Include additional data files
- Modify compression settings
- Add version information

### Creating an Installer
For professional distribution, consider using:
- **Inno Setup** (free, Windows)
- **NSIS** (free, Windows)
- **WiX Toolset** (free, Windows)

These can create proper installers with uninstall capabilities. 