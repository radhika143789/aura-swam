# Final Submission Checklist

## Deployment

1. Push `main` to GitHub.
2. Open https://share.streamlit.io.
3. Select repository `radhika143789/aura-swam`.
4. Select branch `main`.
5. Set main file path to `app.py`.
6. Deploy and copy the public URL.

## Local Validation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
python -m src.qa.run_stabilization_benchmarks --strict --details
streamlit run app.py
```

For the desktop PyGame simulator:

```bash
pip install -r requirements-local.txt
python -m src.main
```

## Required Submission Assets

- Public Streamlit URL
- GitHub repository URL
- 3-minute demo video
- README with setup, QA, and metrics
- Screenshot or screen recording of telemetry dashboard

## Judge Talking Points

- Dynamic local gravity vector: `[0, +g]` outside field, `[0, -alpha g]` inside field
- Feed-forward plus PID control: `F_thrust = -m g_local + F_pid`
- Centralized simulation state prevents drift between physics, control, and telemetry
- Headless QA suite proves stabilization across fluctuation, mass changes, thrust saturation, and timestep variation
