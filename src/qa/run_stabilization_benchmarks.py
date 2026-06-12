from __future__ import annotations

import argparse
import math
from collections import Counter
from dataclasses import replace
from statistics import mean

import numpy as np

from src.control.pid_controller import PIDController
from src.physics.engine import PhysicsEngine
from src.utils import config
from src.utils.state import SimulationState


class BenchmarkFailure(RuntimeError):
    pass


def _norm(vector: np.ndarray) -> float:
    return float(np.linalg.norm(vector))


def _rmse(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values])) if values else 0.0


def _settling_time(samples: list[dict], threshold_px: float = 25.0, velocity_limit: float = 20.0) -> float | None:
    """Return first time after which error and velocity remain bounded."""

    for index, sample in enumerate(samples):
        tail = samples[index:]
        if all(item["error"] <= threshold_px and item["velocity"] <= velocity_limit for item in tail):
            return float(sample["time"])
    return None


def _format_float(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


def _run_case(
    *,
    name: str,
    duration_seconds: float,
    dt: float,
    stabilizer_enabled: bool = True,
    disturbance_enabled: bool = False,
    target_position: tuple[float, float] = config.TARGET_POSITION,
    max_thrust: float = config.MAX_THRUST,
    alpha_mode: str = "constant",
    mass_mode: str = "constant",
) -> dict:
    state = SimulationState.create_default()
    state.stabilizer_enabled = stabilizer_enabled
    state.disturbance_enabled = disturbance_enabled
    state.target_position = np.array(target_position, dtype=float)

    engine = PhysicsEngine()
    controller = PIDController(
        kp=config.PID_KP,
        ki=config.PID_KI,
        kd=config.PID_KD,
        max_force=max_thrust,
    )

    samples: list[dict] = []
    mass_events: list[dict] = []
    saturation_count = 0
    nan_detected = False
    steps = int(duration_seconds / dt)

    for step in range(steps):
        time_seconds = step * dt

        if alpha_mode == "fluctuating":
            alpha = 1.25 + 0.45 * math.sin(time_seconds * 3.1) + 0.20 * math.sin(time_seconds * 9.7)
            alpha = float(np.clip(alpha, 0.75, 1.75))
            state.field_model = replace(state.field_model, alpha=alpha)

        if mass_mode == "dynamic":
            previous_mass = state.payload.mass
            if time_seconds >= 20.0:
                state.payload.mass = 1.0
            elif time_seconds >= 10.0:
                state.payload.mass = 4.0
            else:
                state.payload.mass = config.PAYLOAD_MASS
            if state.payload.mass != previous_mass:
                mass_events.append(
                    {
                        "time": time_seconds,
                        "from": previous_mass,
                        "to": state.payload.mass,
                        "error_before": state.error_magnitude,
                    }
                )

        if stabilizer_enabled:
            state.thrust_force = controller.compute(state.target_position, state.payload.position, dt)
        else:
            state.thrust_force *= 0.0

        thrust_norm = _norm(state.thrust_force)
        if thrust_norm >= max_thrust * 0.999:
            saturation_count += 1

        engine.step(state, dt)

        values = np.concatenate(
            [
                state.payload.position,
                state.payload.velocity,
                state.payload.acceleration,
                state.thrust_force,
            ]
        )
        if not np.all(np.isfinite(values)):
            nan_detected = True

        samples.append(
            {
                "time": state.time_seconds,
                "error": state.error_magnitude,
                "velocity": state.velocity_magnitude,
                "thrust": thrust_norm,
                "inside_field": state.inside_field,
                "stability": state.stability,
                "alpha": state.field_model.alpha,
                "mass": state.payload.mass,
                "position": state.payload.position.copy(),
            }
        )

    errors = [sample["error"] for sample in samples]
    velocities = [sample["velocity"] for sample in samples]
    thrusts = [sample["thrust"] for sample in samples]
    inside_flags = [sample["inside_field"] for sample in samples]
    alpha_values = [sample["alpha"] for sample in samples]
    stability_counts = Counter(sample["stability"] for sample in samples)
    settling_time = _settling_time(samples)

    metrics = {
        "scenario_name": name,
        "duration_seconds": duration_seconds,
        "mean_error_px": mean(errors),
        "max_error_px": max(errors),
        "rmse_error_px": _rmse(errors),
        "final_error_px": errors[-1],
        "settling_time_seconds": settling_time,
        "stable_time_ratio": stability_counts.get("stable", 0) / len(samples),
        "field_inside_ratio": sum(inside_flags) / len(samples),
        "mean_velocity_px_s": mean(velocities),
        "max_velocity_px_s": max(velocities),
        "mean_thrust": mean(thrusts),
        "max_thrust": max(thrusts),
        "thrust_saturation_ratio": saturation_count / len(samples),
        "stability_state_counts": dict(stability_counts),
        "alpha_min": min(alpha_values),
        "alpha_max": max(alpha_values),
        "mass_change_events": mass_events,
        "nan_detected": nan_detected,
        "final_position": samples[-1]["position"].tolist(),
        "dt": dt,
    }
    metrics["pass_or_fail"] = _evaluate_case(metrics, name)
    return metrics


def _evaluate_case(metrics: dict, name: str) -> str:
    if metrics["nan_detected"]:
        return "FAIL"

    checks = {
        "baseline_pid": metrics["mean_error_px"] <= 45.0 and metrics["final_error_px"] <= 35.0,
        "baseline_uncontrolled": metrics["max_error_px"] > 80.0,
        "field_fluctuation": metrics["mean_error_px"] <= 65.0 and metrics["max_error_px"] <= 190.0,
        "dynamic_mass": metrics["final_error_px"] <= 45.0 and metrics["max_error_px"] <= 220.0,
        "thrust_saturation": metrics["thrust_saturation_ratio"] > 0.0 and metrics["max_error_px"] <= 260.0,
        "target_center": metrics["final_error_px"] <= 35.0,
        "target_above": metrics["final_error_px"] <= 45.0,
        "target_right": metrics["final_error_px"] <= 45.0,
        "target_below": metrics["final_error_px"] <= 60.0,
        "dt_30hz": metrics["final_error_px"] <= 55.0,
        "dt_60hz": metrics["final_error_px"] <= 45.0,
        "dt_120hz": metrics["final_error_px"] <= 45.0,
    }
    return "PASS" if checks.get(name, False) else "FAIL"


def _print_table(results: list[dict]) -> None:
    columns = [
        "scenario",
        "mean_err",
        "max_err",
        "rmse",
        "final_err",
        "settle_s",
        "stable_ratio",
        "inside_ratio",
        "mean_vel",
        "max_vel",
        "mean_thr",
        "max_thr",
        "sat_ratio",
        "result",
    ]
    widths = [22, 10, 10, 10, 10, 10, 12, 12, 10, 10, 10, 10, 10, 8]
    header = " ".join(column.ljust(width) for column, width in zip(columns, widths))
    print(header)
    print("-" * len(header))

    for item in results:
        row = [
            item["scenario_name"],
            _format_float(item["mean_error_px"]),
            _format_float(item["max_error_px"]),
            _format_float(item["rmse_error_px"]),
            _format_float(item["final_error_px"]),
            _format_float(item["settling_time_seconds"]),
            _format_float(item["stable_time_ratio"]),
            _format_float(item["field_inside_ratio"]),
            _format_float(item["mean_velocity_px_s"]),
            _format_float(item["max_velocity_px_s"]),
            _format_float(item["mean_thrust"]),
            _format_float(item["max_thrust"]),
            _format_float(item["thrust_saturation_ratio"]),
            item["pass_or_fail"],
        ]
        print(" ".join(value.ljust(width) for value, width in zip(row, widths)))


def _print_details(results: list[dict]) -> None:
    print("\nDetailed edge-case telemetry")
    print("-" * 30)
    for item in results:
        print(f"{item['scenario_name']}:")
        print(f"  alpha_min={item['alpha_min']:.3f}, alpha_max={item['alpha_max']:.3f}, dt={item['dt']:.5f}")
        print(f"  final_position={[round(value, 3) for value in item['final_position']]}")
        print(f"  stability_state_counts={item['stability_state_counts']}")
        if item["mass_change_events"]:
            print(f"  mass_change_events={item['mass_change_events']}")


def run_suite() -> list[dict]:
    target = config.TARGET_POSITION
    cases = [
        dict(name="baseline_pid", duration_seconds=30.0, dt=config.DT),
        dict(name="baseline_uncontrolled", duration_seconds=30.0, dt=config.DT, stabilizer_enabled=False),
        dict(name="field_fluctuation", duration_seconds=30.0, dt=config.DT, alpha_mode="fluctuating"),
        dict(name="dynamic_mass", duration_seconds=30.0, dt=config.DT, mass_mode="dynamic"),
        dict(name="thrust_saturation", duration_seconds=30.0, dt=config.DT, max_thrust=config.MAX_THRUST * 0.5),
        dict(name="target_center", duration_seconds=20.0, dt=config.DT, target_position=target),
        dict(name="target_above", duration_seconds=20.0, dt=config.DT, target_position=(target[0], target[1] - 80.0)),
        dict(name="target_right", duration_seconds=20.0, dt=config.DT, target_position=(target[0] + 80.0, target[1])),
        dict(name="target_below", duration_seconds=20.0, dt=config.DT, target_position=(target[0], target[1] + 100.0)),
        dict(name="dt_30hz", duration_seconds=20.0, dt=1.0 / 30.0),
        dict(name="dt_60hz", duration_seconds=20.0, dt=1.0 / 60.0),
        dict(name="dt_120hz", duration_seconds=20.0, dt=1.0 / 120.0),
    ]
    return [_run_case(**case) for case in cases]


def main() -> None:
    parser = argparse.ArgumentParser(description="Run headless stabilization QA benchmarks.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero if any scenario fails.")
    parser.add_argument("--details", action="store_true", help="Print detailed scenario telemetry.")
    args = parser.parse_args()

    results = run_suite()
    _print_table(results)
    if args.details:
        _print_details(results)

    failed = [item["scenario_name"] for item in results if item["pass_or_fail"] != "PASS"]
    if failed and args.strict:
        raise BenchmarkFailure(f"Failed benchmark scenarios: {', '.join(failed)}")


if __name__ == "__main__":
    main()
