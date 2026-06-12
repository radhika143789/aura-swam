from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Payload:
    """Point-mass payload state in screen-space physics coordinates."""

    mass: float
    position: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=float))

    @classmethod
    def create(cls, mass: float, position: tuple[float, float], velocity: tuple[float, float]) -> "Payload":
        return cls(
            mass=mass,
            position=np.array(position, dtype=float),
            velocity=np.array(velocity, dtype=float),
        )

    def reset(self, position: tuple[float, float], velocity: tuple[float, float]) -> None:
        self.position = np.array(position, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.acceleration = np.zeros(2, dtype=float)
