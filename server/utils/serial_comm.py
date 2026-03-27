"""
serial_comm.py
──────────────
Serial communication module for SimulIDE Arduino integration.
Sends environment data to Arduino via serial port.
"""
import serial
import serial.tools.list_ports
import logging
import time
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArduinoSerial:
    """Handles serial communication with Arduino (SimulIDE)."""
    
    def __init__(self, port: str = None, baud_rate: int = 9600):
        self.port = port
        self.baud_rate = baud_rate
        self.serial_conn: Optional[serial.Serial] = None
        self.connected = False
    
    def list_ports(self) -> list:
        """List available serial ports."""
        ports = serial.tools.list_ports.comports()
        return [f"{p.device} - {p.description}" for p in ports]
    
    def connect(self, port: str = None) -> bool:
        """
        Connect to Arduino via serial port.
        
        Args:
            port: COM port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
                  If None, auto-detects available ports.
        
        Returns:
            True if connection successful, False otherwise.
        """
        if port:
            self.port = port
        
        if not self.port:
            # Auto-detect: try common Arduino ports
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if 'Arduino' in p.description or 'CH340' in p.description or 'USB Serial' in p.description:
                    self.port = p.device
                    logger.info(f"Auto-detected Arduino on {self.port}")
                    break
            
            if not self.port and ports:
                # Use first available port if no Arduino detected
                self.port = ports[0].device
                logger.info(f"Using first available port: {self.port}")
        
        if not self.port:
            logger.warning("No serial ports available")
            return False
        
        try:
            self.serial_conn = serial.Serial(self.port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            self.connected = True
            logger.info(f"Connected to Arduino on {self.port}")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Arduino."""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
            self.connected = False
            logger.info("Disconnected from Arduino")
    
    def send_command(self, command: str) -> bool:
        """
        Send a command to Arduino.
        
        Args:
            command: Command string (will be sent with newline)
        
        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.connected or not self.serial_conn or not self.serial_conn.is_open:
            logger.warning("Not connected to Arduino")
            return False
        
        try:
            self.serial_conn.write(f"{command}\n".encode('utf-8'))
            self.serial_conn.flush()
            logger.debug(f"Sent: {command}")
            return True
        except serial.SerialException as e:
            logger.error(f"Send failed: {e}")
            return False
    
    def read_response(self, timeout: float = 0.1) -> str:
        """Read response from Arduino."""
        if not self.connected or not self.serial_conn:
            return ""
        
        try:
            if self.serial_conn.in_waiting > 0:
                return self.serial_conn.readline().decode('utf-8').strip()
        except Exception as e:
            logger.error(f"Read failed: {e}")
        return ""
    
    def send_environment_data(
        self,
        temperature: float,
        temp_status: str,
        fan_speed: str,
        brightness_pct: int,
        mood: str,
        hour: int
    ) -> bool:
        """
        Send complete environment data to Arduino.
        
        Args:
            temperature: Temperature in Celsius
            temp_status: Temperature status (COLD/NORMAL/HOT)
            fan_speed: Fan speed string (OFF/LOW/MED/HIGH)
            brightness_pct: Light brightness percentage (0-100)
            mood: Scene mood
            hour: Hour of day (0-23)
        
        Returns:
            True if all commands sent successfully.
        """
        if not self.connected:
            return False
        
        # Convert fan_speed string to numeric (0-5)
        fan_map = {
            'OFF': 0, 'NONE': 0,
            'LOW': 2, 'SLOW': 2,
            'MEDIUM': 3, 'MED': 3, 'MID': 3,
            'HIGH': 4, 'FAST': 4,
            'MAX': 5, 'TURBO': 5
        }
        fan_numeric = fan_map.get(fan_speed.upper(), 0)
        
        # Send all data
        commands = [
            f"TEMP:{temperature}",
            f"STATUS:{temp_status}",
            f"FAN:{fan_numeric}",
            f"LIGHT:{brightness_pct}",
            f"MOOD:{mood}",
            f"HOUR:{hour}"
        ]
        
        success = True
        for cmd in commands:
            if not self.send_command(cmd):
                success = False
            time.sleep(0.05)  # Small delay between commands
        
        return success
    
    def get_status(self) -> dict:
        """Request current status from Arduino."""
        if not self.connected:
            return {}
        
        self.send_command("GET_STATUS")
        time.sleep(0.1)
        response = self.read_response()
        
        if response.startswith("ARDUINO_STATUS:"):
            # Parse: ARDUINO_STATUS:FAN=3,LIGHT=50,TEMP=25.5,STATUS=NORMAL
            data = {}
            parts = response[15:].split(',')
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    data[key.strip()] = value.strip()
            return data
        
        return {}
    
    def reset(self) -> bool:
        """Reset Arduino to default state."""
        return self.send_command("RESET")


# Global instance for easy access
_arduino: Optional[ArduinoSerial] = None


def get_arduino() -> ArduinoSerial:
    """Get or create global ArduinoSerial instance."""
    global _arduino
    if _arduino is None:
        _arduino = ArduinoSerial()
    return _arduino


def connect_to_arduino(port: str = None) -> bool:
    """Connect to Arduino (convenience function)."""
    return get_arduino().connect(port)


def send_to_arduino(
    temperature: float,
    temp_status: str,
    fan_speed: str,
    brightness_pct: int,
    mood: str,
    hour: int
) -> bool:
    """Send environment data to Arduino (convenience function)."""
    return get_arduino().send_environment_data(
        temperature, temp_status, fan_speed, brightness_pct, mood, hour
    )
