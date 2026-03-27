# AI Time Loop Environment Emulator — Complete Project Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Data Flow](#data-flow)
4. [Project Structure](#project-structure)
5. [Server Components](#server-components)
6. [Client Components](#client-components)
7. [SimulIDE Integration](#simulide-integration)
8. [API Reference](#api-reference)
9. [Database Schema](#database-schema)
10. [Agent System](#agent-system)
11. [Configuration](#configuration)
12. [Setup & Installation](#setup--installation)
13. [Usage Guide](#usage-guide)
14. [Testing](#testing)
15. [Troubleshooting](#troubleshooting)

---

## Project Overview

**AI Time Loop Environment Emulator** is an intelligent multi-agent system that simulates a smart room environment. It fetches real-world weather data, processes it through AI agents, and visualizes the results in both a 3D interactive environment and a SimulIDE Arduino circuit simulation.

### Key Features

- 🌤️ **Real Weather Data** — Fetches historical/forecast data from Open-Meteo API
- 🤖 **AI Multi-Agent System** — Three specialized agents (Temperature, Light, Scene) powered by LLM
- 🏠 **3D Visualization** — Interactive Three.js room with dynamic lighting, fan, and atmosphere
- 🔌 **SimulIDE Integration** — Virtual Arduino circuit with RGB LED, motor, LCD display
- 💾 **Data Persistence** — SQLite database stores all agent decisions and sensor readings
- 🔄 **Real-time Updates** — Auto-sync between server, client, and SimulIDE

### Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.11+, FastAPI |
| **Frontend** | React 19, TypeScript, Vite |
| **3D Engine** | Three.js, React Three Fiber |
| **AI/LLM** | OpenRouter API (NVIDIA Nemotron-3 Super 120B) |
| **Weather API** | Open-Meteo |
| **Database** | SQLite |
| **Hardware Sim** | SimulIDE (Arduino Uno) |
| **Communication** | HTTP REST, Serial (pyserial) |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI TIME LOOP EMULATOR                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │   PHASE 1    │────▶│   PHASE 2    │────▶│   PHASE 3    │            │
│  │  Data Fetch  │     │  AI Agents   │     │   Storage    │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│         │                   │                    │                      │
│         ▼                   ▼                    ▼                      │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│  │ Open-Meteo   │     │ Temperature  │     │   SQLite     │            │
│  │   Weather    │     │    Light     │     │  Database    │            │
│  │     API      │     │    Scene     │     │              │            │
│  └──────────────┘     └──────────────┘     └──────────────┘            │
│                                                                          │
│         │                   │                    │                      │
│         ▼                   ▼                    ▼                      │
│  ┌──────────────────────────────────────────────────────────┐          │
│  │                    OUTPUT LAYERS                          │          │
│  ├──────────────────────────────────────────────────────────┤          │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │          │
│  │  │  REST API   │  │  3D Client  │  │  SimulIDE   │      │          │
│  │  │  (FastAPI)  │  │  (React)    │  │  (Arduino)  │      │          │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │          │
│  └──────────────────────────────────────────────────────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### High-Level Components

1. **Server (FastAPI)** — REST API, agent orchestration, data collection
2. **Client (React)** — 3D visualization, user controls, SimulIDE panel
3. **Agents (Python)** — Temperature, Light, Scene analysis
4. **SimulIDE (Arduino)** — Circuit simulation with hardware components
5. **Database (SQLite)** — Persistent storage of all data

---

## Data Flow

### Complete Pipeline

```
┌─────────────┐
│ User Input  │ (Date/Hour from Client UI)
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (React)                           │
│  - Date/Time picker                                             │
│  - Run button                                                   │
│  - SimulIDE control panel                                       │
│  - 3D visualization updates                                     │
└──────────────┬──────────────────────────────────────────────────┘
               │ HTTP POST /run?date=YYYY-MM-DD&hour=HH
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVER (FastAPI)                              │
│                                                                  │
│  1. /run endpoint receives request                              │
│  2. Calls get_environment_data(date, hour)                      │
│  3. Fetches weather from Open-Meteo API                         │
│  4. Runs all agents in sequence                                 │
│  5. Stores results in SQLite                                    │
│  6. Returns combined response                                   │
│  7. Auto-sends to SimulIDE if connected                         │
└──────────────┬──────────────────────────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
       ▼                ▼
┌──────────────┐  ┌─────────────────────────────────────────┐
│  Database    │  │         SimulIDE (Serial @ 9600)        │
│  (SQLite)    │  │  - RGB LED (temp status)                │
│  - Insert    │  │  - White LED (brightness)               │
│  - Store     │  │  - DC Motor (fan speed)                 │
│  - History   │  │  - LCD Display (data)                   │
└──────────────┘  └─────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT VISUAL UPDATES                        │
│  - timeOfDay ← hour (morning/afternoon/evening/night)          │
│  - fanSpeed ← fan_speed (0-5 scale)                            │
│  - lightIntensity ← brightness_pct (0-100)                     │
│  - Environment data panel shows:                               │
│    temperature, mood, comfort, radiation, lux                  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Decision Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  INPUT DATA                                   │
│  temperature: 28.5°C                                          │
│  radiation: 45.2 W/m²                                         │
│  weathercode: 0 (clear sky)                                   │
│  hour: 14 (2 PM)                                              │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│              PHASE 1: Calculate Derived Data                  │
│  lux = radiation × 120 = 5424 lux                            │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│           PHASE 2: Run Temperature Agent                      │
│  Input: temp=28.5°C, weathercode=0, hour=14                  │
│  LLM Reasoning: "Temperature is within comfortable range..." │
│  Output:                                                      │
│    - status: "NORMAL"                                        │
│    - fan_speed: "SLOW"                                       │
│    - comfort_level: 8                                        │
│    - reasoning: "..."                                        │
│    - health_note: "..."                                      │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│             PHASE 3: Run Light Agent                          │
│  Input: lux=5424, weathercode=0, hour=14                     │
│  LLM Reasoning: "Sufficient natural light..."                │
│  Output:                                                      │
│    - decision: "OFF"                                         │
│    - brightness_pct: 0                                       │
│    - color_temp: "NEUTRAL"                                   │
│    - circadian_note: "..."                                   │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│             PHASE 4: Run Scene Agent                          │
│  Input: temp=28.5, lux=5424, light="OFF", temp="NORMAL"      │
│  LLM Synthesis: "The room is bright and comfortable..."      │
│  Output:                                                      │
│    - description: "2-3 sentences..."                         │
│    - mood: "bright"                                          │
│    - summary: "28°C, lights off, feels bright."              │
│    - recommendation: "..."                                   │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────┐
│              PHASE 5: Store & Return                          │
│  - Insert to SQLite database                                 │
│  - Return combined result to client                          │
│  - Send to SimulIDE (if connected)                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
AI time loop emulator/
│
├── client/                          # React Frontend Application
│   ├── src/
│   │   ├── components/              # 3D Scene Components
│   │   │   ├── Architecture.tsx     # Walls, floors, windows, doors
│   │   │   ├── Fixtures.tsx         # Ceiling fan, lights, tube lights
│   │   │   ├── Furniture.tsx        # Sofa, TV, kitchen, bed
│   │   │   ├── InteractableRooms.tsx# Room hover detection
│   │   │   └── Lighting.tsx         # Sun, sky, interior lights
│   │   ├── api.ts                   # API service layer
│   │   ├── App.tsx                  # Main application component
│   │   ├── main.tsx                 # React entry point
│   │   ├── index.css                # Tailwind CSS
│   │   └── materials.ts             # Three.js materials
│   ├── index.html                   # HTML template
│   ├── package.json                 # Node dependencies
│   ├── tsconfig.json                # TypeScript config
│   ├── vite.config.ts               # Vite bundler config
│   └── README.md
│
├── server/                          # Python Backend Application
│   ├── agents/                      # AI Agent System
│   │   ├── agents.py                # Base AI agent class
│   │   ├── temp_agent.py            # Temperature analysis agent
│   │   ├── light_agent.py           # Lighting analysis agent
│   │   ├── scene_agent.py           # Scene synthesis agent
│   │   └── run_all_agent.py         # Agent orchestrator
│   │
│   ├── utils/                       # Utility Modules
│   │   ├── fetch_weather.py         # Open-Meteo API client
│   │   ├── serial_comm.py           # SimulIDE serial communication
│   │   └── lux.py                   # Light utilities
│   │
│   ├── arduino/                     # Arduino Code
│   │   └── time_loop_controller/
│   │       └── time_loop_controller.ino
│   │
│   ├── data/                        # Database Storage
│   │   └── env.db                   # SQLite database (auto-created)
│   │
│   ├── api.py                       # FastAPI REST API
│   ├── config.py                    # Configuration (API keys, location)
│   ├── db_handler.py                # Database operations
│   ├── main.py                      # Continuous loop runner
│   ├── phase1_data.py               # Weather data collection
│   ├── pyproject.toml               # Python dependencies
│   ├── simulide_circuit.simu        # SimulIDE circuit file
│   ├── led_control.ino              # Legacy Arduino code
│   │
│   └── Documentation/
│       ├── README.md                # Server documentation
│       ├── QUICKSTART.md            # Quick start guide
│       ├── TESTING_GUIDE.md         # Testing instructions
│       ├── CURL_TEST_COMMANDS.md    # API test commands
│       └── SIMULIDE_SETUP.md        # SimulIDE setup guide
│
├── frontend/                        # (Legacy/Alternative frontend)
│   └── ...
│
└── Documentation/
    └── PROJECT_DOCUMENTATION.md     # This file
```

---

## Server Components

### 1. FastAPI Application (`api.py`)

**Purpose:** REST API server that handles all client requests and orchestrates data flow.

**Key Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/current` | GET | Get latest environment data |
| `/history` | GET | Get historical records |
| `/run` | POST | Trigger agent run with date/hour |
| `/weather` | GET | Fetch weather without agents |
| `/simulide/ports` | GET | List serial ports |
| `/simulide/connect` | POST | Connect to SimulIDE |
| `/simulide/send` | POST | Send data to SimulIDE |
| `/simulide/status` | GET | Get SimulIDE status |

**Auto-Send Feature:** When SimulIDE is connected, `/current` and `/run` automatically send data to the Arduino circuit.

### 2. Agent System (`agents/`)

#### Base Agent (`agents.py`)
Abstract base class with LLM integration via OpenRouter API.

#### Temperature Agent (`temp_agent.py`)
**Input:** temperature, weathercode, hour, humidity, trend
**Output:**
- `status`: LOW/NORMAL/HIGH
- `fan_speed`: OFF/SLOW/MEDIUM/FAST
- `comfort_level`: 1-10
- `reasoning`, `action`, `health_note`

**AI Prompt Example:**
```
Temperature: 28.5°C
Trend: rising
Weather: clear sky
Time: afternoon (hour 14)

Analyze thermal comfort and decide fan speed.
```

**Fallback Logic:**
```python
if temp < 20: return LOW, OFF
elif temp > 30: return HIGH, FAST
else: return NORMAL, SLOW/OFF
```

#### Light Agent (`light_agent.py`)
**Input:** lux, weathercode, hour, radiation, trend
**Output:**
- `decision`: ON/DIM/OFF
- `brightness_pct`: 0-100
- `color_temp`: WARM/NEUTRAL/COOL
- `reasoning`, `action`, `circadian_note`

**Fallback Logic:**
```python
if lux < 100: return ON, 90%, WARM
elif lux < 500: return DIM, 45%, NEUTRAL
else: return OFF, 0%, NEUTRAL
```

#### Scene Agent (`scene_agent.py`)
**Input:** temperature, lux, light_decision, temp_status, weather
**Output:**
- `description`: 2-3 sentence narrative
- `mood`: one word (bright, cozy, sultry, etc.)
- `summary`: one-sentence snapshot
- `recommendation`: practical tip

### 3. Data Collection (`phase1_data.py`)

Fetches weather data from Open-Meteo API:
- Temperature (°C)
- Shortwave radiation (W/m²)
- Weather code (0=clear, 61=rain, etc.)

**Location:** Chennai, India (13.0827°N, 80.2707°E)

### 4. Database Handler (`db_handler.py`)

SQLite operations:
- `insert_data(data)` — Store complete record
- `get_current()` — Get latest record
- `get_history(limit)` — Get recent records
- `close()` — Close connection

### 5. SimulIDE Integration (`utils/serial_comm.py`)

Serial communication module:
- Auto-detect serial ports
- Send commands: `TEMP:`, `STATUS:`, `FAN:`, `LIGHT:`, `MOOD:`, `HOUR:`
- Read responses from Arduino
- Connection management

---

## Client Components

### 1. Main Application (`App.tsx`)

**State Management:**
```typescript
// Environment state
const [timeOfDay, setTimeOfDay] = useState<TimeOfDay>('afternoon');
const [fanSpeed, setFanSpeed] = useState(3);
const [lightIntensity, setLightIntensity] = useState(0);

// Server integration
const [inputDate, setInputDate] = useState<string>(today);
const [inputHour, setInputHour] = useState<number>(currentHour);
const [serverData, setServerData] = useState<ServerResponse | null>(null);

// SimulIDE state
const [simulIDEConnected, setSimulIDEConnected] = useState(false);
const [availablePorts, setAvailablePorts] = useState<string[]>([]);
```

**Data Mapping:**
```typescript
// Server hour → timeOfDay
hourToTimeOfDay(hour: number): 'morning' | 'afternoon' | 'evening' | 'night' {
  if (hour >= 6 && hour <= 11) return 'morning';
  if (hour >= 12 && hour <= 16) return 'afternoon';
  if (hour >= 17 && hour <= 20) return 'evening';
  return 'night';
}

// Server fan_speed → fanSpeed (0-5)
fanSpeedToNumber(fanSpeed: string): number {
  if (fanSpeed === 'OFF') return 0;
  if (fanSpeed === 'LOW') return 2;
  if (fanSpeed === 'MEDIUM') return 3;
  if (fanSpeed === 'HIGH') return 4;
  if (fanSpeed === 'MAX') return 5;
  return 0;
}
```

### 2. 3D Components (`src/components/`)

#### Lighting.tsx
- Sun position and color based on `timeOfDay`
- Hemisphere light for sky/ground
- Interior lights respond to `lightIntensity`
- Smooth transitions with lerp

#### Fixtures.tsx
- **CeilingFan:** Rotates based on `fanSpeed`
- **WallLights:** Brightness from `lightIntensity`
- **TubeLights:** PWM-like dimming

#### Architecture.tsx
- Walls, floors, windows, doors
- Static geometry with shadows

#### Furniture.tsx
- Sofa, TV, kitchen counter, bed
- All with appropriate materials

#### InteractableRooms.tsx
- Hover detection for room names
- Tooltip display

### 3. API Service (`api.ts`)

Type-safe API client:
```typescript
// Server endpoints
getCurrentData(): Promise<ServerResponse>
runAgents(date: string, hour: number): Promise<RunAgentsResponse>
getWeather(date: string, hour: number): Promise<WeatherData>

// SimulIDE endpoints
listSerialPorts(): Promise<{ ports: string[] }>
connectSimulIDE(port?: string): Promise<{ connected: boolean }>
sendToSimulIDE(data: SimulIDEData): Promise<{ status: string }>
```

---

## SimulIDE Integration

### Circuit Components

| Component | Pin | Purpose |
|-----------|-----|---------|
| **RGB LED (Common Anode)** | D9 (Red), D10 (Green), D6 (Blue) | Temperature status |
| **White LED** | D7 (PWM) | Light brightness |
| **DC Motor** | D8 (PWM) | Fan speed |
| **LCD 16x2** | D12 (RS), D11 (EN), D5-D2 (D4-D7) | Display data |
| **Push Button** | D13 | Manual override |
| **USB Serial** | TX/RX | Communication with Python |

### Arduino Commands

**From Python to Arduino:**
```
TEMP:28.5          # Set temperature
STATUS:NORMAL      # Set temp status (COLD/NORMAL/HOT)
FAN:3              # Set fan speed (0-5)
LIGHT:50           # Set brightness % (0-100)
MOOD:bright        # Set mood
HOUR:14            # Set hour (0-23)
RESET              # Reset to defaults
GET_STATUS         # Request current status
```

**Arduino Response:**
```
ARDUINO_STATUS:FAN=3,LIGHT=50,TEMP=28.5,STATUS=NORMAL
```

### Visual Indicators

| Component | State | Meaning |
|-----------|-------|---------|
| **RGB LED - Red** | ON | Temperature HOT (>30°C) |
| **RGB LED - Green** | ON | Temperature NORMAL (20-30°C) |
| **RGB LED - Blue** | ON | Temperature COLD (<20°C) |
| **White LED** | Brightness % | Artificial light level |
| **DC Motor** | Speed | Fan speed (0-5) |
| **LCD Line 1** | `T:28.5C 14:00` | Temperature and hour |
| **LCD Line 2** | `NORMAL F:3/5` | Status and fan speed |

---

## API Reference

### Environment Endpoints

#### `GET /`
Health check.

**Response:**
```json
{
  "status": "online",
  "service": "AI Time Loop Environment Emulator",
  "timestamp": "2026-03-27T18:30:00.000000"
}
```

#### `GET /current`
Get latest environment data with all agent decisions.

**Response:**
```json
{
  "timestamp": "2026-03-27T18:30:00.000000",
  "temperature": 28.5,
  "radiation": 45.2,
  "lux": 5424.0,
  "weathercode": 0,
  "hour": 14,
  "temp_status": "NORMAL",
  "fan_speed": "SLOW",
  "comfort_level": 8,
  "temp_reasoning": "Temperature is within comfortable range...",
  "light_decision": "OFF",
  "brightness_pct": 0,
  "mood": "bright",
  "scene_summary": "28°C, lights off, feels bright.",
  "model_used": "nvidia/nemotron-3-super-120b-a12b:free"
}
```

#### `POST /run?input_date=YYYY-MM-DD&input_hour=HH`
Trigger full agent run with specified date/time.

**Response:**
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
    "fan_speed": "SLOW",
    "light_decision": "OFF",
    "brightness_pct": 0,
    "mood": "bright",
    "model": "nvidia/nemotron-3-super-120b-a12b:free"
  },
  "simulide_sent": true
}
```

#### `GET /history?limit=100`
Get historical records.

**Response:**
```json
{
  "count": 10,
  "data": [
    {
      "id": 1,
      "timestamp": "2026-03-27T18:30:00",
      "temperature": 28.5,
      "temp_status": "NORMAL",
      "fan_speed": "SLOW",
      "light_decision": "OFF",
      "scene_summary": "28°C, lights off, feels bright."
    }
  ]
}
```

### SimulIDE Endpoints

#### `GET /simulide/ports`
List available serial ports.

**Response:**
```json
{
  "ports": [
    "COM3 - Standard Serial over Bluetooth link",
    "COM4 - USB Serial Device"
  ]
}
```

#### `POST /simulide/connect`
Connect to Arduino/SimulIDE.

**Request:**
```json
{
  "port": "COM3"
}
```

**Response:**
```json
{
  "connected": true,
  "port": "COM3"
}
```

#### `POST /simulide/send`
Send environment data to SimulIDE.

**Request:**
```json
{
  "temperature": 28.5,
  "temp_status": "NORMAL",
  "fan_speed": "SLOW",
  "brightness_pct": 0,
  "mood": "bright",
  "hour": 14
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Data sent to SimulIDE",
  "data": {
    "temperature": 28.5,
    "temp_status": "NORMAL",
    "fan_speed": "SLOW",
    "brightness_pct": 0,
    "mood": "bright",
    "hour": 14
  }
}
```

---

## Database Schema

```sql
CREATE TABLE env_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,

    -- Raw sensor data
    temperature REAL,
    radiation REAL,
    lux REAL,
    weathercode INTEGER,
    hour INTEGER,

    -- Temperature agent decisions
    temp_status TEXT,          -- LOW/NORMAL/HIGH
    fan_speed TEXT,            -- OFF/SLOW/MEDIUM/FAST
    comfort_level INTEGER,     -- 1-10
    temp_reasoning TEXT,
    temp_action TEXT,
    health_note TEXT,

    -- Light agent decisions
    light_decision TEXT,       -- ON/DIM/OFF
    brightness_pct INTEGER,    -- 0-100
    color_temp TEXT,           -- WARM/NEUTRAL/COOL
    light_reasoning TEXT,
    light_action TEXT,
    circadian_note TEXT,

    -- Scene agent output
    scene_description TEXT,
    mood TEXT,                 -- bright/cozy/sultry/etc.
    scene_summary TEXT,
    recommendation TEXT,

    -- Metadata
    model_used TEXT            -- AI model or "rule-based"
);
```

---

## Agent System

### Agent Architecture

Each agent inherits from `BaseAIAgent` which provides:
- LLM API integration (OpenRouter)
- JSON schema validation
- Fallback to rule-based logic
- Logging and error handling

### AI Model Configuration

**Provider:** OpenRouter API
**Model:** NVIDIA Nemotron-3 Super 120B
**Fallback:** Rule-based logic when AI unavailable

### Agent Prompts

Each agent has a system prompt that defines:
- Role and purpose
- Required JSON schema
- Validation rules
- Output format

**Example (Temperature Agent):**
```
You are a smart building thermal comfort AI agent.
You receive real-time temperature data and contextual information,
and you reason about occupant comfort, energy efficiency, and health.

You MUST respond with ONLY a valid JSON object.

Your response MUST conform to this exact JSON schema:
{
  "status": {"type": "string", "enum": ["LOW", "NORMAL", "HIGH"]},
  "fan_speed": {"type": "string", "enum": ["OFF", "SLOW", "MEDIUM", "FAST"]},
  "comfort_level": {"type": "integer", "minimum": 1, "maximum": 10},
  "reasoning": {"type": "string"},
  "action": {"type": "string"},
  "health_note": {"type": "string"}
}
```

### Decision Orchestration

`run_all_agent.py` coordinates the flow:
1. Calculate lux from radiation
2. Run TemperatureAgent
3. Run LightAgent
4. Run SceneAgent (uses outputs from both)
5. Combine all results
6. Return unified response

---

## Configuration

### Server Config (`config.py`)

```python
# Location coordinates (Chennai, India)
LATITUDE = 13.0827
LONGITUDE = 80.2707

# Open-Meteo Weather API
API_URL = "https://api.open-meteo.com/v1/forecast"

# OpenRouter AI API
OPENROUTER_API_KEY = "sk-or-v1-..."
MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"

# Database
DB_PATH = "data/env.db"
```

### Client Config

**Vite (`vite.config.ts`):**
- Port: 3000
- HMR enabled
- Tailwind CSS integration

**Environment (`.env.example`):**
```
GEMINI_API_KEY="MY_GEMINI_API_KEY"
APP_URL="MY_APP_URL"
```

---

## Setup & Installation

### Prerequisites

- **Python:** 3.11 or higher
- **Node.js:** 18+ (for client)
- **SimulIDE:** Download from [simulide.com](https://www.simulide.com)

### Server Installation

```bash
cd server

# Install dependencies
pip install fastapi uvicorn requests pydantic httpx pyserial

# Or using uv (recommended)
uv sync

# Verify installation
python -c "import serial; print('pyserial OK')"
```

### Client Installation

```bash
cd client

# Install dependencies
npm install

# Verify installation
npm run lint
```

### SimulIDE Setup

1. Download and install SimulIDE
2. Open `server/simulide_circuit.simu`
3. Load Arduino sketch: `server/arduino/time_loop_controller/time_loop_controller.ino`
4. Click **Play** to start simulation

---

## Usage Guide

### 1. Start Server

```bash
cd server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

**Verify:**
```bash
curl http://localhost:8000/
# {"status":"online","service":"AI Time Loop Environment Emulator"}
```

### 2. Start Client

```bash
cd client
npm run dev
```

**Open browser:** http://localhost:5173

### 3. Connect SimulIDE (Optional)

1. Open SimulIDE and load circuit
2. Click **Play** in SimulIDE
3. In client UI, click **SimulIDE** button (top-right)
4. Click **Connect**
5. Status should show "Connected"

### 4. Run Agents

**Via Client UI:**
1. Select date from date picker
2. Select hour from dropdown
3. Click **Run** button
4. Wait for response
5. Observe 3D scene and SimulIDE updates

**Via API:**
```bash
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"
```

**Via Auto-Sync:**
1. Enable **Auto-sync** toggle in client
2. Change date/hour
3. Agents run automatically

### 5. View Data

**Environment Panel (top-left):**
- Temperature
- Status (NORMAL/HOT/COLD)
- Comfort level
- Mood
- Radiation
- Lux

**Manual Controls (bottom):**
- Fan speed slider (0-5)
- Light intensity slider (0-100)
- Time buttons (morning/afternoon/evening/night)

---

## Testing

### Server Tests

```bash
cd server

# Health check
curl http://localhost:8000/

# Get current data
curl http://localhost:8000/current

# Run agents
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"

# Get history
curl "http://localhost:8000/history?limit=10"
```

### SimulIDE Tests

```bash
# List ports
curl http://localhost:8000/simulide/ports

# Connect
curl -X POST http://localhost:8000/simulide/connect

# Send data
curl -X POST http://localhost:8000/simulide/send \
  -H "Content-Type: application/json" \
  -d '{"temperature":28.5,"temp_status":"NORMAL","fan_speed":"SLOW","brightness_pct":0,"mood":"bright","hour":14}'

# Check status
curl http://localhost:8000/simulide/status
```

### Client Tests

```bash
cd client

# TypeScript check
npm run lint

# Build production
npm run build

# Preview production
npm run preview
```

---

## Troubleshooting

### Server Issues

**Error: `ModuleNotFoundError: No module named 'serial'`**
```bash
pip install pyserial
```

**Error: Port 8000 already in use**
```bash
uvicorn api:app --reload --port 8001
```

**Error: Database errors**
```bash
# Delete and recreate database
rm data/env.db
python test_p1.py
```

### Client Issues

**Error: `vite` not found**
```bash
npm install
```

**Error: TypeScript errors**
```bash
npm run lint
# Fix reported errors
```

**Build fails**
```bash
rm -rf node_modules
npm install
npm run build
```

### SimulIDE Issues

**No serial ports detected**
- Install CH340/CP2102 drivers for USB-serial adapters
- Check Device Manager (Windows) for available COM ports
- Try manual port selection instead of auto-detect

**Arduino not responding**
- Verify sketch is compiled in SimulIDE
- Check simulation is running (Play button)
- Open Serial Monitor in SimulIDE (9600 baud)
- Use `/simulide/reset` endpoint

**Components not working**
- RGB LED: Ensure it's set to "Common Anode" type
- Motor: Check fan_speed > 0
- LCD: Verify wiring matches pinout diagram
- LED: Check brightness_pct > 0

### API Issues

**404 Not Found**
- Check server is running: `curl http://localhost:8000/`
- Verify endpoint path is correct

**500 Internal Server Error**
- Check server logs for details
- Verify API key is valid in `config.py`
- Test with fallback (rule-based) by removing API key

**503 Service Unavailable (SimulIDE)**
- Connect to SimulIDE first: `POST /simulide/connect`
- Check serial port is not in use by another program

---

## Quick Reference

### Common Commands

```bash
# Start server
cd server && uvicorn api:app --reload

# Start client
cd client && npm run dev

# Test API
curl http://localhost:8000/current

# Run agents for specific time
curl -X POST "http://localhost:8000/run?input_date=2026-03-27&input_hour=14"

# Connect SimulIDE
curl -X POST http://localhost:8000/simulide/connect

# Check database
sqlite3 server/data/env.db "SELECT * FROM env_data ORDER BY id DESC LIMIT 5;"
```

### Data Mapping Summary

| Server Field | Client Visual | SimulIDE Component |
|--------------|---------------|-------------------|
| `hour` | timeOfDay | LCD hour display |
| `temp_status` | (used in panel) | RGB LED color |
| `fan_speed` | fanSpeed (0-5) | DC Motor speed |
| `brightness_pct` | lightIntensity (0-100) | White LED PWM |
| `mood` | Display panel | (narrative only) |
| `temperature` | Display panel | LCD temp display |

### File Locations

| File | Path |
|------|------|
| Server API | `server/api.py` |
| Agent Orchestrator | `server/agents/run_all_agent.py` |
| SimulIDE Serial | `server/utils/serial_comm.py` |
| Client App | `client/src/App.tsx` |
| Client API | `client/src/api.ts` |
| Arduino Sketch | `server/arduino/time_loop_controller/time_loop_controller.ino` |
| SimulIDE Circuit | `server/simulide_circuit.simu` |
| Database | `server/data/env.db` |

---

## License & Credits

**Project:** AI Time Loop Environment Emulator
**Architecture:** Multi-agent AI system with 3D visualization and hardware simulation
**Location:** Chennai, India (13.0827°N, 80.2707°E)
**Weather API:** Open-Meteo (free, no API key required)
**AI Model:** NVIDIA Nemotron-3 Super 120B via OpenRouter

---

**End of Documentation**
