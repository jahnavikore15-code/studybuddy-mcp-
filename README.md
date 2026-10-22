# StudyBuddy MCP

StudyBuddy MCP is a local study assistant demo with note storage, practice prompts, and a revision planner. It demonstrates real MCP tools exposed over Streamable HTTP and called by a separate FastAPI web API through the official Python MCP client.

## Features
- Save and retrieve study notes by topic using SQLite.
- List saved topics.
- Generate deterministic practice prompts from notes (AI integration is a later extension).
- Create a date-based revision plan.
- Simple responsive frontend with optional browser speech-to-text where supported.

## Requirements
- Python 3.11+ (tested target: Python 3.14; package compatibility can depend on installed SDK versions)
- Node.js/npm for MCP Inspector
- Windows PowerShell or Command Prompt

## Setup on Windows PowerShell
```powershell
cd "$HOME\OneDrive\Desktop\studybuddy-mcp"
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:
```cmd
venv\Scripts\activate.bat
```

## Run the application

### Quick Start (One-Click)
Run either script from the project folder:
```powershell
.\run_all.ps1
```
or double-click `run_all.bat`. This automatically starts all 3 services in separate windows and opens `http://127.0.0.1:5500` in your browser.

---

### Manual Start (Three Terminals)
Open **three terminals** in the project folder. Activate the venv in each terminal.

### Terminal 1 — MCP server
```powershell
python server.py
```
MCP endpoint: `http://127.0.0.1:8000/mcp`

### Terminal 2 — Web API
```powershell
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
```
API health check: `http://127.0.0.1:8001/api/health`
API docs: `http://127.0.0.1:8001/docs`

### Terminal 3 — Frontend
```powershell
python -m http.server 5500 --directory web
```
Open `http://127.0.0.1:5500` in your browser.

Keep all three terminals open while using the app.

## Test MCP with Inspector
With Terminal 1 running, open another terminal and run:
```powershell
npx -y @modelcontextprotocol/inspector
```
Open the local URL printed by the command and connect using Streamable HTTP to:
`http://127.0.0.1:8000/mcp`

Tools: `add_note`, `get_study_notes`, `list_study_topics`, `quiz_me`, `revision_plan`.

## Architecture
Browser → FastAPI API (port 8001) → official MCP Python client → MCP server (port 8000) → SQLite / helper functions.

## Important notes
- The quiz generator is a local, deterministic fallback, not an LLM.
- AWS Bedrock is not configured in this starter version. Add an AI provider in a later phase.
- Do not commit AWS credentials or `.env` files.
- This is a demo project; don't put sensitive personal notes into it.
