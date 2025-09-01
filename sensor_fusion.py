from typing import Optional, Dict

class ComplementaryFusion:
    def __init__(self, alpha: float = 0.98):
        self.alpha = alpha
        self.state = {'roll': 0.0, 'pitch': 0.0}

    def update(self, imu: Optional[Dict]=None, gps: Optional[Dict]=None, baro: Optional[Dict]=None):
        roll = self.state['roll']
        pitch = self.state['pitch']
        if imu:
            roll = self.alpha * roll + (1 - self.alpha) * float(imu.get('roll', 0.0))
            pitch = self.alpha * pitch + (1 - self.alpha) * float(imu.get('pitch', 0.0))
        self.state.update({'roll': roll, 'pitch': pitch})
        return dict(self.state)