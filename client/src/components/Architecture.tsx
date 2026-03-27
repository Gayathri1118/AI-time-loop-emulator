import { mats } from '../materials';

const wallH = 2.6;
const t = 0.4;

function Wall({ x, z, w, d, h = wallH, yOffset = 0 }: { x: number, z: number, w: number, d: number, h?: number, yOffset?: number }) {
    return (
        <mesh position={[x, yOffset + h / 2, z]} material={mats.wall} castShadow receiveShadow>
            <boxGeometry args={[w, h, d]} />
        </mesh>
    );
}

function Window({ x, z, w, d }: { x: number, z: number, w: number, d: number }) {
    return (
        <group>
            <Wall x={x} z={z} w={w} d={d} h={0.8} yOffset={0} />
            <Wall x={x} z={z} w={w} d={d} h={0.6} yOffset={2.0} />
            <mesh position={[x, 1.4, z]} material={mats.glass}>
                <boxGeometry args={[w, 1.2, t / 4]} />
            </mesh>
        </group>
    );
}

function Doorway({ x, z, w, d }: { x: number, z: number, w: number, d: number }) {
    return <Wall x={x} z={z} w={w} d={d} h={0.6} yOffset={2.0} />;
}

function Door({ x, z, w, h = 2.0, rotY = 0, openAngle = 0 }: { x: number, z: number, w: number, h?: number, rotY?: number, openAngle?: number }) {
    return (
        <group position={[x, h / 2, z]} rotation={[0, rotY + openAngle, 0]}>
            <mesh position={[w / 2, 0, 0]} material={mats.woodLight} castShadow receiveShadow>
                <boxGeometry args={[w, h, 0.08]} />
            </mesh>
            {/* Knob */}
            <mesh position={[w - 0.1, 0, 0.06]} material={mats.metal} castShadow>
                <sphereGeometry args={[0.04, 16, 16]} />
            </mesh>
            <mesh position={[w - 0.1, 0, -0.06]} material={mats.metal} castShadow>
                <sphereGeometry args={[0.04, 16, 16]} />
            </mesh>
        </group>
    );
}

export function Architecture() {
    return (
        <group>
            {/* Yard */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]} material={mats.grass} receiveShadow>
                <planeGeometry args={[45, 35]} />
            </mesh>

            {/* Pathway */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0.5, 0.01, 10]} material={mats.concrete} receiveShadow>
                <planeGeometry args={[2, 8]} />
            </mesh>

            {/* Floors */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[-3.5, 0, 0]} material={mats.woodFloor} receiveShadow>
                <planeGeometry args={[9, 12]} />
            </mesh>
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[4.5, 0, -2.5]} material={mats.woodFloor} receiveShadow>
                <planeGeometry args={[7, 7]} />
            </mesh>
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[4.5, 0, 3.5]} material={mats.tileFloor} receiveShadow>
                <planeGeometry args={[7, 5]} />
            </mesh>

            {/* Perimeter Walls */}
            <Wall x={0} z={-6} w={16 + t} d={t} /> {/* North */}
            <Wall x={-8} z={0} w={t} d={12} /> {/* West */}
            <Wall x={8} z={0} w={t} d={12} /> {/* East */}

            {/* South (Windows & Entrance) */}
            <Wall x={-7} z={6} w={2} d={t} />
            <Window x={-3.5} z={6} w={5} d={t} />
            <Wall x={-0.55} z={6} w={0.9} d={t} />
            <Doorway x={0.5} z={6} w={1.2} d={t} />
            <Door x={-0.1} z={6} w={1.2} openAngle={Math.PI / 4} />
            <Wall x={1.55} z={6} w={0.9} d={t} />
            <Window x={4} z={6} w={4} d={t} />
            <Wall x={7} z={6} w={2} d={t} />

            {/* Dividers & Interior Doors */}
            <Wall x={1} z={-4.5} w={t} d={3} />
            <Doorway x={1} z={-2} w={t} d={2} />
            <Door x={1} z={-3} w={2} rotY={Math.PI / 2} openAngle={-Math.PI / 3} />
            <Wall x={1} z={2.5} w={t} d={7} />
            <Wall x={4.5} z={1} w={7} d={t} />
            <Wall x={1.5} z={3.5} w={t} d={3} />
            <Doorway x={3} z={3.5} w={3} d={t} />
            <Door x={1.5} z={3.5} w={3} openAngle={Math.PI / 6} />
        </group>
    );
}
