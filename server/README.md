# AI Time Loop Environment Emulator - Server

A multi-agent AI system that analyzes environmental data and makes intelligent decisions about room climate, lighting, and atmosphere.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI TIME LOOP EMULATOR                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │   Phase 1    │────▶│   Phase 2    │────▶│   Phase 3    │    │
│  │  Data Fetch  │     │  AI Agents   │     │   Storage    │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│         │                   │                    │              │
│         ▼                   ▼                    ▼              │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │ Open-Meteo   │     │ Temperature  │     │   SQLite     │    │
│  │   Weather    │     │    Light     │     │  Database    │    │
│  │     API      │     │    Scene     │     │              │    │
│  └──────────────┘     └──────────────┘     └──────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Server Files

| File | Description |
|------|-------------|
| `config.py` | Centralized configuration (API keys, location, model) |
| `api.py` | FastAPI REST API endpoints |
| `main.py` | Continuous loop runner (updates every 5 seconds) |
| `db_handler.py` | SQLite database operations |
| `phase1_data.py` | Weather data collection |
| `test_p1.py` | Test script for full pipeline |

### Agents (`agents/`)

| Agent | Purpose |
|-------|---------|
| `agents.py` | Base AI agent with LLM API handling |
| `temp_agent.py` | Temperature/thermal comfort analysis |
| `light_agent.py` | Lighting/circadian rhythm analysis |
| `scene_agent.py` | Narrative scene synthesis |
| `run_all_agent.py` | Orchestrates all agents |

### Utilities (`utils/`)

| Module | Purpose |
|--------|---------|
| `fetch_weather.py` | Open-Meteo API client |

## Installation

```bash
# Using uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Usage

### Run API Server (for frontend)
```bash
uvicorn api:app --reload --port 8000
```

### Run Continuous Loop
```bash
python main.py
```

### Run Tests
```bash
# Full automated test suite
python test_api.py

# Or use the batch file (Windows)
run_tests.bat

# Or follow the detailed guide
# See TESTING_GUIDE.md for step-by-step instructions
```

### Run Test Pipeline
```bash
python test_p1.py
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/current` | GET | Latest environment + agent data |
| `/history` | GET | Historical records |
| `/run` | POST | Trigger manual agent run |
| `/weather` | GET | Fetch weather without agents |

## AI Integration

- **Provider**: OpenRouter API
- **Model**: NVIDIA Nemotron-3 Super 120B
- **Fallback**: Rule-based logic when AI unavailable

## Fallback Logic

Each agent has intelligent fallback:

1. **AI Available** → Full LLM reasoning with context
2. **AI Unavailable** → Rule-based decisions

```
Temperature Agent:
  < 20°C → LOW (heating needed)
  20-30°C → NORMAL (comfortable)
  > 30°C → HIGH (cooling needed)

Light Agent:
  < 100 lux → ON (dark, full brightness)
  100-500 lux → DIM (supplementary light)
  > 500 lux → OFF (sufficient natural light)
```

## Database Schema

```sql
CREATE TABLE env_data (
    -- Raw sensor data
    temperature REAL,
    radiation REAL,
    lux REAL,
    weathercode INTEGER,
    hour INTEGER,
    
    -- Temperature agent
    temp_status TEXT,
    fan_speed TEXT,
    comfort_level INTEGER,
    temp_reasoning TEXT,
    temp_action TEXT,
    health_note TEXT,
    
    -- Light agent
    light_decision TEXT,
    brightness_pct INTEGER,
    color_temp TEXT,
    light_reasoning TEXT,
    light_action TEXT,
    circadian_note TEXT,
    
    -- Scene agent
    scene_description TEXT,
    mood TEXT,
    scene_summary TEXT,
    recommendation TEXT,
    
    -- Metadata
    model_used TEXT,
    timestamp TEXT
);
```

## Configuration

Edit `config.py` to customize:

```python
LATITUDE = 13.0827      # Location
LONGITUDE = 80.2707     # Chennai, India
OPENROUTER_API_KEY = "..."  # Your API key
MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"
```

## Project Structure

```
server/
├── agents/
│   ├── __init__.py
│   ├── agents.py          # Base agent
│   ├── temp_agent.py      # Temperature agent
│   ├── light_agent.py     # Light agent
│   ├── scene_agent.py     # Scene agent
│   └── run_all_agent.py   # Orchestrator
├── utils/
│   ├── __init__.py
│   └── fetch_weather.py   # Weather API client
├── data/
│   └── env.db             # SQLite database (auto-created)
├── config.py              # Configuration
├── api.py                 # REST API
├── main.py                # Main loop
├── db_handler.py          # Database operations
├── phase1_data.py         # Data collection
├── test_p1.py             # Test script
├── pyproject.toml         # Dependencies
└── README.md              # This file
```
