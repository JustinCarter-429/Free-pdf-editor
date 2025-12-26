@echo off
REM Build a Windows .exe using PyInstaller

echo Building PDF Tool...

REM Clean old builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

pyinstaller ^
  --onefile ^
  --windowed ^
  --name "PDFTool" ^
  --add-data "*.py;." ^
  main.py

echo.
echo Build complete! Check the 'dist' folder for PDFTool.exe
echo.
pause
