import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Eye landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

def eye_aspect_ratio(landmarks, eye_indices):
    # landmarks are normalized (x,y) in image coordinates
    p1 = landmarks[eye_indices[0]]
    p2 = landmarks[eye_indices[1]]
    p3 = landmarks[eye_indices[2]]
    p4 = landmarks[eye_indices[3]]
    p5 = landmarks[eye_indices[4]]
    p6 = landmarks[eye_indices[5]]
    
    # Compute vertical distances
    v1 = np.linalg.norm(p2 - p6)
    v2 = np.linalg.norm(p3 - p5)
    # Horizontal distance
    h = np.linalg.norm(p1 - p4)
    ear = (v1 + v2) / (2.0 * h + 1e-6)
    return ear

class BlinkDetector:
    def __init__(self, blink_thresh=0.2, consec_frames=2):
        self.blink_thresh = blink_thresh
        self.consec_frames = consec_frames
        self.ear_history = deque(maxlen=consec_frames)
        self.blink_counter = 0
        self.total_frames = 0
        self.last_blink_time = None
        self.blink_timestamps = deque(maxlen=100)  # store timestamps of blinks

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        if not results.multi_face_landmarks:
            return None
        
        h, w, _ = frame.shape
        landmarks = results.multi_face_landmarks[0].landmark
        points = np.array([(lm.x * w, lm.y * h) for lm in landmarks])
        
        left_ear = eye_aspect_ratio(points, LEFT_EYE)
        right_ear = eye_aspect_ratio(points, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0
        
        self.ear_history.append(ear)
        if len(self.ear_history) >= self.consec_frames:
            # Detect blink if EAR drops below threshold for consecutive frames
            if all(e < self.blink_thresh for e in self.ear_history):
                # Check if we haven't recorded a blink too recently
                now = time.time()
                if self.last_blink_time is None or (now - self.last_blink_time) > 0.3:
                    self.blink_timestamps.append(now)
                    self.last_blink_time = now
                    self.blink_counter += 1
            # Reset history to avoid multiple detections for same blink
            self.ear_history.clear()
        
        return ear

    def get_blink_rate(self, window_seconds=10):
        now = time.time()
        # Keep only blinks within the window
        while self.blink_timestamps and now - self.blink_timestamps[0] > window_seconds:
            self.blink_timestamps.popleft()
        # Blinks per minute
        if len(self.blink_timestamps) < 2:
            return 0.0
        # Compute rate based on first and last blink in window
        time_span = self.blink_timestamps[-1] - self.blink_timestamps[0]
        if time_span > 0:
            rate = (len(self.blink_timestamps) - 1) * 60.0 / time_span
            return min(rate, 60.0)  # cap at 60 blinks/min
        return 0.0

    def reset(self):
        self.blink_counter = 0
        self.total_frames = 0
        self.ear_history.clear()
        self.blink_timestamps.clear()
        self.last_blink_time = None