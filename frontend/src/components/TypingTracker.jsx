import React, { useEffect, useState, useRef } from 'react';

const TypingTracker = ({ onStatsUpdate }) => {
    const [stats, setStats] = useState({ wpm: 0, errorRate: 0 });
    const keyCountRef = useRef(0);
    const backspaceCountRef = useRef(0);
    const startTimeRef = useRef(Date.now());
    const intervalRef = useRef(null);

    const handleKeyPress = (e) => {
        if (e.key.length === 1) {
            keyCountRef.current += 1;
        } else if (e.key === 'Backspace') {
            backspaceCountRef.current += 1;
        }
    };

    useEffect(() => {
        intervalRef.current = setInterval(() => {
            const now = Date.now();
            const seconds = (now - startTimeRef.current) / 1000;
            if (seconds >= 2) {
                const charsTyped = keyCountRef.current;
                const wpm = (charsTyped / 5) / (seconds / 60);
                const totalKeys = keyCountRef.current + backspaceCountRef.current;
                const errorRate = totalKeys > 0 ? backspaceCountRef.current / totalKeys : 0;

                const newStats = { wpm: Math.min(wpm, 150), errorRate: Math.min(errorRate, 0.5) };
                setStats(newStats);
                onStatsUpdate(newStats);

                keyCountRef.current = 0;
                backspaceCountRef.current = 0;
                startTimeRef.current = now;
            }
        }, 1000);
        return () => clearInterval(intervalRef.current);
    }, [onStatsUpdate]);

    return (
        <div className="p-4 bg-white rounded-lg shadow-md border border-gray-200">
            <h3 className="text-lg font-bold mb-3 text-blue-800">Typing Accuracy Test</h3>
            <textarea
                className="w-full p-3 border-2 border-dashed border-gray-300 rounded h-24 focus:border-blue-500 focus:outline-none transition-colors"
                placeholder="Type here to test speed and accuracy..."
                onKeyDown={handleKeyPress}
            ></textarea>
            <div className="mt-3 flex justify-between text-sm font-medium">
                <span className="text-gray-600">Speed: <b className="text-blue-600">{stats.wpm.toFixed(0)} WPM</b></span>
                <span className="text-gray-600">Errors: <b className="text-red-600">{(stats.errorRate * 100).toFixed(1)}%</b></span>
            </div>
        </div>
    );
};

export default TypingTracker;