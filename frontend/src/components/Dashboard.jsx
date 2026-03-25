import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const Dashboard = ({ currentLoad, loadHistory, alertSound }) => {
    const getLoadColor = (load) => {
        switch (load) {
            case 'LOW': return 'text-green-600';
            case 'MEDIUM': return 'text-yellow-600';
            case 'HIGH': return 'text-red-600';
            default: return 'text-gray-600';
        }
    };

    const getBgColor = (load) => {
        switch (load) {
            case 'LOW': return 'bg-green-100 border-green-500';
            case 'MEDIUM': return 'bg-yellow-100 border-yellow-500';
            case 'HIGH': return 'bg-red-100 border-red-500';
            default: return 'bg-gray-100 border-gray-500';
        }
    };

    React.useEffect(() => {
        if (currentLoad === 'HIGH' && alertSound) {
            const audio = new Audio('/alert.mp3'); // place an alert.mp3 in public folder
            audio.play().catch(e => console.log("Audio play failed", e));
        }
    }, [currentLoad, alertSound]);

    return (
        <div className={`p-6 rounded-lg shadow-lg border-l-8 ${getBgColor(currentLoad)}`}>
            <h2 className="text-2xl font-bold mb-4">Cognitive Load</h2>
            <div className={`text-4xl font-extrabold mb-6 ${getLoadColor(currentLoad)}`}>
                {currentLoad}
            </div>

            <div className="mt-8">
                <h3 className="text-lg font-semibold mb-2">Load History (last 10)</h3>
                <ResponsiveContainer width="100%" height={200}>
                    <LineChart data={loadHistory}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="index" />
                        <YAxis domain={[0, 2]} tickFormatter={(val) => ['LOW', 'MEDIUM', 'HIGH'][val]} />
                        <Tooltip />
                        <Line type="monotone" dataKey="loadLevel" stroke="#8884d8" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default Dashboard;