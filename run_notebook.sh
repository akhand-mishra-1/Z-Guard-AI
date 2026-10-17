#!/usr/bin/env bash
# Linux / macOS / s390x Launcher for Jupyter Notebook
# IBM Z Datathon 2026

set -e

source .venv/bin/activate
echo "[INFO] Launching Jupyter Notebook on port 8888..."
jupyter notebook --ip=0.0.0.0 --notebook-dir=.
