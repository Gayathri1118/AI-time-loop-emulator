# SimulIDE Integration Guide

## Overview

This guide explains how to integrate the AI Time Loop Environment Emulator with **SimulIDE**, an open-source electronic circuit simulator. The integration allows you to visualize server outputs on a virtual Arduino circuit with:

- **RGB LED** - Shows temperature status (Red=HOT, Green=NORMAL, Blue=COLD)
- **White LED** - Shows light brightness (PWM controlled)
- **DC Motor** - Shows fan speed (PWM controlled)
- **LCD Display** - Shows environment data (temperature, hour, status, fan speed)
- **Push Button** - Manual override trigger

---

## Prerequisites

1. **SimulIDE** - Download from [simulide.com](https://www.simulide.com/)
2. **Python pyserial** - Already included in server dependencies
3. **Server running** - FastAPI server on port 8000

---

## Installation

### Step 1: Install SimulIDE

1. Download SimulIDE from [https://www.simulide.com](https://www.simulide.com)
2. Install and launch the application

### Step 2: Install Server Dependencies

```bash
cd server
pip install pyserial
# Or if using uv:
uv add pyserial
```

### Step 3: Load Arduino Sketch

1. Open SimulIDE
2. Go to **Microcontrollers → Arduino → Arduino Uno**
3. Right-click the Arduino → **Load Firmware**
4. Navigate to: `server/arduino/time_loop_controller/time_loop_controller.ino`
5. Click **Compile** in the Arduino IDE window that opens
6. Wait for compilation to complete

---

## Circuit Setup

### Option A: Use Provided Circuit File

1. In SimulIDE, go to **File → Open**
2. Select: `server/simulide_circuit.simu`
3. The circuit will load with all components pre-wired

### Option B: Build Circuit Manually

#### Components Needed:
| Component | Location in SimulIDE | Quantity |
|-----------|---------------------|----------|
| Arduino Uno | Microcontrollers → Arduino | 1 |
| USB Serial | Connections → Serial | 1 |
| RGB LED (Common Anode) | Leds → RGB | 1 |
| White LED | Leds → Standard | 1 |
| DC Motor | Motors → DC | 1 |
| LCD 16x2 | Displays → LCD | 1 |
| Push Button | Switches → Push | 1 |
| Ground | Sources → Ground | 3 |
| VCC (5V) | Sources → VCC | 2 |

#### Wiring Diagram:

```
Arduino Uno Pin Connections:
─────────────────────────────────────────────────────────
Pin   │ Component        │ Purpose
──────┼──────────────────┼─────────────────────────────
D2    │ LCD D7           │ LCD Data
D3    │ LCD D6           │ LCD Data
D4    │ LCD D5           │ LCD Data
D5    │ LCD D4           │ LCD Data
D6    │ RGB LED (Blue)   │ Temperature: COLD
D7    │ White LED (Anode)│ Light Control (PWM)
D8    │ DC Motor (+)     │ Fan Control (PWM)
D9    │ RGB LED (Red)    │ Temperature: HOT
D10   │ RGB LED (Green)  │ Temperature: NORMAL
D11   │ LCD EN           │ LCD Enable
D12   │ LCD RS           │ LCD Register Select
D13   │ Push Button      │ Manual Override
TX    │ USB Serial RX    │ Serial Communication
RX    │ USB Serial TX    │ Serial Communication
GND   │ All GND pins     │ Ground
5V    │ LCD VCC, RGB VCC │ Power
```

---

## Running the Integration

### Step 1: Start the Server

```bash
cd server
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Step 2: Open SimulIDE Circuit

1. Open SimulIDE
2. Load `simulide_circuit.simu` or build your circuit
3. Ensure the Arduino has the sketch loaded
4. Click **Play** button in SimulIDE to start simulation

### Step 3: Connect via Client UI

1. Open the client application (`npm run dev`)
2. Click the **SimulIDE** button in the top-right corner
3. The panel will show connection status

**Connect to SimulIDE:**
1. Click **Refresh** to list available serial ports
2. Select a port (or leave as "Auto-detect")
3. Click **Connect**
4. Status should change to "Connected"

### Step 4: Send Data to SimulIDE

**Automatic:**
- When SimulIDE is connected, data is automatically sent when you:
  - Call `/current` endpoint
  - Run agents via `/run` endpoint
  - Use the client "Run" button

**Manual:**
- Use the API endpoint directly:

```bash
curl -X POST http://localhost:8000/simulide/send \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 28.5,
    "temp_status": "NORMAL",
    "fan_speed": "LOW",
    "brightness_pct": 50,
    "mood": "bright",
    "hour": 14
  }'
```

---

## API Endpoints

### SimulIDE Control

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/simulide/ports` | GET | List available serial ports |
| `/simulide/connect` | POST | Connect to Arduino/SimulIDE |
| `/simulide/disconnect` | POST | Disconnect from SimulIDE |
| `/simulide/send` | POST | Send environment data |
| `/simulide/status` | GET | Get connection status |
| `/simulide/reset` | POST | Reset Arduino to defaults |

### Example: Connect to SimulIDE

```bash
# List ports
curl http://localhost:8000/simulide/ports

# Connect (auto-detect)
curl -X POST http://localhost:8000/simulide/connect

# Connect (specific port)
curl -X POST http://localhost:8000/simulide/connect \
  -H "Content-Type: application/json" \
  -d '{"port": "COM3"}'

# Check status
curl http://localhost:8000/simulide/status

# Disconnect
curl -X POST http://localhost:8000/simulide/disconnect
```

---

## Arduino Serial Commands

The Arduino sketch accepts the following serial commands:

| Command | Format | Example | Description |
|---------|--------|---------|-------------|
| Temperature | `TEMP:<value>` | `TEMP:28.5` | Set temperature |
| Status | `STATUS:<status>` | `STATUS:NORMAL` | Set temp status (COLD/NORMAL/HOT) |
| Fan Speed | `FAN:<0-5>` | `FAN:3` | Set fan speed (0-5) |
| Light | `LIGHT:<0-100>` | `LIGHT:50` | Set brightness % |
| Mood | `MOOD:<mood>` | `MOOD:bright` | Set mood |
| Hour | `HOUR:<0-23>` | `HOUR:14` | Set hour |
| Reset | `RESET` | `RESET` | Reset to defaults |
| Get Status | `GET_STATUS` | `GET_STATUS` | Request current status |

### Response Format

Arduino responds to `GET_STATUS` with:
```
ARDUINO_STATUS:FAN=3,LIGHT=50,TEMP=28.5,STATUS=NORMAL
```

---

## Troubleshooting

### SimulIDE Not Connecting

1. **Check server is running** - `http://localhost:8000/` should respond
2. **Install pyserial** - `pip install pyserial`
3. **Check available ports** - Use `/simulide/ports` endpoint
4. **Try manual port selection** - Don't use auto-detect

### Arduino Not Responding

1. **Check sketch is compiled** - Re-compile in SimulIDE
2. **Check simulation is running** - Click Play in SimulIDE
3. **Check serial monitor** - Open Serial Monitor in SimulIDE (9600 baud)
4. **Reset Arduino** - Use `/simulide/reset` endpoint

### Components Not Working

1. **RGB LED stays off** - Check it's set to "Common Anode" type
2. **Motor not spinning** - Check fan_speed is > 0
3. **LCD shows blanks** - Check wiring matches pinout diagram
4. **LED not brightening** - Check brightness_pct is > 0

### Serial Port Issues (Windows)

1. **No ports listed** - Install CH340/CP2102 drivers if using USB-serial adapter
2. **Port in use** - Close Serial Monitor or other programs using the port
3. **Access denied** - Run SimulIDE as Administrator

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (React App)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Date/Time    │  │ SimulIDE     │  │ 3D Visual    │          │
│  │ Input        │  │ Panel        │  │ Environment  │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  ┌──────────────────────────────────────────────────┐          │
│  │              API Calls (HTTP)                     │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SERVER (FastAPI)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ /run         │  │ /current     │  │ /simulide/*  │          │
│  │ (Agents)     │  │ (Data)       │  │ (Serial)     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  ┌──────────────────────────────────────────────────┐          │
│  │         Serial Communication (pyserial)           │          │
│  └──────────────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (Serial @ 9600 baud)
┌─────────────────────────────────────────────────────────────────┐
│                    SimulIDE (Arduino)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ RGB LED      │  │ White LED    │  │ DC Motor     │          │
│  │ (Temp)       │  │ (Light)      │  │ (Fan)        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ LCD Display  │  │ Push Button  │                             │
│  │ (Data)       │  │ (Override)   │                             │
│  └──────────────┘  └──────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start Checklist

- [ ] SimulIDE installed
- [ ] Server dependencies installed (`pip install pyserial`)
- [ ] Server running on port 8000
- [ ] Arduino sketch loaded in SimulIDE
- [ ] Circuit built or loaded (`simulide_circuit.simu`)
- [ ] Simulation started (Play button clicked)
- [ ] Client connected to SimulIDE via panel
- [ ] Run agents → See updates in SimulIDE!

---

## Files Reference

| File | Location | Description |
|------|----------|-------------|
| Arduino Sketch | `server/arduino/time_loop_controller/time_loop_controller.ino` | Main Arduino code |
| Circuit File | `server/simulide_circuit.simu` | Pre-built SimulIDE circuit |
| Serial Module | `server/utils/serial_comm.py` | Python serial communication |
| API Endpoints | `server/api.py` | SimulIDE API routes |
| Client API | `client/src/api.ts` | SimulIDE client functions |
| This Guide | `server/SIMULIDE_SETUP.md` | Setup documentation |

---

## Next Steps

1. **Test with different scenarios** - Try various temperatures and times
2. **Observe hardware response** - Watch LEDs and motor react to data
3. **Monitor LCD display** - See real-time data updates
4. **Experiment with manual override** - Press the button in SimulIDE

For issues or questions, check the troubleshooting section or review the server logs.
