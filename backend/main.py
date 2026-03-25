import base64
import io
import os
import sqlite3
import numpy as np
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from PIL import Image
import cv2

from utils import FaceAnalyzer, GlobalInputTracker
from model import load_model

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Setup
DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  load_level INTEGER, 
                  blink_rate REAL, 
                  wpm REAL, 
                  score_name TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Load ML model
try:
    model, scaler = load_model()
except Exception as e:
    print(f"CRITICAL ERROR loading model: {e}")
    model, scaler = None, None

# Global system tracking
global_tracker = GlobalInputTracker()
global_tracker.start()

# Session storage for face analyzers
sessions = {}

class BlinkRequest(BaseModel):
    session_id: str
    image: str

class BlinkResponse(BaseModel):
    blink_rate: float
    blink_count: int
    current_ear: float
    brow_stress: float
    mouth_stress: float

class GlobalStatsResponse(BaseModel):
    wpm: float
    error_rate: float
    mouse_speed: float

class AnalyzeRequest(BaseModel):
    blink_rate: float
    typing_speed: float
    error_rate: float
    mouse_movement: float
    brow_stress: Optional[float] = 0.0
    mouth_stress: Optional[float] = 0.0

class AnalyzeResponse(BaseModel):
    cognitive_load: str
    load_level: int
    probabilities: List[float]

@app.post("/blink", response_model=BlinkResponse)
async def process_blink(request: BlinkRequest):
    session_id = request.session_id
    if session_id not in sessions:
        sessions[session_id] = FaceAnalyzer()
    
    try:
        img_data = request.image.split(',')[1] if ',' in request.image else request.image
        img_bytes = base64.b64decode(img_data)
        pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        opencv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    detector = sessions[session_id]
    ear = detector.process_frame(opencv_img)
    
    return BlinkResponse(
        blink_rate=detector.get_blink_rate(),
        blink_count=detector.blink_counter,
        current_ear=float(ear if ear is not None else 0.0),
        brow_stress=float(detector.brow_dist_norm),
        mouth_stress=float(detector.mouth_ratio)
    )

@app.get("/global_stats", response_model=GlobalStatsResponse)
async def get_global_stats():
    return GlobalStatsResponse(**global_tracker.get_stats())

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    load_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    pred = 0
    face_stress = 0
    if request.brow_stress < 0.12: face_stress += 1
    if request.mouth_stress > 0.15: face_stress += 1
    
    if request.blink_rate > 30 or request.typing_speed > 90 or face_stress >= 2:
        pred = 2
    elif request.blink_rate > 15 or request.typing_speed > 60 or face_stress >= 1:
        pred = 1
    
    # Log to DB for daily summary
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO logs (timestamp, load_level, blink_rate, wpm, score_name) VALUES (?,?,?,?,?)",
                  (datetime.now().isoformat(), pred, request.blink_rate, request.typing_speed, load_map[pred]))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Log Error: {e}")

    return AnalyzeResponse(
        cognitive_load=load_map[pred],
        load_level=pred,
        probabilities=[0.0, 0.0, 0.0]
    )

@app.get("/summary")
async def get_summary():
    # Returns history of today's load
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Limit to last 1000 records
    c.execute("SELECT timestamp, load_level, blink_rate, wpm FROM logs ORDER BY id DESC LIMIT 1000")
    rows = c.fetchall()
    conn.close()
    
    return [
        {"time": r[0], "level": r[1], "blink": r[2], "wpm": r[3]}
        for r in rows
    ]

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)