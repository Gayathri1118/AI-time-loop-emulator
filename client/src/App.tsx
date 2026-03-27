/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { Lighting, TimeOfDay } from './components/Lighting';
import { Architecture } from './components/Architecture';
import { Fixtures } from './components/Fixtures';
import { Furniture } from './components/Furniture';
import { InteractableRooms } from './components/InteractableRooms';
import { Fan, Sun, Sunset, Moon, CloudSun, Lightbulb, Play, Loader2, AlertCircle, Cpu, Plug, Power } from 'lucide-react';
import { runAgents, getCurrentData, hourToTimeOfDay, fanSpeedToNumber, getSimulIDEStatus, connectSimulIDE, disconnectSimulIDE, listSerialPorts } from './api';

export default function App() {
    const [timeOfDay, setTimeOfDay] = useState<TimeOfDay>('afternoon');
    const [fanSpeed, setFanSpeed] = useState(3);
    const [lightIntensity, setLightIntensity] = useState(0);
    const [hoveredRoom, setHoveredRoom] = useState<string | null>(null);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

    // Server integration state
    const [inputDate, setInputDate] = useState(() => new Date().toISOString().split('T')[0]);
    const [inputHour, setInputHour] = useState(() => new Date().getHours());
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [serverData, setServerData] = useState<any>(null);
    const [autoSync, setAutoSync] = useState(false);

    // SimulIDE state
    const [simulIDEConnected, setSimulIDEConnected] = useState(false);
    const [simulIDEPort, setSimulIDEPort] = useState<string | null>(null);
    const [availablePorts, setAvailablePorts] = useState<string[]>([]);
    const [selectedPort, setSelectedPort] = useState<string>('');
    const [showSimulIDEPanel, setShowSimulIDEPanel] = useState(false);

    useEffect(() => {
        if (timeOfDay === 'night') setLightIntensity(100);
        else if (timeOfDay === 'evening') setLightIntensity(60);
        else setLightIntensity(0);
    }, [timeOfDay]);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            setMousePos({ x: e.clientX, y: e.clientY });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    // Auto-sync: fetch server data when time changes
    useEffect(() => {
        if (autoSync) {
            handleRunAgents();
        }
    }, [autoSync, inputDate, inputHour]);

    const handleRunAgents = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const result = await runAgents(inputDate, inputHour);
            const agents = result.agents;
            
            setServerData(agents);
            
            // Map server data to visual parameters
            setTimeOfDay(hourToTimeOfDay(agents.hour));
            setFanSpeed(fanSpeedToNumber(agents.fan_speed));
            setLightIntensity(agents.brightness_pct);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch from server');
        } finally {
            setIsLoading(false);
        }
    };

    const handleLoadCurrent = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const data = await getCurrentData();
            setServerData(data);
            
            setTimeOfDay(hourToTimeOfDay(data.hour));
            setFanSpeed(fanSpeedToNumber(data.fan_speed));
            setLightIntensity(data.brightness_pct);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch current data');
        } finally {
            setIsLoading(false);
        }
    };

    // SimulIDE functions
    const handleRefreshPorts = async () => {
        try {
            const result = await listSerialPorts();
            setAvailablePorts(result.ports);
        } catch (err) {
            setError('Failed to list serial ports');
        }
    };

    const handleConnectSimulIDE = async () => {
        try {
            const result = await connectSimulIDE(selectedPort || undefined);
            setSimulIDEConnected(result.connected);
            setSimulIDEPort(result.port);
            if (!result.connected) {
                setError('Failed to connect to SimulIDE');
            }
        } catch (err) {
            setError('Failed to connect to SimulIDE');
        }
    };

    const handleDisconnectSimulIDE = async () => {
        try {
            await disconnectSimulIDE();
            setSimulIDEConnected(false);
            setSimulIDEPort(null);
        } catch (err) {
            setError('Failed to disconnect from SimulIDE');
        }
    };

    const handleCheckSimulIDEStatus = async () => {
        try {
            const status = await getSimulIDEStatus();
            setSimulIDEConnected(status.connected);
            setSimulIDEPort(status.port);
        } catch (err) {
            // Silently fail - status check is optional
        }
    };

    useEffect(() => {
        handleCheckSimulIDEStatus();
        handleRefreshPorts();
    }, []);

    return (
        <div className="w-screen h-screen overflow-hidden bg-black font-sans text-white">
            <Canvas
                shadows
                camera={{ position: [0, 22, 18], fov: 45 }}
                gl={{ antialias: true, toneMappingExposure: 1.1 }}
            >
                <Lighting timeOfDay={timeOfDay} lightIntensity={lightIntensity} />
                <Architecture />
                <Fixtures fanSpeed={fanSpeed} lightIntensity={lightIntensity} />
                <Furniture />
                <InteractableRooms setHoveredRoom={setHoveredRoom} />
                <OrbitControls
                    enableDamping
                    dampingFactor={0.05}
                    maxPolarAngle={Math.PI / 2.2}
                    minDistance={5}
                    maxDistance={50}
                />
            </Canvas>

            {/* Server Data Display */}
            {serverData && (
                <div className="absolute top-4 left-4 bg-slate-900/80 backdrop-blur-md p-4 rounded-2xl border border-white/10 shadow-2xl max-w-sm">
                    <h3 className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
                        <Play className="w-4 h-4 text-emerald-400" />
                        Environment Data
                    </h3>
                    <div className="space-y-2 text-xs">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Temperature</span>
                            <span className="font-bold text-white">{serverData.temperature}°C</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Status</span>
                            <span className={`font-bold px-2 py-0.5 rounded ${
                                serverData.temp_status === 'NORMAL' ? 'bg-emerald-500/20 text-emerald-400' :
                                serverData.temp_status === 'COLD' ? 'bg-blue-500/20 text-blue-400' :
                                'bg-red-500/20 text-red-400'
                            }`}>{serverData.temp_status}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Comfort</span>
                            <span className="font-bold text-white">{serverData.comfort_level}/10</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Mood</span>
                            <span className="font-bold text-sky-400 capitalize">{serverData.mood}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Radiation</span>
                            <span className="font-bold text-white">{serverData.radiation} W/m²</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Lux</span>
                            <span className="font-bold text-white">{serverData.lux}</span>
                        </div>
                        <div className="pt-2 border-t border-white/10">
                            <p className="text-gray-400 text-[10px]">{serverData.scene_summary}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Error Display */}
            {error && (
                <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-red-900/90 backdrop-blur-md px-6 py-3 rounded-full border border-red-500/50 shadow-2xl flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    <span className="text-sm font-semibold text-white">{error}</span>
                </div>
            )}

            {/* SimulIDE Toggle Button */}
            <button
                onClick={() => setShowSimulIDEPanel(!showSimulIDEPanel)}
                className={`absolute top-4 right-4 flex items-center gap-2 px-4 py-2 rounded-full font-semibold text-xs transition-all duration-300 border shadow-2xl ${
                    simulIDEConnected
                        ? 'bg-emerald-600 text-white border-emerald-600'
                        : 'bg-slate-800/80 text-gray-300 border-white/10 hover:bg-slate-700'
                }`}
            >
                <Cpu className="w-4 h-4" />
                SimulIDE {simulIDEConnected ? 'Connected' : 'Disconnected'}
            </button>

            {/* SimulIDE Panel */}
            {showSimulIDEPanel && (
                <div className="absolute top-16 right-4 w-80 bg-slate-900/90 backdrop-blur-md p-4 rounded-2xl border border-white/10 shadow-2xl z-50">
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                            <Cpu className="w-4 h-4 text-sky-400" />
                            SimulIDE Control
                        </h3>
                        <button
                            onClick={() => setShowSimulIDEPanel(false)}
                            className="text-gray-400 hover:text-white text-xs"
                        >
                            ✕
                        </button>
                    </div>

                    {/* Connection Status */}
                    <div className={`flex items-center gap-2 mb-4 px-3 py-2 rounded-lg ${
                        simulIDEConnected ? 'bg-emerald-500/20' : 'bg-red-500/20'
                    }`}>
                        {simulIDEConnected ? (
                            <Plug className="w-4 h-4 text-emerald-400" />
                        ) : (
                            <Power className="w-4 h-4 text-red-400" />
                        )}
                        <span className={`text-xs font-semibold ${
                            simulIDEConnected ? 'text-emerald-400' : 'text-red-400'
                        }`}>
                            {simulIDEConnected ? `Connected: ${simulIDEPort}` : 'Not Connected'}
                        </span>
                    </div>

                    {/* Port Selection */}
                    <div className="space-y-3">
                        <div>
                            <label className="text-xs font-semibold text-gray-400 mb-1 block">
                                Serial Port
                            </label>
                            <select
                                value={selectedPort}
                                onChange={(e) => setSelectedPort(e.target.value)}
                                className="w-full bg-slate-800/50 border border-white/10 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
                            >
                                <option value="">Auto-detect</option>
                                {availablePorts.map((port) => (
                                    <option key={port} value={port.split(' - ')[0]} className="bg-slate-800">
                                        {port}
                                    </option>
                                ))}
                            </select>
                        </div>

                        {/* Connection Buttons */}
                        <div className="flex gap-2">
                            <button
                                onClick={handleRefreshPorts}
                                className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-slate-700 text-xs font-semibold text-gray-300 hover:bg-slate-600 transition-colors"
                            >
                                Refresh
                            </button>
                            {simulIDEConnected ? (
                                <button
                                    onClick={handleDisconnectSimulIDE}
                                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-red-600 text-xs font-semibold text-white hover:bg-red-700 transition-colors"
                                >
                                    Disconnect
                                </button>
                            ) : (
                                <button
                                    onClick={handleConnectSimulIDE}
                                    className="flex-1 flex items-center justify-center gap-1 px-3 py-2 rounded-lg bg-emerald-600 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors"
                                >
                                    Connect
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Info */}
                    <div className="mt-4 pt-4 border-t border-white/10">
                        <p className="text-[10px] text-gray-500">
                            Open SimulIDE circuit file and load the Arduino sketch.
                            Server will auto-send data when connected.
                        </p>
                    </div>
                </div>
            )}

            {/* Controls Container */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-4 w-full max-w-2xl px-4 pointer-events-none">

                {/* Server Input Controls */}
                <div className="flex w-full gap-3 pointer-events-auto items-end">
                    {/* Date Input */}
                    <div className="flex-1 bg-slate-900/80 backdrop-blur-md p-4 rounded-2xl border border-white/10 shadow-2xl flex flex-col gap-2">
                        <label className="text-xs font-semibold text-gray-400">Date</label>
                        <input
                            type="date"
                            value={inputDate}
                            onChange={(e) => setInputDate(e.target.value)}
                            className="bg-slate-800/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
                        />
                    </div>

                    {/* Hour Input */}
                    <div className="flex-1 bg-slate-900/80 backdrop-blur-md p-4 rounded-2xl border border-white/10 shadow-2xl flex flex-col gap-2">
                        <label className="text-xs font-semibold text-gray-400">Hour</label>
                        <select
                            value={inputHour}
                            onChange={(e) => setInputHour(parseInt(e.target.value))}
                            className="bg-slate-800/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
                        >
                            {Array.from({ length: 24 }, (_, i) => (
                                <option key={i} value={i} className="bg-slate-800">
                                    {i.toString().padStart(2, '0')}:00
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Run Button */}
                    <button
                        onClick={handleRunAgents}
                        disabled={isLoading}
                        className={`flex items-center gap-2 px-6 py-3 rounded-2xl font-semibold transition-all duration-300 border shadow-2xl ${
                            isLoading
                                ? 'bg-slate-700 text-gray-400 border-slate-600 cursor-not-allowed'
                                : 'bg-sky-500 text-white border-sky-500 hover:bg-sky-600 hover:shadow-[0_0_20px_rgba(14,165,233,0.6)]'
                        }`}
                    >
                        {isLoading ? (
                            <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                            <Play className="w-5 h-5" />
                        )}
                        Run
                    </button>
                </div>

                {/* Auto-sync Toggle & Load Current */}
                <div className="flex gap-3 pointer-events-auto">
                    <button
                        onClick={handleLoadCurrent}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-4 py-2 rounded-full font-semibold text-xs transition-all duration-300 border bg-emerald-600 text-white border-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:text-gray-400"
                    >
                        Load Current
                    </button>
                    <label className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 shadow-2xl cursor-pointer">
                        <input
                            type="checkbox"
                            checked={autoSync}
                            onChange={(e) => setAutoSync(e.target.checked)}
                            className="w-4 h-4 accent-sky-500"
                        />
                        <span className="text-xs font-semibold text-gray-300">Auto-sync</span>
                    </label>
                </div>

                {/* Regulators */}
                <div className="flex w-full gap-4 pointer-events-auto">
                    {/* Fan Regulator */}
                    <div className="flex-1 bg-slate-900/80 backdrop-blur-md p-4 rounded-2xl border border-white/10 shadow-2xl flex flex-col gap-3">
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                                <Fan className={`w-4 h-4 ${fanSpeed > 0 ? 'animate-spin' : ''}`} style={{ animationDuration: fanSpeed > 0 ? `${2 / fanSpeed}s` : '0s' }} />
                                Fan Speed
                            </span>
                            <span className="text-xs font-bold text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md">{fanSpeed}</span>
                        </div>
                        <input 
                            type="range" min="0" max="5" step="1" 
                            value={fanSpeed} onChange={(e) => setFanSpeed(parseInt(e.target.value))}
                            className="w-full accent-emerald-500 cursor-pointer"
                        />
                    </div>

                    {/* Light Regulator */}
                    <div className="flex-1 bg-slate-900/80 backdrop-blur-md p-4 rounded-2xl border border-white/10 shadow-2xl flex flex-col gap-3">
                        <div className="flex justify-between items-center">
                            <span className="text-sm font-semibold text-gray-300 flex items-center gap-2">
                                <Lightbulb className="w-4 h-4 text-amber-300" />
                                Illuminance
                            </span>
                            <span className="text-xs font-bold text-amber-400 bg-amber-400/10 px-2 py-1 rounded-md">{lightIntensity}%</span>
                        </div>
                        <input 
                            type="range" min="0" max="100" step="1" 
                            value={lightIntensity} onChange={(e) => setLightIntensity(parseInt(e.target.value))}
                            className="w-full accent-amber-500 cursor-pointer"
                        />
                    </div>
                </div>

                {/* Time Controls */}
                <div className="flex gap-2 bg-slate-900/80 backdrop-blur-md px-4 py-2 rounded-full border border-white/10 shadow-2xl pointer-events-auto">
                    <TimeButton active={timeOfDay === 'morning'} onClick={() => setTimeOfDay('morning')} icon={<CloudSun className="w-4 h-4" />} label="Morning" />
                    <TimeButton active={timeOfDay === 'afternoon'} onClick={() => setTimeOfDay('afternoon')} icon={<Sun className="w-4 h-4" />} label="Afternoon" />
                    <TimeButton active={timeOfDay === 'evening'} onClick={() => setTimeOfDay('evening')} icon={<Sunset className="w-4 h-4" />} label="Evening" />
                    <TimeButton active={timeOfDay === 'night'} onClick={() => setTimeOfDay('night')} icon={<Moon className="w-4 h-4" />} label="Night" />
                </div>
            </div>

            {/* Tooltip */}
            <div 
                className={`absolute bg-white/95 text-gray-900 px-4 py-2 rounded-lg text-sm font-bold pointer-events-none shadow-xl border border-gray-200 transition-opacity duration-200 -translate-x-1/2 -translate-y-[150%] ${hoveredRoom ? 'opacity-100' : 'opacity-0'}`}
                style={{ left: mousePos.x, top: mousePos.y }}
            >
                {hoveredRoom || 'Room Name'}
            </div>
        </div>
    );
}

function TimeButton({ active, onClick, icon, label }: { active: boolean, onClick: () => void, icon: React.ReactNode, label: string }) {
    return (
        <button 
            onClick={onClick}
            className={`flex items-center gap-2 px-4 py-2 rounded-full font-semibold transition-all duration-300 border ${
                active 
                    ? 'bg-sky-500 text-white border-sky-500 shadow-[0_0_15px_rgba(14,165,233,0.6)]' 
                    : 'bg-white/5 text-gray-300 border-white/10 hover:bg-white/15 hover:text-white'
            }`}
        >
            {icon}
            {label}
        </button>
    );
}
