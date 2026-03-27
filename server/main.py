"""
main.py
───────
Main entry point for the AI Time Loop Environment Emulator.
Runs continuously, collecting environment data and processing through AI agents.
"""
from phase1_data import get_environment_data
from agents.run_all_agent import run_all_agents
from db_handler import insert_data
from config import OPENROUTER_API_KEY
from datetime import datetime
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_cycle(input_date: str, input_hour: int):
    """
    Run one complete cycle of data collection and agent processing.
    
    Args:
        input_date: Date string in YYYY-MM-DD format
        input_hour: Hour of day (0-23)
    
    Returns:
        Dictionary with combined environment and agent results
    """
    logger.info(f"Starting cycle for {input_date} {input_hour}:00")
    
    # Phase 1: Data collection
    env_data = get_environment_data(input_date, input_hour)

    if "error" in env_data:
        logger.error(f"Phase 1 failed: {env_data['error']}")
        return None

    logger.info(f"Environment data: temp={env_data['temperature']}°C, "
                f"radiation={env_data['radiation']}W/m², "
                f"weathercode={env_data['weathercode']}")

    # Phase 2: Agent processing
    result = run_all_agents(
        temperature=env_data["temperature"],
        radiation=env_data["radiation"],
        weathercode=env_data["weathercode"],
        hour_of_day=input_hour,
        api_key=OPENROUTER_API_KEY
    )

    # Add metadata
    result["timestamp"] = datetime.now().isoformat()
    result["model_used"] = result.get("model", "rule-based")

    # Phase 3: Store results
    insert_data(result)

    logger.info(f"Cycle complete - Status: {result.get('temp_status', 'N/A')}, "
                f"Light: {result.get('light_decision', 'N/A')}, "
                f"Mood: {result.get('mood', 'N/A')}")

    return result


def main():
    """
    Main loop - runs continuously, updating every 5 seconds.
    Uses current date/time for live data.
    """
    logger.info("AI Time Loop Environment Emulator starting...")
    logger.info(f"Location: 13.0827°N, 80.2707°E (Chennai, India)")
    
    try:
        while True:
            now = datetime.now()
            input_date = now.strftime("%Y-%m-%d")
            input_hour = now.hour
            
            result = run_cycle(input_date, input_hour)
            
            if result:
                print("\n" + "="*60)
                print(f"  Timestamp: {result['timestamp']}")
                print(f"  Temperature: {result['temperature']}°C ({result['temp_status']})")
                print(f"  Light: {result['light_decision']} ({result['brightness_pct']}%)")
                print(f"  Scene: {result['scene_summary']}")
                print(f"  Mood: {result['mood']}")
                print("="*60 + "\n")
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
