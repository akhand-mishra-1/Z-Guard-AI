#!/usr/bin/env bash
# Linux / macOS / s390x Launcher for JupyterLab (Z-Guard AI)
# IBM Z Datathon 2026

set -e

echo "=========================================================="
echo "  Z-Guard AI: Launching JupyterLab Environment"
echo "  IBM Z Datathon 2026"
echo "=========================================================="

if [ ! -d ".venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

if ! python3 -c "import jupyterlab" &> /dev/null; then
    echo "[SETUP] Installing JupyterLab..."
    pip install jupyterlab
fi

echo "[INFO] Launching JupyterLab on port 8888..."
jupyter lab --ip=0.0.0.0 --notebook-dir=.
