"""
api.py
──────
FastAPI REST API for the AI Time Loop Environment Emulator.
Provides endpoints for current data, history, and manual agent triggers.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging

from config import OPENROUTER_API_KEY
from db_handler import get_current, get_history, insert_data
from phase1_data import get_environment_data
from agents.run_all_agent import run_all_agents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Time Loop Environment Emulator API")

# CORS - allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """API health check."""
    return {
        "status": "online",
        "service": "AI Time Loop Environment Emulator",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/current")
def get_current_data():
    """
    Get the most recent environment data with all agent decisions.
    This is the main endpoint for the frontend dashboard.
    """
    data = get_current()
    
    if not data:
        # Return default data if database is empty
        return {
            "temperature": 24.0,
            "radiation": 0.0,
            "lux": 500.0,
            "weathercode": 0,
            "hour": 12,
            "temp_status": "NORMAL",
            "fan_speed": "OFF",
            "comfort_level": 5,
            "temp_reasoning": "No data available yet",
            "temp_action": "",
            "health_note": "",
            "light_decision": "OFF",
            "brightness_pct": 0,
            "color_temp": "NEUTRAL",
            "light_reasoning": "",
            "light_action": "",
            "circadian_note": "",
            "scene_description": "Waiting for first data collection cycle...",
            "mood": "neutral",
            "scene_summary": "System initializing",
            "recommendation": "",
            "model_used": "none"
        }
    
    # Format for frontend compatibility
    return {
        "timestamp": data["timestamp"],
        "temperature": data["temperature"],
        "radiation": data["radiation"],
        "lux": data["lux"],
        "weathercode": data["weathercode"],
        "hour": data["hour"],
        "temp_status": data["temp_status"],
        "fan_speed": data["fan_speed"],
        "comfort_level": data["comfort_level"],
        "temp_reasoning": data["temp_reasoning"],
        "temp_action": data["temp_action"],
        "health_note": data["health_note"],
        "light_decision": data["light_decision"],
        "brightness_pct": data["brightness_pct"],
        "color_temp": data["color_temp"],
        "light_reasoning": data["light_reasoning"],
        "light_action": data["light_action"],
        "circadian_note": data["circadian_note"],
        "scene_description": data["scene_description"],
        "mood": data["mood"],
        "scene_summary": data["scene_summary"],
        "recommendation": data["recommendation"],
        "model_used": data["model_used"]
    }


@app.get("/history")
def get_history_data(limit: int = 100):
    """
    Get historical environment data.
    
    Args:
        limit: Maximum number of records to return (default: 100)
    """
    try:
        history = get_history(limit)
        return {"count": len(history), "data": history}
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run")
def run_agents(input_date: str = None, input_hour: int = None):
    """
    Manually trigger a full agent run with specified or current time.
    This runs Phase 1 (data collection) and Phase 2 (agents).
    
    Args:
        input_date: Optional date in YYYY-MM-DD format (default: today)
        input_hour: Optional hour 0-23 (default: current hour)
    """
    try:
        # Use current date/time if not specified
        if input_date is None:
            input_date = datetime.now().strftime("%Y-%m-%d")
        if input_hour is None:
            input_hour = datetime.now().hour
        
        logger.info(f"Running agents for {input_date} {input_hour}:00")
        
        # Phase 1: Get environment data
        env_data = get_environment_data(input_date, input_hour)
        
        if "error" in env_data:
            raise HTTPException(status_code=500, detail=env_data["error"])
        
        # Phase 2: Run all agents
        result = run_all_agents(
            temperature=env_data["temperature"],
            radiation=env_data["radiation"],
            weathercode=env_data["weathercode"],
            hour_of_day=input_hour,
            api_key=OPENROUTER_API_KEY
        )
        
        # Add timestamp and store
        result["timestamp"] = datetime.now().isoformat()
        insert_data(result)
        
        logger.info("Agent run completed successfully")
        return {
            "status": "success",
            "input": {"date": input_date, "hour": input_hour},
            "environment": env_data,
            "agents": result
        }
        
    except Exception as e:
        logger.error(f"Agent run failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/weather")
def get_weather(date: str = None, hour: int = None):
    """
    Get weather data for a specific date/hour without running agents.
    Useful for debugging data collection.
    """
    try:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        if hour is None:
            hour = datetime.now().hour
            
        env_data = get_environment_data(date, hour)
        return env_data
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
def shutdown():
    """Cleanup on server shutdown."""
    from db_handler import close
    close()
