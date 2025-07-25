#!/bin/bash
echo "Starting zPass Frontend..."

# Python bytecode dosyalarinin olusmasini engelle
export PYTHONDONTWRITEBYTECODE=1

# Sanal ortami aktif et
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Frontend'i baslat
python main.py
