/*
 * AI Time Loop Environment Emulator - Arduino Controller
 * For SimulIDE Simulation
 * 
 * Receives serial commands from Python server and controls:
 * - RGB LED (temperature status)
 * - White LED (light control)
 * - DC Motor (fan speed)
 * - LCD Display (environment data)
 */

#include <LiquidCrystal.h>

// LCD pins: RS, EN, D4, D5, D6, D7
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

// RGB LED pins (common anode)
const int RED_PIN = 9;
const int GREEN_PIN = 10;
const int BLUE_PIN = 6;

// White LED pin (light control)
const int WHITE_LED_PIN = 7;

// DC Motor pin (fan control via PWM)
const int FAN_PIN = 8;

// Button for manual override
const int BUTTON_PIN = 13;

// State variables
int fanSpeed = 0;        // 0-5 scale
int lightBrightness = 0; // 0-100%
String tempStatus = "NORMAL";
String mood = "neutral";
float temperature = 25.0;
int hour = 12;

// Serial input buffer
String inputBuffer = "";

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  while (!Serial) {
    ; // Wait for serial port to connect
  }

  // Initialize pins
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(WHITE_LED_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Initialize LCD
  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("AI Time Loop");
  lcd.setCursor(0, 1);
  lcd.print("Initializing...");
  
  delay(2000);
  
  // Set default states
  updateRGBLed();
  updateWhiteLed();
  updateFan();
  updateDisplay();
}

void loop() {
  // Read serial input
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }

  // Update display every 100ms
  static unsigned long lastUpdate = 0;
  if (millis() - lastUpdate > 100) {
    lastUpdate = millis();
    updateDisplay();
  }

  // Check button for manual override
  static bool lastButtonState = HIGH;
  bool buttonState = digitalRead(BUTTON_PIN);
  if (lastButtonState == HIGH && buttonState == LOW) {
    // Button pressed - toggle auto/manual mode
    Serial.println("BUTTON_PRESSED");
  }
  lastButtonState = buttonState;
  
  delay(10);
}

void processCommand(String cmd) {
  cmd.trim();
  
  if (cmd.startsWith("TEMP:")) {
    // Temperature update: TEMP:25.5
    temperature = cmd.substring(5).toFloat();
  }
  else if (cmd.startsWith("STATUS:")) {
    // Temperature status: STATUS:NORMAL|COLD|HOT
    tempStatus = cmd.substring(7);
    updateRGBLed();
  }
  else if (cmd.startsWith("FAN:")) {
    // Fan speed: FAN:0-5
    fanSpeed = cmd.substring(4).toInt();
    updateFan();
  }
  else if (cmd.startsWith("LIGHT:")) {
    // Light brightness: LIGHT:0-100
    lightBrightness = cmd.substring(6).toInt();
    updateWhiteLed();
  }
  else if (cmd.startsWith("MOOD:")) {
    // Mood: MOOD:bright|calm|dark|etc
    mood = cmd.substring(5);
  }
  else if (cmd.startsWith("HOUR:")) {
    // Hour: HOUR:14
    hour = cmd.substring(5).toInt();
  }
  else if (cmd == "RESET") {
    // Reset to defaults
    fanSpeed = 0;
    lightBrightness = 0;
    tempStatus = "NORMAL";
    temperature = 25.0;
    updateRGBLed();
    updateWhiteLed();
    updateFan();
  }
  else if (cmd == "GET_STATUS") {
    // Return current status
    Serial.print("ARDUINO_STATUS:");
    Serial.print("FAN=");
    Serial.print(fanSpeed);
    Serial.print(",LIGHT=");
    Serial.print(lightBrightness);
    Serial.print(",TEMP=");
    Serial.print(temperature);
    Serial.print(",STATUS=");
    Serial.print(tempStatus);
    Serial.println();
  }
}

void updateRGBLed() {
  // Common anode RGB LED (LOW = on)
  if (tempStatus == "COLD") {
    // Blue for cold
    analogWrite(RED_PIN, 255);
    analogWrite(GREEN_PIN, 255);
    analogWrite(BLUE_PIN, 0);
  }
  else if (tempStatus == "HOT" || tempStatus == "HIGH") {
    // Red for hot
    analogWrite(RED_PIN, 0);
    analogWrite(GREEN_PIN, 255);
    analogWrite(BLUE_PIN, 255);
  }
  else {
    // Green for normal
    analogWrite(RED_PIN, 255);
    analogWrite(GREEN_PIN, 0);
    analogWrite(BLUE_PIN, 255);
  }
}

void updateWhiteLed() {
  // Map brightness (0-100) to PWM (0-255)
  int pwmValue = map(lightBrightness, 0, 100, 0, 255);
  analogWrite(WHITE_LED_PIN, pwmValue);
}

void updateFan() {
  // Map fan speed (0-5) to PWM (0-255)
  int pwmValue = map(fanSpeed, 0, 5, 0, 255);
  analogWrite(FAN_PIN, pwmValue);
}

void updateDisplay() {
  lcd.clear();
  
  // Line 1: Temp and hour
  lcd.print("T:");
  lcd.print(temperature, 1);
  lcd.print("C ");
  lcd.print(hour);
  lcd.print(":00 ");
  
  // Line 2: Status and fan
  lcd.print(tempStatus);
  lcd.print(" F:");
  lcd.print(fanSpeed);
  lcd.print("/5");
}
