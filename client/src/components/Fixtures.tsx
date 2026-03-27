import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { mats } from '../materials';

const wallH = 2.6;

function CeilingFan({ x, z, fanSpeed, lightIntensity }: { x: number, z: number, fanSpeed: number, lightIntensity: number }) {
    const bladesRef = useRef<THREE.Group>(null);
    const lightRef = useRef<THREE.PointLight>(null);

    useFrame((state, delta) => {
        if (bladesRef.current) {
            const speed = fanSpeed * 0.04;
            bladesRef.current.rotation.y -= speed * (delta * 60);
        }
        
        if (lightRef.current) {
            const targetLights = (lightIntensity / 100) * 1.2;
            lightRef.current.intensity = THREE.MathUtils.lerp(lightRef.current.intensity, targetLights, 0.015 * (delta * 60));
        }
    });

    return (
        <group position={[x, wallH, z]}>
            <mesh material={mats.metal}>
                <cylinderGeometry args={[0.04, 0.04, 0.4]} />
            </mesh>
            <mesh position={[0, -0.2, 0]} material={mats.metal}>
                <cylinderGeometry args={[0.25, 0.25, 0.15]} />
            </mesh>
            <mesh position={[0, -0.3, 0]} material={mats.bulb}>
                <sphereGeometry args={[0.12, 16, 16]} />
            </mesh>
            <pointLight ref={lightRef} position={[0, -0.4, 0]} color={0xffeedd} intensity={0} distance={8} castShadow shadow-bias={-0.002} />
            
            <group ref={bladesRef} position={[0, -0.2, 0]}>
                {[0, 1, 2, 3].map(i => (
                    <group key={i} rotation={[0, (Math.PI / 2) * i, 0]}>
                        <mesh position={[0.8, 0, 0]} material={mats.woodDark} castShadow>
                            <boxGeometry args={[1.4, 0.02, 0.15]} />
                        </mesh>
                    </group>
                ))}
            </group>
        </group>
    );
}

function WallLight({ x, z, lightIntensity }: { x: number, z: number, lightIntensity: number }) {
    const lightRef = useRef<THREE.PointLight>(null);

    useFrame((state, delta) => {
        if (lightRef.current) {
            const targetLights = (lightIntensity / 100) * 1.0;
            lightRef.current.intensity = THREE.MathUtils.lerp(lightRef.current.intensity, targetLights, 0.015 * (delta * 60));
        }
    });

    return (
        <group position={[x, wallH - 0.2, z]}>
            <mesh material={mats.metal}>
                <cylinderGeometry args={[0.2, 0.2, 0.1]} />
            </mesh>
            <mesh position={[0, -0.1, 0]} material={mats.bulb}>
                <sphereGeometry args={[0.15, 16, 16]} />
            </mesh>
            <pointLight ref={lightRef} position={[0, -0.2, 0]} color={0xffeedd} intensity={0} distance={6} castShadow />
        </group>
    );
}

function TubeLight({ x, z, rotY, lightIntensity }: { x: number, z: number, rotY: number, lightIntensity: number }) {
    const lightRef = useRef<THREE.PointLight>(null);

    useFrame((state, delta) => {
        if (lightRef.current) {
            const targetLights = (lightIntensity / 100) * 1.5;
            lightRef.current.intensity = THREE.MathUtils.lerp(lightRef.current.intensity, targetLights, 0.015 * (delta * 60));
        }
    });

    return (
        <group position={[x, wallH - 0.05, z]} rotation={[0, rotY, 0]}>
            <mesh material={mats.tubeLight}>
                <boxGeometry args={[1.2, 0.05, 0.1]} />
            </mesh>
            <pointLight ref={lightRef} color={0xffffff} intensity={0} distance={12} castShadow shadow-bias={-0.002} />
        </group>
    );
}

export function Fixtures({ fanSpeed, lightIntensity }: { fanSpeed: number, lightIntensity: number }) {
    return (
        <group>
            <CeilingFan x={-3.5} z={0} fanSpeed={fanSpeed} lightIntensity={lightIntensity} />
            <CeilingFan x={4.5} z={-2.5} fanSpeed={fanSpeed} lightIntensity={lightIntensity} />
            <WallLight x={4.5} z={3.5} lightIntensity={lightIntensity} />
            
            {/* Tube Lights */}
            <TubeLight x={-3.5} z={-4.5} rotY={0} lightIntensity={lightIntensity} /> {/* Kitchen */}
            <TubeLight x={6.5} z={-2.5} rotY={Math.PI / 2} lightIntensity={lightIntensity} /> {/* Bedroom */}
            <TubeLight x={6.5} z={3.5} rotY={Math.PI / 2} lightIntensity={lightIntensity} /> {/* Bathroom */}
        </group>
    );
}
