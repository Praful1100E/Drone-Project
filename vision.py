import cv2
import numpy as np
from typing import Dict, List

class VisionPipeline:
    def __init__(self):
        self.input_size = (320,240)

    def detect_obstacles(self, frame: np.ndarray) -> List[Dict]:
        resized = cv2.resize(frame, self.input_size)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blur, 50, 150)
        cnts, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        obstacles = []
        for c in cnts:
            area = cv2.contourArea(c)
            if area < 200:
                continue
            x,y,w,h = cv2.boundingRect(c)
            obstacles.append({'bbox':[int(x),int(y),int(w),int(h)], 'area': float(area)})
        return obstacles[:20]

    def estimate_state(self, frame: np.ndarray) -> Dict:
        h,w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dx = float(np.mean(gray[:, w//2:]) - np.mean(gray[:, :w//2]))
        dy = float(np.mean(gray[h//2:, :]) - np.mean(gray[:h//2, :]))
        roll = np.clip(dx / 255.0 * 10.0, -10.0, 10.0)
        pitch = np.clip(dy / 255.0 * 10.0, -10.0, 10.0)
        return {'roll': roll, 'pitch': pitch}