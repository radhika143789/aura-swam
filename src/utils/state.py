from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src.physics.field import AntiGravityField
from src.physics.payload import Payload
from src.utils import config


@dataclass
class SimulationState:
    """Single source of truth shared by simulation spokes."""

    payload: Payload
    field_model: AntiGravityField
    target_position: np.ndarray
    time_seconds: float = 0.0
    paused: bool = False
    stabilizer_enabled: bool = True
    disturbance_enabled: bool = False
    thrust_force: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=float))
    gravity_vector: np.ndarray = field(default_factory=lambda: np.zeros(2, dtype=float))
    stable_seconds: float = 0.0
    stability: str = "correcting"

    @classmethod
    def create_default(cls) -> "SimulationState":
        payload = Payload.create(
            mass=config.PAYLOAD_MASS,
            position=config.INITIAL_POSITION,
            velocity=config.INITIAL_VELOCITY,
        )
        field_model = AntiGravityField.create(
            center=config.FIELD_CENTER,
            radius=config.FIELD_RADIUS,
            alpha=config.ANTI_GRAVITY_ALPHA,
            gravity=config.GRAVITY,
        )
        return cls(
            payload=payload,
            field_model=field_model,
            target_position=np.array(config.TARGET_POSITION, dtype=float),
        )

    @property
    def error_vector(self) -> np.ndarray:
        return self.target_position - self.payload.position

    @property
    def error_magnitude(self) -> float:
        return float(np.linalg.norm(self.error_vector))

    @property
    def velocity_magnitude(self) -> float:
        return float(np.linalg.norm(self.payload.velocity))

    @property
    def inside_field(self) -> bool:
        return self.field_model.contains(self.payload.position)

    def reset(self) -> None:
        self.payload.reset(config.INITIAL_POSITION, config.INITIAL_VELOCITY)
        self.time_seconds = 0.0
        self.thrust_force = np.zeros(2, dtype=float)
        self.gravity_vector = np.zeros(2, dtype=float)
        self.stable_seconds = 0.0
        self.stability = "correcting"
