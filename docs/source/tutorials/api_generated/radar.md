# radar

Range-direction detector.

`radar` is a subclass of `seeker`
and utilizes its functionality and errors model for angular measurements.
This documentation supplaments the information concerning range measurements.
Refer to `seeker` for the full documentation.

The `radar` class models sensors that
measure both the range and the direction to a target.
The direction is measured in terms of azimuth and elevation.
Sensors that provide precise range measurements
typically use electro-magnetical technology,
though other technologies may also be employed.

As a subclass of `seeker`, the `radar`
can operate in one of two modes: ideal mode,
providing precise range and direction measurements,
or non-ideal mode,
where measurements may be affected by errors such as
`scale factor`, `bias`, and `noise`,
according to the errors model.
A random variable generation mechanism allows
for Monte Carlo simulations.

Parameters
==========

origin : `rigidbody`, optional
    A `rigidbody` object whose state vector `X`
    determines the radar's initial position and attitude.
    Defaults: a `rigidbody` object with zeros vector, `X = numpy.zeros(12)`.
isideal : bool, optional
    A flag indicating whether the errors model is off.
    Defaults False.

Keyword Arguments
=================
rng_noise_std : float
    A standard deviation of the radar range. Default value for
    non-ideal radar: `rng_noise_std = 1m`.
bias_std : float
    The standard deviation of the bias error, [radians]. Defaults $0.3°$.
scale_factor_std : float
    The standard deviation of the scale factor error, [dimensionless].
    Defaults $0.07 (= 7\%)$.
noise_std : float
    The standard deviation of the radar angular noise, [radians].
    Default value for non-ideal radar: $0.8°$.
dt : float
    The time-constant of the operational rate of the radar
    (below which the radar measures return None), [seconds]. Default value: $dt = -1sec$
    (no limit between calls to `measure`).

* Note the default values for angular parameters, `bias_std`, `scale_factor_std`,
  and `noise_std`, differ from those in a `seeker` object.

See Also
========
.filters
.eqm
.seeker

**Functionality**

At each sample the seeker returns measures based on the true geometry
with the target.

Let the relative coordinates in an arbitrary frame of reference:

$$
dx = target.x - seeker.x
dy = target.y - seeker.y
dz = target.z - seeker.z
$$
The relative coordinates in the seeker body frame are given by:

$$
x_b = [BR] \cdot [dx, dy, dz]^T
$$
where $[BR]$ is a
Body from Reference DCM (Direction Cosine Matrix)
formed by the seeker three Euler angles. See the `rigidbody` section below.

The azimuth and elevation measures are then the spatial angles:

$$
az = tan^{-1}{x_b[1] \over x_b[0]}
el = tan^{-1}{x_b[2] \over \sqrt{x_b[0]^2 + x_b[1]^2}}
$$
Where:

- $az$ is the azimuth angle
- $el$ is the elevation angle
- $x_b$ is the target-radar position vector in radar body frame

For a `radar` object, the range is defined as:

$$
range = \sqrt{x_b^2 + y_b^2 + z_b^2}
$$
Where:

- $range$ is the target-radar distance
- $x_b$ is the target-radar position vector in radar body frame

  Fig-1: Range and angles definition

**Errors Model**

The azimuth and elevation angles are subject to errors: scale factor, bias, and noise,
as detailed in `seeker`.
A `radar` instance has in addition range noise:

- ``Range Noise``:
  represents random variations or fluctuations in the measurements
  that are not systematic.
  The noise at each sample (`measure`)
  is a normally distributed variable
  with `mean = 0` and `std = rng_noise_std`, where `rng_noise_std`
  is a `radar` parameter with default value of `1m`.

Angular errors:

- ``Bias``:
  represents a constant offset or deviation from the
  true value in the seeker's measurements.
  It is a systematic error that consistently affects the measured values.
  The bias of a `seeker` instance is a normally distributed variable with `mean = 0`
  and `std = bias_std`, where `bias_std` is a parameter with default value of `0.3°`.
- ``Scale Factor``:
  a multiplier applied to the true value of a measurement.
  It represents a scaling error in the measurements made by the seeker.
  The scale factor of a `seeker` instance is
  a normally distributed variable
  with `mean = 0` and `std = scale_factor_std`,
  , where `scale_factor_std` is a parameter with default value of `0.07`.
- ``Noise``:
  represents random variations or fluctuations in the measurements
  that are not systematic.
  The noise at each seeker sample (`measure`)
  is a normally distributed variable
  with `mean = 0` and `std = noise_std`, where `noise_std`
  is a parameter with default value of `0.8°`.

The errors model generates random variables for each radar instance,
allowing for the simulation of different scenarios or variations in the radar behavior
in a technique known as Monte Carlo.
Monte Carlo simulations leverage this randomness to statistically analyze
the impact of these biases and scale factors over a large number of iterations,
providing insights into potential outcomes and system reliability.

**Radar vs Seeker**

The following table
lists the main differences between
`seeker` and `radar`
in terms of measurements and
default error parameters:

.. list-table::
  :widths: 22 13 13 13 13 13 13
  :header-rows: 1

  * -
    - Angles
    - Range
    - $σ_{Bias}$
    - $σ_{Scale Factor}$
    - $σ_{Angular Noise}$
    - $σ_{Range Noise}$

  * - Seeker
    - ✔️
    - ❌
    - $0.1°$
    - $5%$
    - $0.4°$
    - $--$

  * - Radar
    - ✔️
    - ✔️
    - $0.3°$
    - $7%$
    - $0.8°$
    - $1m$

**rigidbody**

The radar class is also a subclass of
`rigidbody`, i.e.
it suggests attributes of position and attitude and the manipulation of them.

As a fundamental propety, the
rigidbody's state vector
`X`
sets the spatial coordinates of the radar:

$$
X = [x, y, z, v_x, v_y, v_z, {\varphi}, {\theta}, {\psi}, p, q, r]^T
$$
The first six coordinates determine the translational position and velocity of the radar
while the last six determine its angular attitude in terms of Euler angles and
the body rates.

Passing a rigidbody parameter as an `origin` sets
the initial conditions of the radar.

**Construction**

A radar instance is created by making a direct call
to the radar constructor:

```python
>>> rdr = c4d.sensors.radar()
```
Initialization of the instance does not require any
mandatory arguments, but the radar parameters can be
determined using the \**kwargs argument as detailed above.

Examples
========

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
**Target**

For the examples below let's generate the trajectory of a target with constant velocity:

```python
>>> tgt = c4d.datapoint(x = 1000, y = 0, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
>>> for t in np.arange(0, 60, 0.01):
...   tgt.inteqm(np.zeros(3), .01) # doctest: +IGNORE_OUTPUT
...   tgt.store(t)
```
The method `inteqm`
of the
`datapoint` class
integrates the 3 degrees of freedom equations of motion with respect to
the input force vector (`np.zeros(3)` here).

Since the call to `measure` requires a target as a `datapoint` object
we utilize a custom `create` function that returns a new `datapoint` object for
a given `X` state vector in time.

- :code:`c4d.kmh2ms` converts kilometers per hour to meters per second.
- :code:`c4d.r2d` converts radians to degrees.
- :code:`c4d.d2r` converts degrees to radians.

**Origin**

Let's also introduce a pedestal as an origin for the radar.
The pedestal is a `rigidbody` object with position and attitude:

```python
>>> pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
```
**Ideal Radar**

Measure the target position with an ideal radar:

```python
>>> rdr_ideal = c4d.sensors.radar(origin = pedestal, isideal = True)
>>> for x in tgt.data():
...   rdr_ideal.measure(c4d.create(x[1:]), t = x[0], store = True)  # doctest: +IGNORE_OUTPUT
```
Comparing the radar measurements with the true target angles requires
converting the relative position to the radar body frame:

```python
>>> dx =  tgt.data('x')[1] - rdr_ideal.x
>>> dy =  tgt.data('y')[1] - rdr_ideal.y
>>> dz =  tgt.data('z')[1] - rdr_ideal.z
>>> Xb = np.array([rdr_ideal.BR @ [X[1] - rdr_ideal.x,
...     X[2] - rdr_ideal.y, X[3] - rdr_ideal.z]
...     for X in tgt.data()])
```
where `rdr_ideal.BR` is a
Body from Reference DCM (Direction Cosine Matrix)
formed by the radar three Euler angles

Now `az_true` and `el_true` are the true target angles with respect to the radar, and
`rng_true` is the true range (`atan2d` is an aliasing of `numpy's arctan2`
with a modification returning the angles in degrees):

```python
>>> az_true = c4d.atan2d(Xb[:, 1], Xb[:, 0])
>>> el_true = c4d.atan2d(Xb[:, 2], c4d.sqrt(Xb[:, 0]**2 + Xb[:, 1]**2))
>>> # plot results
>>> fig, axs = plt.subplots(2, 1)  # doctest: +IGNORE_OUTPUT
>>> # range
>>> axs[0].plot(tgt.data('t'), c4d.norm(Xb, axis = 1),
...     label = 'target'
... )  # doctest: +IGNORE_OUTPUT
>>> axs[0].plot(*rdr_ideal.data('range'), label = 'radar')  # doctest: +IGNORE_OUTPUT
>>> # angles
>>> axs[1].plot(tgt.data('t'), c4d.atan2d(Xb[:, 1], Xb[:, 0]),
...     label = 'target azimuth'
... )  # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr_ideal.data('az', scale = c4d.r2d),
...     label = 'radar azimuth'
... )  # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(tgt.data('t'), c4d.atan2d(Xb[:, 2],
...     c4d.sqrt(Xb[:, 0]**2 + Xb[:, 1]**2)),
...     label = 'target elevation'
... )  # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr_ideal.data('el', scale = c4d.r2d),
...     label = 'radar elevation'
... )  # doctest: +IGNORE_OUTPUT
```

**Non-ideal Radar**

Measure the target position with a *non-ideal* radar.
The radar's errors model introduces bias, scale factor, and
noise that corrupt the measurements:

To reproduce the result, let's set the random generator seed (61 is arbitrary):

```python
>>> np.random.seed(61)
```

```python
>>> rdr = c4d.sensors.radar(origin = pedestal)
>>> for x in tgt.data():
...   rdr.measure(c4d.create(x[1:]), t = x[0], store = True)  # doctest: +IGNORE_OUTPUT
```
Results with respect to an ideal radar:

```python
>>> fig, axs = plt.subplots(2, 1)
>>> # range
>>> axs[0].plot(*rdr_ideal.data('range'), label = 'target') # doctest: +IGNORE_OUTPUT
>>> axs[0].plot(*rdr.data('range'), label = 'radar') # doctest: +IGNORE_OUTPUT
>>> # angles
>>> axs[1].plot(*rdr_ideal.data('az', scale = c4d.r2d),
...     label = 'target azimuth'
... ) # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr.data('az', scale = c4d.r2d),
...     label = 'radar azimuth'
... ) # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr_ideal.data('el', scale = c4d.r2d),
...     label = 'target elevation'
... ) # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr.data('el', scale = c4d.r2d),
...     label = 'radar elevation'
... ) # doctest: +IGNORE_OUTPUT
```
`target` labels mean the true position as measured by an ideal radar.

The bias, scale factor, and noise that used to generate these measures
can be examined by:

```python
>>> rdr.rng_noise_std # doctest: +ELLIPSIS
1.0
>>> rdr.bias * c4d.r2d  # doctest: +ELLIPSIS
0.13...
>>> rdr.scale_factor # doctest: +ELLIPSIS
0.96...
>>> rdr.noise_std * c4d.r2d
0.8
```
Points to consider here:

- The scale factor error increases with the angle, such that for a $7%$
  scale factor,
  the error of $Azimuth = 100°$ is $7°$, whereas the error for
  $Elevation = -15°$ is only $-1.05°$.
- The standard deviation of the noise in the two angle channels is the same.
  However, as the `Elevation` values are confined to a smaller range, the effect
  appears more pronounced there.

**Rotating Radar**

Measure the target position with a rotating radar.
The radar origin is yawing (performed by the increment of $\psi$)
in the direction of the target motion:

```python
>>> rdr = c4d.sensors.radar(origin = pedestal)
>>> for x in tgt.data():
...   rdr.psi += .02 * c4d.d2r
...   rdr.measure(c4d.create(x[1:]), t = x[0], store = True)# doctest: +IGNORE_OUTPUT
...   rdr.store(x[0])
```
The radar yaw angle:

And the target angles with respect to the yawing radar are:

```python
>>> fig, axs = plt.subplots(2, 1)
>>> # range
>>> axs[0].plot(*rdr_ideal.data('range'), label = 'ideal static') # doctest: +IGNORE_OUTPUT
>>> axs[0].plot(*rdr.data('range'),label = 'non-ideal yawing') # doctest: +IGNORE_OUTPUT
>>> # angles
>>> axs[1].plot(*rdr_ideal.data('az', c4d.r2d),
...     label = 'az: ideal static'
... ) # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr.data('az', c4d.r2d),
...     label = 'az: non-ideal yawing'
... ) # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr_ideal.data('el', scale = c4d.r2d),
...     label = 'el: ideal static'
... ) # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr.data('el', scale = c4d.r2d),
...     label = 'el: non-ideal yawing'
... ) # doctest: +IGNORE_OUTPUT
```

- The rotation of the radar with the target direction
  keeps the azimuth angle limited, such that non-rotating radars with limited
  FOV (field of view)
  would have lost the target.

**Operation Time**

By default, the radar returns measurments for each
call to `measure`. However, setting the parameter `dt`
to a positive number makes `measure` return `None`
for any `t < last_t + dt`, where `t` is the current measure time,
`last_t` is the last measurement time, and `dt` is the radar time-constant:

```python
>>> np.random.seed(770)
>>> tgt = c4d.datapoint(x = 100, y = 100)
>>> rdr = c4d.sensors.radar(dt = 0.01)
>>> for t in np.arange(0, .025, .005):  # doctest: +ELLIPSIS
...   print(f'{t}: {rdr.measure(tgt, t = t)}')
0.0: (0.7..., 0.01..., 140.1...)
0.005: (None, None, None)
0.01: (0.72..., -0.04..., 142.1...)
0.015: (None, None, None)
0.02: (0.72..., -0.003..., 140.4...)
```
**Random Distribution**

The distribution of normally generated random variables
is characterized by its bell-shaped curve, which is symmetric about the mean.
The area under the curve represents probability, with about `68%` of the data
falling within one standard deviation (1σ) of the mean, `95%` within two,
and `99.7%` within three,
making it a useful tool for understanding and predicting data behavior.

In `radar` objects, and `seeker` objects in general,
the `bias` and `scale factor` vary
among different instances to allow a realistic simulation
of performance behavior in a technique known as Monte Carlo.

Let's examine the `bias` distribution across

mutliple `radar` instances with a default `bias_std = 0.3°`
in comparison to `seeker` instances with a default `bias_std = 0.1°`:

```python
>>> from c4dynamics.sensors import seeker, radar
>>> seekers = []
>>> radars = []
>>> for i in range(1000):
...   seekers.append(seeker().bias * c4d.r2d)
...   radars.append(radar().bias * c4d.r2d)
```
The histogram highlights the broadening of the distribution
as the standard deviation increases:

  >>> ax = plt.subplot()
  >>> ax.hist(seekers, 30, label = 'Seekers') # doctest: +IGNORE_OUTPUT
  >>> ax.hist(radars, 30, label = 'Radars')  # doctest: +IGNORE_OUTPUT

### `BR`

```python
BR(self)
```

Returns a Body-from-Reference Direction Cosine Matrix (DCM).

Based on the current Euler angles, `BR` returns the DCM in a 3-2-1 order,
i.e. first rotation about the z axis (yaw, $\psi$), then a rotation about the
y axis (pitch, $\theta$), and finally a rotation about the x axis
(roll, $\varphi$).

The `DCM321` matrix is calculated by the
`rotmat` module and is given by:

$$
R = \begin{bmatrix}
c\theta \cdot c\psi
& c\theta \cdot s\psi
& -s\theta \\
s\varphi \cdot s\theta \cdot c\psi - c\varphi \cdot s\psi
& s\varphi \cdot s\theta \cdot s\psi + c\varphi \cdot c\psi
& s\varphi \cdot c\theta \\
c\varphi \cdot s\theta \cdot c\psi + s\varphi \cdot s\psi
& c\varphi \cdot s\theta \cdot s\psi - s\varphi \cdot c\psi
& c\varphi \cdot c\theta
\end{bmatrix}
$$
where

- $c\varphi \equiv cos(\varphi)$
- $s\varphi \equiv sin(\varphi)$
- $c\theta \equiv cos(\theta)$
- $s\theta \equiv sin(\theta)$
- $c\psi \equiv cos(\psi)$
- $s\psi \equiv sin(\psi)$

For the background material regarding the rotational matrix operations,
see `rotmat`.

### Returns
out : numpy.ndarray
    A 3x3 DCM matrix uses to rotate a vector
    to the body frame
    from a reference frame of coordinates.

### Example
```python
>>> v_inertial = [1, 0, 0]
>>> rb = c4d.rigidbody(psi = 45 * c4d.d2r)
>>> v_body = rb.BR @ v_inertial
>>> v_body  # doctest: +NUMPY_FORMAT
```
  [0.707  -0.707  0.0]

### `I`

```python
I(self)
```

Gets and sets the array of moments of inertia.

$$
I = [I_{xx}, I_{yy}, I_{zz}]
$$
Default: $I = [0, 0, 0]$

### Parameters
I : numpy.array or list
    An array of three moments of inertia about each
    one of the axes $([I_{xx}, I_{yy}, I_{zz}])$.

### Returns
out : numpy.array
    An array of the three moments of inertia $[I_{xx}, I_{yy}, I_{zz}]$.

### Example
The moment of inertia
determines how much torque is required for a
desired angular acceleration about a rotational axis.

In this example, two physical pendulums with the same
initial conditions
show the effect of different moments of inertia
on the time period of an oscillation:

$$
T = 2 \cdot \pi \cdot \sqrt{{I \over m \cdot g \cdot l}}
$$
where here $m$ is the mass $m = 1$,
$l$ is the length from the center of mass $l = 1$,
$g$ is the gravity acceleration,
and $I$ is the moment of inertia about $y$,
$I_{yy1} = 0.5, I_{yy2} = 0.05$

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> from scipy.integrate import odeint
>>> import numpy as np
```
Settings and initial condtions:

```python
>>> b = 0.5
>>> dt = 0.01
>>> g = c4d.g_ms2
>>> theta0 = 80 * c4d.d2r
>>> rb05  = c4d.rigidbody(theta = theta0)
>>> rb05.I = [0, .5, 0]
>>> rb005 = c4d.rigidbody(theta = theta0)
>>> rb005.I = [0, .05, 0]
```
Physical pendulum dynamics:

```python
>>> def pendulum(yin, t, Iyy):
...   theta, q = yin[7], yin[10]
...   yout = np.zeros(12)
...   yout[7] = q
...   yout[10] = -g * c4d.sin(theta) / Iyy - b * q
...   return yout
```
Main loop

```python
>>> for ti in np.arange(0, 5, dt):
...   # Iyy = 0.5
...   rb05.X = odeint(pendulum, rb05.X, [ti, ti + dt], (rb05.I[1],))[1]
...   rb05.store(ti)
...   # Iyy = 0.05
...   rb005.X = odeint(pendulum, rb005.X, [ti, ti + dt], (rb005.I[1],))[1]
...   rb005.store(ti)
```
Plot results:

```python
>>> rb05.plot('theta')
>>> rb005.plot('theta', ax = plt.gca(), color = 'c')
```

### `Position`

```python
Position(self)
```

Returns a vector of position coordinates.

If the state doesn't include any position coordinate (x, y, z),
an empty array is returned.

### Note
In the context of `Position`,
only x, y, z, (case sensitive) are considered position coordinates.

### Returns
out : numpy.array
    A vector containing the values of three position coordinates.

### Examples
```python
>>> s = c4d.state(theta = 3.14, x = 1, y = 2)
>>> s.Position  # doctest: +NUMPY_FORMAT
[1  2  0]
```

```python
>>> s = c4d.state(theta = 3.14, x = 1, y = 2, z = 3)
>>> s.Position  # doctest: +NUMPY_FORMAT
[1  2  3]
```

```python
>>> s = c4d.state(theta = 3.14, z = -100)
>>> s.Position  # doctest: +NUMPY_FORMAT
[0  0  -100]
```

```python
>>> s = c4d.state(theta = 3.14)
>>> s.Position   # doctest: +IGNORE_OUTPUT
Position is valid when at least one cartesian coordinate variable (x, y, z) exists...
```
  []

### `RB`

```python
RB(self)
```

Returns a Reference-from-Body Direction Cosine Matrix (DCM).

Based on the current Euler angles, `RB` returns the
transpose matrix of `BR`,
where `BR`
is the Body from Reference
DCM in 3-2-1 order.

The transpose matrix of the DCM generated by
three Euler angles $\varphi$ (rotation about `x`),
$\theta$ (about `y`), and $\psi$ (about `z`) in 3-2-1 order,
is given by:

$$
R = \begin{bmatrix}
c\theta \cdot c\psi
& s\varphi \cdot s\theta \cdot c\psi - c\varphi \cdot s\psi
& c\varphi \cdot s\theta \cdot c\psi + s\varphi \cdot s\psi \\
c\theta \cdot s\psi
& s\varphi \cdot s\theta \cdot s\psi + c\varphi \cdot c\psi
& c\varphi \cdot s\theta \cdot s\psi - s\varphi \cdot c\psi \\
-s\theta
& s\varphi \cdot c\theta
& c\varphi \cdot c\theta
\end{bmatrix}
$$
where

- $c\varphi \equiv cos(\varphi)$
- $s\varphi \equiv sin(\varphi)$
- $c\theta \equiv cos(\theta)$
- $s\theta \equiv sin(\theta)$
- $c\psi \equiv cos(\psi)$
- $s\psi \equiv sin(\psi)$

For the background material regarding the rotational matrix operations,
see `rotmat`.

### Returns
out : numpy.ndarray
    A 3x3 DCM matrix uses to rotate a vector from a body frame
    to a reference frame of coordinates.

### Example
```python
>>> v_body = [np.sqrt(3), 0, 1]
>>> rb = c4d.rigidbody(theta = 30 * c4d.d2r)
>>> v_inertial = rb.RB @ v_body
>>> v_inertial   # doctest: +NUMPY_FORMAT
```
  [2.0  0.0  0.0]

### `Velocity`

```python
Velocity(self)
```

Returns a vector of velocity coordinates.

If the state doesn't include any velocity coordinate (vx, vy, vz),
an empty array is returned.

### Note
In the context of `Velocity`,
only vx, vy, vz, (case sensitive) are considered velocity coordinates.

### Returns
out : numpy.array
    A vector containing the values of three velocity coordinates.

### Examples
```python
>>> s = c4d.state(x = 100, y = 0, vx = -10, vy = 5)
>>> s.Velocity # doctest: +NUMPY_FORMAT
[-10  5  0]
```

```python
>>> s = c4d.state(x = 100, vz = -100)
>>> s.Velocity # doctest: +NUMPY_FORMAT
[0  0  -100]
```

```python
>>> s = c4d.state(z = 100)
>>> s.Velocity  # doctest: +IGNORE_OUTPUT
Warning: Velocity is valid when at least one velocity coordinate
variable (vx, vy, vz) exists.
```
  []

### `X`

```python
X(self) -> NDArray[typing.Any]
```

Gets and sets the state vector variables.

### Parameters
x : array_like
    Values vector to set the variables of the state.

### Returns
out : numpy.array
    Values vector of the state.

### Examples
Getter:

```python
>>> s = c4d.state(x1 = 0, x2 = -1)
>>> s.X   # doctest: +NUMPY_FORMAT
[0  -1]
```
Setter:

```python
>>> s = c4d.state(x1 = 0, x2 = -1)
>>> s.X += [0, 1] # equivalent to: s.X = s.X + [0, 1]
>>> s.X   # doctest: +NUMPY_FORMAT
[0  0]
```
`datapoint` getter - setter:

```python
>>> dp = c4d.datapoint()
>>> dp.X   # doctest: +NUMPY_FORMAT
[0  0  0  0  0  0]
>>> #       x     y    z  vx vy vz
>>> dp.X = [1000, 100, 0, 0, 0, -100]
>>> dp.X   # doctest: +NUMPY_FORMAT
```
  [1000  100  0  0  0  -100]

### `X0`

```python
X0(self)
```

Returns the initial conditions of the state vector.

The initial conditions are determined at the stage of constructing
the state object.
Modifying the initial conditions is possible by direct assignment
of the state variable with a '0' suffix. For a state variable
$s.x$, its initial condition is modifyied by:
:code:`s.x0 = x0`, where :code:`x0` is an arbitrary parameter.

### Returns
out : numpy.array
    An array representing the initial values of the state variables.

### Examples
```python
>>> s = c4d.state(x1 = 0, x2 = -1)
>>> s.X += [0, 1]
>>> s.X0   # doctest: +NUMPY_FORMAT
[0  -1]
```

```python
>>> s = c4d.state(x1 = 1, x2 = 1)
>>> s.X0   # doctest: +NUMPY_FORMAT
[1  1]
>>> s.x10 = s.x20 = 0
>>> s.X0   # doctest: +NUMPY_FORMAT
```
  [0  0]

### `addvars`

```python
addvars(self, **kwargs)
```

Add state variables.

Adding variables to the state outside the `state`
constructor is possible by using `addvars()`.

### Parameters
**kwargs : float or int
    Keyword arguments representing the variables and their initial conditions.
    Each key is a variable name and each value is its initial condition.

### Note
If `store()` is called before
adding the new variables, then the time histories of the new states
are filled with zeros to maintain the same size as the other state variables.

### Examples
```python
>>> s = c4d.state(x = 0, y = 0)
>>> print(s)
[ x  y ]
>>> s.addvars(vx = 0, vy = 0)
>>> print(s)
[ x  y  vx  vy ]
```
calling `store()` before
adding the new variables:

```python
>>> s = c4d.state(x = 1, y = 1)
>>> s.store()
>>> s.store()
>>> s.store()
>>> s.addvars(vx = 0, vy = 0)
>>> s.data('x')[1]   # doctest: +NUMPY_FORMAT
[1  1  1]
>>> s.data('vx')[1]   # doctest: +NUMPY_FORMAT
```
  [0  0  0]

### `ang_rates`

```python
ang_rates(self)
```

Returns an array of angular rates.

$$
angular rates = [p, q, r]
$$
### Returns
out : numpy.array
    An array of three angular rates of the body axes
    $([p, q, r])$

### Examples
```python
>>> q0 = 30
>>> rb = c4d.rigidbody(q = q0)
>>> rb.ang_rates # doctest: +NUMPY_FORMAT
```
  [0  30  0]

### `angles`

```python
angles(self)
```

Returns an array of Euler angles.

$$
angles = [\varphi, \theta, \psi]
$$
### Returns
out : numpy.array
    An array of three Euler angles, about each one of the axes
    $([\varphi, \theta, \psi])$

### Examples
```python
>>> rb = c4d.rigidbody(phi = 135)
>>> rb.angles # doctest: +NUMPY_FORMAT
```
  [135  0  0]

### `animate`

```python
animate(self, modelpath, angle0=[0, 0, 0], modelcolor=None, dt=0.001, savedir=None, cbackground=[1, 1, 1])
```

Animate a rigidbody.

Animates the rigid body's motion using a 3D model
according to the 3-2-1 Euler angles histories.

**Important Note**

Using the `animate` function requires installation of
`Open3D` which is not a prerequisite of `C4dynamics`.
For the different ways to install `Open3D` please
refer to its `official website <https://www.open3d.org/>`_.
A direct installation with pip:

::

  pip install open3d

### Parameters
modelpath : str
    A path to a single file model or a path to a folder containing multiple
    model files.
    If the provided path is of a folder, only model files should exist in it.
    Typically supported files for mesh models are .obj, .stl, .ply.
    Supported point cloud file is .pcd.
    If your point cloud file has .ply extension, convert it to a .pcd first.
    You may do that by using `Open3D`, see note below.

angle0 : array_like, optional
    Initial Euler angles $[\varphi, \theta, \psi]$, in radians, representing
    the model attitude with respect to the screen frame, see note below.

modelcolor : array_like, optional
    Colors array [R, G, B] of values between 0 and 1.
    The shape of `modelcolor` is `mx3`, where m is either 1 or as
    the number of the model files.
    If `m > 1`, then the order of the colors in the array
    should match the alphabetical order of the files in `modelpath`.

dt : float, optional
    Time step between two frames for the animation.
    Default is 1msec.

savedir : str, optional
    If provided, saves each frame as an image in the specified directory.
    Default is None.

### Note
- Currently, only 321 Euler order of rotation is supported.
  Therefore if the stored angular state is produced by
  using other set of Euler angles, they have to be converted to a 321 set first.
- If the provided path is of a folder, only model files should exist in it.
  Typically supported files for mesh models are .obj, .stl, .ply.
  Supported point cloud file is .pcd.
  If your point cloud file has .ply extension, convert it to a .pcd first.
  You may do that by using `Open3D`:

  
```python
>>> import open3d as o3d
  >>> pcd = o3d.io.read_point_cloud('model.ply') # doctest: +IGNORE_OUTPUT
  >>> o3d.io.write_point_cloud('model.pcd', pcd) # doctest: +IGNORE_OUTPUT

For more info see `Open3D documentation
<https://www.open3d.org/docs/release/tutorial/geometry/file_io.html>`_
```
- Initial Euler angles $[\varphi, \theta, \psi]$, in radians, representing
  the model attitude with respect to the screen frame, see note below.
  The screen frame is defined as follows:

  ::

    x: right
    y: up
    z: outside

  Default attitude [0, 0, 0].

### Examples
The 3D models used in the following examples can be downloaded and
fetched by c4dynamics' datasets:

```python
>>> import c4dynamics as c4d
```

```python
>>> bunnypath = c4d.datasets.d3_model('bunny') # 'bunny.pcd': point cloud data file
Fetched successfully
>>> bunnymesh_path = c4d.datasets.d3_model('bunnymesh') # 'bunny_mesh.ply': polygon file
Fetched successfully
>>> f16path = c4d.datasets.d3_model('f16') # folder of 10 stl files.
Fetched successfully
```
For more details, refer to `c4dynamics.datasets`.

**Animate Stanford bunny**

1. The Stanford bunny is a computer graphics 3D test model
developed by Greg Turk and Marc Levoy in 1994 at Stanford University.
The model consists of 69,451 triangles, with the data determined by
3D scanning a ceramic figurine of a rabbit. For more details, refer to
`The Stanford 3D Scanning Repository <https://graphics.stanford.edu/data/3Dscanrep/#bunny>`_

```python
>>> bunny = c4d.rigidbody()
>>> # generate an arbitrary attitude motion
>>> dt = 0.01
>>> T = 5
>>> for t in np.arange(0, T, dt):
...   bunny.psi += dt * 360 * c4d.d2r / T
...   bunny.store(t)
>>> bunny.animate(bunnypath, cbackground = [0, 0, 0])
```

2. You can change the model's color by setting the `modelcolor` parameter.
Here is an example of a mesh version of Stanford bunny with a custom color:

```python
>>> bunny.animate(bunnymesh_path, cbackground = [0, 0, 0], modelcolor = [1, 0, .5]) # doctest: +IGNORE_OUTPUT
```

**Motion of a dynamic system**

3. An F16 has the following Euler angles:

```python
>>> f16 = c4d.rigidbody()
>>> dt = 0.01
>>> for t in np.arange(0, 9, dt):
...   if t < 3:
...     f16.psi += dt * 180 * c4d.d2r / 3
...   elif t < 6:
...     f16.theta += dt * 180 * c4d.d2r / 3
...   else:
...     f16.phi -= dt * 180 * c4d.d2r / 3
...   f16.store(t)
```

The jet model is consisted of multiple files, therefore the `f16` rigidbody object
that was simulated with the above motion is provided with a path to the consisting folder.

```python
>>> f16.animate(f16path)
```

4. It's obvious that the animated model doesn't follow the required rotation as simulated above.
This because the model initial postion isn't aligned with the screen frame.
To align the aircraft body frame which defined as:

::

  x: centerline
  z: perpendicular to x, downward
  y: completes the right-hand coordinate system

With the screen frame which defined as:

::

  x: rightward
  y: upward
  z: outside the screen

We should examine a frame of the model before any rotation.
It can be achieved by using `Open3D`:

```python
>>> import os
>>> import open3d as o3d
```

```python
>>> model = []
>>> for f in sorted(os.listdir(f16path)):
...   mfilepath = os.path.join(f16path, f)
...   m = o3d.io.read_triangle_mesh(mfilepath)
...   m.compute_vertex_normals() # doctest: +IGNORE_OUTPUT
...   model.append(m)
>>> o3d.visualization.draw_geometries(model)
```

It turns out that for 3-2-1 order of rotation (see `rotmat`)
the body frame with respect to the screen frame is given by:

- Rotation of `180deg` about `y` (up the screen)

- Rotation of `90deg` about `x` (right the screen)

Let's re-run with the correct initial conditions:

```python
>>> x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r]
>>> f16.animate(f16path, angle0 = x0)
```

5. The attitude is correct but the the model is colorless.
Let's give it some color;
We sort the colors by the jet's parts alphabetically as it
assigns the values according to the order of an alphabetical
reading of the files in the folder.
Finally convert it to a list.

```python
>>> f16colors = list({'Aileron_A_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
...                 , 'Aileron_B_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
...                 , 'Body_F16':          [0.8, 0.8, 0.8]
...                 , 'Cockpit_F16':       [0.1, 0.1, 0.1]
...                 , 'LE_Slat_A_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
...                 , 'LE_Slat_B_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
...                     , 'Rudder_F16':        [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
...                       , 'Stabilator_A_F16':  [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
...                          , 'Stabilator_B_F16':  [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
...                 }.values())
>>> f16.animate(f16path, angle0 = x0, modelcolor = f16colors)
```

6. It can also be painted with a single color for all its
parts and a single color for the background:

```python
>>> f16.animate(f16path, angle0 = x0, modelcolor = [0, 0, 0],
... cbackground = np.array([230, 230, 255]) / 255
... )
```

7. Finally, let's use the `savedir` option using the c4dynamics' gif
util to generate a gif file out of the model animation

```python
>>> f16colors = np.vstack(([255, 215, 0], [255, 215, 0]
...                         , [184, 134, 11], [0, 32, 38]
...                             , [218, 165, 32], [218, 165, 32], [54, 69, 79]
...                                 , [205, 149, 12], [205, 149, 12])) / 255
>>> outfol = os.path.join('tests', '_out', 'f16a')
>>> f16.animate(f16path, angle0 = x0, savedir = outfol, modelcolor = f16colors)   # doctest: +IGNORE_OUTPUT
>>> # the storage folder 'outfol' is the source of images for the gif function
>>> # the 'duration' parameter sets the required length of the animation
>>> gifname = 'f16_animation.gif'
>>> c4d.gif(outfol, gifname, duration = 1)
```
Viewing the gif on a Jupyter notebook is possible by using
the `Image` funtion of the `IPython` module:

```python
>>> import os
>>> from IPython.display import Image
```

```python
>>> gifpath = os.path.join(outfol, gifname)
>>> Image(filename = gifpath) # doctest: +IGNORE_OUTPUT
```

### `bias`

```python
bias(self) -> float
```

Gets and sets the object's bias.

The bias is a random variable generated once at the stage of constructing the
instance by the errors model:

$$
bias = std \cdot randn
$$
Where `bias_std` is a parameter with default
value of `0.1°` for `seeker` object,
and `0.3°` for
`radar` object.

To get the bias generated by the errors model, or to override it, the user may call
`bias` to get or set the final bias error.

### Parameters
bias : float
    Required bias, [radians].

### Returns
bias : float
    Current bias, [radians].

### Example
The following example for a `seeker` object is directly applicable
to a `radar` object too.
Simply replace :code:`c4d.sensors.seeker(origin = pedestal,...)`
with :code:`c4d.sensors.radar(origin = pedestal,...)`.

Required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial conditions:

(see `seeker` examples for more details):

Target:

```python
>>> tgt = c4d.datapoint(x = 1000, y = 0, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
>>> for t in np.arange(0, 60, 0.01):
...   tgt.inteqm(np.zeros(3), .01) # doctest: +IGNORE_OUTPUT
...   tgt.store(t)
```
Origin:

```python
>>> pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
```
Ground truth reference:

```python
>>> skr_ideal = c4d.sensors.seeker(origin = pedestal, isideal = True)
```
**Tracking with bias**

Define a seeker with a bias error only (mute the scale factor and the noise)
and set it to `0.5°` to track a constant velocity target:

```python
>>> skr = c4d.sensors.seeker(origin = pedestal, scale_factor_std = 0, noise_std = 0)
>>> skr.bias = .5 * c4d.d2r
>>> for x in tgt.data():
...   skr_ideal.measure(c4d.create(x[1:]), t = x[0],
...       store = True
...    )  # doctest: +IGNORE_OUTPUT
...   skr.measure(c4d.create(x[1:]), t = x[0], store = True)  # doctest: +IGNORE_OUTPUT
```
Compare the biased seeker with the true target angles (ideal seeker):

```python
>>> ax = plt.subplot()
>>> ax.plot(*skr_ideal.data('el', scale = c4d.r2d),
...     label = 'target'
... )  # doctest: +IGNORE_OUTPUT
>>> ax.plot(*skr.data('el', scale = c4d.r2d), label = 'seeker')  # doctest: +IGNORE_OUTPUT
```

### Example
The distribution of normally generated random variables
is characterized by its bell-shaped curve, which is symmetric about the mean.
The area under the curve represents probability, with about `68%` of the data
falling within one standard deviation (1σ) of the mean, `95%` within two,
and `99.7%` within three,
making it a useful tool for understanding and predicting data behavior.

In `radar` objects, and `seeker` objects in general,
the `bias` and `scale factor` vary
among different instances to allow a realistic simulation
of performance behavior in a technique known as Monte Carlo.

Let's examine the `bias` distribution across
mutliple `radar` instances with a default `bias_std = 0.3°`
in comparison to `seeker` instances with a default `bias_std = 0.1°`:

```python
>>> from c4dynamics.sensors import seeker, radar
>>> seekers = []
>>> radars = []
>>> for i in range(1000):
...   seekers.append(seeker().bias * c4d.r2d)
...   radars.append(radar().bias * c4d.r2d)
```
The histogram highlights the broadening of the distribution
as the standard deviation increases:

  >>> ax = plt.subplot()
  >>> ax.hist(seekers, 30, label = 'Seekers') # doctest: +IGNORE_OUTPUT
  >>> ax.hist(radars, 30, label = 'Radars')  # doctest: +IGNORE_OUTPUT

### `data`

```python
data(self, var=None, scale=1.0)
```

Returns arrays of stored time and data.

`data()` returns a tuple containing two
numpy arrays:
the first consists of timestamps, and the second
contains the values of a `var` corresponding to those timestamps.

`var` may be each one of the state variables or the parameters.

If `var` is not introduced, `data()`
returns a single array of the entire state histories.

If data were not stored, `data()`
returns an empty array.

### Parameters
var : str
    The name of the variable or parameter of the required histories.

scale : float or int, optional
    A scaling factor to apply to the variable values, by default 1.

### Returns
out : array or tuple of numpy arrays
    if `var` is introduced, `out` is a tuple of a timestamps array
    and an array of `var` values corresponding to those timestamps.
    If `var` is not introduced, then $n \times m+1$ numpy array is returned,
    where `n` is the number of stored samples, and `m+1` is the
    number of state variables and times.

### Examples
Get all stored data:

```python
>>> np.random.seed(100) # to reproduce results
>>> s = c4d.state(x = 1, y = 0, z = 0)
>>> for t in np.linspace(0, 1, 3):
...   s.X = np.random.rand(3)
...   s.store(t)
>>> s.data() # doctest: +NUMPY_FORMAT
[[0.   0.543  0.278  0.424]
 [0.5  0.845  0.005  0.121]
 [1.   0.671  0.826  0.137]]
```
Data of a variable:

```python
>>> time, x_data = s.data('x')
>>> time  # doctest: +NUMPY_FORMAT
[0.  0.5  1.]
>>> x_data  # doctest: +NUMPY_FORMAT
[0.543  0.845  0.671]
>>> s.data('y')[1]  # doctest: +NUMPY_FORMAT
[0.278  0.005  0.826]
```
Get data with scaling:

```python
>>> s = c4d.state(phi = 0)
>>> for p in np.linspace(0, c4d.pi):
...   s.phi = p
...   s.store()
>>> s.data('phi', c4d.r2d)[1]  # doctest: +IGNORE_OUTPUT
[0  3.7  7.3  ...  176.3  180]
```
Data of a parameter

```python
>>> s = c4d.state(x = 100, vx = 10)
>>> s.mass = 25
>>> s.storeparams('mass', t = 0.1)
>>> s.data('mass')
```
  (array([0.1]), array([25.]))

### `dist`

```python
dist(self, state2=None)
```

Euclidean distance.

Calculates the Euclidean distance between the self state object and
a second object `state2`. If `state2` is not provided, then the self
Euclidean distance is calculated.

When a second state object is provided:

$$
dist = \sum_{k=x,y,z} (self.k - state2.k)^2
$$
Otherwise:

$$
dist = \sum_{k=x,y,z} self.k^2
$$
### Raises
TypeError
    If the states don't include any position coordinate (x, y, z).

### Note
1. The provided states must have at least oneposition coordinate (x, y, z).
2. In the context of `dist()`,
   x, y, z, (case sensitive) are considered position coordinates.

### Parameters
state2 : `state`
    A second state object for which the relative distance is calculated.

### Returns
out : float
    Euclidean norm of the distance vector. The return type specifically is a numpy.float64.

### Examples
```python
>>> import c4dynamics as c4d
```

```python
>>> s = c4d.state(theta = 3.14, x = 1, y = 1)
>>> s.dist()   # doctest: +ELLIPSIS
1.414...
```

```python
>>> s  = c4d.state(theta = 3.14, x = 1, y = 1)
>>> s2 = c4d.state(x = 1)
>>> s.dist(s2)
1.0
```

```python
>>> s  = c4d.state(theta = 3.14, x = 1, y = 1)
>>> s2 = c4d.state(z = 1)
>>> s.dist(s2)   # doctest: +ELLIPSIS
1.73...
```
For final example, import required packages:

```python
>>> import numpy as np
>>> from matplotlib import pyplot as plt
```
Settings and initial conditions:

```python
>>> camera = c4d.state(x = 0, y = 0)
>>> car    = c4d.datapoint(x = -100, vx = 40, vy = -7)
>>> dist   = []
>>> time   = np.linspace(0, 10, 1000)
```
Main loop:

```python
>>> for t in time:
...   car.inteqm(np.zeros(3), time[1] - time[0]) # doctest: +IGNORE_OUTPUT
...   dist.append(camera.dist(car))
```
Show results:

```python
>>> plt.plot(time, dist, 'm') # doctest: +IGNORE_OUTPUT
>>> c4d.plotdefaults(plt.gca(), 'Distance', 'Time (s)', '(m)')
>>> plt.show()
```

### `inteqm`

```python
inteqm(self, forces, moments, dt)
```

Advances the state vector, `rigidbody.X`,
with respect to the input
forces and moments on a single step of time, `dt`.

Integrates equations of six degrees motion using the Runge-Kutta method.

This method numerically integrates the equations of motion for a dynamic system
using the fourth-order Runge-Kutta method as given by
`eqm.int6`.

The derivatives of the equations are of six dimensional motion as
given by
:py`eqm.eqm6`.

### Parameters
forces : numpy.array or list
    An external forces vector acting on the body, `forces = [Fx, Fy, Fz]`
moments : numpy.array or list
    An external moments vector acting on the body, `moments = [Mx, My, Mz]`
dt : float or int
    Interval time step for integration.

### Returns
out : numpy.float64
    An acceleration array at the final time step.

### Warning
This method is not recommanded when the vectors
of forces or moments depend on the state variables.
Since the vectors of forces and moments are provided once at the
entrance to the integration, they remain constant
for the entire steps.
Therefore, when the forces or moments depend on the state variables
the results of this method are not accurate and may lead to instability.

### Examples
A torque is applied by spacecraft thrusters to stabilize
the roll in a constant rate.

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial conditions:

```python
>>> dt = 0.001
>>> torque = [0.1, 0, 0]
>>> rb = c4d.rigidbody()
>>> rb.I = [0.5, 0, 0]  # Moment of inertia about x
```
Main loop:

```python
>>> for ti in np.arange(0, 5, dt):
...   rb.inteqm(np.zeros(3), torque, dt)  # doctest: +IGNORE_OUTPUT
...   if rb.p >= 10 * c4d.d2r:
...     torque = [0, 0, 0]
...   rb.store(ti)
```
Plot results:

```python
>>> rb.plot('p')
```

### `mass`

```python
mass(self)
```

Gets and sets the object's mass.

Default value $mass = 1$.

### Parameters
mass : float or int
    Mass of the object.

### Returns
out : float or int
    A scalar representing the object's mass.

### Example
1. `datapoint`

Two floating balloons of 1kg and 10kg float with total force of L = 0.5N
and expreience a side wind of 10k.

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial conditions:

```python
>>> dt = 0.01
>>> tf = 10 + dt
>>> F = [0, 0, .5]
>>> #
>>> bal1 = c4d.datapoint(vx = 10 * c4d.k2ms)
>>> bal1.mass = 1
>>> #
>>> bal10 = c4d.datapoint(vx = 10 * c4d.k2ms)
>>> bal10.mass = 10
```
Main loop:

```python
>>> for t in np.arange(0, tf, dt):
...   bal1.store(t)
...   bal10.store(t)
...   bal1.X = c4d.eqm.int3(bal1, F, dt)
...   bal10.X = c4d.eqm.int3(bal10, F, dt)
```

```python
>>> bal1.plot('side')
>>> bal10.plot('side', ax = plt.gca(), color = 'c')
```

2. `rigidbody`

The previous example for a `datapoint` object is directly applicable
to the `rigidbody` object, as both classes share the same underlying principles
concerning translational dynamics. Simply replace :code:`c4d.datapoint(vx = 10 * c4d.k2ms)`
with :code:`c4d.rigidbody(vx = 10 * c4d.k2ms)`.

### `measure`

```python
measure(self, target: 'c4d.state', t: float = -1, store: bool = False) -> tuple[typing.Optional[float], typing.Optional[float], typing.Optional[float]]
```

Measures range, azimuth and elevation between the radar and a `target`.

If the radar time-constant `dt` was provided when the `radar` was created,
then `measure` returns `None` for any `t < last_t + dt`,
where `t` is the time input, `last_t` is the last measurement time,
and `dt` is the radar time-constant.
Default behavior, returns measurements for each call.

If `store = True`, the method stores the measured
azimuth and elevation along with a timestamp
(`t = -1` by default, if not provided otherwise).

### Parameters
target : state
    A Cartesian state object to measure by the radar, including at
    least one position coordinate (x, y, z).
store : bool, optional
    A flag indicating whether to store the measured values. Defaults `False`.
t : float, optional
    Timestamp [seconds]. Defaults -1.

### Returns
out : tuple
    range [meters, float], azimuth and elevation, [radians, float].

### Raises
ValueError
    If `target` doesn't include any position coordinate (x, y, z).

### Example
`measure` in a program simulating
real-time tracking of a constant velcoity target.

The target is represented by a
`datapoint`
and is simulated using the `eqm` module,
which integrating the point-mass equations of motion.

An ideal radar uses as reference to the true position of the target.

At each cycle, the the radars take measurements and store the samples for
later use in plotting the results.

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial conditions:

```python
>>> dt = 0.01
>>> np.random.seed(321)
>>> tgt = c4d.datapoint(x = 1000, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
>>> pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
>>> rdr = c4d.sensors.radar(origin = pedestal, dt = 0.05)
>>> rdr_ideal = c4d.sensors.radar(origin = pedestal, isideal = True)
```
Main loop:

```python
>>> for t in np.arange(0, 60, dt):
...   tgt.inteqm(np.zeros(3), dt)  # doctest: +IGNORE_OUTPUT
...   rdr_ideal.measure(tgt, t = t, store = True)    # doctest: +IGNORE_OUTPUT
...   rdr.measure(tgt, t = t, store = True)    # doctest: +IGNORE_OUTPUT
...   tgt.store(t)
```
Before viewing the results, let's examine the error parameters generated by
the errors model (`c4d.r2d` converts radians to degrees):

```python
>>> rdr.rng_noise_std
1.0
>>> rdr.bias * c4d.r2d # doctest: +ELLIPSIS
0.49...
>>> rdr.scale_factor # doctest: +ELLIPSIS
1.01...
>>> rdr.noise_std * c4d.r2d
0.8
```
Then we excpect a constant bias of -0.02° and a 'compression' or 'squeeze' of `5%` with
respect to the target (as represented by the ideal radar):

```python
>>> _, axs = plt.subplots(2, 1)  # doctest: +IGNORE_OUTPUT
>>> # range
>>> axs[0].plot(*rdr_ideal.data('range'), '.m',
...     label = 'target'
... )  # doctest: +IGNORE_OUTPUT
>>> axs[0].plot(*rdr.data('range'), '.c', label = 'radar')  # doctest: +IGNORE_OUTPUT
>>> # angles
>>> axs[1].plot(*rdr_ideal.data('az', scale = c4d.r2d), '.m',
...     label = 'target'
... )  # doctest: +IGNORE_OUTPUT
>>> axs[1].plot(*rdr.data('az', scale = c4d.r2d), '.c',
...     label = 'radar'
... )  # doctest: +IGNORE_OUTPUT
```

The sample rate of the radar was set by the parameter `dt = 0.05`.
In cycles that don't satisfy `t < last_t + dt`, `measure` returns None,
as shown in a close-up view:

### `norm`

```python
norm(self)
```

Returns the Euclidean norm of the state vector.

### Returns
out : float
    The computed norm of the state vector. The return type specifically is a numpy.float64.

### Examples
```python
>>> s = c4d.state(x1 = 1, x2 = -1)
>>> s.norm  # doctest: +ELLIPSIS
```
  1.414...

### `normalize`

```python
normalize(self)
```

Returns a unit vector representation of the state vector.

### Returns
out : numpy.array
    A normalized vector of the same direction and shape as `self.X`, where
    the norm of the vector is `1`.

### Examples
```python
>>> s = c4d.state(x = 1, y = 2, z = 3)
>>> s.normalize   # doctest: +NUMPY_FORMAT
```
  [0.267  0.534  0.801]

### `plot`

```python
plot(self, var, scale=1, ax=None, filename=None, darkmode=True, **kwargs)
```

Draws plots of trajectories or variable evolution over time.

`var` can be each one of the state variables, or `top`, `side`, for trajectories.

### Parameters
var : str
    The variable to be plotted.
    Possible variables for trajectories: `top`, `side`.
    For time evolution, any one of the state variables is possible:
    `x`, `y`, `z`, `vx`, `vy`, `vz` - for a datapoint object, and
    also `phi`, `theta`, `psi`, `p`, `q`, `r` - for a rigidbody object.

scale : float or int, optional
    A scaling factor to apply to the variable values. Defaults to `1`.

ax : matplotlib.axes.Axes, optional
    An existing Matplotlib axis to plot on.
    If None, a new figure and axis will be created. By default None.

filename : str, optional
    Full file name to save the plot image.
    If None, the plot will not be saved, by default None.

darkmode : bool, optional
    Directory path to save the plot image.
    If None, the plot will not be saved, by default None.

**kwargs : dict, optional
    Additional key-value arguments passed to `matplotlib.pyplot.plot`.
    These can include any keyword arguments accepted by `plot`,
    such as `color`, `linestyle`, `marker`, etc.

### Notes
- The method overrides the `plot` of
  the parent `state` object and is
  applicable to `datapoint`
  and its subclass `rigidbody`.

- Uses matplotlib for plotting.

- Trajectory views (`top` and `side`) show the crossrange vs
  downrange or downrange vs altitude.

### Examples
Import necessary packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
>>> import scipy
```
1) `datapoint`:

```python
>>> pt = c4d.datapoint()
>>> for t in np.arange(0, 10, .01):
...   pt.x = 10 + np.random.randn()
...   pt.store(t)
>>> pt.plot('x')
```

2) `rigidbody`:

A physical pendulum is represented by a rigidoby object.
`scipy's odeint` integrates the equations of motion to simulate
the angle of rotation of the pendulum over time.

Settings and initial conditions:

```python
>>> dt =.01
>>> pndlm  = c4d.rigidbody(theta = 80 * c4d.d2r)
>>> pndlm.I = [0, .5, 0]
```
Dynamic equations:

```python
>>> def pendulum(yin, t, Iyy):
...   yout = np.zeros(12)
...   yout[7]  =  yin[10]
...   yout[10] = -c4d.g_ms2 * c4d.sin(yin[7]) / Iyy - .5 * yin[10]
...   return yout
```
Main loop:

```python
>>> for ti in np.arange(0, 4, dt):
...   pndlm.X = scipy.integrate.odeint(pendulum, pndlm.X, [ti, ti + dt], (pndlm.I[1],))[1]
...   pndlm.store(ti)
```
Plot results:

```python
>>> pndlm.plot('theta', scale = c4d.r2d)
```

### `scale_factor`

```python
scale_factor(self) -> float
```

Gets and sets the object's scale_factor.

The scale factor is a random variable generated once at the stage of constructing the
instance by the errors model:

$$
scalefactor = std \cdot randn
$$
Where `scale_factor_std` is a parameter with default
value of `0.05 (5%)` for `seeker`
object, and `0.07 (7%)` for
`radar` object.

To get the scale factor generated by the errors model,
or to override it, the user may call
`scale_factor` to get or set the final scale factor error.

### Parameters
scale_factor : float
  Required scale factor, [dimensionless].

### Returns
scale_factor : float
  Current scale factor, [dimensionless].

### Example
The following example for a `seeker` object is directly applicable
to a `radar` object too.
Simply replace :code:`c4d.sensors.seeker(...)`
with :code:`c4d.sensors.radar(...)`.

Required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial conditions:

(see `seeker`
or `radar`
examples for more details):

Target:

```python
>>> tgt = c4d.datapoint(x = 1000, y = 0, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
>>> for t in np.arange(0, 60, 0.01):
...   tgt.inteqm(np.zeros(3), .01) # doctest: +IGNORE_OUTPUT
...   tgt.store(t)
```
Origin:

```python
>>> pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
```
Ground truth reference:

```python
>>> skr_ideal = c4d.sensors.seeker(origin = pedestal, isideal = True)
```
**Tracking with scale factor**

Define a seeker with a scale factor error only (mute the bias and the noise)
and set it to `1.2 (= 20%)` to track a constant velocity target:

```python
>>> skr = c4d.sensors.seeker(origin = pedestal, bias_std = 0, noise_std = 0)
>>> skr.scale_factor = 1.2
>>> for x in tgt.data():
...   skr_ideal.measure(c4d.create(x[1:]), t = x[0],
...     store = True
...   )  # doctest: +IGNORE_OUTPUT
...   skr.measure(c4d.create(x[1:]), t = x[0], store = True)    # doctest: +IGNORE_OUTPUT
```
Compare with the true target angles (ideal seeker):

```python
>>> ax = plt.subplot()
>>> ax.plot(*skr_ideal.data('az', scale = c4d.r2d),
...     label = 'target'
... )  # doctest: +IGNORE_OUTPUT
>>> ax.plot(*skr.data('az', scale = c4d.r2d),
...     label = 'seeker'
... )  # doctest: +IGNORE_OUTPUT
```

### `store`

```python
store(self, t=-1)
```

Stores the current state.

The current state is defined by the vector of variables
as given by `state.X`.
`store()` is used to store the
instantaneous state variables.

### Parameters
t : float or int, optional
    Time stamp for the stored state.

### Note
1. Time `t` is an optional parameter with a default value of $t = -1$.
The time is always appended at the head of the array to store. However,
if `t` is not given, default $t = -1$ is stored instead.

2. The method `store()` goes together with
the methods `data()`
and `timestate()` as input and outputs.

3. `store()` only stores
state variables (those construct `state.X`).
For other parameters, use `storeparams()`.

### Examples
```python
>>> s = c4d.state(x = 1, y = 0, z = 0)
>>> s.store()
```
**Store with time stamp:**

```python
>>> s = c4d.state(x = 1, y = 0, z = 0)
>>> s.store(t = 0.5)
```
**Store in a for-loop:**

```python
>>> s = c4d.state(x = 1, y = 0, z = 0)
>>> for t in np.linspace(0, 1, 3):
...   s.X = np.random.rand(3)
...   s.store(t)
```
Usage of `store()`
inside a program with a `datapoint`
from the `states library`:

```python
>>> t = 0
>>> dt = 1e-3
>>> h0 = 100
>>> dp = c4d.datapoint(z = h0)
>>> while dp.z >= 0:
...   dp.inteqm([0, 0, -c4d.g_ms2], dt) # doctest: +IGNORE_OUTPUT
...   t += dt
...   dp.store(t)
>>> for z in dp.data('z'):   # doctest: +IGNORE_OUTPUT
...   print(z)
99.9999950
99.9999803
99.9999558
...
0.00033469
```
  -0.0439570

### `storeparams`

```python
storeparams(self, params, t=-1.0)
```

Stores parameters.

Parameters are data attributes which are not part of the state vector.
`storeparams()` is
used to store the instantaneous parameters.

### Parameters
params : str or list of str
    Name or names of the parameters to store.
t : float or int, optional
    Time stamp for the stored state.

### Note
1. Time `t` is an optional parameter with a default value of $t = -1$.
The time is always appended at the head of the array to store. However,
if `t` is not given, default $t = -1$ is stored instead.

2. The method `storeparams()`
goes together with the method `data()`
as input and output.

### Examples
```python
>>> s = c4d.state(x = 100, vx = 10)
>>> s.mass = 25
>>> s.storeparams('mass')
>>> s.data('mass')[1]   # doctest: +NUMPY_FORMAT
[25]
```
**Store with time stamp:**

```python
>>> s = c4d.state(x = 100, vx = 10)
>>> s.mass = 25
>>> s.storeparams('mass', t = 0.1)
>>> s.data('mass')
(array([0.1]), array([25.]))
```
**Store multiple parameters:**

```python
>>> s = c4d.state(x = 100, vx = 10)
>>> s.x_std = 5
>>> s.vx_std = 10
>>> s.storeparams(['x_std', 'vx_std'])
>>> s.data('x_std')[1]   # doctest: +NUMPY_FORMAT
[5]
>>> s.data('vx_std')[1] # doctest: +NUMPY_FORMAT
[10]
```
**Objects classification:**

```python
>>> s = c4d.state(x = 25, y = 25, w = 20, h = 10)
>>> np.random.seed(44)
>>> for i in range(3):
...   s.X += 1
...   s.w, s.h = np.random.randint(0, 50, 2)
...   if s.w > 40 or s.h > 20:
...     s.class_id = 'truck'
...   else:
...     s.class_id = 'car'
...   s.store() # stores the state
...   s.storeparams('class_id') # store the class_id parameter
>>> print('   x    y    w    h    class')  # doctest: +IGNORE_OUTPUT
>>> print(np.hstack((s.data()[:, 1:].astype(int),
...       np.atleast_2d(s.data('class_id')[1]).T)))  # doctest: +IGNORE_OUTPUT
x   y   w   h   class
26  26  20  35  truck
27  27  49  45  car
28  28  3   32  car
```
The `morphospectra` implements a custom method `getdim` to update
the dimension parameter `dim` with respect to the position coordinates:

```python
>>> import types
>>> #
>>> def getdim(s):
...   if s.X[2] != 0:
...     # z
...     s.dim = 3
...   elif s.X[1] != 0:
...     # y
...     s.dim = 2
...   elif s.X[0] != 0:
...     # x
...     s.dim = 1
...   else:
...     # none
...     s.dim = 0
>>> #
>>> morphospectra = c4d.state(x = 0, y = 0, z = 0)
>>> morphospectra.dim = 0
>>> morphospectra.getdim = types.MethodType(getdim, morphospectra)
>>> #
>>> for r in range(10):
...   morphospectra.X = np.random.choice([0, 1], 3)
...   morphospectra.getdim()
...   morphospectra.store()
...   morphospectra.storeparams('dim')
>>> #
>>> print('x y z  | dim')  # doctest: +IGNORE_OUTPUT
>>> print('------------')  # doctest: +IGNORE_OUTPUT
>>> for x, dim in zip(morphospectra.data().astype(int)[:, 1 : 4].tolist(),
...   morphospectra.data('dim')[1].tolist()):  # doctest: +IGNORE_OUTPUT
...       print(*(x + [' | '] + [dim]))
x y z  | dim
------------
0 1 0  |  2
1 1 0  |  2
1 0 0  |  1
0 1 1  |  3
1 0 0  |  1
1 1 1  |  3
1 1 0  |  2
1 1 0  |  2
1 0 1  |  3
```
  1 0 1  |  3

### `timestate`

```python
timestate(self, t)
```

Returns the state as stored at time `t`.

The method searches the closest time
to time `t` in the sampled histories and
returns the state that stored at the time.

If data were not stored returns None.

### Parameters
t : float or int
    The time at the required sample.

### Returns
X : numpy.array
    An array of the state vector
    `state.X`
    at time `t`.

### Examples
```python
>>> s = c4d.state(x = 0, y = 0, z = 0)
>>> for t in np.linspace(0, 1, 3):
...   s.X += 1
...   s.store(t)
>>> s.timestate(0.5) # doctest: +NUMPY_FORMAT
[2  2  2]
```

```python
>>> s = c4d.state(x = 1, y = 0, z = 0)
>>> s.timestate(0.5)  # doctest: +IGNORE_OUTPUT
Warning: no history of state samples.
```
  None

### `vel_mag`

```python
vel_mag(self)
```

Velocity Magnitude.

Calculates the magnitude of the object velocity :

$$
vel mag = \sum_{k=v_x,v_y,v_z} self.k^2
$$
If the state doesn't include any velocity coordinate (vx, vy, vz),
a `ValueError` is raised.

### Returns
out : float
    Euclidean norm of the velocity vector. The return type specifically is a numpy.float64.

### Raises
TypeError
    If the state does not include any velocity coordinate (vx, vy, vz).

### Note
In the context of `vel_mag()`,
vx, vy, vz, (case sensitive) are considered velocity coordinates.

### Examples
```python
>>> s = c4d.state(vx = 7, vy = 24)
>>> s.vel_mag()
25.0
```

```python
>>> s = c4d.state(x = 100, y = 0, vx = -10, vy = 7)
>>> s.vel_mag()   # doctest: +ELLIPSIS
12.2...
```
Uncommenting the following line throws a type error:

```python
>>> s = c4d.state(x = 100, y = 0)
>>> # s.vel_mag()
```
  TypeError: state must have at least one velocity coordinate (vx, vy, or vz)

