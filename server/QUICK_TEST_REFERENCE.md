# Quick Test Reference Card

## Start Server
```powershell
cd "C:\Users\Gayathri\OneDrive\Desktop\F2\AI time loop emulator\server"
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## Test All Endpoints (One Command)
```powershell
python test_api.py
```

## Test Individual Endpoints

| Test | Command |
|------|---------|
| **Health** | `python -c "import requests; print(requests.get('http://localhost:8000/').json())"` |
| **Current Data** | `python -c "import requests; print(requests.get('http://localhost:8000/current').json())"` |
| **Run Agents** | `python -c "import requests; print(requests.post('http://localhost:8000/run', params={'input_date': '2026-03-27', 'input_hour': 14}).json())"` |
| **History** | `python -c "import requests; print(requests.get('http://localhost:8000/history', params={'limit': 5}).json())"` |
| **Weather** | `python -c "import requests; print(requests.get('http://localhost:8000/weather', params={'date': '2026-03-27', 'hour': 14}).json())"` |

## Test Individual Agents

### Temperature Agent
```powershell
python -c "from agents.temp_agent import TemperatureAgent; a = TemperatureAgent(); r = a.run(temperature=30.0); print('Status:', r['status'], '| Fan:', r['fan_speed'])"
```

### Light Agent
```powershell
python -c "from agents.light_agent import LightAgent; a = LightAgent(); r = a.run(lux=100); print('Decision:', r['decision'], '| Brightness:', r['brightness_pct'], '%')"
```

### Scene Agent
```powershell
python -c "from agents.scene_agent import SceneAgent; a = SceneAgent(); r = a.run(temperature=25, lux=500, light_decision='DIM', temp_status='NORMAL', hour_of_day=18); print('Mood:', r['mood'], '| Summary:', r['scene_summary'])"
```

### All Agents Together
```powershell
python test_p1.py
```

## PowerShell Commands (Alternative)

```powershell
# Health
Invoke-RestMethod http://localhost:8000/

# Current Data
Invoke-RestMethod http://localhost:8000/current

# Run Agents
Invoke-RestMethod -Method POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"

# History
Invoke-RestMethod "http://localhost:8000/history?limit=5"
```

## Browser URLs

- **Health:** http://localhost:8000/
- **Current:** http://localhost:8000/current
- **History:** http://localhost:8000/history?limit=10
- **Weather:** http://localhost:8000/weather?date=2026-03-27&hour=14

## Expected Values

| Field | Possible Values |
|-------|-----------------|
| `temp_status` | `LOW`, `NORMAL`, `HIGH` |
| `fan_speed` | `OFF`, `SLOW`, `MEDIUM`, `FAST` |
| `light_decision` | `ON`, `DIM`, `OFF` |
| `brightness_pct` | `0` to `100` |
| `color_temp` | `WARM`, `NEUTRAL`, `COOL` |
| `mood` | `cozy`, `bright`, `sultry`, `dim`, `pleasant` |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Server won't start | `pip install fastapi uvicorn requests pydantic httpx` |
| Port 8000 in use | Use `--port 8001` or kill process |
| Connection refused | Make sure server is running in another terminal |
| AI API errors | System falls back to rule-based logic automatically |

## Files Reference

| File | Purpose |
|------|---------|
| `test_api.py` | Test all API endpoints |
| `test_p1.py` | Test full agent pipeline |
| `run_tests.bat` | Windows batch file for all tests |
| `TESTING_GUIDE.md` | Detailed step-by-step testing guide |
| `QUICKSTART.md` | Installation and setup guide |

---

**For detailed testing instructions, see:** `TESTING_GUIDE.md`
