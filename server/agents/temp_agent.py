"""
temp_agent.py
─────────────
AI-powered temperature agent for thermal comfort analysis.
"""
import logging
from .agents import BaseAIAgent
from config import MODEL_NAME
from typing import Optional

logger = logging.getLogger(__name__)


class TemperatureAgent(BaseAIAgent):
    """
    AI-powered temperature agent.

    Instead of: if temp < 20 → LOW
    Now does: reasons about thermal comfort, humidity context,
              time of day, trend direction, and health implications.

    Output keys:
        status        : "LOW" | "NORMAL" | "HIGH"
        fan_speed     : "OFF" | "SLOW" | "MEDIUM" | "FAST"
        comfort_level : 1–10
        reasoning     : one-sentence explanation
        action        : what the smart room should do
        health_note   : brief health/comfort advisory
    """

    name = "TemperatureAgent"

    SYSTEM = """You are a smart building thermal comfort AI agent.
You receive real-time temperature data and contextual information,
and you reason about occupant comfort, energy efficiency, and health.

You MUST respond with ONLY a valid JSON object — no markdown, no preamble, no explanations.

Your response MUST conform to this exact JSON schema:
{
  "type": "object",
  "required": ["status", "fan_speed", "comfort_level", "reasoning", "action", "health_note"],
  "properties": {
    "status": {"type": "string", "enum": ["LOW", "NORMAL", "HIGH"]},
    "fan_speed": {"type": "string", "enum": ["OFF", "SLOW", "MEDIUM", "FAST"]},
    "comfort_level": {"type": "integer", "minimum": 1, "maximum": 10},
    "reasoning": {"type": "string", "description": "One sentence explaining your decision"},
    "action": {"type": "string", "description": "One concrete smart-room action to take"},
    "health_note": {"type": "string", "description": "Brief health/comfort advisory"}
  },
  "additionalProperties": false
}

Rules for status:
  LOW    = thermally cold, heating may be needed
  NORMAL = comfortable range for most occupants
  HIGH   = warm/hot, cooling or ventilation needed

Rules for fan_speed:
  OFF    = no cooling needed
  SLOW   = gentle air circulation
  MEDIUM = active cooling
  FAST   = aggressive cooling, urgent

comfort_level: integer 1 (very uncomfortable) to 10 (perfect comfort)
reasoning: one sentence explaining your decision based on the data
action: one concrete smart-room action to take right now
health_note: brief advisory about health/comfort at this temperature

Respond with ONLY the JSON object, nothing else."""

    def run(
        self,
        temperature: float,
        weathercode: int = 0,
        hour_of_day: int = 12,
        humidity_pct: Optional[float] = None,
        prev_temp: Optional[float] = None,
    ) -> dict:
        """
        Analyze temperature and return AI decision.

        Args:
            temperature  : current temperature in °C
            weathercode  : Open-Meteo weather code (0=clear, 61=rain, etc.)
            hour_of_day  : 0–23, used for circadian reasoning
            humidity_pct : relative humidity 0–100 (optional)
            prev_temp    : previous reading for trend detection (optional)
        """
        logger.info("[%s] Starting temperature analysis", self.name)
        logger.info("[%s] Input: temp=%.1f°C, weathercode=%d, hour=%d, prev_temp=%s",
                    self.name, temperature, weathercode, hour_of_day,
                    f"{prev_temp:.1f}" if prev_temp else "None")

        trend = "unknown"
        if prev_temp is not None:
            diff = temperature - prev_temp
            trend = "rising" if diff > 0.3 else "falling" if diff < -0.3 else "stable"
            logger.info("[%s] Temperature trend: %s (diff: %.2f°C)", self.name, trend, diff)

        weather_desc = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy",
            3: "overcast", 45: "foggy", 51: "light drizzle",
            61: "light rain", 63: "moderate rain", 71: "light snow",
            80: "rain showers", 95: "thunderstorm",
        }.get(weathercode, f"weather code {weathercode}")

        period = (
            "night" if hour_of_day < 6 else
            "morning" if hour_of_day < 12 else
            "midday" if hour_of_day < 14 else
            "afternoon" if hour_of_day < 18 else
            "evening" if hour_of_day < 21 else
            "night"
        )
        logger.info("[%s] Weather: %s, Time period: %s", self.name, weather_desc, period)

        humidity_line = (
            f"- Relative humidity: {humidity_pct:.0f}%"
            if humidity_pct is not None
            else "- Humidity: not available"
        )

        user_prompt = f"""Current sensor readings for smart room environment:

- Temperature: {temperature:.1f}°C
- Temperature trend: {trend}
{humidity_line}
- Outside weather: {weather_desc}
- Time of day: {period} (hour {hour_of_day})
- Previous temperature: {f'{prev_temp:.1f}°C' if prev_temp else 'no prior reading'}

Analyze the thermal environment and decide the appropriate status,
fan speed, and smart room action. Consider:
1. Is this temperature comfortable for a typical occupant?
2. Is the trend concerning (rapidly rising in already hot conditions)?
3. Does the time of day affect what "comfortable" means?
4. What is the most energy-efficient action?

Respond with JSON only."""

        logger.info("[%s] Calling LLM for temperature analysis", self.name)
        result = self._call_llm(self.SYSTEM, user_prompt)

        if not result:
            logger.info("[%s] LLM call returned empty result, using fallback", self.name)
            result = self._fallback(temperature)
        else:
            logger.info("[%s] LLM response received, validating...", self.name)
            # Validate and normalize the result
            result = self._validate_result(result, temperature)

        logger.info("[%s] Final decision: status=%s, fan_speed=%s, comfort_level=%d",
                    self.name, result.get("status"), result.get("fan_speed"),
                    result.get("comfort_level", 5))
        result["temperature"] = temperature
        result["agent"] = self.name
        result["model"] = MODEL_NAME if self.api_key else "rule-based"
        return result

    def _validate_result(self, result: dict, temperature: float) -> dict:
        """
        Validate and normalize the AI result to ensure consistent schema.
        Falls back to rule-based if validation fails.
        """
        logger.info("[%s] Validating AI result", self.name)
        required_fields = ["status", "fan_speed", "comfort_level", "reasoning", "action", "health_note"]
        valid_status = ["LOW", "NORMAL", "HIGH"]
        valid_fan_speeds = ["OFF", "SLOW", "MEDIUM", "FAST"]

        # Check all required fields exist
        for field in required_fields:
            if field not in result:
                logger.info("[%s] Missing field '%s', using fallback", self.name, field)
                return self._fallback(temperature)

        # Validate and normalize status
        status = str(result.get("status", "")).upper()
        if status not in valid_status:
            logger.info("[%s] Invalid status '%s', using fallback", self.name, status)
            return self._fallback(temperature)
        result["status"] = status

        # Validate and normalize fan_speed
        fan_speed = str(result.get("fan_speed", "")).upper()
        if fan_speed not in valid_fan_speeds:
            logger.info("[%s] Invalid fan_speed '%s', using fallback", self.name, fan_speed)
            return self._fallback(temperature)
        result["fan_speed"] = fan_speed

        # Validate comfort_level is integer 1-10
        try:
            comfort_level = int(result.get("comfort_level", 5))
            comfort_level = max(1, min(10, comfort_level))
            result["comfort_level"] = comfort_level
        except (ValueError, TypeError):
            logger.info("[%s] Invalid comfort_level, using fallback", self.name)
            return self._fallback(temperature)

        # Ensure string fields are strings
        for field in ["reasoning", "action", "health_note"]:
            result[field] = str(result.get(field, ""))

        logger.info("[%s] Validation successful", self.name)
        return result

    def _fallback(self, temperature: float) -> dict:
        """Rule-based fallback when AI is unavailable."""
        logger.info("[%s] Using rule-based fallback for temp=%.1f°C", self.name, temperature)
        if temperature < 20:
            logger.info("[%s] Fallback decision: LOW (temp < 20°C)", self.name)
            return {
                "status": "LOW",
                "fan_speed": "OFF",
                "comfort_level": 4,
                "reasoning": f"Temperature {temperature:.1f}°C is below comfortable range.",
                "action": "Activate heating or close windows.",
                "health_note": "Cold temperatures can cause discomfort and reduce productivity.",
            }
        elif temperature > 30:
            logger.info("[%s] Fallback decision: HIGH (temp > 30°C)", self.name)
            return {
                "status": "HIGH",
                "fan_speed": "FAST",
                "comfort_level": 3,
                "reasoning": f"Temperature {temperature:.1f}°C exceeds comfort threshold.",
                "action": "Activate cooling, increase fan speed, close blinds.",
                "health_note": "Heat stress risk — ensure hydration and ventilation.",
            }
        else:
            logger.info("[%s] Fallback decision: NORMAL (20°C <= temp <= 30°C)", self.name)
            return {
                "status": "NORMAL",
                "fan_speed": "SLOW" if temperature > 26 else "OFF",
                "comfort_level": 8,
                "reasoning": f"Temperature {temperature:.1f}°C is within comfortable range.",
                "action": "Maintain current settings.",
                "health_note": "Comfortable conditions — no action required.",
            }
