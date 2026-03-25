import React from 'react';

const StatsPanel = ({ blinkData, typingWpm, errorRate, mouseMovement }) => {
    return (
        <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                <div className={`p-2 border rounded ${blinkData.current_ear < 0.24 ? 'bg-blue-50 border-blue-400' : ''}`}>
                    <div className="text-sm text-gray-500 font-medium">Blinks & Eyes</div>
                    <div className="text-xl font-bold">{blinkData.blink_rate.toFixed(1)} <span className="text-xs">rate</span></div>
                    <div className="text-[10px] text-gray-400">EAR: {blinkData.current_ear.toFixed(2)} | Blinks: {blinkData.blink_count}</div>
                </div>
                <div className="p-2 border rounded">
                    <div className="text-sm text-gray-500 font-medium">Facial Stress</div>
                    <div className="text-sm font-semibold">
                        Brows: {blinkData.brow_stress < 0.12 ? '🔴 Furrowed' : '🟢 Relaxed'}
                    </div>
                    <div className="text-sm font-semibold">
                        Mouth: {blinkData.mouth_stress > 0.15 ? '🔴 Open/Stress' : '🟢 Normal'}
                    </div>
                </div>
            </div>

            <div className="relative p-4 bg-gradient-to-br from-gray-50 to-blue-50 rounded-lg shadow-sm border border-blue-100">
                <div className="absolute top-2 right-2 flex items-center space-x-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-[10px] text-green-600 font-bold uppercase tracking-widest">Global OS Tracking</span>
                </div>
                <div className="grid grid-cols-3 gap-2 mt-4">
                    <div className="text-center">
                        <div className="text-[10px] text-gray-400 uppercase">OS Speed</div>
                        <div className="text-lg font-bold text-gray-700">{typingWpm.toFixed(0)} WPM</div>
                    </div>
                    <div className="text-center border-l border-gray-200">
                        <div className="text-[10px] text-gray-400 uppercase">OS Errors</div>
                        <div className="text-lg font-bold text-gray-700">{(errorRate * 100).toFixed(0)}%</div>
                    </div>
                    <div className="text-center border-l border-gray-200">
                        <div className="text-[10px] text-gray-400 uppercase">Mouse Act.</div>
                        <div className="text-lg font-bold text-gray-700">{mouseMovement.toFixed(0)}</div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default StatsPanel;