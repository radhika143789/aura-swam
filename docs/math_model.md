# Mathematical Model

## Coordinate System

The simulator uses screen-space coordinates:

```text
x increases right
y increases downward
normal gravity = [0, +g]
anti-gravity = [0, -alpha * g]
```

The default scale is:

```text
g = 9.81 m/s^2 * 50 px/m = 490.5 px/s^2
```

## Payload State

```text
p(t) = [x, y]
v(t) = [vx, vy]
a(t) = [ax, ay]
m = payload mass
```

## Localized Field

```text
c = field center
r = field radius
alpha = anti-gravity strength
```

Membership:

```text
d = ||p - c||
inside_field = d <= r
```

Effective gravity:

```text
if inside_field:
    g_eff = [0, -alpha * g]
else:
    g_eff = [0, +g]
```

## Force Composition

```text
F_gravity = m * g_eff
F_net = F_gravity + F_thrust + F_disturbance
```

Acceleration:

```text
a = F_net / m
```

## Numerical Integration

The MVP uses semi-implicit Euler integration:

```text
v_next = v + a * dt
p_next = p + v_next * dt
```

Semi-implicit Euler is stable enough for a 48-hour visual physics sandbox and is easier to reason about than higher-order solvers during live demo work.

## PID Stabilizer

Error:

```text
e = target_position - payload_position
```

Controller force:

```text
F_thrust = Kp * e + Ki * integral(e) + Kd * derivative(e)
```

Clamp:

```text
||F_thrust|| <= max_thrust
```

## Stability Criteria

The simulator reports `stable` when:

```text
error < 15 px
velocity < 10 px/s
for at least 2 seconds
```

It reports `unstable` when:

```text
error > 250 px
```
