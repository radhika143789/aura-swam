from __future__ import annotations

import pygame

from src.control.pid_controller import PIDController
from src.physics.engine import PhysicsEngine
from src.ui.pygame_renderer import PygameRenderer
from src.utils import config
from src.utils.state import SimulationState


def handle_events(state: SimulationState, controller: PIDController) -> bool:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_SPACE:
                state.paused = not state.paused
            if event.key == pygame.K_r:
                state.reset()
                controller.reset()
            if event.key == pygame.K_s:
                state.stabilizer_enabled = not state.stabilizer_enabled
                controller.reset()
            if event.key == pygame.K_d:
                state.disturbance_enabled = not state.disturbance_enabled
    return True


def run() -> None:
    state = SimulationState.create_default()
    engine = PhysicsEngine()
    controller = PIDController(
        kp=config.PID_KP,
        ki=config.PID_KI,
        kd=config.PID_KD,
        max_force=config.MAX_THRUST,
    )
    renderer = PygameRenderer()

    running = True
    while running:
        elapsed = renderer.tick()
        dt = min(elapsed, config.DT * 2.0)
        running = handle_events(state, controller)

        if not state.paused:
            if state.stabilizer_enabled:
                gravity_vector = state.field_model.gravity_vector(state.payload.position)
                gravity_feed_forward = -state.payload.mass * gravity_vector
                state.thrust_force = controller.compute(
                    state.target_position,
                    state.payload.position,
                    dt,
                    feed_forward=gravity_feed_forward,
                )
            else:
                state.thrust_force *= 0.0
            engine.step(state, dt)

        renderer.draw(state)

    renderer.close()


if __name__ == "__main__":
    run()
