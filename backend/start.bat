@echo off
echo Starting zPass Backend...

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

REM Backend'i baslat
python run.py

pause
