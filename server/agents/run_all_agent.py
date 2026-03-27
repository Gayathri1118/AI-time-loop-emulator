"""
run_all_agent.py
────────────────
Orchestrator that runs all agents in sequence and combines results.
"""
import logging
from .temp_agent import TemperatureAgent
from .light_agent import LightAgent
from .scene_agent import SceneAgent
from typing import Optional

logger = logging.getLogger(__name__)


def run_all_agents(
    temperature: float,
    radiation: float,
    weathercode: int = 0,
    hour_of_day: int = 12,
    prev_temp: Optional[float] = None,
    prev_lux: Optional[float] = None,
    api_key: str = "",
) -> dict:
    """
    Run Temperature, Light, and Scene agents in sequence.

    Args:
        temperature  : current temperature in °C
        radiation    : shortwave radiation in W/m²
        weathercode  : Open-Meteo weather code
        hour_of_day  : hour of day (0-23)
        prev_temp    : previous temperature reading (optional, for trend)
        prev_lux     : previous lux reading (optional, for trend)
        api_key      : OpenRouter API key (uses default if empty)

    Returns:
        Combined result dictionary with all agent outputs
    """
    logger.info("[run_all_agents] Starting agent orchestration")
    logger.info("[run_all_agents] Input: temp=%.1f°C, radiation=%.1fW/m², weathercode=%d, hour=%d",
                temperature, radiation, weathercode, hour_of_day)

    # Calculate lux from radiation (approximate conversion)
    lux = radiation * 120
    logger.info("[run_all_agents] Calculated lux: %.0f (radiation * 120)", lux)

    # Initialize agents
    logger.info("[run_all_agents] Initializing agents")
    temp_agent = TemperatureAgent(api_key=api_key)
    light_agent = LightAgent(api_key=api_key)
    scene_agent = SceneAgent(api_key=api_key)

    # Run temperature agent
    logger.info("[run_all_agents] Running TemperatureAgent...")
    temp_result = temp_agent.run(
        temperature=temperature,
        weathercode=weathercode,
        hour_of_day=hour_of_day,
        prev_temp=prev_temp,
    )
    logger.info("[run_all_agents] TemperatureAgent complete: status=%s, fan_speed=%s",
                temp_result.get("status", "N/A"), temp_result.get("fan_speed", "N/A"))

    # Run light agent
    logger.info("[run_all_agents] Running LightAgent...")
    light_result = light_agent.run(
        lux=lux,
        weathercode=weathercode,
        hour_of_day=hour_of_day,
        radiation=radiation,
        prev_lux=prev_lux,
    )
    logger.info("[run_all_agents] LightAgent complete: decision=%s, brightness=%d%%",
                light_result.get("decision", "N/A"), light_result.get("brightness_pct", 0))

    # Run scene agent (synthesizes both agent outputs)
    logger.info("[run_all_agents] Running SceneAgent...")
    scene_result = scene_agent.run(
        temperature=temperature,
        lux=lux,
        light_decision=light_result.get("decision", "OFF"),
        temp_status=temp_result.get("status", "NORMAL"),
        weathercode=weathercode,
        hour_of_day=hour_of_day,
        light_reasoning=light_result.get("reasoning", ""),
        temp_reasoning=temp_result.get("reasoning", ""),
    )
    logger.info("[run_all_agents] SceneAgent complete: mood=%s", scene_result.get("mood", "N/A"))

    # Combine all results
    combined = {
        # Raw sensor data
        "temperature": temperature,
        "radiation": radiation,
        "lux": lux,
        "weathercode": weathercode,
        "hour": hour_of_day,

        # Temperature agent outputs
        "temp_status": temp_result.get("status", "NORMAL"),
        "fan_speed": temp_result.get("fan_speed", "OFF"),
        "comfort_level": temp_result.get("comfort_level", 5),
        "temp_reasoning": temp_result.get("reasoning", ""),
        "temp_action": temp_result.get("action", ""),
        "health_note": temp_result.get("health_note", ""),

        # Light agent outputs
        "light_decision": light_result.get("decision", "OFF"),
        "brightness_pct": light_result.get("brightness_pct", 0),
        "color_temp": light_result.get("color_temp", "NEUTRAL"),
        "light_reasoning": light_result.get("reasoning", ""),
        "light_action": light_result.get("action", ""),
        "circadian_note": light_result.get("circadian_note", ""),

        # Scene agent outputs
        "scene_description": scene_result.get("description", ""),
        "mood": scene_result.get("mood", ""),
        "scene_summary": scene_result.get("summary", ""),
        "recommendation": scene_result.get("recommendation", ""),

        # Metadata
        "model": temp_result.get("model", "rule-based"),
    }

    logger.info("[run_all_agents] Agent orchestration complete")
    logger.info("[run_all_agents] Summary: temp_status=%s, light=%s, mood=%s",
                combined["temp_status"], combined["light_decision"], combined["mood"])
    return combined
