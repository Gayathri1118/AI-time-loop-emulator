# Quick Start Guide

## Prerequisites

- Python 3.11 or higher
- pip or uv package manager

---

## Option 1: Using pip (Recommended for Windows)

### Step 1: Install dependencies
```bash
cd server
pip install fastapi uvicorn requests pydantic httpx
```

### Step 2: Run the API server
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

---

## Testing the Server

### Method 1: Using Python Test Script (Easiest)
```bash
cd server
python test_api.py
```

This runs all API tests automatically.

### Method 2: Using PowerShell Commands

**Health Check:**
```powershell
Invoke-RestMethod http://localhost:8000/
```

**Get Current Data:**
```powershell
Invoke-RestMethod http://localhost:8000/current
```

**Run Agent Pipeline:**
```powershell
Invoke-RestMethod -Method POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"
```

**Get History:**
```powershell
Invoke-RestMethod "http://localhost:8000/history?limit=10"
```

### Method 3: Using curl (Git Bash only)
```bash
curl http://localhost:8000/
curl http://localhost:8000/current
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"
```

### Method 4: Browser
Open in your browser:
- http://localhost:8000/
- http://localhost:8000/current
- http://localhost:8000/history?limit=10

---

## Running Modes

### Mode 1: API Server (For Frontend)
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```
- Keeps server running
- Frontend can poll `/current` every 5 seconds
- Manual triggers via `/run` endpoint

### Mode 2: Continuous Loop (Standalone)
```bash
python main.py
```
- Runs automatically every 5 seconds
- Collects data and runs agents continuously
- Stores results in database

---

## Verify Everything Works

1. **Server starts without errors** ✅
2. **`/current` returns data** ✅
3. **`/run` triggers agent processing** ✅
4. **Database stores records** ✅
5. **Fallback works when AI unavailable** ✅

---

## Troubleshooting

### Port 8000 already in use
```bash
uvicorn api:app --reload --port 8001
```

### Module not found errors
```bash
cd server
pip install -e .
```

### Database errors
```bash
# Delete old database and recreate
del data\env.db
python test_p1.py
```

### API key issues
The system has fallback logic - it will use rule-based decisions if the AI API is unavailable.

---

## Default Configuration

- **Location**: Chennai, India (13.0827°N, 80.2707°E)
- **Update Interval**: 5 seconds
- **AI Model**: NVIDIA Nemotron-3 Super 120B (via OpenRouter)
- **Database**: `data/env.db` (SQLite, auto-created)
