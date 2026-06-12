from __future__ import annotations

import math
from collections import Counter
from dataclasses import replace

import numpy as np
import streamlit as st
import streamlit.components.v1 as components

from src.control.pid_controller import PIDController
from src.physics.engine import PhysicsEngine
from src.utils import config
from src.utils.state import SimulationState


st.set_page_config(
    page_title="AI-Stabilized Antigravity Simulator",
    page_icon="AG",
    layout="wide",
)


def feed_forward(state: SimulationState) -> np.ndarray:
    gravity_vector = state.field_model.gravity_vector(state.payload.position)
    return -state.payload.mass * gravity_vector


def run_simulation(
    *,
    duration_seconds: float,
    target_x: float,
    target_y: float,
    alpha: float,
    max_thrust: float,
    stabilizer_enabled: bool,
    fluctuation_enabled: bool,
    dynamic_mass_enabled: bool,
    disturbance_enabled: bool,
) -> tuple[SimulationState, list[dict]]:
    state = SimulationState.create_default()
    state.target_position = np.array([target_x, target_y], dtype=float)
    state.field_model = replace(state.field_model, alpha=alpha)
    state.stabilizer_enabled = stabilizer_enabled
    state.disturbance_enabled = disturbance_enabled

    engine = PhysicsEngine()
    controller = PIDController(
        kp=config.PID_KP,
        ki=config.PID_KI,
        kd=config.PID_KD,
        max_force=max_thrust,
    )

    samples: list[dict] = []
    steps = int(duration_seconds / config.DT)

    for step in range(steps):
        time_seconds = step * config.DT

        if fluctuation_enabled:
            dynamic_alpha = alpha + 0.45 * math.sin(time_seconds * 3.1) + 0.20 * math.sin(time_seconds * 9.7)
            dynamic_alpha = float(np.clip(dynamic_alpha, 0.75, 1.75))
            state.field_model = replace(state.field_model, alpha=dynamic_alpha)

        if dynamic_mass_enabled:
            if time_seconds >= 20.0:
                state.payload.mass = 1.0
            elif time_seconds >= 10.0:
                state.payload.mass = 4.0
            else:
                state.payload.mass = config.PAYLOAD_MASS

        if stabilizer_enabled:
            state.thrust_force = controller.compute(
                state.target_position,
                state.payload.position,
                config.DT,
                feed_forward=feed_forward(state),
            )
        else:
            state.thrust_force *= 0.0

        engine.step(state, config.DT)

        samples.append(
            {
                "time": state.time_seconds,
                "error_px": state.error_magnitude,
                "velocity_px_s": state.velocity_magnitude,
                "thrust": float(np.linalg.norm(state.thrust_force)),
                "x": float(state.payload.position[0]),
                "y": float(state.payload.position[1]),
                "inside_field": state.inside_field,
                "stability": state.stability,
                "alpha": state.field_model.alpha,
                "mass": state.payload.mass,
            }
        )

    return state, samples


def settling_time(samples: list[dict], threshold_px: float = 25.0, velocity_limit: float = 20.0) -> float | None:
    for index, sample in enumerate(samples):
        tail = samples[index:]
        if all(item["error_px"] <= threshold_px and item["velocity_px_s"] <= velocity_limit for item in tail):
            return float(sample["time"])
    return None


def rmse(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.0


def svg_scene(state: SimulationState, samples: list[dict]) -> str:
    width = 760
    height = 520
    scale_x = width / config.SCREEN_WIDTH
    scale_y = height / config.SCREEN_HEIGHT

    def sx(value: float) -> float:
        return value * scale_x

    def sy(value: float) -> float:
        return value * scale_y

    field = state.field_model
    payload = state.payload
    target = state.target_position
    trail = samples[:: max(1, len(samples) // 140)]
    trail_points = " ".join(f"{sx(item['x']):.1f},{sy(item['y']):.1f}" for item in trail)

    g = state.gravity_vector * 0.08
    thrust = state.thrust_force / max(payload.mass, 1.0) * 0.035
    velocity = payload.velocity * 0.18

    def vector_line(vector: np.ndarray, color: str) -> str:
        x1 = sx(payload.position[0])
        y1 = sy(payload.position[1])
        x2 = sx(payload.position[0] + vector[0])
        y2 = sy(payload.position[1] + vector[1])
        return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="3" stroke-linecap="round" />'

    return f"""
    <svg width="100%" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" role="img">
      <rect width="{width}" height="{height}" fill="#0c1018" />
      <circle cx="{sx(field.center[0]):.1f}" cy="{sy(field.center[1]):.1f}" r="{field.radius * scale_x:.1f}" fill="#1c3454" stroke="#4a90e2" stroke-width="3" />
      <polyline points="{trail_points}" fill="none" stroke="#8ea3c4" stroke-width="2" opacity="0.58" />
      <line x1="{sx(target[0] - 14):.1f}" y1="{sy(target[1]):.1f}" x2="{sx(target[0] + 14):.1f}" y2="{sy(target[1]):.1f}" stroke="#76ffbf" stroke-width="2" />
      <line x1="{sx(target[0]):.1f}" y1="{sy(target[1] - 14):.1f}" x2="{sx(target[0]):.1f}" y2="{sy(target[1] + 14):.1f}" stroke="#76ffbf" stroke-width="2" />
      <circle cx="{sx(target[0]):.1f}" cy="{sy(target[1]):.1f}" r="13" fill="none" stroke="#76ffbf" stroke-width="1" />
      {vector_line(g, "#ff7474")}
      {vector_line(thrust, "#78dcff")}
      {vector_line(velocity, "#bf89ff")}
      <circle cx="{sx(payload.position[0]):.1f}" cy="{sy(payload.position[1]):.1f}" r="10" fill="#f4d660" stroke="#ffffff" stroke-width="2" />
      <text x="18" y="28" fill="#e8eef7" font-family="Consolas, monospace" font-size="16">Anti-gravity field + stabilized payload</text>
      <text x="18" y="52" fill="#8ea3c4" font-family="Consolas, monospace" font-size="13">red=g vector, cyan=thrust, violet=velocity</text>
    </svg>
    """


def metric_summary(samples: list[dict]) -> dict:
    errors = [item["error_px"] for item in samples]
    velocities = [item["velocity_px_s"] for item in samples]
    thrusts = [item["thrust"] for item in samples]
    stability_counts = Counter(item["stability"] for item in samples)
    return {
        "mean_error_px": sum(errors) / len(errors),
        "max_error_px": max(errors),
        "rmse_error_px": rmse(errors),
        "final_error_px": errors[-1],
        "settling_time_seconds": settling_time(samples),
        "stable_time_ratio": stability_counts.get("stable", 0) / len(samples),
        "field_inside_ratio": sum(1 for item in samples if item["inside_field"]) / len(samples),
        "mean_velocity_px_s": sum(velocities) / len(velocities),
        "max_velocity_px_s": max(velocities),
        "mean_thrust": sum(thrusts) / len(thrusts),
        "max_thrust": max(thrusts),
        "stability_state_counts": dict(stability_counts),
    }


st.title("AI-Stabilized Antigravity Physics Simulator")
st.caption("A browser-ready MVP demonstrating inverted gravity vector modeling and model-aware PID stabilization.")

with st.sidebar:
    st.header("Simulation Controls")
    duration = st.slider("Duration (seconds)", 5.0, 40.0, 30.0, 1.0)
    target_x = st.slider("Target X", 300.0, 760.0, float(config.TARGET_POSITION[0]), 5.0)
    target_y = st.slider("Target Y", 180.0, 520.0, float(config.TARGET_POSITION[1]), 5.0)
    alpha = st.slider("Anti-gravity strength alpha", 0.75, 1.75, float(config.ANTI_GRAVITY_ALPHA), 0.05)
    max_thrust = st.slider("Max thrust", 600.0, 3000.0, float(config.MAX_THRUST), 100.0)
    stabilizer_enabled = st.toggle("Stabilizer enabled", value=True)
    fluctuation_enabled = st.toggle("Fluctuating field", value=True)
    dynamic_mass_enabled = st.toggle("Dynamic payload mass", value=False)
    disturbance_enabled = st.toggle("External disturbance", value=False)

state, samples = run_simulation(
    duration_seconds=duration,
    target_x=target_x,
    target_y=target_y,
    alpha=alpha,
    max_thrust=max_thrust,
    stabilizer_enabled=stabilizer_enabled,
    fluctuation_enabled=fluctuation_enabled,
    dynamic_mass_enabled=dynamic_mass_enabled,
    disturbance_enabled=disturbance_enabled,
)
summary = metric_summary(samples)

cols = st.columns(6)
cols[0].metric("Final Error", f"{summary['final_error_px']:.2f} px")
cols[1].metric("Mean Error", f"{summary['mean_error_px']:.2f} px")
cols[2].metric("RMSE", f"{summary['rmse_error_px']:.2f} px")
settled = summary["settling_time_seconds"]
cols[3].metric("Settling Time", "n/a" if settled is None else f"{settled:.2f}s")
cols[4].metric("Stable Ratio", f"{summary['stable_time_ratio']:.2%}")
cols[5].metric("Inside Field", f"{summary['field_inside_ratio']:.2%}")

left, right = st.columns([1.55, 1.0])
with left:
    components.html(svg_scene(state, samples), height=530)

with right:
    st.subheader("Control Law")
    st.latex(r"\mathbf{F}_{thrust} = -m\mathbf{g}_{local} + K_p\mathbf{e} + K_i\int\mathbf{e}\,dt + K_d\frac{d\mathbf{e}}{dt}")
    st.json(
        {
            "time": round(state.time_seconds, 3),
            "inside_field": state.inside_field,
            "position": [round(float(v), 3) for v in state.payload.position],
            "velocity_px_s": round(state.velocity_magnitude, 3),
            "gravity": [round(float(v), 3) for v in state.gravity_vector],
            "thrust": [round(float(v), 3) for v in state.thrust_force],
            "error_px": round(state.error_magnitude, 3),
            "stability": state.stability,
        }
    )

st.subheader("Telemetry Curves")
st.line_chart(
    {
        "error_px": [item["error_px"] for item in samples],
        "velocity_px_s": [item["velocity_px_s"] for item in samples],
    }
)
st.line_chart({"thrust": [item["thrust"] for item in samples], "alpha": [item["alpha"] * 1000 for item in samples]})

st.subheader("Verification Summary")
st.table(
    [
        {"metric": key, "value": round(value, 3) if isinstance(value, float) else value}
        for key, value in summary.items()
    ]
)
