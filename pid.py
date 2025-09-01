from dataclasses import dataclass
from typing import Tuple

@dataclass
class PID:
    kp: float
    ki: float
    kd: float
    clamp: Tuple[float,float] = (-1.0,1.0)

    def __post_init__(self):
        self._i = 0.0
        self._prev_e = None

    def reset(self):
        self._i = 0.0
        self._prev_e = None

    def step(self, setpoint: float, measurement: float, dt: float) -> float:
        e = setpoint - measurement
        p = self.kp * e
        self._i += self.ki * e * dt
        d = 0.0 if self._prev_e is None else self.kd * (e - self._prev_e) / max(dt,1e-6)
        self._prev_e = e
        u = p + self._i + d
        lo, hi = self.clamp
        return max(lo, min(hi, u))