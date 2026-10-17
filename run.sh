#!/usr/bin/env bash
# Linux / IBM LinuxONE (s390x) Launcher for Z-Guard AI
# IBM Z Datathon 2026

set -e

echo "=========================================================="
echo "  Z-Guard AI: Real-Time Server Anomaly Detection"
echo "  IBM Z Datathon 2026"
echo "  Target: IBM LinuxONE (s390x) / Enterprise Cloud"
echo "=========================================================="

ARCH=$(uname -m)
echo "[INFO] Detected Architecture: $ARCH"

if [ ! -d ".venv" ]; then
    echo "[SETUP] Initializing virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "[INFO] Launching Z-Guard AI on port 8501..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
