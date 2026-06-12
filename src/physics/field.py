from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class AntiGravityField:
    """Circular field that inverts and scales gravity inside its radius."""

    center: np.ndarray
    radius: float
    alpha: float
    gravity: float

    @classmethod
    def create(
        cls,
        center: tuple[float, float],
        radius: float,
        alpha: float,
        gravity: float,
    ) -> "AntiGravityField":
        return cls(np.array(center, dtype=float), radius, alpha, gravity)

    def contains(self, position: np.ndarray) -> bool:
        return float(np.linalg.norm(position - self.center)) <= self.radius

    def gravity_vector(self, position: np.ndarray) -> np.ndarray:
        if self.contains(position):
            return np.array([0.0, -self.alpha * self.gravity], dtype=float)
        return np.array([0.0, self.gravity], dtype=float)
