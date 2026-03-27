"""
scene_agent.py
──────────────
AI-powered scene description agent that synthesizes agent decisions into narrative.
"""
import logging
from .agents import BaseAIAgent
from config import MODEL_NAME
from typing import Optional

logger = logging.getLogger(__name__)


class SceneAgent(BaseAIAgent):
    """
    AI-powered scene description agent.
    Reads decisions from both other agents and synthesizes a
    human-readable narrative of the current smart room environment.
    
    Output keys:
        description   : 2-3 sentences describing the room atmosphere
        mood          : one word capturing the room's atmosphere
        summary       : one short sentence — the essential state
        recommendation: one practical tip for the occupant
    """

    name = "SceneAgent"

    SYSTEM = """You are a smart environment narrator for an AI-powered room.
You receive sensor readings and agent decisions, and you write
a vivid, human-friendly description of the current environment.

You MUST respond with ONLY a valid JSON object — no markdown, no preamble, no explanations.

Your response MUST conform to this exact JSON schema:
{
  "type": "object",
  "required": ["description", "mood", "summary", "recommendation"],
  "properties": {
    "description": {"type": "string", "description": "2-3 sentences describing the room atmosphere"},
    "mood": {"type": "string", "description": "One word capturing the room's atmosphere"},
    "summary": {"type": "string", "description": "One short sentence — the essential state"},
    "recommendation": {"type": "string", "description": "One practical tip for the occupant"}
  },
  "additionalProperties": false
}

description: 2–3 sentences describing what the room feels like right now.
             Be specific about temperature feel, light quality, and atmosphere.
mood: one word capturing the room's atmosphere (e.g. "cozy", "bright", "sultry", "dim")
summary: one short sentence — the essential state in plain English
recommendation: one practical tip for the occupant right now

Respond with ONLY the JSON object, nothing else."""

    def run(
        self,
        temperature: float,
        lux: float,
        light_decision: str,
        temp_status: str,
        weathercode: int = 0,
        hour_of_day: int = 12,
        light_reasoning: str = "",
        temp_reasoning: str = "",
    ) -> dict:
        """
        Synthesize environment data and agent decisions into a narrative.

        Args:
            temperature     : current temperature in °C
            lux             : light intensity in lux
            light_decision  : "ON" | "DIM" | "OFF"
            temp_status     : "LOW" | "NORMAL" | "HIGH"
            weathercode     : Open-Meteo weather code
            hour_of_day     : 0-23
            light_reasoning : from light agent (optional)
            temp_reasoning  : from temp agent (optional)
        """
        logger.info("[%s] Starting scene synthesis", self.name)
        logger.info("[%s] Input: temp=%.1f°C, lux=%.0f, light=%s, temp_status=%s, hour=%d",
                    self.name, temperature, lux, light_decision, temp_status, hour_of_day)

        weather_desc = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy",
            3: "overcast", 45: "foggy", 61: "light rain",
            63: "moderate rain", 80: "rain showers", 95: "thunderstorm",
        }.get(weathercode, f"code {weathercode}")

        logger.info("[%s] Weather: %s", self.name, weather_desc)

        user_prompt = f"""Smart room environment snapshot:

Sensor data:
  Temperature : {temperature:.1f}°C  → agent says: {temp_status}
  Light (lux) : {lux:.0f} lux     → agent says: {light_decision}
  Outside     : {weather_desc}
  Time        : {hour_of_day:02d}:00

Agent reasoning:
  Temp agent  : {temp_reasoning or 'not provided'}
  Light agent : {light_reasoning or 'not provided'}

Write a natural, vivid description of what this room environment feels like.
Respond with JSON only."""

        logger.info("[%s] Calling LLM for scene synthesis", self.name)
        result = self._call_llm(self.SYSTEM, user_prompt, max_tokens=300)

        if not result:
            logger.info("[%s] LLM call returned empty result, using fallback", self.name)
            result = self._scene_fallback(temperature, lux, light_decision, temp_status)
        else:
            logger.info("[%s] LLM response received, validating...", self.name)
            # Validate and normalize the result
            result = self._validate_result(result)

        logger.info("[%s] Final scene: mood=%s, summary=%s",
                    self.name, result.get("mood"), result.get("summary"))
        result["agent"] = self.name
        result["model"] = MODEL_NAME if self.api_key else "rule-based"
        return result

    def _validate_result(self, result: dict) -> dict:
        """
        Validate and normalize the AI result to ensure consistent schema.
        Falls back to rule-based if validation fails.
        """
        logger.info("[%s] Validating AI result", self.name)
        required_fields = ["description", "mood", "summary", "recommendation"]

        # Check all required fields exist
        for field in required_fields:
            if field not in result:
                logger.info("[%s] Missing field '%s', using fallback", self.name, field)
                return self._scene_fallback(
                    result.get("temperature", 25),
                    result.get("lux", 500),
                    result.get("light_decision", "OFF"),
                    result.get("temp_status", "NORMAL")
                )

        # Ensure all fields are strings
        for field in required_fields:
            result[field] = str(result.get(field, ""))

        logger.info("[%s] Validation successful", self.name)
        return result

    def _scene_fallback(self, temp: float, lux: float, light: str, temp_status: str) -> dict:
        """Rule-based fallback when AI is unavailable."""
        logger.info("[%s] Using rule-based fallback", self.name)
        mood = (
            "cozy" if temp_status == "LOW" and light == "ON" else
            "bright" if lux > 5000 and temp_status == "NORMAL" else
            "sultry" if temp_status == "HIGH" else
            "dim" if light in ("ON", "DIM") else
            "pleasant"
        )
        logger.info("[%s] Fallback mood: %s", self.name, mood)
        return {
            "description": (
                f"The room sits at {temp:.1f}°C with {lux:.0f} lux of ambient light. "
                f"Artificial lighting is {light.lower()}. "
                f"The thermal environment is classified as {temp_status.lower()}."
            ),
            "mood": mood,
            "summary": f"{temp:.0f}°C, lights {light.lower()}, feels {mood}.",
            "recommendation": (
                "Open a window for ventilation." if temp_status == "HIGH" else
                "Consider a light layer of clothing." if temp_status == "LOW" else
                "Conditions are comfortable — enjoy your space."
            ),
        }
