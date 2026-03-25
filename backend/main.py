import base64
import io
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
from PIL import Image
import cv2

from utils import BlinkDetector
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

# Load ML model
model, scaler = load_model()

# Session storage for blink detectors
sessions = {}

class BlinkRequest(BaseModel):
    session_id: str
    image: str  # base64 encoded image

class BlinkResponse(BaseModel):
    blink_rate: float

class AnalyzeRequest(BaseModel):
    blink_rate: float
    typing_speed: float  # words per minute
    error_rate: float    # 0-1
    mouse_movement: float  # normalized 0-100

class AnalyzeResponse(BaseModel):
    cognitive_load: str  # LOW, MEDIUM, HIGH
    load_level: int      # 0,1,2
    probabilities: List[float]

@app.post("/blink", response_model=BlinkResponse)
async def process_blink(request: BlinkRequest):
    session_id = request.session_id
    if session_id not in sessions:
        sessions[session_id] = BlinkDetector()
    
    # Decode base64 image
    try:
        # Remove data URL prefix if present
        img_data = request.image.split(',')[1] if ',' in request.image else request.image
        img_bytes = base64.b64decode(img_data)
        pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        # Convert PIL to OpenCV (BGR)
        opencv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {str(e)}")
    
    detector = sessions[session_id]
    detector.process_frame(opencv_img)
    blink_rate = detector.get_blink_rate()
    return BlinkResponse(blink_rate=blink_rate)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    # Prepare features
    features = np.array([[request.blink_rate, request.typing_speed,
                          request.error_rate, request.mouse_movement]])
    features_scaled = scaler.transform(features)
    probs = model.predict_proba(features_scaled)[0]
    pred = model.predict(features_scaled)[0]
    
    load_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}
    return AnalyzeResponse(
        cognitive_load=load_map[pred],
        load_level=int(pred),
        probabilities=probs.tolist()
    )

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)