# Windows PowerShell Launcher for Classic Jupyter Notebook
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Z-Guard AI: Launching Jupyter Notebook" -ForegroundColor Yellow
Write-Host "  IBM Z Datathon 2026" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Open Jupyter Notebook
Write-Host "Opening Jupyter Notebook in your browser..." -ForegroundColor Green
& .venv\Scripts\jupyter-notebook.exe --notebook-dir=.
