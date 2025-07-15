#!/usr/bin/env python3
"""
SoPDF Build Script
Creates an optimized .exe file for Windows distribution
"""

import os
import sys
import shutil
import subprocess

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")
    
    # Directories to clean
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Removed: {dir_name}/")
    
    # Files to clean
    files_to_clean = ['SoPDF.spec']
    for file_name in files_to_clean:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   Removed: {file_name}")

def prepare_poppler_binaries():
    """Prepare Poppler binaries for inclusion in the build"""
    print("📦 Preparing Poppler binaries...")
    
    # Check if we have the extracted poppler binaries
    poppler_source = "poppler-temp/poppler-24.08.0/Library"
    poppler_dest = "poppler"
    
    if os.path.exists(poppler_source):
        # Copy poppler binaries to a simpler path for PyInstaller
        if os.path.exists(poppler_dest):
            shutil.rmtree(poppler_dest)
        
        # Copy the bin directory with all binaries
        shutil.copytree(os.path.join(poppler_source, "bin"), os.path.join(poppler_dest, "bin"))
        
        # Calculate total size
        total_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, dirnames, filenames in os.walk(poppler_dest)
            for filename in filenames
        ) / (1024*1024)
        
        print(f"   ✅ Poppler binaries prepared ({total_size:.1f} MB)")
        return True
    else:
        print("   ⚠️  Poppler binaries not found")
        print("   ℹ️  Building without bundled Poppler (users will need to install it separately)")
        return False

def check_dependencies():
    """Check if required build dependencies are installed"""
    print("🔍 Checking build dependencies...")
    
    try:
        import PyInstaller
        print(f"   ✅ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("   ❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller>=5.13.0"])
        import PyInstaller
        print(f"   ✅ PyInstaller {PyInstaller.__version__} installed")
    
    # Check other dependencies
    dependencies = ['customtkinter', 'PIL', 'fitz']
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} not found")
            return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building SoPDF executable...")
    
    # PyInstaller command with optimization flags
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # Single executable file
        '--windowed',                   # No console window
        '--name=SoPDF',                 # Executable name
        '--icon=assets/SoPDF_icon.ico', # Application icon
        '--optimize=2',                 # Python optimization level
        '--strip',                      # Strip debug symbols (if available)
        '--clean',                      # Clean PyInstaller cache
        
        # Add data files
        '--add-data=assets;assets',     # Include assets folder
        '--add-data=docs;docs',         # Include docs folder
        
        # Hidden imports for CustomTkinter and PDF processing
        '--hidden-import=customtkinter',
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=fitz',
        
        # Exclude only obviously unnecessary modules (safe exclusions)
        '--exclude-module=tkinter.test',
        '--exclude-module=test',
        '--exclude-module=unittest',
        '--exclude-module=pydoc',
        '--exclude-module=doctest',
        
        # Development/debugging tools (safe to exclude)
        '--exclude-module=pdb',
        '--exclude-module=profile',
        '--exclude-module=cProfile',
        
        # Clearly unused GUI modules
        '--exclude-module=turtle',
        '--exclude-module=turtledemo',
        
        # Entry point
        'run.py'
    ]
    
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Build failed with error:")
        print(f"   {e.stderr}")
        return False

def optimize_build():
    """Additional optimization steps"""
    print("⚡ Applying additional optimizations...")
    
    # Check if UPX is available for compression (optional)
    try:
        subprocess.run(['upx', '--version'], capture_output=True, check=True)
        print("   UPX found - attempting compression...")
        
        exe_path = 'dist/SoPDF.exe'
        if os.path.exists(exe_path):
            # Create backup
            backup_path = 'dist/SoPDF_uncompressed.exe'
            shutil.copy2(exe_path, backup_path)
            
            try:
                subprocess.run(['upx', '--best', exe_path], check=True)
                print("   ✅ UPX compression applied")
                
                # Show size comparison
                original_size = os.path.getsize(backup_path) / (1024*1024)
                compressed_size = os.path.getsize(exe_path) / (1024*1024)
                savings = ((original_size - compressed_size) / original_size) * 100
                
                print(f"   📊 Size: {original_size:.1f}MB → {compressed_size:.1f}MB ({savings:.1f}% savings)")
                
                # Remove backup if compression successful
                os.remove(backup_path)
                
            except subprocess.CalledProcessError:
                print("   ⚠️  UPX compression failed, keeping uncompressed version")
                shutil.move(backup_path, exe_path)
                
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ℹ️  UPX not found - skipping compression (optional)")
        print("      Install UPX from https://upx.github.io/ for smaller executables")

def show_build_info():
    """Show information about the built executable"""
    exe_path = 'dist/SoPDF.exe'
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024*1024)
        print(f"\n🎉 Build completed successfully!")
        print(f"   📁 Location: {os.path.abspath(exe_path)}")
        print(f"   📊 Size: {size_mb:.1f} MB")
        print(f"   🚀 Ready for distribution!")
        print(f"\n💡 Distribution notes:")
        print(f"   • The .exe file is standalone and doesn't require Python")
        print(f"   • No external dependencies required - fully self-contained")
        print(f"   • PDF processing uses PyMuPDF library")
        print(f"   • Preview mode included with pure Python PDF rendering")
    else:
        print("\n❌ Build failed - executable not found")

def main():
    """Main build process"""
    print("🏗️  SoPDF Build Process Starting...")
    print("=" * 50)
    
    # Step 1: Clean previous builds
    clean_build()
    print()
    
    # Step 2: PyMuPDF is now included for preview functionality
    print("📄 PDF preview functionality included via PyMuPDF")
    print("   ✅ Pure Python PDF rendering - no external binaries required")
    print()
    
    # Step 3: Check dependencies
    if not check_dependencies():
        print("\n❌ Missing dependencies. Please install them first:")
        print("   pip install -r requirements-build.txt")
        return False
    print()
    
    # Step 4: Build executable
    if not build_executable():
        return False
    print()
    
    # Step 5: Optimize
    optimize_build()
    print()
    
    # Step 6: Show results
    show_build_info()
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n✨ Build process completed! Check the 'dist' folder for your executable.")
    else:
        print(f"\n💥 Build process failed. Check the error messages above.")
        sys.exit(1) 