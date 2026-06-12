from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class PIDController:
    """Two-axis PID controller that outputs a clamped thrust force vector."""

    kp: float
    ki: float
    kd: float
    max_force: float
    integral: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=float))
    previous_error: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=float))

    def reset(self) -> None:
        self.integral = np.zeros(2, dtype=float)
        self.previous_error = np.zeros(2, dtype=float)

    def compute(self, target: np.ndarray, position: np.ndarray, dt: float) -> np.ndarray:
        error = target - position
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0.0 else np.zeros(2, dtype=float)
        self.previous_error = error

        force = self.kp * error + self.ki * self.integral + self.kd * derivative
        magnitude = float(np.linalg.norm(force))
        if magnitude > self.max_force:
            force = force / magnitude * self.max_force
        return force
