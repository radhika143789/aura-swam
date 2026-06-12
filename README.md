# AI-Stabilized Antigravity Physics Simulator

A 48-hour hackathon MVP that simulates a localized anti-gravity field and stabilizes a payload inside it using a deterministic control loop.

## MVP Use Case

A single payload enters a circular anti-gravity anomaly. Inside the anomaly, gravity is inverted and scaled. A stabilizer applies thrust to keep the payload near a target hover point.

## Core Features

- 2D PyGame physics sandbox
- Localized circular anti-gravity field
- Centralized simulation state
- Semi-implicit Euler integration
- PID-based stabilizer
- Live vector visualization for gravity, thrust, and velocity
- Telemetry panel for position, velocity, acceleration, error, and stability
- Architecture and mathematical model documentation

## Tech Stack

- Python
- PyGame
- NumPy
- PyTorch-ready controller boundary
- Pytest
- Figma for dashboard prototyping

## Repository Structure

```text
src/
  main.py
  control/
    pid_controller.py
  physics/
    engine.py
    field.py
    payload.py
  ui/
    pygame_renderer.py
    telemetry_panel.py
  utils/
    config.py
    state.py
tests/
  test_physics.py
  test_controller.py
docs/
  architecture.md
  math_model.md
  figma_wireframes.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python -m src.main
```

## Controls

- `Space`: pause/resume
- `R`: reset simulation
- `S`: toggle stabilizer
- `D`: toggle disturbance
- `Esc`: quit

## MVP Limitations

This simulator is a computational physics and control-system demo. It does not claim to model real-world anti-gravity, general relativity, rigid-body rotation, fluid dynamics, drag, or aerodynamics.

## Stretch Work

- PyTorch policy trained from PID telemetry
- CSV telemetry export
- Multi-field anomaly scenarios
- Disturbance curriculum
- Web dashboard
