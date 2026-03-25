import cv2
import mediapipe as mp
import numpy as np
import time
import threading
from collections import deque
from pynput import mouse, keyboard

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
INNER_BROWS = [107, 336] # Inner points of left and right brows
INNER_LIPS = [13, 14]   # Top and bottom of inner mouth

def eye_aspect_ratio(landmarks, eye_indices):
    p = landmarks[eye_indices]
    v1 = np.linalg.norm(p[1] - p[5])
    v2 = np.linalg.norm(p[2] - p[4])
    h = np.linalg.norm(p[0] - p[3])
    return (v1 + v2) / (2.0 * h + 1e-6)

class FaceAnalyzer:
    def __init__(self, blink_thresh=0.24):
        self.blink_thresh = blink_thresh
        self.blink_counter = 0
        self.is_blinking = False
        self.blink_timestamps = deque(maxlen=100)
        
        # Expressions (Unused but kept for structure)
        self.current_ear = 0.3
        self.brow_dist_norm = 0.15
        self.mouth_ratio = 0.0

    def process_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)
        if not results.multi_face_landmarks:
            return 0.3
        
        h, w, _ = frame.shape
        landmarks = results.multi_face_landmarks[0].landmark
        points = np.array([(lm.x * w, lm.y * h) for lm in landmarks])
        
        # 1. Blink Detection on "Edge"
        left_ear = eye_aspect_ratio(points, LEFT_EYE)
        right_ear = eye_aspect_ratio(points, RIGHT_EYE)
        self.current_ear = float((left_ear + right_ear) / 2.0)
        
        if self.current_ear < self.blink_thresh:
            self.is_blinking = True
        else:
            if self.is_blinking:
                # Blink ended, count it
                self.blink_counter += 1
                self.blink_timestamps.append(time.time())
                self.is_blinking = False
        
        # Measurements
        head_width = np.linalg.norm(points[33] - points[263])
        brow_dist = np.linalg.norm(points[INNER_BROWS[0]] - points[INNER_BROWS[1]])
        self.brow_dist_norm = brow_dist / head_width if head_width > 0 else 1.0
        
        face_height = np.linalg.norm(points[10] - points[152])
        mouth_dist = np.linalg.norm(points[INNER_LIPS[0]] - points[INNER_LIPS[1]])
        self.mouth_ratio = mouth_dist / face_height if face_height > 0 else 0.0
        
        return self.current_ear

    def get_blink_rate(self, window_seconds=5):
        now = time.time()
        while self.blink_timestamps and now - self.blink_timestamps[0] > window_seconds:
            self.blink_timestamps.popleft()
        return (len(self.blink_timestamps) * 60.0) / window_seconds

class GlobalInputTracker:
    def __init__(self):
        self.key_count = 0
        self.backspace_count = 0
        self.mouse_distance = 0.0
        self.last_mouse_pos = None
        self.start_time = time.time()
        
        # Threading for listeners
        self.mouse_listener = mouse.Listener(on_move=self._on_move)
        self.key_listener = keyboard.Listener(on_press=self._on_press)

    def start(self):
        try:
            self.mouse_listener.start()
            self.key_listener.start()
            print("INFO: Global input listeners started successfully.")
        except Exception as e:
            print(f"WARNING: Could not start global input listeners: {e}")
            print("Note: On some systems, this requires specific permissions.")

    def _on_move(self, x, y):
        if self.last_mouse_pos:
            dx = x - self.last_mouse_pos[0]
            dy = y - self.last_mouse_pos[1]
            dist = np.sqrt(dx*dx + dy*dy)
            # Limit huge jumps (multi-monitor/teleport)
            if dist < 500:
                self.mouse_distance += dist
        self.last_mouse_pos = (x, y)

    def _on_press(self, key):
        self.key_count += 1
        if key == keyboard.Key.backspace:
            self.backspace_count += 1

    def get_stats(self, window_seconds=2):
        now = time.time()
        duration = now - self.start_time
        if duration < 0.1: return {"wpm": 0, "error_rate": 0, "mouse_speed": 0}
        
        # WPM: (keys/5) / (duration/60)
        wpm = (self.key_count / 5.0) / (duration / 60.0)
        # Error rate
        total_keys = self.key_count + self.backspace_count
        error_rate = self.backspace_count / total_keys if total_keys > 0 else 0
        # Mouse speed
        mouse_speed = self.mouse_distance / duration # px/s
        
        # Reset counters after snapshot
        self.key_count = 0
        self.backspace_count = 0
        self.mouse_distance = 0
        self.start_time = now
        
        return {
            "wpm": min(wpm, 150),
            "error_rate": min(error_rate, 0.5),
            "mouse_speed": min(mouse_speed / 10, 100) # norm 0-100
        }