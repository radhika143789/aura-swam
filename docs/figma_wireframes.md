# Figma Wireframe Blueprint

Create one desktop frame named `AI-Stabilized Antigravity Simulator`.

## Layout

```text
+---------------------------------------------------+
| Top Telemetry Banner                              |
+----------------------------------+----------------+
|                                  |                |
| Simulation View                  | Control Panel  |
|                                  |                |
+----------------------------------+----------------+
| Live Physics / Stabilizer Log                     |
+---------------------------------------------------+
```

## Top Telemetry Banner

Use six compact scorecards:

1. Payload Position `(x, y)`
2. Velocity Magnitude
3. Stabilization Error
4. Field Status: `Normal-G` or `Anti-G`
5. Controller Mode: `PID` or `Open Loop`
6. Stability State: `Stable`, `Correcting`, or `Unstable`

## Simulation View

Show:

- Circular anti-gravity field boundary
- Payload marker
- Target hover point
- Gravity vector arrow
- Thrust vector arrow
- Velocity vector arrow
- Optional payload trail

## Control Panel

Controls to mock:

- Start / Pause / Reset
- Stabilizer toggle
- Disturbance toggle
- Anti-gravity strength slider
- Payload mass slider
- PID gain fields: `Kp`, `Ki`, `Kd`

## Log Pane

Use a terminal-style JSON payload:

```json
{
  "time": 12.42,
  "inside_field": true,
  "position": [548.2, 352.8],
  "velocity": [-1.4, 3.1],
  "gravity": [0.0, -613.1],
  "thrust": [2.8, 9.6],
  "error": [1.8, -2.8],
  "stability": "correcting"
}
```

## Visual Direction

Use a dark technical dashboard, high-contrast vectors, compact controls, and clear engineering telemetry. Avoid a marketing landing page; the first screen should feel like an operational simulator.
