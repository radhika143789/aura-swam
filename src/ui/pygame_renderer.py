from __future__ import annotations

import pygame

from src.ui.telemetry_panel import TelemetryPanel
from src.utils import config
from src.utils.state import SimulationState


class PygameRenderer:
    """Renders the physics sandbox and telemetry."""

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("AI-Stabilized Antigravity Physics Simulator")
        self.surface = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.telemetry = TelemetryPanel()

    def tick(self) -> float:
        return self.clock.tick(config.FPS) / 1000.0

    def draw(self, state: SimulationState) -> None:
        self.surface.fill(config.BACKGROUND)
        self._draw_field(state)
        self._draw_target(state)
        self._draw_vectors(state)
        self._draw_payload(state)
        self.telemetry.draw(self.surface, state)
        pygame.display.flip()

    def _draw_field(self, state: SimulationState) -> None:
        center = state.field_model.center.astype(int)
        radius = int(state.field_model.radius)
        pygame.draw.circle(self.surface, config.FIELD_FILL, center, radius)
        pygame.draw.circle(self.surface, config.FIELD_COLOR, center, radius, 3)

    def _draw_target(self, state: SimulationState) -> None:
        target = state.target_position.astype(int)
        pygame.draw.line(self.surface, config.TARGET_COLOR, (target[0] - 12, target[1]), (target[0] + 12, target[1]), 2)
        pygame.draw.line(self.surface, config.TARGET_COLOR, (target[0], target[1] - 12), (target[0], target[1] + 12), 2)
        pygame.draw.circle(self.surface, config.TARGET_COLOR, target, 18, 1)

    def _draw_payload(self, state: SimulationState) -> None:
        position = state.payload.position.astype(int)
        pygame.draw.circle(self.surface, config.PAYLOAD_COLOR, position, config.PAYLOAD_RADIUS)
        pygame.draw.circle(self.surface, (255, 255, 255), position, config.PAYLOAD_RADIUS, 2)

    def _draw_vectors(self, state: SimulationState) -> None:
        origin = state.payload.position
        self._arrow(origin, state.gravity_vector * 0.08, config.GRAVITY_VECTOR_COLOR)
        self._arrow(origin, state.thrust_force / max(state.payload.mass, 1.0) * 0.035, config.THRUST_VECTOR_COLOR)
        self._arrow(origin, state.payload.velocity * 0.18, config.VELOCITY_VECTOR_COLOR)

    def _arrow(self, origin, vector, color) -> None:
        start = origin.astype(int)
        end = (origin + vector).astype(int)
        pygame.draw.line(self.surface, color, start, end, 3)
        pygame.draw.circle(self.surface, color, end, 4)

    def close(self) -> None:
        pygame.quit()
