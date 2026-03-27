import { mats } from '../materials';

function Box({ w, h, d, mat, x = 0, y = 0, z = 0 }: { w: number, h: number, d: number, mat: any, x?: number, y?: number, z?: number }) {
    return (
        <mesh position={[x, y + h / 2, z]} material={mat} castShadow receiveShadow>
            <boxGeometry args={[w, h, d]} />
        </mesh>
    );
}

export function Furniture() {
    return (
        <group>
            {/* Living Room Set */}
            <group position={[-5.5, 0, 1.5]}>
                <Box w={3.5} h={0.4} d={1.2} mat={mats.fabric} />
                <Box w={3.5} h={0.6} d={0.3} mat={mats.fabric} y={0.4} z={-0.45} />
                <Box w={0.4} h={0.3} d={1.2} mat={mats.fabric} x={-1.55} y={0.4} />
                <Box w={0.4} h={0.3} d={1.2} mat={mats.fabric} x={1.55} y={0.4} />
            </group>

            {/* TV Set */}
            <group position={[-5.5, 0, 5.6]}>
                <Box w={4} h={0.5} d={0.6} mat={mats.woodDark} />
                <Box w={2.8} h={1.4} d={0.05} mat={mats.tvScreen} y={0.5} />
            </group>

            <Box w={1.8} h={0.35} d={1.2} mat={mats.woodDark} x={-5.5} y={0} z={3.5} />

            {/* Kitchen */}
            <group position={[-3.5, 0, -3.5]}>
                <Box w={4.5} h={0.9} d={1.2} mat={mats.woodDark} />
                <Box w={4.7} h={0.05} d={1.4} mat={mats.whiteShiny} y={0.9} />
                <Box w={0.4} h={0.65} d={0.4} mat={mats.fabric} x={-1.2} z={1} />
                <Box w={0.4} h={0.65} d={0.4} mat={mats.fabric} x={1.2} z={1} />
            </group>
            <Box w={1.1} h={2.0} d={1.2} mat={mats.metal} x={-7.2} z={-4.5} />

            {/* Bedroom */}
            <group position={[5.5, 0, -3.5]}>
                <Box w={3.0} h={0.3} d={3.4} mat={mats.woodDark} />
                <Box w={2.8} h={0.25} d={3.2} mat={mats.whiteShiny} y={0.3} />
                <Box w={2.8} h={0.1} d={2.2} mat={mats.fabric} y={0.55} z={0.5} />
                <Box w={0.9} h={0.15} d={0.6} mat={mats.whiteShiny} x={-0.7} y={0.55} z={-1} />
                <Box w={0.9} h={0.15} d={0.6} mat={mats.whiteShiny} x={0.7} y={0.55} z={-1} />
            </group>
            <Box w={1.8} h={2.2} d={0.8} mat={mats.woodDark} x={2.0} z={-5} />

            {/* Bathroom */}
            <group position={[6.8, 0, 4]}>
                <Box w={1.8} h={0.6} d={3.2} mat={mats.woodDark} />
                <Box w={1.6} h={0.1} d={3.0} mat={mats.whiteShiny} y={0.5} />
            </group>
            <Box w={1.4} h={0.85} d={0.8} mat={mats.whiteShiny} x={2.5} z={4.5} />
        </group>
    );
}
