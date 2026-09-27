@echo off
REM Ejecutar desde un entorno con las dependencias instaladas.
pyinstaller --noconfirm --clean --onefile --windowed --name WordSearchBookMaker main.py
