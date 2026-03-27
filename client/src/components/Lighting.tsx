import { useFrame, useThree } from '@react-three/fiber';
import { useRef } from 'react';
import * as THREE from 'three';
import { mats } from '../materials';

export type TimeOfDay = 'morning' | 'afternoon' | 'evening' | 'night';

const timeStates = {
    morning: {
        sunPos: new THREE.Vector3(-25, 12, -15), sunColor: new THREE.Color(0xffebd6), sunIntensity: 1.1,
        hemiSky: new THREE.Color(0x99bbff), hemiGround: new THREE.Color(0x443322), hemiIntensity: 0.7,
        bgColor: new THREE.Color(0x77aaff), intLights: 0, tvGlow: 0
    },
    afternoon: {
        sunPos: new THREE.Vector3(5, 28, 12), sunColor: new THREE.Color(0xffffff), sunIntensity: 1.3,
        hemiSky: new THREE.Color(0xffffff), hemiGround: new THREE.Color(0x666666), hemiIntensity: 0.9,
        bgColor: new THREE.Color(0x5599ff), intLights: 0, tvGlow: 0
    },
    evening: {
        sunPos: new THREE.Vector3(25, 6, 15), sunColor: new THREE.Color(0xff8844), sunIntensity: 0.9,
        hemiSky: new THREE.Color(0xff9977), hemiGround: new THREE.Color(0x332222), hemiIntensity: 0.4,
        bgColor: new THREE.Color(0xff7755), intLights: 0.6, tvGlow: 0.2
    },
    night: {
        sunPos: new THREE.Vector3(10, 20, 10), sunColor: new THREE.Color(0x5577cc), sunIntensity: 0.1, 
        hemiSky: new THREE.Color(0x050515), hemiGround: new THREE.Color(0x020205), hemiIntensity: 0.05,
        bgColor: new THREE.Color(0x020208), intLights: 1.2, tvGlow: 1.0
    }
};

export function Lighting({ timeOfDay, lightIntensity }: { timeOfDay: TimeOfDay, lightIntensity: number }) {
    const sunRef = useRef<THREE.DirectionalLight>(null);
    const hemiRef = useRef<THREE.HemisphereLight>(null);
    const { scene } = useThree();

    useFrame((state, delta) => {
        const target = timeStates[timeOfDay];
        const lerpSpeed = 0.015 * (delta * 60); // Normalize to 60fps

        if (sunRef.current) {
            sunRef.current.position.lerp(target.sunPos, lerpSpeed);
            sunRef.current.color.lerp(target.sunColor, lerpSpeed);
            sunRef.current.intensity = THREE.MathUtils.lerp(sunRef.current.intensity, target.sunIntensity, lerpSpeed);
        }

        if (hemiRef.current) {
            hemiRef.current.color.lerp(target.hemiSky, lerpSpeed);
            hemiRef.current.groundColor.lerp(target.hemiGround, lerpSpeed);
            hemiRef.current.intensity = THREE.MathUtils.lerp(hemiRef.current.intensity, target.hemiIntensity, lerpSpeed);
        }

        if (scene.background instanceof THREE.Color) {
            scene.background.lerp(target.bgColor, lerpSpeed);
        } else {
            scene.background = target.bgColor.clone();
        }

        if (scene.fog instanceof THREE.FogExp2) {
            scene.fog.color.lerp(target.bgColor, lerpSpeed);
        } else {
            scene.fog = new THREE.FogExp2(target.bgColor.getHex(), 0.012);
        }

        const targetLight = (lightIntensity / 100) * 1.5;
        mats.bulb.emissiveIntensity = THREE.MathUtils.lerp(mats.bulb.emissiveIntensity, targetLight, lerpSpeed);
        mats.tubeLight.emissiveIntensity = THREE.MathUtils.lerp(mats.tubeLight.emissiveIntensity, targetLight * 2, lerpSpeed);
        
        const targetTv = timeOfDay === 'night' ? 1.0 : timeOfDay === 'evening' ? 0.2 : 0;
        mats.tvScreen.emissiveIntensity = THREE.MathUtils.lerp(mats.tvScreen.emissiveIntensity, targetTv, lerpSpeed);
    });

    return (
        <>
            <hemisphereLight ref={hemiRef} color={0xffffff} groundColor={0x666666} intensity={0.8} />
            <directionalLight 
                ref={sunRef}
                position={[5, 25, 10]} 
                color={0xffffff} 
                intensity={1.2} 
                castShadow 
                shadow-mapSize-width={2048}
                shadow-mapSize-height={2048}
                shadow-camera-left={-20}
                shadow-camera-right={20}
                shadow-camera-top={20}
                shadow-camera-bottom={-20}
                shadow-bias={-0.0005}
            />
        </>
    );
}
