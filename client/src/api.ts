/**
 * API service for communicating with the AI Time Loop Environment Emulator server.
 */

const API_BASE_URL = 'http://localhost:8000';

export interface ServerResponse {
  timestamp: string;
  temperature: number;
  radiation: number;
  lux: number;
  weathercode: number;
  hour: number;
  temp_status: string;
  fan_speed: string;
  comfort_level: number;
  temp_reasoning: string;
  temp_action: string;
  health_note: string;
  light_decision: string;
  brightness_pct: number;
  color_temp: string;
  light_reasoning: string;
  light_action: string;
  circadian_note: string;
  scene_description: string;
  mood: string;
  scene_summary: string;
  recommendation: string;
  model_used: string;
}

export interface RunAgentsResponse {
  status: string;
  input: {
    date: string;
    hour: number;
  };
  environment: {
    temperature: number;
    radiation: number;
    lux: number;
    weathercode: number;
    hour: number;
  };
  agents: ServerResponse;
}

export interface SimulIDEStatus {
  connected: boolean;
  port: string | null;
  status: {
    FAN?: string;
    LIGHT?: string;
    TEMP?: string;
    STATUS?: string;
  };
}

/**
 * Fetch current environment data from the server.
 */
export async function getCurrentData(): Promise<ServerResponse> {
  const response = await fetch(`${API_BASE_URL}/current`);
  if (!response.ok) {
    throw new Error(`Failed to fetch current data: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Run agents with specified date and hour.
 */
export async function runAgents(date: string, hour: number): Promise<RunAgentsResponse> {
  const response = await fetch(
    `${API_BASE_URL}/run?input_date=${encodeURIComponent(date)}&input_hour=${hour}`,
    {
      method: 'POST',
    }
  );
  if (!response.ok) {
    throw new Error(`Failed to run agents: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get weather data only (without running agents).
 */
export async function getWeather(date: string, hour: number): Promise<{
  temperature: number;
  radiation: number;
  lux: number;
  weathercode: number;
  hour: number;
}> {
  const response = await fetch(
    `${API_BASE_URL}/weather?date=${encodeURIComponent(date)}&hour=${hour}`
  );
  if (!response.ok) {
    throw new Error(`Failed to fetch weather: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get historical data.
 */
export async function getHistory(limit: number = 100): Promise<{
  count: number;
  data: ServerResponse[];
}> {
  const response = await fetch(`${API_BASE_URL}/history?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.statusText}`);
  }
  return response.json();
}

// ─────────────────────────────────────────────────────────────────────────────
// SimulIDE / Arduino API Functions
// ─────────────────────────────────────────────────────────────────────────────

/**
 * List available serial ports.
 */
export async function listSerialPorts(): Promise<{ ports: string[] }> {
  const response = await fetch(`${API_BASE_URL}/simulide/ports`);
  if (!response.ok) {
    throw new Error(`Failed to list serial ports: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Connect to SimulIDE/Arduino.
 */
export async function connectSimulIDE(port?: string): Promise<{ connected: boolean; port: string | null }> {
  const response = await fetch(`${API_BASE_URL}/simulide/connect`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ port }),
  });
  if (!response.ok) {
    throw new Error(`Failed to connect to SimulIDE: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Disconnect from SimulIDE/Arduino.
 */
export async function disconnectSimulIDE(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/simulide/disconnect`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to disconnect from SimulIDE: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Send environment data to SimulIDE.
 */
export async function sendToSimulIDE(data: {
  temperature: number;
  temp_status: string;
  fan_speed: string;
  brightness_pct: number;
  mood: string;
  hour: number;
}): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/simulide/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error(`Failed to send to SimulIDE: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Get SimulIDE connection status.
 */
export async function getSimulIDEStatus(): Promise<SimulIDEStatus> {
  const response = await fetch(`${API_BASE_URL}/simulide/status`);
  if (!response.ok) {
    throw new Error(`Failed to get SimulIDE status: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Reset SimulIDE/Arduino to default state.
 */
export async function resetSimulIDE(): Promise<{ status: string; message: string }> {
  const response = await fetch(`${API_BASE_URL}/simulide/reset`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Failed to reset SimulIDE: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Convert server hour (0-23) to client timeOfDay.
 */
export function hourToTimeOfDay(hour: number): 'morning' | 'afternoon' | 'evening' | 'night' {
  if (hour >= 6 && hour <= 11) return 'morning';
  if (hour >= 12 && hour <= 16) return 'afternoon';
  if (hour >= 17 && hour <= 20) return 'evening';
  return 'night';
}

/**
 * Convert server fan_speed string to client fanSpeed number (0-5).
 */
export function fanSpeedToNumber(fanSpeed: string): number {
  const normalized = fanSpeed.toUpperCase();
  if (normalized === 'OFF' || normalized === 'NONE') return 0;
  if (normalized === 'LOW' || normalized === 'SLOW') return 2;
  if (normalized === 'MEDIUM' || normalized === 'MED' || normalized === 'MID') return 3;
  if (normalized === 'HIGH' || normalized === 'FAST') return 4;
  if (normalized === 'MAX' || normalized === 'TURBO') return 5;
  // Try to parse as number
  const parsed = parseInt(fanSpeed, 10);
  if (!isNaN(parsed) && parsed >= 0 && parsed <= 5) return parsed;
  return 0; // Default to OFF
}
