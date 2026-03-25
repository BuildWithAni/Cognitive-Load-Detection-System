import base64
import io
import os
import sqlite3
import numpy as np
import traceback
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from PIL import Image
import cv2

# Global setup with extra error catching
try:
    from utils import FaceAnalyzer, GlobalInputTracker
    from model import load_model
    print("INFO: Successfully imported local modules.")
except Exception as e:
    print(f"CRITICAL ERROR during imports: {e}")
    traceback.print_exc()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")
def init_db():
    try:
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
        print(f"INFO: Database initialized at {DB_PATH}")
    except Exception as e:
        print(f"ERROR initializing DB: {e}")

init_db()

try:
    model, scaler = load_model()
    print("INFO: ML Model loaded.")
except Exception as e:
    print(f"WARNING: ML Model load failed (using heuristic): {e}")
    model, scaler = None, None

try:
    global_tracker = GlobalInputTracker()
    global_tracker.start()
    print("INFO: Global input tracker started.")
except Exception as e:
    print(f"WARNING: Global input tracker failed: {e}")
    global_tracker = None

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
        if not request.image or len(request.image) < 100:
            return BlinkResponse(blink_rate=0, blink_count=0, current_ear=0.3, brow_stress=0.15, mouth_stress=0.0)
            
        img_data = request.image.split(',')[1] if ',' in request.image else request.image
        img_bytes = base64.b64decode(img_data)
        pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        opencv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        
        detector = sessions[session_id]
        ear = detector.process_frame(opencv_img)
        
        return BlinkResponse(
            blink_rate=detector.get_blink_rate(),
            blink_count=detector.blink_counter,
            current_ear=float(ear if ear is not None else 0.3),
            brow_stress=float(detector.brow_dist_norm),
            mouth_stress=float(detector.mouth_ratio)
        )
    except Exception as e:
        # Don't crash on bad frame
        return BlinkResponse(blink_rate=0, blink_count=0, current_ear=0.3, brow_stress=0.15, mouth_stress=0.0)

@app.get("/global_stats", response_model=GlobalStatsResponse)
async def get_global_stats():
    if global_tracker:
        return GlobalStatsResponse(**global_tracker.get_stats())
    return GlobalStatsResponse(wpm=0, error_rate=0, mouse_speed=0)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    load_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    pred = 0
    face_stress = 0
    
    # Sensitivity Logic
    if request.brow_stress < 0.14: face_stress += 1
    if request.mouth_stress > 0.10: face_stress += 1
    
    if request.blink_rate > 22 or request.typing_speed > 75 or face_stress >= 2 or (face_stress >= 1 and request.typing_speed > 40):
        pred = 2
    elif request.blink_rate > 10 or request.typing_speed > 30 or face_stress >= 1:
        pred = 1
    
    # DB Logging
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        c = conn.cursor()
        c.execute("INSERT INTO logs (timestamp, load_level, blink_rate, wpm, score_name) VALUES (?,?,?,?,?)",
                  (datetime.now().isoformat(), int(pred), float(request.blink_rate), float(request.typing_speed), load_map[pred]))
        conn.commit()
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        if conn: conn.close()

    return AnalyzeResponse(
        cognitive_load=load_map[pred],
        load_level=int(pred),
        probabilities=[0.0, 0.0, 0.0]
    )

@app.get("/summary")
async def get_summary():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT timestamp, load_level, blink_rate, wpm FROM logs ORDER BY id DESC LIMIT 500")
        rows = c.fetchall()
        conn.close()
        return [{"time": r[0], "level": r[1], "blink": r[2], "wpm": r[3]} for r in rows]
    except:
        return []

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting FastAPI Backend...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")