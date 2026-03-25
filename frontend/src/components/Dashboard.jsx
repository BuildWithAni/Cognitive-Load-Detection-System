import React, { useEffect } from 'react';

const Dashboard = ({ currentLoad, loadScore = 0, alertSound }) => {
    
    const blocks = Array.from({ length: 10 }, (_, i) => i + 1);

    const getBlockColor = (index, score) => {
        if (index > score) return 'bg-gray-200 border-gray-300'; // Off block
        if (index <= 3) return 'bg-emerald-500 border-emerald-600 shadow-[0_0_10px_rgba(16,185,129,0.5)]'; // Low
        if (index <= 7) return 'bg-yellow-400 border-yellow-500 shadow-[0_0_10px_rgba(251,191,36,0.5)]'; // Med
        return 'bg-rose-500 border-rose-600 shadow-[0_0_15px_rgba(225,29,72,0.8)] animate-pulse'; // High
    };

    useEffect(() => {
        if (loadScore >= 8 && alertSound) {
            const audio = new Audio('/alert.mp3');
            audio.play().catch(e => {});
        }
    }, [loadScore, alertSound]);

    return (
        <div className="p-8 bg-slate-900 rounded-3xl shadow-2xl border-4 border-slate-700 relative overflow-hidden">
            {/* Background Glow */}
            <div className={`absolute top-0 right-0 w-32 h-32 blur-3xl opacity-20 -mr-16 -mt-16 transition-all duration-700 ${loadScore >= 8 ? 'bg-rose-500' : 'bg-emerald-500'}`}></div>
            
            <div className="flex justify-between items-end mb-8">
                <div>
                    <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-1">Performance Meter</h2>
                    <div className="flex items-center space-x-2">
                        <div className={`text-6xl font-black tracking-tighter ${loadScore >= 8 ? 'text-rose-500' : loadScore >= 4 ? 'text-yellow-400' : 'text-emerald-400'}`}>
                            {loadScore}<span className="text-xl text-slate-500">/10</span>
                        </div>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-[10px] font-black text-slate-500 uppercase">Load Category</div>
                    <div className={`text-xl font-black uppercase tracking-tight ${loadScore >= 8 ? 'text-rose-500' : loadScore >= 4 ? 'text-yellow-400' : 'text-emerald-400'}`}>
                        {loadScore >= 8 ? 'Critical Stress' : loadScore >= 4 ? 'Focused' : 'Relaxed'}
                    </div>
                </div>
            </div>

            {/* LED 10-BLOCK METER */}
            <div className="flex justify-between items-center h-24 space-x-3">
                {blocks.map((b) => (
                    <div
                        key={b}
                        className={`flex-1 h-full rounded-lg border-2 transition-all duration-300 transform ${b <= loadScore ? 'scale-y-110' : 'scale-y-90'} ${getBlockColor(b, loadScore)}`}
                    />
                ))}
            </div>

            <div className="mt-8 flex justify-between items-center border-t border-slate-700 pt-4">
                <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-slate-600 rounded-full"></div>
                    <span className="text-[10px] font-bold text-slate-500 uppercase">Engine Status: O.K.</span>
                </div>
                <div className="text-[10px] font-black text-slate-600 space-x-4">
                    <span>120 FPS</span>
                    <span>SENSITIVITY: MAX</span>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;