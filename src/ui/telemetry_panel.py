from __future__ import annotations

import pygame

from src.utils import config
from src.utils.state import SimulationState


class TelemetryPanel:
    """Right-side live telemetry surface."""

    def __init__(self) -> None:
        self.font = pygame.font.SysFont("consolas", 18)
        self.title_font = pygame.font.SysFont("consolas", 22, bold=True)

    def draw(self, surface: pygame.Surface, state: SimulationState) -> None:
        panel_x = 780
        pygame.draw.rect(surface, (18, 25, 36), (panel_x, 0, config.SCREEN_WIDTH - panel_x, config.SCREEN_HEIGHT))
        pygame.draw.line(surface, (46, 61, 82), (panel_x, 0), (panel_x, config.SCREEN_HEIGHT), 2)

        lines = [
            ("Telemetry", True),
            (f"time: {state.time_seconds:6.2f}s", False),
            (f"mode: {'PID ON' if state.stabilizer_enabled else 'OPEN LOOP'}", False),
            (f"field: {'ANTI-G' if state.inside_field else 'NORMAL-G'}", False),
            (f"status: {state.stability.upper()}", False),
            ("", False),
            (f"pos x: {state.payload.position[0]:8.2f}", False),
            (f"pos y: {state.payload.position[1]:8.2f}", False),
            (f"vel:   {state.velocity_magnitude:8.2f} px/s", False),
            (f"acc x: {state.payload.acceleration[0]:8.2f}", False),
            (f"acc y: {state.payload.acceleration[1]:8.2f}", False),
            ("", False),
            (f"err:   {state.error_magnitude:8.2f} px", False),
            (f"g y:   {state.gravity_vector[1]:8.2f}", False),
            (f"thr x: {state.thrust_force[0]:8.2f}", False),
            (f"thr y: {state.thrust_force[1]:8.2f}", False),
            ("", False),
            ("Space pause/resume", False),
            ("R reset", False),
            ("S stabilizer", False),
            ("D disturbance", False),
            ("Esc quit", False),
        ]

        y = 28
        for text, title in lines:
            font = self.title_font if title else self.font
            color = config.TEXT_COLOR if text else config.MUTED_TEXT_COLOR
            rendered = font.render(text, True, color)
            surface.blit(rendered, (panel_x + 24, y))
            y += 32 if title else 26
