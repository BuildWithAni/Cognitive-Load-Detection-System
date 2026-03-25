import React, { useRef, useEffect } from 'react';
import { sendBlinkFrame } from '../api';

const WebcamFeed = ({ sessionId, onBlinkRateUpdate }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const intervalRef = useRef(null);
    const isProcessingRef = useRef(false);

    useEffect(() => {
        const startWebcam = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (err) {
                console.error("Webcam error:", err);
            }
        };
        startWebcam();

        return () => {
            if (videoRef.current && videoRef.current.srcObject) {
                const tracks = videoRef.current.srcObject.getTracks();
                tracks.forEach(track => track.stop());
            }
            if (intervalRef.current) clearInterval(intervalRef.current);
        };
    }, []);

    useEffect(() => {
        intervalRef.current = setInterval(async () => {
            if (isProcessingRef.current) return;

            const video = videoRef.current;
            const canvas = canvasRef.current;
            
            if (video && canvas && video.readyState === 4) {
                isProcessingRef.current = true;
                const ctx = canvas.getContext('2d');
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                const imageData = canvas.toDataURL('image/jpeg', 0.8);

                if (imageData && imageData.length > 200) {
                    try {
                        const data = await sendBlinkFrame(sessionId, imageData);
                        onBlinkRateUpdate(data);
                    } catch (err) {
                        console.error("Blink API error:", err);
                    } finally {
                        isProcessingRef.current = false;
                    }
                } else {
                    isProcessingRef.current = false;
                }
            }
        }, 200); // 5 FPS

        return () => clearInterval(intervalRef.current);
    }, [sessionId, onBlinkRateUpdate]);

    return (
        <div className="relative w-full max-w-md mx-auto">
            <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full rounded-lg shadow-lg border-2 border-gray-200"
            />
            <canvas ref={canvasRef} className="hidden" />
        </div>
    );
};

export default WebcamFeed;