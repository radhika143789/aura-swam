from __future__ import annotations

import math

import numpy as np

from src.utils import config
from src.utils.state import SimulationState


class PhysicsEngine:
    """Owns force composition, integration, and simulation health state."""

    def step(self, state: SimulationState, dt: float) -> None:
        payload = state.payload
        state.gravity_vector = state.field_model.gravity_vector(payload.position)

        gravity_force = payload.mass * state.gravity_vector
        disturbance_force = self._disturbance(state.time_seconds) if state.disturbance_enabled else np.zeros(2)
        net_force = gravity_force + state.thrust_force + disturbance_force

        payload.acceleration = net_force / payload.mass
        payload.velocity = payload.velocity + payload.acceleration * dt
        payload.position = payload.position + payload.velocity * dt
        state.time_seconds += dt

        self._constrain_to_screen(state)
        self._update_stability(state, dt)

    def _disturbance(self, time_seconds: float) -> np.ndarray:
        return np.array([
            140.0 * math.sin(time_seconds * 2.2),
            90.0 * math.cos(time_seconds * 1.7),
        ])

    def _constrain_to_screen(self, state: SimulationState) -> None:
        payload = state.payload
        radius = config.PAYLOAD_RADIUS
        min_x = radius
        max_x = config.SCREEN_WIDTH - radius
        min_y = radius
        max_y = config.SCREEN_HEIGHT - radius

        if payload.position[0] < min_x or payload.position[0] > max_x:
            payload.velocity[0] *= -0.35
            payload.position[0] = float(np.clip(payload.position[0], min_x, max_x))
        if payload.position[1] < min_y or payload.position[1] > max_y:
            payload.velocity[1] *= -0.35
            payload.position[1] = float(np.clip(payload.position[1], min_y, max_y))

    def _update_stability(self, state: SimulationState, dt: float) -> None:
        if state.error_magnitude > config.UNSTABLE_ERROR_RADIUS:
            state.stable_seconds = 0.0
            state.stability = "unstable"
            return

        is_stable_now = (
            state.error_magnitude < config.STABLE_ERROR_RADIUS
            and state.velocity_magnitude < config.STABLE_VELOCITY_LIMIT
        )
        if is_stable_now:
            state.stable_seconds += dt
        else:
            state.stable_seconds = 0.0

        state.stability = (
            "stable"
            if state.stable_seconds >= config.STABLE_SECONDS_REQUIRED
            else "correcting"
        )
