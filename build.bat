@echo off
echo ===================================
echo       SoPDF Build Script
echo ===================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Installing/updating build dependencies...
python -m pip install -r requirements-build.txt

echo.
echo Starting build process...
python build.py

echo.
echo Build process completed!
echo Check the 'dist' folder for your SoPDF.exe file
echo.
pause 