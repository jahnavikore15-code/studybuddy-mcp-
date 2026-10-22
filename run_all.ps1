# Run all StudyBuddy MCP components in separate PowerShell windows
Write-Host "Starting StudyBuddy MCP Services..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; python server.py"
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001"
Start-Sleep -Seconds 2

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PSScriptRoot'; .\venv\Scripts\Activate.ps1; python -m http.server 5500 --directory web"
Start-Sleep -Seconds 1

Write-Host "All services started! Opening frontend at http://127.0.0.1:5500..." -ForegroundColor Green
Start-Process "http://127.0.0.1:5500"
