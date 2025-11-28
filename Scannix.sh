#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

VENV_DIR="$PROJECT_DIR/config/venv"
VENV_PYTHON="$VENV_DIR/bin/python3"
GUI_SCRIPT="$PROJECT_DIR/modules/gui.py"

if [ ! -d "$VENV_DIR" ]; then
    echo "[+] Creating virtual environment..."
    python3 -m venv "$VENV_DIR" || exit 1
fi

echo "[+] Installing dependencies..."
"$VENV_PYTHON" -m pip install --quiet --upgrade pip
"$VENV_PYTHON" -m pip install --quiet -r "$PROJECT_DIR/requirements.txt"

if [ "$EUID" -ne 0 ]; then
    echo "[+] Restarting with administrator privileges..."
    exec sudo "$VENV_PYTHON" "$GUI_SCRIPT"
fi

exec "$VENV_PYTHON" "$GUI_SCRIPT"