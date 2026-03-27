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
import { Fan, Sun, Sunset, Moon, CloudSun, Lightbulb } from 'lucide-react';

export default function App() {
    const [timeOfDay, setTimeOfDay] = useState<TimeOfDay>('afternoon');
    const [fanSpeed, setFanSpeed] = useState(3);
    const [lightIntensity, setLightIntensity] = useState(0);
    const [hoveredRoom, setHoveredRoom] = useState<string | null>(null);
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

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

            {/* Controls Container */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-4 w-full max-w-2xl px-4 pointer-events-none">
                
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
