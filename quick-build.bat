@echo off
echo ===============================
echo     Quick SoPDF Build
echo ===============================

REM Simple build command for testing
pip install pyinstaller
pyinstaller --onefile --windowed --name=SoPDF --icon=assets/SoPDF_icon.ico run.py

echo.
echo Build completed! Check dist/SoPDF.exe
pause 