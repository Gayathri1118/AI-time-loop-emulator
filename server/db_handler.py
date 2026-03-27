"""
db_handler.py
─────────────
Database handler for storing environment and agent decision data.
"""
import sqlite3
from config import DB_PATH
import os

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Database connection (thread-safe for reads, serialized for writes)
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# Create table with all agent data columns
cursor.execute("""
CREATE TABLE IF NOT EXISTS env_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    
    -- Raw sensor data
    temperature REAL,
    radiation REAL,
    lux REAL,
    weathercode INTEGER,
    hour INTEGER,
    
    -- Temperature agent decisions
    temp_status TEXT,
    fan_speed TEXT,
    comfort_level INTEGER,
    temp_reasoning TEXT,
    temp_action TEXT,
    health_note TEXT,
    
    -- Light agent decisions
    light_decision TEXT,
    brightness_pct INTEGER,
    color_temp TEXT,
    light_reasoning TEXT,
    light_action TEXT,
    circadian_note TEXT,
    
    -- Scene agent output
    scene_description TEXT,
    mood TEXT,
    scene_summary TEXT,
    recommendation TEXT,
    
    -- Metadata
    model_used TEXT
)
""")
conn.commit()


def insert_data(data: dict):
    """
    Insert a complete environment + agent data record.
    
    Args:
        data: Dictionary containing all sensor and agent data
    """
    cursor.execute("""
    INSERT INTO env_data (
        timestamp,
        temperature, radiation, lux, weathercode, hour,
        temp_status, fan_speed, comfort_level, temp_reasoning, temp_action, health_note,
        light_decision, brightness_pct, color_temp, light_reasoning, light_action, circadian_note,
        scene_description, mood, scene_summary, recommendation,
        model_used
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("timestamp", ""),
        data.get("temperature", 0),
        data.get("radiation", 0),
        data.get("lux", 0),
        data.get("weathercode", 0),
        data.get("hour", 12),
        data.get("temp_status", "NORMAL"),
        data.get("fan_speed", "OFF"),
        data.get("comfort_level", 5),
        data.get("temp_reasoning", ""),
        data.get("temp_action", ""),
        data.get("health_note", ""),
        data.get("light_decision", "OFF"),
        data.get("brightness_pct", 0),
        data.get("color_temp", "NEUTRAL"),
        data.get("light_reasoning", ""),
        data.get("light_action", ""),
        data.get("circadian_note", ""),
        data.get("scene_description", ""),
        data.get("mood", ""),
        data.get("scene_summary", ""),
        data.get("recommendation", ""),
        data.get("model_used", "unknown")
    ))
    conn.commit()


def get_current():
    """
    Get the most recent environment data record.
    Returns a dictionary with all fields.
    """
    cursor.execute("""
    SELECT * FROM env_data ORDER BY id DESC LIMIT 1
    """)
    row = cursor.fetchone()
    
    if not row:
        return None
    
    # Column indices based on CREATE TABLE
    return {
        "id": row[0],
        "timestamp": row[1],
        "temperature": row[2],
        "radiation": row[3],
        "lux": row[4],
        "weathercode": row[5],
        "hour": row[6],
        "temp_status": row[7],
        "fan_speed": row[8],
        "comfort_level": row[9],
        "temp_reasoning": row[10],
        "temp_action": row[11],
        "health_note": row[12],
        "light_decision": row[13],
        "brightness_pct": row[14],
        "color_temp": row[15],
        "light_reasoning": row[16],
        "light_action": row[17],
        "circadian_note": row[18],
        "scene_description": row[19],
        "mood": row[20],
        "scene_summary": row[21],
        "recommendation": row[22],
        "model_used": row[23]
    }


def get_history(limit: int = 100):
    """
    Get recent environment data records.
    
    Args:
        limit: Maximum number of records to return
    
    Returns:
        List of dictionaries with environment data
    """
    cursor.execute(f"""
    SELECT * FROM env_data ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "timestamp": row[1],
            "temperature": row[2],
            "radiation": row[3],
            "lux": row[4],
            "weathercode": row[5],
            "hour": row[6],
            "temp_status": row[7],
            "fan_speed": row[8],
            "light_decision": row[13],
            "scene_summary": row[21]
        })
    
    return data


def close():
    """Close database connection."""
    conn.close()


print("Database handler initialized")
