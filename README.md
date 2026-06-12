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
- Headless QA benchmark suite for stabilization metrics
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
  qa/
    run_stabilization_benchmarks.py
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

## QA Benchmarks

Run unit tests:

```bash
pytest
```

Run the Phase 4 stabilization benchmark suite:

```bash
python -m src.qa.run_stabilization_benchmarks --details
```

Use strict mode for CI or final validation:

```bash
python -m src.qa.run_stabilization_benchmarks --strict --details
```

The benchmark suite logs:

- `mean_error_px`
- `max_error_px`
- `rmse_error_px`
- `final_error_px`
- `settling_time_seconds`
- `stable_time_ratio`
- `field_inside_ratio`
- `mean_velocity_px_s`
- `max_velocity_px_s`
- `mean_thrust`
- `max_thrust`
- `thrust_saturation_ratio`
- `stability_state_counts`
- `pass_or_fail`

Covered scenarios:

- baseline PID stabilization
- uncontrolled baseline
- fluctuating anti-gravity field strength
- dynamic payload mass changes
- max thrust saturation
- target offset tests
- timestep variation tests

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
