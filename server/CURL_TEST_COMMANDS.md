# CURL Test Commands for AI Time Loop Environment Emulator

## Base URL
```
http://localhost:8000
```

---

## 1. API Health Check

### Root Endpoint
Check if the API is online.
```bash
curl -X GET http://localhost:8000/
```

**Expected Response:**
```json
{
  "status": "online",
  "service": "AI Time Loop Environment Emulator",
  "timestamp": "2026-03-27T16:30:00.000000"
}
```

---

## 2. Current Data Endpoint

### Get Current Agent Decisions
Get the most recent environment data with all agent decisions.
```bash
curl -X GET http://localhost:8000/current
```

**Expected Response:**
```json
{
  "timestamp": "2026-03-27T16:30:00.000000",
  "temperature": 28.5,
  "radiation": 45.2,
  "lux": 5424.0,
  "weathercode": 0,
  "hour": 14,
  "temp_status": "NORMAL",
  "fan_speed": "OFF",
  "comfort_level": 8,
  "temp_reasoning": "...",
  "temp_action": "...",
  "health_note": "...",
  "light_decision": "OFF",
  "brightness_pct": 0,
  "color_temp": "NEUTRAL",
  "light_reasoning": "...",
  "light_action": "...",
  "circadian_note": "...",
  "scene_description": "...",
  "mood": "bright",
  "scene_summary": "...",
  "recommendation": "...",
  "model_used": "rule-based"
}
```

---

## 3. Run Agents Endpoint

### Run with Current Time
Trigger agents with current date/time.
```bash
curl -X POST http://localhost:8000/run
```

### Run with Specific Date and Hour
```bash
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"
```

### Run with Different Times (Test Scenarios)

**Morning (6 AM):**
```bash
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=6"
```

**Midday (12 PM):**
```bash
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=12"
```

**Evening (7 PM):**
```bash
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=19"
```

**Night (11 PM):**
```bash
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=23"
```

**Expected Response:**
```json
{
  "status": "success",
  "input": {
    "date": "2026-03-27",
    "hour": 14
  },
  "environment": {
    "temperature": 28.5,
    "radiation": 45.2,
    "lux": 5424.0,
    "weathercode": 0
  },
  "agents": {
    "temperature": 28.5,
    "temp_status": "NORMAL",
    "fan_speed": "OFF",
    "comfort_level": 8,
    "light_decision": "OFF",
    "brightness_pct": 0,
    "mood": "bright",
    "scene_summary": "28°C, lights off, feels bright.",
    "model": "rule-based"
  }
}
```

---

## 4. Weather Data Endpoint

### Get Weather for Current Time
```bash
curl -X GET http://localhost:8000/weather
```

### Get Weather for Specific Date/Hour
```bash
curl -X GET "http://localhost:8000/weather?date=2026-03-27&hour=14"
```

**Expected Response:**
```json
{
  "temperature": 28.5,
  "radiation": 45.2,
  "lux": 5424.0,
  "weathercode": 0,
  "hour": 14
}
```

---

## 5. History Endpoint

### Get Last 100 Records
```bash
curl -X GET http://localhost:8000/history
```

### Get Last 10 Records
```bash
curl -X GET "http://localhost:8000/history?limit=10"
```

**Expected Response:**
```json
{
  "count": 10,
  "data": [
    {
      "id": 1,
      "timestamp": "2026-03-27T16:30:00",
      "temperature": 28.5,
      "temp_status": "NORMAL",
      ...
    }
  ]
}
```

---

## 6. Individual Agent Testing (Python)

Since agents are Python classes, test them directly:

### Test TemperatureAgent
```bash
cd server

# Test with low temperature (15°C)
python -c "from agents.temp_agent import TemperatureAgent; a = TemperatureAgent(api_key=''); r = a.run(temperature=15.0); print('Status:', r['status'], '| Fan:', r['fan_speed'], '| Comfort:', r['comfort_level'])"

# Test with normal temperature (25°C)
python -c "from agents.temp_agent import TemperatureAgent; a = TemperatureAgent(api_key=''); r = a.run(temperature=25.0); print('Status:', r['status'], '| Fan:', r['fan_speed'], '| Comfort:', r['comfort_level'])"

# Test with high temperature (35°C)
python -c "from agents.temp_agent import TemperatureAgent; a = TemperatureAgent(api_key=''); r = a.run(temperature=35.0); print('Status:', r['status'], '| Fan:', r['fan_speed'], '| Comfort:', r['comfort_level'])"
```

### Test LightAgent
```bash
cd server

# Test with low lux (50)
python -c "from agents.light_agent import LightAgent; a = LightAgent(api_key=''); r = a.run(lux=50); print('Decision:', r['decision'], '| Brightness:', r['brightness_pct'], '%')"

# Test with medium lux (300)
python -c "from agents.light_agent import LightAgent; a = LightAgent(api_key=''); r = a.run(lux=300); print('Decision:', r['decision'], '| Brightness:', r['brightness_pct'], '%')"

# Test with high lux (5000)
python -c "from agents.light_agent import LightAgent; a = LightAgent(api_key=''); r = a.run(lux=5000); print('Decision:', r['decision'], '| Brightness:', r['brightness_pct'], '%')"
```

### Test SceneAgent
```bash
cd server

# Test scene synthesis
python -c "from agents.scene_agent import SceneAgent; a = SceneAgent(api_key=''); r = a.run(temperature=25, lux=500, light_decision='OFF', temp_status='NORMAL', hour_of_day=14); print('Mood:', r['mood'], '| Summary:', r['scene_summary'])"
```

### Test All Agents Together
```bash
cd server

# Run all agents with sample data
python -c "from agents.run_all_agent import run_all_agents; r = run_all_agents(temperature=25, radiation=40, weathercode=0, hour_of_day=12, api_key=''); print('Temp:', r['temp_status'], '| Light:', r['light_decision'], '| Mood:', r['mood'])"
```

---

## 7. Complete Test Suite

### Run All Tests in Sequence
```bash
# Save this as test_api.bat on Windows

@echo off
echo ========================================
echo AI Time Loop API Test Suite
echo ========================================

echo.
echo [1/8] Testing root endpoint...
curl -s http://localhost:8000/

echo.
echo [2/8] Testing current data...
curl -s http://localhost:8000/current

echo.
echo [3/8] Testing weather endpoint...
curl -s http://localhost:8000/weather

echo.
echo [4/8] Running agents for morning (6 AM)...
curl -s -X POST "http://localhost:8000/run?input_date=2026-03-27^&input_hour=6"

echo.
echo [5/8] Running agents for midday (12 PM)...
curl -s -X POST "http://localhost:8000/run?input_date=2026-03-27^&input_hour=12"

echo.
echo [6/8] Running agents for evening (7 PM)...
curl -s -X POST "http://localhost:8000/run?input_date=2026-03-27^&input_hour=19"

echo.
echo [7/8] Getting history (last 5 records)...
curl -s "http://localhost:8000/history?limit=5"

echo.
echo [8/8] Final current data...
curl -s http://localhost:8000/current

echo.
echo ========================================
echo Test Suite Complete
echo ========================================
```

---

## 8. Formatted/Pretty Output

### Using jq for Pretty JSON
```bash
# Install jq first: choco install jq (Windows) or brew install jq (Mac)

# Pretty print current data
curl -s http://localhost:8000/current | jq

# Pretty print run result
curl -s -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14" | jq

# Extract specific fields
curl -s http://localhost:8000/current | jq '.temperature, .temp_status, .mood'
```

### Using Python for Pretty Print
```bash
# Pretty print with Python
curl -s http://localhost:8000/current | python -m json.tool

# Extract and display specific fields
curl -s http://localhost:8000/current | python -c "import sys,json; d=json.load(sys.stdin); print(f\"Temp: {d['temperature']}°C | Status: {d['temp_status']} | Mood: {d['mood']}\")"
```

---

## 9. Load Testing

### Run Multiple Requests
```bash
# Run 10 consecutive requests
for i in {1..10}; do
  echo "Request $i:"
  curl -s -X POST "http://localhost:8000/run" | python -c "import sys,json; d=json.load(sys.stdin); print('Status:', d.get('status', 'error'))"
done
```

### Test Response Time
```bash
# Measure response time
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/current
```

Create `curl-format.txt`:
```
    time_namelookup:  %{time_namelookup}\n
       time_connect:  %{time_connect}\n
    time_appconnect:  %{time_appconnect}\n
   time_pretransfer:  %{time_pretransfer}\n
      time_redirect:  %{time_redirect}\n
 time_starttransfer:  %{time_starttransfer}\n
                    ----------\n
         time_total:  %{time_total}\n
```

---

## 10. Error Testing

### Test Invalid Date
```bash
curl -X POST "http://localhost:8000/run?input_date=invalid&input_hour=25"
```

### Test Invalid Hour
```bash
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=30"
```

### Test Invalid History Limit
```bash
curl -X GET "http://localhost:8000/history?limit=-1"
```

---

## Quick Reference Table

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/current` | GET | Get latest agent decisions |
| `/run` | POST | Trigger agent run |
| `/weather` | GET | Get weather data only |
| `/history` | GET | Get historical data |

## Common Test Scenarios

| Scenario | Command |
|----------|---------|
| Cold morning (15°C, 6 AM) | `curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=6"` |
| Hot afternoon (35°C, 2 PM) | `curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"` |
| Comfortable evening (25°C, 7 PM) | `curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=19"` |
| Night mode (22°C, 11 PM) | `curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=23"` |
