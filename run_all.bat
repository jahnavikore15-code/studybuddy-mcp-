@echo off
echo Starting StudyBuddy MCP Services...

start "StudyBuddy - MCP Server (Port 8000)" cmd /k "call .\venv\Scripts\activate.bat && python server.py"
timeout /t 2 >nul

start "StudyBuddy - Web API (Port 8001)" cmd /k "call .\venv\Scripts\activate.bat && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001"
timeout /t 2 >nul

start "StudyBuddy - Frontend (Port 5500)" cmd /k "call .\venv\Scripts\activate.bat && python -m http.server 5500 --directory web"
timeout /t 1 >nul

echo All services launched!
echo - MCP Server: http://127.0.0.1:8000/mcp
echo - Web API:    http://127.0.0.1:8001
echo - Frontend:   http://127.0.0.1:5500
echo.
echo Opening browser at http://127.0.0.1:5500 ...
start http://127.0.0.1:5500
