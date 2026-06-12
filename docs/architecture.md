# System Architecture

## MVP Runtime Topology

The simulator uses a deterministic hub-and-spoke architecture. The simulation loop is the orchestrator; all subsystems communicate through `SimulationState`.

```text
              Simulation Loop
                    |
     +--------------+--------------+
     |              |              |
 PhysicsEngine  AntiGravityField  PIDController
     |              |              |
     +--------------+--------------+
                    |
            SimulationState
                    |
              PyGameRenderer
```

## Design Rules

1. `SimulationState` is the single source of truth.
2. Physics integration is owned only by `PhysicsEngine`.
3. Field logic is owned only by `AntiGravityField`.
4. Stabilizer logic returns a force vector; it does not mutate position or velocity.
5. The renderer is read-only with respect to physics state.
6. Constants live in `src/utils/config.py`.

## Modules

- `src/main.py`: orchestration loop and keyboard events
- `src/utils/state.py`: centralized state object
- `src/utils/config.py`: MVP constants
- `src/physics/field.py`: localized anti-gravity field
- `src/physics/engine.py`: Newtonian force composition and integration
- `src/physics/payload.py`: point-mass payload model
- `src/control/pid_controller.py`: stabilizer baseline
- `src/ui/pygame_renderer.py`: simulation visualization
- `src/ui/telemetry_panel.py`: live dashboard panel

## Controller Boundary

The PID controller is the deterministic baseline. A PyTorch controller can later replace it by implementing the same interface:

```python
force = controller.compute(target_position, payload_position, dt)
```

This makes the system suitable for PID imitation learning or reinforcement-learning experiments without rewriting the physics engine.
