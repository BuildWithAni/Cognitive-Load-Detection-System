import React, { useEffect, useRef } from 'react';

const MouseTracker = ({ onMovementUpdate }) => {
    const lastPosRef = useRef({ x: 0, y: 0 });
    const totalDistanceRef = useRef(0);
    const intervalRef = useRef(null);
    const startTimeRef = useRef(Date.now());

    useEffect(() => {
        const handleMouseMove = (e) => {
            const now = Date.now();
            const dx = e.clientX - lastPosRef.current.x;
            const dy = e.clientY - lastPosRef.current.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance > 0 && distance < 500) { // ignore large jumps
                totalDistanceRef.current += distance;
            }
            lastPosRef.current = { x: e.clientX, y: e.clientY };
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    useEffect(() => {
        intervalRef.current = setInterval(() => {
            const now = Date.now();
            const seconds = (now - startTimeRef.current) / 1000;
            if (seconds >= 2) {
                const movement = totalDistanceRef.current / seconds; // pixels per second
                // Normalize to 0-100 (assuming max 1000 px/s)
                const normalized = Math.min(movement / 10, 100);
                onMovementUpdate(normalized);
                totalDistanceRef.current = 0;
                startTimeRef.current = now;
            }
        }, 1000);
        return () => clearInterval(intervalRef.current);
    }, [onMovementUpdate]);

    return null; // no UI
};

export default MouseTracker;