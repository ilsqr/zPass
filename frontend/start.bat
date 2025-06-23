@echo off
echo Starting zPass Frontend...

REM Python bytecode dosyalarinin olusmasini engelle
set PYTHONDONTWRITEBYTECODE=1

REM Sanal ortami aktif et
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

REM Frontend'i baslat
python main.py

pause
