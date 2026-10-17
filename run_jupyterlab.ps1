# Windows PowerShell Launcher for JupyterLab (Z-Guard AI)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  Z-Guard AI: Launching JupyterLab Environment" -ForegroundColor Yellow
Write-Host "  IBM Z Datathon 2026" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

# Check if .venv exists
if (-Not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Virtual environment not found. Setting up .venv..." -ForegroundColor Yellow
    py -3.13 -m venv .venv
    .venv\Scripts\python.exe -m pip install -r requirements.txt
}

# Check if jupyterlab is installed
& .venv\Scripts\python.exe -c "import jupyterlab" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing JupyterLab in virtual environment..." -ForegroundColor Yellow
    & .venv\Scripts\python.exe -m pip install jupyterlab
}

Write-Host "Opening JupyterLab in your browser..." -ForegroundColor Green
& .venv\Scripts\jupyter-lab.exe --notebook-dir=.
