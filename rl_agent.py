from typing import Any, Dict, List, Tuple
import os, torch

class RLAgent:
    def __init__(self):
        self.model = None
        self.mode = 'rl'
        self.last_loaded = None

    def load(self, model_path: str) -> Tuple[bool, str]:
        if not os.path.exists(model_path):
            return False, f'Model not found: {model_path}'
        try:
            if model_path.endswith('.pt'):
                self.model = torch.jit.load(model_path)
            else:
                self.model = torch.load(model_path, map_location='cpu')
            self.model.eval()
            self.last_loaded = model_path
            return True, 'Model loaded'
        except Exception as e:
            return False, f'Failed to load model: {e}'

    def set_mode(self, mode: str):
        self.mode = mode

    @torch.no_grad()
    def act(self, obstacles: List[Dict], state: Dict) -> Dict[str, float]:
        if self.model is not None:
            import torch as _t
            x = _t.tensor([[state.get('roll',0.0), state.get('pitch',0.0), float(len(obstacles))]], dtype=_t.float32)
            y = self.model(x).squeeze(0)
            if y.numel() >= 4:
                return {'pitch': float(y[0]), 'roll': float(y[1]), 'yaw': float(y[2]), 'throttle': float(y[3])}
        num = float(len(obstacles))
        pitch = -0.02 * num
        roll = 0.0
        yaw = 0.0
        throttle = 0.5
        return {'pitch': pitch, 'roll': roll, 'yaw': yaw, 'throttle': throttle}