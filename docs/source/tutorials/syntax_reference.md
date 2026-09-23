# c4dynamics Syntax Quick Reference

A ground-truth reference for the core, most-used c4dynamics classes and functions, verified
directly against the package source (`c4dynamics/**/*.py`). Use this to answer "how do I..."
and "what's the syntax for..." questions accurately — do not guess parameter names or defaults
beyond what is shown here; for anything not covered, say so rather than inventing syntax.

All examples assume:

```python
import c4dynamics as c4d
```

## State objects (`c4dynamics.states`)

### `state` — the base state object

```python
state(**kwargs)
```

Any keyword arguments become state variables with their given initial values.

```python
s = c4d.state(y=1, vy=0.5)   # two-variable state: (y, vy)
s.store(t=0)                 # store the current state at time t
F = [[1, 1],
     [0, 1]]
s.X += F @ s.X                # propagate the state through a transition matrix
s.store(t=1)
s.X                            # current state vector, numpy array
s.data('y')                    # (times, values) stored history for variable 'y'
s.plot('y')                    # plot the stored history of variable 'y'
```

Key `state` methods/properties:
- `s.X` — get/set the full state vector (`numpy.ndarray`).
- `s.addvars(**kwargs)` — add new state variables after construction.
- `s.store(t=-1)` — append the current state to the stored history at time `t`.
- `s.storeparams(params, t=-1.0)` — store auxiliary (non-state) parameters alongside time.
- `s.data(var=None, scale=1.0)` — retrieve stored history; `var=None` returns the full stored
  state matrix, a variable name returns `(t, values)` for that variable.
- `s.plot(var, scale=1, ax=None, filename=None, darkmode=True, block=False, **kwargs)`.

### `datapoint` — 3D translational point mass (extends `state`)

```python
datapoint(x=0, y=0, z=0, vx=0, vy=0, vz=0)
```

```python
dp = c4d.datapoint(x=0, y=0, z=1000, vx=100, vy=0, vz=0)
dp.mass = 10                     # mass in kg (settable property)
dp.inteqm(forces, dt)            # one RK4 integration step of 3D translational motion
```

- `dp.inteqm(forces, dt)` integrates one step of translational motion given `forces` (3-vector,
  N) and time step `dt` (s); backed by `c4dynamics.eqm.integrate.int3`.

### `rigidbody` — 6-DOF rigid body (extends `datapoint`)

```python
rigidbody(x=0, y=0, z=0, vx=0, vy=0, vz=0, phi=0, theta=0, psi=0, p=0, q=0, r=0)
```

```python
rb = c4d.rigidbody(z=1000, phi=0, theta=0, psi=0)
forces  = [0, 0, -9.8 * rb.mass]   # example: gravity only, [Fx, Fy, Fz]
moments = [0, 0, 0]                # [Mx, My, Mz]
rb.inteqm(forces, moments, dt)     # one RK4 step of full 6-DOF motion; forces, moments, dt are all REQUIRED
rb.BR                            # body-from-reference direction cosine matrix
rb.RB                            # reference-from-body direction cosine matrix
```

- `rb.inteqm(forces, moments, dt)` integrates translational + rotational motion together;
  backed by `c4dynamics.eqm.integrate.int6`. `forces`, `moments`, and `dt` are all required
  positional arguments — there is no no-argument form. Calling `rb.inteqm()` with nothing is
  invalid and will raise a `TypeError`.
- `rb.angles` (returns `[phi, theta, psi]`) and `rb.ang_rates` (returns `[p, q, r]`) are
  **read-only** computed properties — they have no setter. To set initial or new values, either
  pass `phi`/`theta`/`psi`/`p`/`q`/`r` to the constructor, or set those individual attributes
  directly (e.g. `rb.phi = 0.1`), never `rb.angles = [...]` or `rb.ang_rates = [...]` (both raise
  `AttributeError: can't set attribute`). `rb.I` (moments of inertia) is the exception among the
  vector-valued properties — it IS settable as a 3-element list: `rb.I = [Ixx, Iyy, Izz]`.

### `pixelpoint` — image-space bounding-box state (extends `state`)

```python
pixelpoint(x=0, y=0, w=0, h=0)
```

Used to represent an object-detection bounding box (center `x, y`, width `w`, height `h`) as a
state object; see the `yolov3` detector below, which returns a list of `pixelpoint` objects.

## Filters (`c4dynamics.filters`)

### `kalman` — linear Kalman filter

```python
kalman(X: dict, F, H, steadystate=False, G=None, P0=None, Q=None, R=None, P_jitter=None)
```

`X` is a dict of state-variable names to initial values (like `state`'s kwargs, but passed as a
dict here because the other matrix arguments are positional). `F`/`H` are the linear transition
and measurement matrices.

```python
kf = c4d.filters.kalman({'x': 0}, F=[[1]], H=[[1]], P0=0.5**2, Q=0.05, R=200)
kf.predict(u=None, Q=None)
kf.update(z=None, R=None, hx=None, innov=None, gate=None)
kf.store(t=-1)
```

### `ekf` — extended Kalman filter (extends `kalman`)

```python
ekf(X: dict, P0, F=None, H=None, G=None, Q=None, R=None, P_jitter=None)
```

```python
_ekf = c4d.filters.ekf({'x': 0}, P0=0.5**2, F=1, H=1, Q=0.05, R=200)
_ekf.predict(F=None, fx=None, dt=None, u=None, Q=None)   # fx (nonlinear derivative) requires dt
_ekf.update(z=None, H=None, hx=None, innov=None, R=None, gate=None)
```

`ekf(...)` and `kalman(...)` always take `X`, `P0`, and the matrix arguments as **separate**
parameters, exactly as shown above — never as a single bundled config dict, e.g.
`ekf(some_config_dict)` is invalid; there is no such constructor form. If example code (from a
specific use case's own notebook) builds a dict of gains/covariances first for organizational
convenience, that dict still has to be unpacked into `X=`, `P0=`, `Q=`, `R=`, etc. when calling
`ekf(...)` — it is never passed as one positional argument.

- `predict(fx=..., dt=...)` — for nonlinear dynamics, pass the nonlinear derivative `fx` together
  with `dt`; omitting `fx` runs a linear predict with the stored/overridden `F`. A real nonlinear
  `predict` call always supplies `F`, `fx`, AND `dt` together (`F` for the covariance propagation,
  `fx`/`dt` to integrate the actual nonlinear state) — never just `F` alone for a nonlinear system,
  and never omit `dt` when `fx` is given. Example, from the actual Ballistic Coefficient Estimation
  use case (a falling object with drag, state `[z, vz, beta]`):
  ```python
  F = np.array([[0, 1, 0], f2i, [0, 0, 0]]) * dt + np.eye(3)   # discretized Jacobian, computed elsewhere
  fx = [ekf.vz, rhoexp * ekf.vz / 2 - c4d.g_fts2, 0]           # nonlinear derivative
  ekf.predict(F=F, fx=fx, dt=dt)
  ```
  If asked for a nonlinear-`predict` example and a specific use case's real one is available, use
  that real one (or say you don't have the exact derivation) — don't substitute an invented,
  simpler physical model while still citing the real use case as the source.
- `update(hx=..., innov=...)` — for a nonlinear measurement, pass `hx` (h(x)); pass `innov`
  directly when the residual isn't a plain subtraction (e.g. an angle-wrapped measurement).
- What does `gate` do (on both `kalman.update` and `ekf.update`)? It's a chi-squared NIS
  (normalized innovation squared) gating threshold. If the innovation fails that statistical test
  — i.e. the new measurement is statistically too far from the prediction to plausibly be a real
  match — `update` rejects the measurement entirely and returns `None`, leaving the state estimate
  unchanged for that step. Omitting `gate` (the default, `None`) disables this check — every
  measurement is accepted regardless of how large the innovation is.

### `lowpass` — first-order low-pass filter

```python
lowpass(alpha=None, dt=None, tau=None, y0=0)
```

Provide either `alpha` (discrete system) or both `dt` and `tau` (continuous system, converted to
`alpha = dt / tau` internally).

```python
lp = c4d.filters.lowpass(dt=0.01, tau=0.1, y0=0)
y = lp.sample(1.0)   # apply the filter to one new input value, returns the filtered output
```

## Sensors (`c4dynamics.sensors`)

All sensor classes live under the `c4d.sensors` submodule.

### `seeker`

```python
c4d.sensors.seeker(origin: rigidbody = None, isideal=False, **kwargs)
```
`.measure(target: state, t=-1, store=False) -> (azimuth, elevation)`

### `radar`

```python
c4d.sensors.radar(origin=None, isideal=False, **kwargs)
```
`.measure(target: state, t=-1, store=False) -> (range, azimuth, elevation)`

What happens if `measure` is called before the sensor's internal time-constant `dt` has elapsed
since the last measurement (at the given `t`)? Both `seeker` and `radar` return `None` — no
exception is raised, and no stale/old value is returned either. The caller must check for `None`
before using the result.

### `gps`, `imu`, `magnetometer`

```python
c4d.sensors.gps(noise_std=0.5, bias=None, isideal=False)
```
`.measure(x_true)`

```python
c4d.sensors.imu(gyro_std=0.01, acc_std=0.05, gyro_bias=None, ...)
```
`.measure(rb: rigidbody, t=-1, store=False)`

```python
c4d.sensors.magnetometer(noise_std=0.02, hard_iron=None, soft_iron=None, ...)
```
`.measure(x_true)`

### `lineofsight`

A distinct sensor from `seeker`/`radar`: it measures the **line-of-sight angular rate** between
two objects (not azimuth/elevation angles), through a two-stage first-order lag — a tracking-loop
lag (`tau1`) and a signal-processing lag (`tau2`). This is what the Proportional Navigation
Guidance use case uses for its seeker model, not the generic `seeker` class.

```python
c4d.sensors.lineofsight(dt, tau1=0.05, tau2=0.05, isideal=False)
```
`.measure(r, v)` — `r`: line-of-sight (range) vector to the target; `v`: relative velocity vector;
returns the filtered LOS angular rate vector. `.store(t=-1)`.

Is this sensor ideal or does it have imperfections? That is controlled by `isideal`: `isideal=True`
bypasses both lags and returns the true instantaneous LOS rate (a perfect seeker); `isideal=False`
(the default) applies the `tau1`/`tau2` lag chain, i.e. an imperfect seeker. In the Proportional
Navigation Guidance use case, the seeker is instantiated as
`c4d.sensors.lineofsight(dt, tau1=0.01, tau2=0.01)` — `isideal` is left at its default `False`, so
that seeker is NOT ideal; it has both lags active.

If a question is about what sensor a specific use case actually uses, check that use case's own
content rather than assuming the sensor with the most generic-sounding name (`seeker`) is the one
in play — `dof6sim` (Proportional Navigation Guidance) is a concrete example where it isn't.

## Object detection (`c4dynamics.detectors`)

### `yolov3`

```python
yolov3(weights_path=None)
```

```python
yolo = c4d.detectors.yolov3()
yolo.confidence_th = 0.5          # settable property
yolo.nms_th = 0.4                 # settable property
detections = yolo.detect(frame)   # returns list[pixelpoint], one per detected object
```

## Rotations (`c4d.rotmat`)

```python
c4d.rotmat.rotx(phi)                          # elementary rotation about x
c4d.rotmat.roty(theta)                        # elementary rotation about y
c4d.rotmat.rotz(psi)                          # elementary rotation about z
c4d.rotmat.dcm321(phi=0.0, theta=0.0, psi=0.0)   # 3-2-1 Euler-angle direction cosine matrix
c4d.rotmat.dcm321euler(dcm)                      # recover 3-2-1 Euler angles from a DCM
```

## Equations of motion (`c4d.eqm`)

```python
c4d.eqm.eqm3(dp: datapoint, F) -> np.ndarray        # 3-DOF translational derivatives
c4d.eqm.eqm6(rb: rigidbody, F, M) -> np.ndarray     # 6-DOF translational + rotational derivatives

c4d.eqm.int3(dp: datapoint, forces, dt, derivs_out=False)        # one RK4 step, 3-DOF
c4d.eqm.int6(rb: rigidbody, forces, moments, dt, derivs_out=False)  # one RK4 step, 6-DOF
```

These are the lower-level functions behind `datapoint.inteqm` / `rigidbody.inteqm` — most use
cases call `.inteqm(...)` on the state object directly rather than these functions.

## Utilities (`c4dynamics.utils`)

These are all imported directly into the top-level `c4d` namespace:

```python
c4d.cprint(txt="", color="white", end="\n")   # colored console print
c4d.tic()                                     # start a stopwatch
c4d.toc(show=True, minutes=False)             # stop and report elapsed time since tic()
c4d.plotdefaults(ax, title, xlabel="", ylabel="", fontsize=8, ilines=None)  # apply house plot style
c4d.gif(dirname, gif_name, duration=None)     # build an animated GIF from a directory of frames
```
