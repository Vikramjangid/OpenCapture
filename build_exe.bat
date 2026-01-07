@echo off
echo Building Snagit Clone EXE...
pyinstaller --noconfirm --onedir --windowed --name "SnagitClone" --paths src src/main.py
echo Build Complete. EXE is in dist/SnagitClone/SnagitClone.exe
pause
