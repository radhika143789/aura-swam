import numpy as np

from src.control.pid_controller import PIDController


def test_pid_controller_clamps_force_magnitude():
    controller = PIDController(kp=100.0, ki=0.0, kd=0.0, max_force=50.0)

    force = controller.compute(
        target=np.array([1000.0, 0.0]),
        position=np.array([0.0, 0.0]),
        dt=0.016,
    )

    assert np.linalg.norm(force) <= 50.000001


def test_pid_controller_pushes_toward_target():
    controller = PIDController(kp=1.0, ki=0.0, kd=0.0, max_force=1000.0)

    force = controller.compute(
        target=np.array([10.0, -5.0]),
        position=np.array([0.0, 0.0]),
        dt=0.1,
    )

    assert force[0] > 0.0
    assert force[1] < 0.0


def test_pid_controller_applies_feed_forward_compensation():
    controller = PIDController(kp=1.0, ki=0.0, kd=0.0, max_force=1000.0)
    feed_forward = np.array([0.0, 42.0])

    force = controller.compute(
        target=np.array([0.0, 0.0]),
        position=np.array([0.0, 0.0]),
        dt=0.1,
        feed_forward=feed_forward,
    )

    assert np.allclose(force, feed_forward)
