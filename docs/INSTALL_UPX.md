# Installing UPX for Smaller Executables

UPX can compress your SoPDF.exe by 50-70%, reducing it from ~20MB to ~8-12MB.

## Installation Options

### Option 1: Direct Download
1. Go to https://github.com/upx/upx/releases
2. Download the latest Windows version (e.g., `upx-4.2.2-win64.zip`)
3. Extract to a folder like `C:\upx\`
4. Add `C:\upx\` to your system PATH:
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → "Environment Variables"
   - Under "System Variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\upx`
   - Click "OK" to save

### Option 2: Using Chocolatey (if installed)
```bash
choco install upx
```

### Option 3: Using Scoop (if installed)
```bash
scoop install upx
```

## Verify Installation
Open a new command prompt and run:
```bash
upx --version
```

## Using UPX
After installing UPX, the build script will automatically detect and use it:
```bash
python build.py
```

The script will show compression statistics like:
```
📊 Size: 20.1MB → 8.5MB (57.7% savings)
```

## Manual Compression
You can also compress manually:
```bash
upx --best dist/SoPDF.exe
``` 