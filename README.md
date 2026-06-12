# AI-Stabilized Antigravity Physics Simulator

A 48-hour hackathon MVP that simulates a localized anti-gravity field and stabilizes a payload inside it using a deterministic control loop.

## MVP Use Case

A single payload enters a circular anti-gravity anomaly. Inside the anomaly, gravity is inverted and scaled. A stabilizer applies thrust to keep the payload near a target hover point.

## Core Features

- Browser-ready Streamlit dashboard in `app.py`
- 2D PyGame physics sandbox for local desktop demos
- Localized circular anti-gravity field
- Centralized simulation state
- Semi-implicit Euler integration
- Gravity feed-forward plus PID stabilizer
- Live vector visualization for gravity, thrust, and velocity
- Telemetry panel for position, velocity, acceleration, error, and stability
- Headless QA benchmark suite for stabilization metrics
- Architecture and mathematical model documentation

## Tech Stack

- Python
- Streamlit
- NumPy
- SciPy
- PyTorch-ready controller boundary
- PyGame for optional local desktop visualization
- Pytest
- Figma for dashboard prototyping

## Repository Structure

```text
app.py
requirements.txt
requirements-local.txt
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
  demo_script.md
  submission_checklist.md
```

## Web Deployment

Run the browser app locally:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Deploy on Streamlit Community Cloud:

1. Open https://share.streamlit.io.
2. Choose GitHub repo `radhika143789/aura-swam`.
3. Select branch `main`.
4. Set main file path to `app.py`.
5. Deploy and copy the generated public URL.

## Local Desktop Simulator

Install the optional PyGame dependency set:

```bash
pip install -r requirements-local.txt
python -m src.main
```

Controls:

- `Space`: pause/resume
- `R`: reset simulation
- `S`: toggle stabilizer
- `D`: toggle disturbance
- `Esc`: quit

## QA Benchmarks

Run unit tests:

```bash
pytest
```

Run the Phase 4 stabilization benchmark suite:

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

## Mathematical Verification and Telemetry

The engine models acceleration from net force:

```text
a = F_net / m
F_net = F_gravity + F_thrust + F_disturbance
```

The local gravity vector changes by field membership:

```text
outside field: g_local = [0, +g]
inside field:  g_local = [0, -alpha * g]
```

The stabilizer uses model-aware gravity compensation plus PID correction:

```text
F_feedforward = -m * g_local
F_pid = Kp * e + Ki * integral(e) + Kd * derivative(e)
F_thrust = F_feedforward + F_pid
```

This fixes the steady-state hover offset that appears in a pure PID controller under persistent inverted gravity.

### Phase 4 Benchmark Snapshot

```text
baseline_pid           PASS  mean_err=3.959   final_err=0.242   settle_s=1.733
baseline_uncontrolled  PASS  mean_err=193.431 final_err=149.959
field_fluctuation      PASS  mean_err=3.959   final_err=0.242
dynamic_mass           PASS  mean_err=31.125  final_err=1.526
thrust_saturation      PASS  sat_ratio=0.844
target_center          PASS  final_err=0.247
target_above           PASS  final_err=0.383
target_right           PASS  final_err=0.282
target_below           PASS  final_err=0.078
dt_30hz                PASS  final_err=0.246
dt_60hz                PASS  final_err=0.247
dt_120hz               PASS  final_err=0.248
```

Additional verification claims:

- Stabilization settling time: approximately `1.7s` in the baseline stabilized scenario
- Controller iteration target: one feedback update per simulation timestep at `60 Hz`
- System state sync: centralized in `SimulationState`, preventing physics/control/telemetry drift

## Demo Video

Use `docs/demo_script.md` for the 3-minute pitch.

Recommended structure:

1. Problem: inverted gravity causes payload instability.
2. Math: local gravity vector switches from `[0, +g]` to `[0, -alpha g]`.
3. Control: feed-forward plus PID counters the field.
4. Proof: benchmark table shows settling time, error, RMSE, and edge-case resilience.
5. Impact: extensible architecture for neural controllers and richer anomaly fields.

## MVP Limitations

This simulator is a computational physics and control-system demo. It does not claim to model real-world anti-gravity, general relativity, rigid-body rotation, fluid dynamics, drag, or aerodynamics.

## Stretch Work

- PyTorch policy trained from PID telemetry
- CSV telemetry export
- Multi-field anomaly scenarios
- Disturbance curriculum
- Web dashboard enhancements
