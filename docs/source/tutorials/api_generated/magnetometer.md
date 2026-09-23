# magnetometer

Magnetometer — 3-axis geomagnetic field sensor.

The `magnetometer` class models a strapdown 3-axis magnetometer.
It measures the local geomagnetic field vector expressed in the vehicle
**body frame**: a fixed reference field in the navigation frame, rotated
into the body frame by the true attitude, then corrupted by soft-iron and
hard-iron distortion and sample-to-sample white Gaussian noise.

Parameters
==========
noise_std : float or array_like, optional
    Standard deviation of the field measurement noise, per body axis, in
    the same units as ``field_intensity`` (dimensionless when the field
    is left normalized).  A scalar is broadcast to all three axes.
    Defaults to ``0.02``.
hard_iron : array_like, optional
    Constant additive bias ``[bx, by, bz]`` (hard-iron offset), in the
    same units as ``field_intensity``.  Defaults to ``[0, 0, 0]``.
soft_iron : array_like, optional
    ``3 x 3`` soft-iron distortion matrix applied to the body-frame field
    before the hard-iron offset and the noise.  Defaults to the identity.
field_intensity : float, optional
    Total intensity $F$ of the reference geomagnetic field.
    Defaults to ``1.0`` (the field is returned normalized).  Set a real
    value (e.g. ``50e-6`` T or ``50`` for µT) to work in physical units —
    ``noise_std`` and ``hard_iron`` then carry the same unit.
inclination : float, optional
    Inclination (dip) angle $I$ of the reference field, [rad],
    positive pointing down.  Defaults to ``np.pi / 3`` ($60^\circ$,
    a typical mid-latitude value).
declination : float, optional
    Declination angle $D$ of the reference field, [rad], positive
    east of north.  Defaults to ``0``.
isideal : bool, optional
    If ``True``, overrides ``noise_std`` / ``hard_iron`` / ``soft_iron``
    to produce an ideal (noise-free, distortion-free) magnetometer.  The
    reference field itself is unaffected.  Defaults to ``False``.

See Also
========
.ekf
.gps
.imu

**Functionality**

The reference field is built from its total intensity, inclination and
declination and held fixed in the navigation frame associated with the
state's 3-2-1 Euler angles (``x`` forward/north, ``y`` right/east, ``z``
down):

$$
m_{ref} = F \cdot
[\cos I \cos D,\ \cos I \sin D,\ \sin I]^T
$$
At each sample, given the 12-state vector

$$
X = [x, y, z, v_x, v_y, v_z, \varphi, \theta, \psi, p, q, r]^T
$$
the reference field is rotated into the body frame by the true attitude
and distorted:

$$
m_{body} = [BI](\varphi, \theta, \psi) \cdot m_{ref}
z = S_i \cdot m_{body} + b_i + n
$$
where $[BI]$ is the body-from-inertial 3-2-1 DCM
(`dcm321`), $S_i$ is the
soft-iron matrix, $b_i$ is the hard-iron offset, and $n$ is a
zero-mean Gaussian vector with per-axis standard deviation ``noise_std``.

``measure`` returns the full 3-axis body-frame field vector.  A consumer
that needs a heading derives it from the horizontal components after
de-rotating roll and pitch (tilt compensation); a filter that consumes
the vector directly (see `ekf`) needs no yaw-wrapping, because the
measurement is linear in the rotated field rather than in the angle
itself.  In a typical setup the magnetometer is sampled at a lower rate
than the IMU, e.g. $50\,Hz$.

**Errors Model**

The magnetometer measurement is subject to three error sources:

- ``Hard iron``:
  a constant additive offset ``[bx, by, bz]`` (magnetized material fixed
  to the body).  Set through the ``hard_iron`` parameter and unchanged
  between measurements.  Defaults to ``[0, 0, 0]``.
- ``Soft iron``:
  a constant ``3 x 3`` linear distortion $S_i$ (nearby ferrous
  material that reshapes the field).  Set through the ``soft_iron``
  parameter.  Defaults to the identity.
- ``Noise``:
  a zero-mean Gaussian sample, drawn independently per axis at every call
  to `measure`, with standard deviation ``noise_std``.

The errors model can be disabled by passing ``isideal = True`` at
construction, which forces ``noise_std = 0``, ``hard_iron = [0, 0, 0]``
and ``soft_iron = I`` regardless of the arguments.  Unlike the
`seeker` model, the magnetometer does not generate a random bias
during construction; the supplied distortion is deterministic for a given
instance.

**Construction**

A magnetometer instance is created by making a direct call to the
constructor:

    >>> mag_sensor = c4d.sensors.magnetometer()

The noise, the hard-iron / soft-iron distortion and the reference-field
geometry can all be specified when creating the sensor.

Examples
========

Import required packages:

```python
>>> import c4dynamics as c4d
>>> import numpy as np
```
**True attitude**

For the examples below, build a 12-state vector and set its attitude
entries (indices 6, 7, 8 = roll, pitch, yaw):

```python
>>> x_true = np.zeros(12)
>>> x_true[8] = 0.5   # true heading [rad]
```
**Ideal magnetometer**

An ideal magnetometer can be created by muting the errors model.  Level
and heading north, it reads the reference field directly — horizontal
component forward, vertical component (the dip) down:

```python
>>> mag_ideal = c4d.sensors.magnetometer(isideal=True)
>>> mag_ideal.measure(np.zeros(12))   # doctest: +NUMPY_FORMAT
[0.5  0.  0.866]
```
Rotating to a heading of ``0.5`` rad swings the horizontal field into the
body ``y`` axis while its magnitude and the vertical component are
preserved:

```python
>>> mag_ideal.measure(x_true)   # doctest: +NUMPY_FORMAT
[0.439  -0.24  0.866]
```
**Non-ideal magnetometer**

A non-ideal magnetometer adds white measurement noise (and, optionally,
hard-iron / soft-iron distortion).  Set the random seed to make the
example reproducible:

```python
>>> np.random.seed(42)
>>> mag_sensor = c4d.sensors.magnetometer(noise_std=0.02)
>>> mag_sensor.measure(x_true)   # doctest: +NUMPY_FORMAT
[0.449  -0.242  0.879]
```
**Hard iron**

The hard-iron offset is constant across all measurements.  A magnetometer
with a ``[0.1, 0, 0]`` offset can be created as follows:

```python
>>> mag_hi = c4d.sensors.magnetometer(noise_std=0, hard_iron=[0.1, 0, 0])
>>> mag_ref = c4d.sensors.magnetometer(isideal=True)
>>> mag_hi.measure(x_true) - mag_ref.measure(x_true)   # doctest: +NUMPY_FORMAT
[0.1  0.  0.]
```
The difference between the measurement and the ideal field is the
specified offset.

**Soft iron**

The soft-iron matrix scales / mixes the body-frame field.  A diagonal
``soft_iron`` with a ``1.2`` gain on the body ``x`` axis:

```python
>>> mag_si = c4d.sensors.magnetometer(
...     noise_std=0, soft_iron=np.diag([1.2, 1.0, 1.0]))
>>> mag_si.measure(np.zeros(12))   # doctest: +NUMPY_FORMAT
[0.6  0.  0.866]
```
**Measurement noise**

With no distortion, repeated measurements of the same state demonstrate
the random per-axis noise generated at every call to `measure`:

```python
>>> np.random.seed(1)
>>> mag_noise = c4d.sensors.magnetometer(noise_std=0.02)
>>> for _ in range(3): # doctest: +IGNORE_OUTPUT
...     print(mag_noise.measure(x_true))
[0.471 -0.252  0.855]
[0.417 -0.222  0.820]
[0.474 -0.255  0.872]
```
**Demo**

The built-in `demo` method provides a compact demonstration of the
magnetometer errors model and plots the true and measured body-frame
field components through an attitude sweep:

```python
>>> fig = c4d.sensors.magnetometer.demo(show=True)
```

The same demonstration can be run without displaying the figure by using
``show=False``.

### `demo`

```python
demo(duration=20.0, dt=0.02, seed=1, show=True)
```

Demonstrate 3-axis magnetometer measurements.

Drives the sensor through a smooth roll / pitch / yaw sweep and
compares the true body-frame geomagnetic field components with the
noisy magnetometer measurements.

### Parameters
duration : float
    Simulation duration [s].
dt : float
    Sampling interval [s].
seed : int
    Random seed for reproducibility.
show : bool
    If True, display the figure.

### Returns
matplotlib.figure.Figure
    Figure containing the true and measured mx, my, mz components.

### `measure`

```python
measure(self, x_true)
```

Measure the body-frame geomagnetic field.

The method rotates the reference field ``mref`` into the body frame
using the attitude entries of ``x_true`` (indices 6, 7, 8), then
applies the soft-iron matrix, the hard-iron offset and a zero-mean
Gaussian noise sample per axis.

### Parameters
x_true : array_like
    True state vector; only the attitude entries
    ``x_true[6:9]`` (roll, pitch, yaw) are used, [rad].

### Returns
numpy.ndarray
    Measured body-frame field ``[mx, my, mz]``, in the units of
    ``field_intensity``.

**Errors Model**

$$
z = S_i \cdot [BI](\varphi, \theta, \psi) \cdot m_{ref}
+ b_i + std \cdot N(0, I_3)
$$
The soft-iron matrix $S_i$ and hard-iron offset $b_i$ are
constant for the magnetometer instance, while the noise is
regenerated at every call.

### Examples
```python
>>> import c4dynamics as c4d
>>> import numpy as np
>>> np.random.seed(42)
>>> mag_sensor = c4d.sensors.magnetometer(isideal=True)
>>> x = np.zeros(12)
>>> x[8] = 0.5
>>> mag_sensor.measure(x)   # doctest: +NUMPY_FORMAT
```
    [0.439  -0.24  0.866]

