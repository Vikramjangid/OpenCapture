@echo off
echo Building OpenCapture EXE...
pyinstaller --noconfirm --onedir --windowed --name "OpenCapture" --paths src src/main.py
echo Build Complete. EXE is in dist/OpenCapture/OpenCapture.exe
pause
