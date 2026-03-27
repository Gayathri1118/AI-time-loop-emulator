import * as THREE from 'three';

function createWoodTexture() {
    const canvas = document.createElement('canvas'); 
    canvas.width = 512; 
    canvas.height = 512;
    const ctx = canvas.getContext('2d');
    if (ctx) {
        ctx.fillStyle = '#9c6f44'; 
        ctx.fillRect(0, 0, 512, 512);
        for(let i=0; i<512; i+=16) { 
            ctx.fillStyle = i % 32 === 0 ? '#8a5e35' : '#a87a4d';
            ctx.fillRect(0, i, 512, 14); 
        }
    }
    const tex = new THREE.CanvasTexture(canvas);
    tex.wrapS = tex.wrapT = THREE.RepeatWrapping; 
    tex.repeat.set(5, 5); 
    return tex;
}

export const mats = {
    wall: new THREE.MeshStandardMaterial({ color: 0xeaeaea, roughness: 0.8 }),
    woodFloor: new THREE.MeshStandardMaterial({ map: createWoodTexture(), roughness: 0.4 }),
    tileFloor: new THREE.MeshStandardMaterial({ color: 0xcccccc, roughness: 0.2 }),
    grass: new THREE.MeshStandardMaterial({ color: 0x3d6e33, roughness: 1 }),
    woodDark: new THREE.MeshStandardMaterial({ color: 0x2b1d0f, roughness: 0.8 }),
    woodLight: new THREE.MeshStandardMaterial({ color: 0xd4a373, roughness: 0.7 }),
    concrete: new THREE.MeshStandardMaterial({ color: 0x888888, roughness: 0.9 }),
    fabric: new THREE.MeshStandardMaterial({ color: 0x2c3e50, roughness: 1 }),
    whiteShiny: new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.1 }),
    glass: new THREE.MeshPhysicalMaterial({ color: 0x88ccff, transmission: 0.9, opacity: 1, transparent: true, roughness: 0.1 }),
    metal: new THREE.MeshStandardMaterial({ color: 0x777777, metalness: 0.8, roughness: 0.2 }),
    tvScreen: new THREE.MeshStandardMaterial({ color: 0x111111, emissive: 0x2255ff, emissiveIntensity: 0 }),
    bulb: new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffeebb, emissiveIntensity: 0 }),
    tubeLight: new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xffffff, emissiveIntensity: 0 })
};
