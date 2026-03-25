import axios from 'axios';

const API_BASE = '/api';  // Vite proxy

export const sendBlinkFrame = async (sessionId, imageBase64) => {
    const response = await axios.post(`${API_BASE}/blink`, {
        session_id: sessionId,
        image: imageBase64,
    });
    return response.data;
};

export const analyze = async (data) => {
    const response = await axios.post(`${API_BASE}/analyze`, data);
    return response.data;
};

export const getGlobalStats = async () => {
    const response = await axios.get(`${API_BASE}/global_stats`);
    return response.data;
};