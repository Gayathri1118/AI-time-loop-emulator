"""
agents.py
──────────
Base AI Agent for the AI Time Loop Environment Emulator.
All agents inherit from BaseAIAgent and use OpenRouter API for LLM calls.
"""
from __future__ import annotations
import json
import logging
import re
import requests
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import OPENROUTER_API_KEY, MODEL_NAME

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def _repair_json_string(content: str) -> str:
    """
    Attempt to repair common JSON issues like unterminated strings.
    Returns the repaired JSON string.
    """
    content = content.strip()
    
    # Remove markdown code blocks
    if content.startswith("```"):
        lines = content.split("\n")
        if lines[0].lower().startswith("```json"):
            lines = lines[1:]
        content = "\n".join(lines)
        if content.endswith("```"):
            content = content[:-3]
    
    content = content.strip()
    
    # Fix unterminated strings by finding unclosed quotes
    # Look for patterns like: "key": "value without closing quote
    def fix_unterminated_strings(match):
        key = match.group(1)
        value = match.group(2)
        # Escape any internal quotes in the value
        value = value.replace('"', '\\"').replace('\n', ' ')
        return f'"{key}": "{value}"'
    
    # Pattern to match "key": "value (without closing quote) followed by comma or }
    content = re.sub(r'"([^"]+)":\s*"([^"]*)(?=[,}\n])', fix_unterminated_strings, content)
    
    # Ensure proper closing
    if not content.endswith("}"):
        content = content.rstrip(",") + "}"
    
    return content


class BaseAIAgent:
    """Base AI agent that handles LLM API calls with fallback support."""

    name: str = "BaseAgent"

    def __init__(self, api_key: str = OPENROUTER_API_KEY):
        self.api_key = api_key
        self.model_name = MODEL_NAME

    def _call_llm(self, system: str, user: str, max_tokens: int = 400) -> dict:
        """
        Call the LLM API and return parsed JSON response.
        Returns empty dict on failure (caller should use fallback).
        """
        logger.info("[%s] Preparing LLM request (model=%s, max_tokens=%d)",
                    self.name, self.model_name, max_tokens)

        if not self.api_key:
            logger.info("[%s] No API key — skipping LLM call, using fallback logic", self.name)
            return {}

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            logger.info("[%s] Sending request to OpenRouter API", self.name)
            response = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=20
            )

            response.raise_for_status()
            data = response.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                logger.info("[%s] Empty content from API response", self.name)
                return {}
            content = content.strip()
            logger.info("[%s] Received LLM response (%d characters)", self.name, len(content))

            # Clean markdown code blocks
            if content.startswith("```"):
                lines = content.split("\n")
                if lines[0].lower().startswith("```json"):
                    lines = lines[1:]
                content = "\n".join(lines)
                if content.endswith("```"):
                    content = content[:-3]
                logger.info("[%s] Cleaned markdown code blocks from response", self.name)

            content = content.strip()

            # Try parsing as-is first
            try:
                parsed = json.loads(content)
                logger.info("[%s] Successfully parsed JSON response", self.name)
                return parsed
            except json.JSONDecodeError:
                logger.info("[%s] Initial JSON parse failed, attempting repair", self.name)
                pass

            # Attempt to repair the JSON
            repaired = _repair_json_string(content)
            try:
                result = json.loads(repaired)
                logger.info("[%s] Successfully repaired JSON", self.name)
                return result
            except json.JSONDecodeError as repair_error:
                logger.info("[%s] JSON repair failed: %s", self.name, str(repair_error)[:100])
                logger.debug("[%s] Raw content: %s", self.name, content[:200])
                logger.debug("[%s] Repaired content: %s", self.name, repaired[:200])
                return {}

        except requests.exceptions.Timeout:
            logger.info("[%s] API request timed out", self.name)
            return {}
        except requests.exceptions.RequestException as e:
            logger.info("[%s] Request error: %s", self.name, e)
            return {}
        except Exception as e:
            logger.info("[%s] Unexpected error: %s", self.name, e)
            return {}
