# Complete Testing Guide - AI Time Loop Environment Emulator

This guide walks you through testing **every endpoint and agent** in the system.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Start the Server](#1-start-the-server)
3. [Test 1: Health Check](#test-1-health-check)
4. [Test 2: Get Current Data](#test-2-get-current-data)
5. [Test 3: Run Full Agent Pipeline](#test-3-run-full-agent-pipeline)
6. [Test 4: Get Historical Data](#test-4-get-historical-data)
7. [Test 5: Weather Only](#test-5-weather-only)
8. [Test 6: Individual Agent Tests](#test-6-individual-agent-tests)
9. [Test 7: Fallback Logic](#test-7-fallback-logic)
10. [Expected Results](#expected-results)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.11 or higher installed
- Server dependencies installed
- Server running on `http://localhost:8000`

---

## 1. Start the Server

### Step 1.1: Open Terminal
Open PowerShell or Command Prompt and navigate to the server directory:

```powershell
cd "C:\Users\Gayathri\OneDrive\Desktop\F2\AI time loop emulator\server"
```

### Step 1.2: Install Dependencies (first time only)
```powershell
pip install fastapi uvicorn requests pydantic httpx
```

### Step 1.3: Start the API Server
```powershell
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Will watch for changes in: 'api.py', 'config.py', ...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal open** - the server must stay running.

---

## Test 1: Health Check

### Purpose
Verify the server is online and responding.

### Method 1: Python Script (Recommended)
Open a **new terminal** and run:
```powershell
python -c "import requests; print(requests.get('http://localhost:8000/').json())"
```

### Method 2: PowerShell
```powershell
Invoke-RestMethod http://localhost:8000/
```

### Method 3: Browser
Open: http://localhost:8000/

### Expected Response
```json
{
  "status": "online",
  "service": "AI Time Loop Environment Emulator",
  "timestamp": "2026-03-27T15:00:00.000000"
}
```

### ✅ Success Criteria
- `status` = `"online"`
- `service` name is correct
- `timestamp` is present

---

## Test 2: Get Current Data

### Purpose
Retrieve the latest environment data with all AI agent decisions.

### Method 1: Python Script
```powershell
python -c "import requests; import json; data = requests.get('http://localhost:8000/current').json(); print(json.dumps(data, indent=2))"
```

### Method 2: PowerShell
```powershell
Invoke-RestMethod http://localhost:8000/current | ConvertTo-Json -Depth 10
```

### Method 3: Browser
Open: http://localhost:8000/current

### Expected Response (Partial)
```json
{
  "timestamp": "2026-03-27T15:49:30.859755",
  "temperature": 34.0,
  "radiation": 882.0,
  "lux": 105840.0,
  "weathercode": 0,
  "hour": 14,
  "temp_status": "HIGH",
  "fan_speed": "FAST",
  "comfort_level": 2,
  "temp_reasoning": "Temperature of 34°C is well above typical comfort range...",
  "light_decision": "OFF",
  "brightness_pct": 0,
  "color_temp": "NEUTRAL",
  "scene_description": "The room feels like a sun-baked greenhouse...",
  "mood": "sultry",
  "scene_summary": "The space is overheated and drenched in overwhelming daylight.",
  "recommendation": "Close the blinds or curtains..."
}
```

### ✅ Success Criteria
| Field | Expected |
|-------|----------|
| `temperature` | Number (°C) |
| `temp_status` | "LOW", "NORMAL", or "HIGH" |
| `fan_speed` | "OFF", "SLOW", "MEDIUM", or "FAST" |
| `light_decision` | "ON", "DIM", or "OFF" |
| `scene_description` | Non-empty string |
| `mood` | Non-empty string |

---

## Test 3: Run Full Agent Pipeline

### Purpose
Trigger a complete run of all AI agents with new data.

### Method 1: Python Test Script (Best)
```powershell
python test_api.py
```

### Method 2: PowerShell
```powershell
$result = Invoke-RestMethod -Method POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"
$result | ConvertTo-Json -Depth 10
```

### Method 3: Python One-liner
```powershell
python -c "import requests; r = requests.post('http://localhost:8000/run', params={'input_date': '2026-03-27', 'input_hour': 14}); print(r.json())"
```

### Expected Response Structure
```json
{
  "status": "success",
  "input": {
    "date": "2026-03-27",
    "hour": 14
  },
  "environment": {
    "temperature": 34.0,
    "radiation": 882.0,
    "weathercode": 0
  },
  "agents": {
    "temp_status": "HIGH",
    "fan_speed": "FAST",
    "light_decision": "OFF",
    "scene_description": "...",
    "mood": "sultry",
    "model": "nvidia/nemotron-3-super-120b-a12b:free"
  }
}
```

### ✅ Success Criteria
- `status` = `"success"`
- `environment` contains weather data
- `agents` contains all agent decisions
- `model` shows AI model name (or "rule-based" if fallback)

---

## Test 4: Get Historical Data

### Purpose
Retrieve stored records from the database.

### Method 1: Python
```powershell
python -c "import requests; r = requests.get('http://localhost:8000/history', params={'limit': 5}); print(r.json())"
```

### Method 2: PowerShell
```powershell
Invoke-RestMethod "http://localhost:8000/history?limit=5" | ConvertTo-Json -Depth 5
```

### Method 3: Browser
Open: http://localhost:8000/history?limit=5

### Expected Response
```json
{
  "count": 5,
  "data": [
    {
      "id": 10,
      "timestamp": "2026-03-27T15:49:30",
      "temperature": 34.0,
      "temp_status": "HIGH",
      "light_decision": "OFF",
      "scene_summary": "34°C, lights off, feels sultry."
    },
    ...
  ]
}
```

### ✅ Success Criteria
- `count` > 0 (after running Test 3)
- `data` array contains records
- Each record has `timestamp`, `temperature`, `temp_status`

---

## Test 5: Weather Only

### Purpose
Fetch weather data without running AI agents (debugging).

### Method 1: Python
```powershell
python -c "import requests; r = requests.get('http://localhost:8000/weather', params={'date': '2026-03-27', 'hour': 14}); print(r.json())"
```

### Method 2: PowerShell
```powershell
Invoke-RestMethod "http://localhost:8000/weather?date=2026-03-27&hour=14" | ConvertTo-Json
```

### Expected Response
```json
{
  "input_date_weather": {
    "temperature": 34.0,
    "radiation": 882.0,
    "weathercode": 0
  },
  "current_weather": {
    "temperature": 32.8,
    "radiation": 582.0,
    "weathercode": 0
  }
}
```

### ✅ Success Criteria
- `input_date_weather` contains data
- `current_weather` contains data
- Both have `temperature`, `radiation`, `weathercode`

---

## Test 6: Individual Agent Tests

### Purpose
Test each agent independently with custom inputs.

### Temperature Agent Test
```powershell
cd server
python -c "
from agents.temp_agent import TemperatureAgent
agent = TemperatureAgent()
result = agent.run(temperature=35.0, weathercode=0, hour_of_day=14)
print('Temperature Agent Result:')
for k, v in result.items():
    print(f'  {k}: {v}')
"
```

### Expected Output
```
Temperature Agent Result:
  status: HIGH
  fan_speed: FAST
  comfort_level: 2
  reasoning: Temperature of 35.0°C far exceeds...
  action: Activate air conditioning...
  health_note: High temperature poses risk...
```

### Light Agent Test
```powershell
python -c "
from agents.light_agent import LightAgent
agent = LightAgent()
result = agent.run(lux=50, weathercode=0, hour_of_day=20)
print('Light Agent Result:')
for k, v in result.items():
    print(f'  {k}: {v}')
"
```

### Expected Output
```
Light Agent Result:
  decision: ON
  brightness_pct: 90
  color_temp: WARM
  reasoning: Very low lux (50) - artificial lighting required.
  action: Turn on lights at high brightness.
  circadian_note: Use warm light in evening...
```

### Scene Agent Test
```powershell
python -c "
from agents.scene_agent import SceneAgent
agent = SceneAgent()
result = agent.run(
    temperature=25.0,
    lux=500,
    light_decision='DIM',
    temp_status='NORMAL',
    weathercode=1,
    hour_of_day=18
)
print('Scene Agent Result:')
for k, v in result.items():
    print(f'  {k}: {v}')
"
```

### Expected Output
```
Scene Agent Result:
  description: The room sits at 25.0°C with 500 lux...
  mood: pleasant
  summary: 25°C, lights dim, feels pleasant.
  recommendation: Conditions are comfortable...
```

### All Agents Together
```powershell
python -c "
from agents.run_all_agent import run_all_agents
result = run_all_agents(
    temperature=28.0,
    radiation=500,
    weathercode=2,
    hour_of_day=12
)
print('All Agents Result:')
print(f'  Temp: {result[\"temp_status\"]} - {result[\"fan_speed\"]}')
print(f'  Light: {result[\"light_decision\"]} - {result[\"brightness_pct\"]}%')
print(f'  Scene: {result[\"mood\"]} - {result[\"scene_summary\"]}')
"
```

---

## Test 7: Fallback Logic

### Purpose
Verify agents work when AI API is unavailable.

### Test with Empty API Key
```powershell
python -c "
from agents.temp_agent import TemperatureAgent
agent = TemperatureAgent(api_key='')  # No API key
result = agent.run(temperature=15.0)
print('Fallback Test (Temperature Agent):')
print(f'  status: {result[\"status\"]}')
print(f'  fan_speed: {result[\"fan_speed\"]}')
print(f'  model: {result[\"model\"]}')
print('  ✓ Fallback logic working!' if result['status'] else '  ✗ Fallback failed!')
"
```

### Expected Output
```
Fallback Test (Temperature Agent):
  status: LOW
  fan_speed: OFF
  model: rule-based
  ✓ Fallback logic working!
```

### Test All Agents Fallback
```powershell
python test_p1.py
```

Look for:
- `[AgentName]` warnings (API unavailable)
- Fallback decisions still returned
- `model: rule-based` in output

---

## Expected Results Summary

| Test | Endpoint/Script | Success Indicator |
|------|----------------|-------------------|
| 1. Health | `GET /` | `{"status": "online"}` |
| 2. Current | `GET /current` | All agent fields present |
| 3. Run Pipeline | `POST /run` | `{"status": "success"}` |
| 4. History | `GET /history` | `count > 0` |
| 5. Weather | `GET /weather` | Temperature data present |
| 6. Agents | Python import | Each agent returns decisions |
| 7. Fallback | Empty API key | `model: rule-based` |

---

## Troubleshooting

### Server Won't Start

**Error: Port 8000 already in use**
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
uvicorn api:app --reload --port 8001
```

**Error: Module not found**
```powershell
pip install fastapi uvicorn requests pydantic httpx
```

### API Returns Empty Data

**Check database:**
```powershell
python -c "from db_handler import get_current; print(get_current())"
```

**Run agents to populate:**
```powershell
python test_p1.py
```

### Connection Refused

1. Verify server is running (check terminal)
2. Check URL: `http://localhost:8000` (not https)
3. Try: `http://127.0.0.1:8000`

### AI API Errors

The system has **fallback logic** - if AI is unavailable:
- Agents use rule-based decisions
- `model` field shows `"rule-based"`
- System continues working normally

---

## Quick Test Commands (Copy-Paste)

```powershell
# 1. Start server (in Terminal 1)
cd "C:\Users\Gayathri\OneDrive\Desktop\F2\AI time loop emulator\server"
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# 2. Run all tests (in Terminal 2)
python test_api.py

# 3. Test individual endpoints
python -c "import requests; print(requests.get('http://localhost:8000/').json())"
python -c "import requests; print(requests.get('http://localhost:8000/current').json())"
python -c "import requests; print(requests.post('http://localhost:8000/run', params={'input_date': '2026-03-27', 'input_hour': 14}).json())"

# 4. Test agents directly
python test_p1.py
```

---

## Test Checklist

Print this and check off as you complete each test:

- [ ] **Test 1:** Health check returns `{"status": "online"}`
- [ ] **Test 2:** `/current` returns all agent data fields
- [ ] **Test 3:** `/run` successfully processes agents
- [ ] **Test 4:** `/history` shows stored records
- [ ] **Test 5:** `/weather` fetches weather data
- [ ] **Test 6:** Individual agents work (temp, light, scene)
- [ ] **Test 7:** Fallback logic works without API key

**All tests passed?** ✅ Your system is fully functional!

---

## Next Steps

After all tests pass:

1. **Connect Frontend:** Point React app to `http://localhost:8000/current`
2. **Run Continuously:** Use `python main.py` for auto-updates every 5 seconds
3. **Deploy:** Configure for production with proper API keys

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-27
