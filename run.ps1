# Windows PowerShell Launcher for Z-Guard AI
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Z-Guard AI: Real-Time Server Anomaly Detection" -ForegroundColor Yellow
Write-Host "  IBM Z Datathon 2026" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if .venv exists
if (-Not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating Python virtual environment in .venv..." -ForegroundColor Yellow
    py -3.13 -m venv .venv
    Write-Host "Installing project dependencies..." -ForegroundColor Yellow
    .venv\Scripts\python.exe -m pip install -r requirements.txt
}

Write-Host "Launching Z-Guard AI Streamlit Dashboard on http://localhost:8501..." -ForegroundColor Green
.venv\Scripts\streamlit.exe run app.py
