## README.md

```markdown
# Cognitive Load Detection System

A real‑time, end‑to‑end system that measures cognitive load using facial analysis (blink rate), keyboard/mouse dynamics, and machine learning.

## Features
- **Real‑time webcam processing** with MediaPipe to detect blinks and compute blink rate.
- **Typing tracking** – calculates Words Per Minute (WPM) and error rate.
- **Mouse movement tracking** – measures movement intensity.
- **Machine Learning classification** (RandomForest) to output **LOW / MEDIUM / HIGH** cognitive load.
- **Live dashboard** with color indicators and load history chart.
- **Sound alert** for HIGH load (optional).
- **Full‑stack implementation** (React + Tailwind frontend, FastAPI + Python backend).

## Tech Stack
- **Frontend**: React, Tailwind CSS, Recharts, Vite
- **Backend**: FastAPI, OpenCV, MediaPipe, scikit‑learn
- **ML Model**: RandomForestClassifier trained on synthetic data (easily replaceable with real data)

## Project Structure
```
cognitive-load-detection/
├── backend/            # FastAPI server & ML model
│   ├── main.py         # API endpoints
│   ├── model.py        # Model training & loading
│   ├── utils.py        # Blink detection logic
│   └── requirements.txt
└── frontend/           # React app
    ├── src/
    │   ├── components/ # Webcam, typing, mouse, dashboard
    │   ├── App.jsx
    │   └── api.js
    └── package.json
```

## Installation & Run

### Prerequisites
- Python 3.8+
- Node.js 16+

### Backend
```bash
cd backend
pip install -r requirements.txt
python model.py              # trains and saves model.pkl
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` and grant camera permissions.

## How It Works
1. **Webcam feed** → OpenCV captures frames → MediaPipe extracts eye landmarks → blink rate is computed per session.
2. **Typing & mouse events** are captured in the browser and sent to the backend every 2 seconds.
3. **Backend** scales the features and uses a pre‑trained RandomForest model to predict cognitive load.
4. **Frontend** displays the result, updates a history chart, and triggers a sound alert if load is HIGH.

## Customizing the ML Model
- The current model is trained on synthetic data (`model.py`). Replace it with your own labeled dataset by modifying the `generate_synthetic_data` function or training externally and saving the model as `model.pkl`.
- The model expects features: `[blink_rate, typing_speed, error_rate, mouse_movement]`.

## Future Improvements
- Add facial expression analysis (e.g., emotion detection).
- Integrate physiological sensors (heart rate, GSR).
- Use deep learning for more accurate blink detection.
- Store historical data for user‑specific models.

## License
MIT

## Acknowledgements
- MediaPipe for face mesh
- OpenCV for image processing
- scikit‑learn for ML pipeline
```

---

## LinkedIn Post

**Headline:** I built a real‑time Cognitive Load Detection System using AI & full‑stack development! 🧠🚀

**Body:**  
Ever wondered how your brain reacts when you're under stress?  
I created a system that detects cognitive load in real‑time by analyzing:

✅ **Facial cues** – blink rate via webcam  
✅ **Typing dynamics** – WPM & error rate  
✅ **Mouse movement** – intensity  
✅ **ML classification** (RandomForest) → LOW / MEDIUM / HIGH load

The entire stack is open‑source and built with:  
🔹 React + Tailwind (frontend)  
🔹 FastAPI + Python (backend)  
🔹 OpenCV + MediaPipe (face/eye tracking)  
🔹 scikit‑learn (ML)

**No face data is stored or shared** – everything runs locally or through your own server. Privacy‑friendly! 👁️‍🗨️

Check out the GitHub repo for full code and instructions: [insert link]

I’d love to hear your thoughts – feel free to fork, star, or suggest improvements!  
#CognitiveLoad #AI #MachineLearning #React #FastAPI #OpenCV #FullStack #OpenSource

---

**Note for user:** The post is written so you don't need to show your face. You can share a screenshot of the dashboard or a diagram instead of a personal photo.
