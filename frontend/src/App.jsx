import React, { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import WebcamFeed from './components/WebcamFeed';
import TypingTracker from './components/TypingTracker';
import Dashboard from './components/Dashboard';
import StatsPanel from './components/StatsPanel';
import { analyze, getGlobalStats } from './api';
import DailySummary from './components/DailySummary';

function App() {
    const [viewMode, setViewMode] = useState('LIVE');
    const [sessionId] = useState(() => uuidv4());
    const [blinkData, setBlinkData] = useState({ 
        blink_rate: 0, 
        blink_count: 0, 
        current_ear: 0.3,
        brow_stress: 0.15,
        mouth_stress: 0.05
    });
    const [typingStats, setTypingStats] = useState({ wpm: 0, errorRate: 0 });
    const [mouseMovement, setMouseMovement] = useState(0);
    const [currentLoad, setCurrentLoad] = useState('LOW');
    const [loadHistory, setLoadHistory] = useState([]);
    const [alertSound, setAlertSound] = useState(true);

    useEffect(() => {
        const fetchGlobal = async () => {
            try {
                const stats = await getGlobalStats();
                setTypingStats({ wpm: stats.wpm, errorRate: stats.error_rate });
                setMouseMovement(stats.mouse_speed);
            } catch (err) {
                console.error("Global stats fetch error:", err);
            }
        };
        const intv = setInterval(fetchGlobal, 1000);
        return () => clearInterval(intv);
    }, []);

    const sendData = useCallback(async () => {
        try {
            const result = await analyze({
                blink_rate: blinkData.blink_rate,
                typing_speed: typingStats.wpm,
                error_rate: typingStats.errorRate,
                mouse_movement: mouseMovement,
                brow_stress: blinkData.brow_stress,
                mouth_stress: blinkData.mouth_stress,
            });
            setCurrentLoad(result.cognitive_load);
            setLoadHistory(prev => {
                const newEntry = { index: prev.length, loadLevel: result.load_level };
                const updated = [...prev, newEntry];
                if (updated.length > 20) updated.shift();
                return updated;
            });
        } catch (err) {
            console.error("Analysis error:", err);
        }
    }, [blinkData, typingStats, mouseMovement]);

    useEffect(() => {
        const interval = setInterval(() => {
            if (viewMode === 'LIVE') sendData();
        }, 1000);
        return () => clearInterval(interval);
    }, [sendData, viewMode]);

    return (
        <div className="min-h-screen bg-gray-100 p-4 md:p-8">
            <div className="max-w-6xl mx-auto space-y-6">
                <header className="flex flex-col md:flex-row justify-between items-center bg-white p-6 rounded-2xl shadow-sm space-y-4 md:space-y-0">
                    <div>
                        <h1 className="text-3xl font-black text-indigo-900">Cognitive Load <span className="text-indigo-400">Tracker</span></h1>
                        <p className="text-sm text-gray-500 font-medium">Tracking biometric and system-wide performance</p>
                    </div>
                    
                    <div className="flex bg-gray-100 p-1 rounded-xl">
                        <button 
                            onClick={() => setViewMode('LIVE')}
                            className={`px-6 py-2 rounded-lg font-bold text-sm transition-all ${viewMode === 'LIVE' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                            Real-time
                        </button>
                        <button 
                            onClick={() => setViewMode('SUMMARY')}
                            className={`px-6 py-2 rounded-lg font-bold text-sm transition-all ${viewMode === 'SUMMARY' ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                            Daily Summary
                        </button>
                    </div>
                </header>

                {viewMode === 'LIVE' ? (
                    <div className="grid md:grid-cols-2 gap-8 items-start">
                        <section className="space-y-6">
                            <WebcamFeed sessionId={sessionId} onBlinkRateUpdate={setBlinkData} />
                            <TypingTracker onStatsUpdate={setTypingStats} />
                        </section>
                        
                        <section className="space-y-6">
                            <Dashboard currentLoad={currentLoad} loadHistory={loadHistory} alertSound={alertSound} />
                            <StatsPanel
                                blinkData={blinkData}
                                typingWpm={typingStats.wpm}
                                errorRate={typingStats.errorRate}
                                mouseMovement={mouseMovement}
                            />
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center justify-between">
                                <label className="flex items-center space-x-3 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={alertSound}
                                        onChange={(e) => setAlertSound(e.target.checked)}
                                        className="w-5 h-5 text-indigo-600 rounded focus:ring-indigo-500"
                                    />
                                    <span className="font-semibold text-gray-700">Audio Alerts (High Load)</span>
                                </label>
                                <div className="text-[10px] text-indigo-400 font-bold uppercase tracking-widest bg-indigo-50 px-2 py-1 rounded">System Active</div>
                            </div>
                        </section>
                    </div>
                ) : (
                    <DailySummary />
                )}
            </div>
        </div>
    );
}

export default App;