import * as THREE from 'three';

const wallH = 2.6;
const hitMats = new THREE.MeshBasicMaterial({ visible: false });

export function InteractableRooms({ setHoveredRoom }: { setHoveredRoom: (name: string | null) => void }) {
    const rooms = [
        { name: "Living Area & Kitchen", args: [9, wallH, 12] as [number, number, number], x: -3.5, z: 0 },
        { name: "Master Bedroom", args: [7, wallH, 7] as [number, number, number], x: 4.5, z: -2.5 },
        { name: "Bathroom", args: [7, wallH, 5] as [number, number, number], x: 4.5, z: 3.5 }
    ];

    return (
        <group>
            {rooms.map((room, i) => (
                <mesh 
                    key={i} 
                    position={[room.x, wallH / 2, room.z]} 
                    material={hitMats}
                    onPointerOver={(e) => {
                        e.stopPropagation();
                        setHoveredRoom(room.name);
                        document.body.style.cursor = 'pointer';
                    }}
                    onPointerOut={(e) => {
                        setHoveredRoom(null);
                        document.body.style.cursor = 'default';
                    }}
                >
                    <boxGeometry args={room.args} />
                </mesh>
            ))}
        </group>
    );
}
