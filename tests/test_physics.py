import numpy as np

from src.physics.engine import PhysicsEngine
from src.physics.field import AntiGravityField
from src.utils import config
from src.utils.state import SimulationState


def test_antigravity_field_inverts_gravity_inside_radius():
    field = AntiGravityField.create((0.0, 0.0), 10.0, 1.25, 9.81)

    inside = field.gravity_vector(np.array([0.0, 0.0]))
    outside = field.gravity_vector(np.array([20.0, 0.0]))

    assert inside[1] == -1.25 * 9.81
    assert outside[1] == 9.81


def test_payload_accelerates_upward_inside_antigravity_zone_without_stabilizer():
    state = SimulationState.create_default()
    state.payload.position = state.field_model.center.copy()
    state.payload.velocity *= 0.0
    state.thrust_force *= 0.0

    PhysicsEngine().step(state, config.DT)

    assert state.payload.acceleration[1] < 0.0
    assert state.payload.velocity[1] < 0.0
