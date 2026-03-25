import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import axios from 'axios';

const DailySummary = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchSummary = async () => {
        try {
            const response = await axios.get('/api/summary');
            // Group by hour or just show last N
            const data = response.data.map((r, i) => ({
                time: new Date(r.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                level: r.level,
                blink: r.blink,
                wpm: r.wpm,
                index: i
            })).reverse();
            setHistory(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchSummary();
    }, []);

    const avgLevel = history.length ? (history.reduce((a, b) => a + b.level, 0) / history.length).toFixed(1) : 0;
    const maxWpm = history.length ? Math.max(...history.map(r => r.wpm)).toFixed(0) : 0;

    return (
        <div className="p-6 bg-white rounded-xl shadow-lg border border-gray-100">
            <div className="flex justify-between items-center mb-8">
                <h2 className="text-3xl font-extrabold text-indigo-900 tracking-tight">Daily Performance Summary</h2>
                <button 
                    onClick={fetchSummary}
                    className="px-4 py-2 bg-indigo-50 text-indigo-700 rounded-lg hover:bg-indigo-100 font-bold transition-all"
                >
                    Refresh History
                </button>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-10">
                <div className="p-4 bg-indigo-600 text-white rounded-xl shadow-indigo-200 shadow-lg">
                    <div className="text-xs uppercase opacity-80 font-bold">Average Load</div>
                    <div className="text-3xl font-black">{avgLevel} / 2.0</div>
                    <div className="text-xs mt-1">({avgLevel > 1.2 ? 'Stressful Day' : 'Productive Day'})</div>
                </div>
                <div className="p-4 bg-emerald-500 text-white rounded-xl shadow-emerald-200 shadow-lg">
                    <div className="text-xs uppercase opacity-80 font-bold">Peak OS Speed</div>
                    <div className="text-3xl font-black">{maxWpm} WPM</div>
                </div>
                <div className="p-4 bg-blue-500 text-white rounded-xl shadow-blue-200 shadow-lg">
                    <div className="text-xs uppercase opacity-80 font-bold">Data Points</div>
                    <div className="text-3xl font-black">{history.length}</div>
                </div>
            </div>

            <div className="space-y-12">
                <div>
                    <h3 className="text-lg font-bold text-gray-700 mb-4 border-l-4 border-indigo-500 pl-3">Cognitive Load Trend (Over Time)</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={history}>
                                <defs>
                                    <linearGradient id="colorLevel" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="time" minTickGap={50} />
                                <YAxis domain={[0, 2]} ticks={[0, 1, 2]} />
                                <Tooltip />
                                <Area type="monotone" dataKey="level" stroke="#6366f1" fillOpacity={1} fill="url(#colorLevel)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="grid md:grid-cols-2 gap-8">
                    <div>
                        <h4 className="text-sm font-bold text-gray-500 mb-2 uppercase">System Usage (WPM)</h4>
                        <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={history.slice(-100)}>
                                    <Bar dataKey="wpm" fill="#10b981" />
                                    <Tooltip />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    <div>
                        <h4 className="text-sm font-bold text-gray-500 mb-2 uppercase">Biometric Activity (Blinks)</h4>
                        <div className="h-48">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={history.slice(-100)}>
                                    <Bar dataKey="blink" fill="#3b82f6" />
                                    <Tooltip />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DailySummary;
