"""
light_agent.py
──────────────
AI-powered light agent for lighting and circadian rhythm analysis.
"""
import logging
from .agents import BaseAIAgent
from config import MODEL_NAME
from typing import Optional

logger = logging.getLogger(__name__)


class LightAgent(BaseAIAgent):
    """
    AI-powered light agent.

    Instead of: if lux < 100 → ON
    Now does: reasons about visual comfort, circadian rhythm,
              energy efficiency, time of day, and task context.

    Output keys:
        decision       : "ON" | "DIM" | "OFF"
        brightness_pct : 0–100 (precise PWM target)
        color_temp     : "WARM" | "NEUTRAL" | "COOL"
        reasoning      : one-sentence explanation
        action         : what the smart lighting should do
        circadian_note : circadian rhythm advisory
    """

    name = "LightAgent"

    SYSTEM = """You are a smart building lighting AI agent.
You receive real-time lux (light intensity) data and contextual information,
and you reason about visual comfort, energy efficiency, and circadian health.

You MUST respond with ONLY a valid JSON object — no markdown, no preamble, no explanations.

Your response MUST conform to this exact JSON schema:
{
  "type": "object",
  "required": ["decision", "brightness_pct", "color_temp", "reasoning", "action", "circadian_note"],
  "properties": {
    "decision": {"type": "string", "enum": ["ON", "DIM", "OFF"]},
    "brightness_pct": {"type": "integer", "minimum": 0, "maximum": 100},
    "color_temp": {"type": "string", "enum": ["WARM", "NEUTRAL", "COOL"]},
    "reasoning": {"type": "string", "description": "One sentence explaining the lighting decision"},
    "action": {"type": "string", "description": "One concrete smart-lighting action to execute"},
    "circadian_note": {"type": "string", "description": "How this lighting choice affects circadian rhythm"}
  },
  "additionalProperties": false
}

Rules for decision:
  ON  = artificial lighting should be fully active
  DIM = partial/supplementary lighting needed
  OFF = sufficient natural light, no artificial light needed

brightness_pct: integer 0–100
  0        = lights off
  1–30     = very dim (night mode / accent)
  31–60    = medium (evening / overcast supplement)
  61–90    = bright (work light)
  91–100   = full (very dark conditions)

color_temp:
  WARM    = 2700K feel — evening, relaxation, wind-down
  NEUTRAL = 4000K feel — general daytime tasks
  COOL    = 6500K feel — morning alertness, focus tasks

reasoning: one sentence explaining the lighting decision
action: one concrete smart-lighting action to execute now
circadian_note: how this lighting choice affects the circadian clock

Respond with ONLY the JSON object, nothing else."""

    def run(
        self,
        lux: float,
        weathercode: int = 0,
        hour_of_day: int = 12,
        radiation: Optional[float] = None,
        prev_lux: Optional[float] = None,
    ) -> dict:
        """
        Analyze lux and context, return AI lighting decision.

        Args:
            lux         : light intensity in lux
            weathercode : Open-Meteo weather code
            hour_of_day : 0–23
            radiation   : shortwave radiation W/m² (optional)
            prev_lux    : previous lux reading (optional)
        """
        logger.info("[%s] Starting light analysis", self.name)
        logger.info("[%s] Input: lux=%.0f, weathercode=%d, hour=%d, radiation=%s",
                    self.name, lux, weathercode, hour_of_day,
                    f"{radiation:.1f}" if radiation else "None")

        trend = "unknown"
        if prev_lux is not None:
            diff = lux - prev_lux
            trend = "brightening" if diff > 200 else "dimming" if diff < -200 else "stable"
            logger.info("[%s] Light trend: %s (diff: %.0f lux)", self.name, trend, diff)

        weather_desc = {
            0: "clear sky", 1: "mainly clear", 2: "partly cloudy",
            3: "overcast", 45: "foggy", 61: "light rain",
            63: "moderate rain", 80: "rain showers", 95: "thunderstorm",
        }.get(weathercode, f"weather code {weathercode}")

        period = (
            "night" if hour_of_day < 6 else
            "early morning" if hour_of_day < 8 else
            "morning" if hour_of_day < 12 else
            "midday" if hour_of_day < 14 else
            "afternoon" if hour_of_day < 18 else
            "evening" if hour_of_day < 21 else
            "night"
        )
        logger.info("[%s] Weather: %s, Time period: %s", self.name, weather_desc, period)

        radiation_line = (
            f"- Solar radiation: {radiation:.1f} W/m²"
            if radiation is not None
            else "- Solar radiation: not available"
        )

        user_prompt = f"""Current sensor readings for smart room lighting:

- Light intensity (lux): {lux:.0f} lux
- Light trend: {trend}
{radiation_line}
- Outside weather: {weather_desc}
- Time of day: {period} (hour {hour_of_day})
- Previous lux: {f'{prev_lux:.0f} lux' if prev_lux else 'no prior reading'}

Analyze the lighting environment and decide appropriate artificial lighting.
Consider:
1. Is natural light sufficient for comfortable indoor visibility?
2. What time-of-day factor affects ideal brightness and color temperature?
3. Is lux trending in a direction that requires preemptive adjustment?
4. How can lighting support circadian rhythm health?
5. What is the most energy-efficient setting?

Typical references:
  < 100 lux    = very dark (heavy overcast, night)
  100–500      = dim indoor / overcast day
  500–2000     = comfortable indoor / cloudy outdoor
  2000–10000   = bright day
  > 10000      = direct sunlight

Respond with JSON only."""

        logger.info("[%s] Calling LLM for light analysis", self.name)
        result = self._call_llm(self.SYSTEM, user_prompt)

        if not result:
            logger.info("[%s] LLM call returned empty result, using fallback", self.name)
            result = self._fallback(lux, hour_of_day)
        else:
            logger.info("[%s] LLM response received, validating...", self.name)
            # Validate and normalize the result
            result = self._validate_result(result, lux, hour_of_day)

        logger.info("[%s] Final decision: decision=%s, brightness=%d%%, color_temp=%s",
                    self.name, result.get("decision"), result.get("brightness_pct", 0),
                    result.get("color_temp"))
        result["lux"] = lux
        result["agent"] = self.name
        result["model"] = MODEL_NAME if self.api_key else "rule-based"
        return result

    def _validate_result(self, result: dict, lux: float, hour: int) -> dict:
        """
        Validate and normalize the AI result to ensure consistent schema.
        Falls back to rule-based if validation fails.
        """
        logger.info("[%s] Validating AI result", self.name)
        required_fields = ["decision", "brightness_pct", "color_temp", "reasoning", "action", "circadian_note"]
        valid_decisions = ["ON", "DIM", "OFF"]
        valid_color_temps = ["WARM", "NEUTRAL", "COOL"]

        # Check all required fields exist
        for field in required_fields:
            if field not in result:
                logger.info("[%s] Missing field '%s', using fallback", self.name, field)
                return self._fallback(lux, hour)

        # Validate and normalize decision
        decision = str(result.get("decision", "")).upper()
        if decision not in valid_decisions:
            logger.info("[%s] Invalid decision '%s', using fallback", self.name, decision)
            return self._fallback(lux, hour)
        result["decision"] = decision

        # Validate and normalize color_temp
        color_temp = str(result.get("color_temp", "")).upper()
        if color_temp not in valid_color_temps:
            logger.info("[%s] Invalid color_temp '%s', using fallback", self.name, color_temp)
            return self._fallback(lux, hour)
        result["color_temp"] = color_temp

        # Validate brightness_pct is integer 0-100
        try:
            brightness_pct = int(result.get("brightness_pct", 50))
            brightness_pct = max(0, min(100, brightness_pct))
            result["brightness_pct"] = brightness_pct
        except (ValueError, TypeError):
            logger.info("[%s] Invalid brightness_pct, using fallback", self.name)
            return self._fallback(lux, hour)

        # Ensure string fields are strings
        for field in ["reasoning", "action", "circadian_note"]:
            result[field] = str(result.get(field, ""))

        logger.info("[%s] Validation successful", self.name)
        return result

    def _fallback(self, lux: float, hour: int = 12) -> dict:
        """Rule-based fallback when AI is unavailable."""
        logger.info("[%s] Using rule-based fallback for lux=%.0f, hour=%d", self.name, lux, hour)
        night = hour < 6 or hour >= 21
        if lux < 100:
            logger.info("[%s] Fallback decision: ON (lux < 100)", self.name)
            return {
                "decision": "ON",
                "brightness_pct": 90,
                "color_temp": "WARM" if night else "NEUTRAL",
                "reasoning": f"Very low lux ({lux:.0f}) — artificial lighting required.",
                "action": "Turn on lights at high brightness.",
                "circadian_note": "Use warm light in evening to avoid melatonin suppression.",
            }
        elif lux < 500:
            logger.info("[%s] Fallback decision: DIM (100 <= lux < 500)", self.name)
            return {
                "decision": "DIM",
                "brightness_pct": 45,
                "color_temp": "WARM" if night else "NEUTRAL",
                "reasoning": f"Low lux ({lux:.0f}) — supplementary lighting helpful.",
                "action": "Activate lights at medium brightness to supplement natural light.",
                "circadian_note": "Neutral light appropriate for daytime tasks.",
            }
        else:
            logger.info("[%s] Fallback decision: OFF (lux >= 500)", self.name)
            return {
                "decision": "OFF",
                "brightness_pct": 0,
                "color_temp": "NEUTRAL",
                "reasoning": f"Sufficient natural light ({lux:.0f} lux) — no artificial lighting needed.",
                "action": "Keep lights off to save energy.",
                "circadian_note": "Ample natural light supports healthy daytime alertness.",
            }


def light_decision(lux: float) -> str:
    """Quick helper to get just the light decision."""
    agent = LightAgent()
    result = agent.run(lux=lux)
    return result.get("decision", "OFF")
