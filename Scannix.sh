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

DATA_DIR="$PROJECT_DIR/data"

if [ "$EUID" -ne 0 ]; then
    exec sudo SUDO_USER="$USER" "$0"
fi

if [ -n "$SUDO_USER" ]; then
    mkdir -p "$DATA_DIR"
    chown -R "$SUDO_USER":"$SUDO_USER" "$DATA_DIR" 2>/dev/null || true
fi

exec "$VENV_PYTHON" "$GUI_SCRIPT"