# 3-Minute Demo Video Script

## 0:00 - 0:30 | Hook and Problem

Visual: Open the Streamlit dashboard and show the live telemetry cards.

Script:

"Localized gravity anomalies are hard to simulate because the control problem changes instantly when the payload crosses a field boundary. A normal gravity vector `[0, +g]` becomes an inverted vector `[0, -alpha g]`, so a payload that was falling begins accelerating upward. Without compensation, the hover state fails immediately."

## 0:30 - 1:30 | Math and Architecture

Visual: Show `docs/math_model.md`, then return to the dashboard control law.

Script:

"Our MVP treats gravity as a dynamic local vector, not a global constant. The physics engine computes local acceleration from net force using `a = F_net / m`, and the anti-gravity field swaps the sign of `g` inside a circular boundary. The stabilizer combines gravity feed-forward with PID correction: `F_thrust = -m g_local + F_pid`. That feed-forward term cancels the inverted field, and PID removes residual error. The simulator is organized around a centralized simulation state so physics, control, and telemetry stay synchronized."

## 1:30 - 2:30 | Live MVP Demonstration

Visual: In Streamlit, toggle stabilizer off, then on. Enable fluctuating field and dynamic payload mass.

Script:

"Here is the uncontrolled case. The payload cannot hold the target because the field is constantly pushing it away from equilibrium. Now we enable stabilization. The controller reads live position, velocity, local gravity, and thrust, then applies corrective force every timestep. Even when field strength fluctuates and the mass changes mid-flight, the payload returns to the target hover state. Our QA benchmark shows settling around 1.7 seconds in the baseline and sub-pixel final error in stabilized scenarios."

## 2:30 - 3:00 | Metrics, Impact, and Close

Visual: Show the benchmark terminal table or README QA section.

Script:

"The final benchmark suite measures mean error, RMSE, final error, settling time, field containment, velocity, thrust saturation, and timestep stability. This proves the simulator is not only visual, but empirically validated. The project is open source, deployable through Streamlit Community Cloud, and ready for extensions like neural policy imitation, orbital dynamics, or more complex anomaly fields."
