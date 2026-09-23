# gps

GPS receiver.

The `gps` class models a GPS receiver that measures the inertial
position of a vehicle in terms of ``[x, y, z]``.  The measurement is
affected by a constant bias and sample-to-sample white Gaussian noise.

Parameters
==========
noise_std : float, optional
    Standard deviation of the position measurement noise, [m].
    Defaults to ``0.5``.
bias : array_like, optional
    Constant position bias ``[bx, by, bz]``, [m].  Defaults to
    ``[0, 0, 0]``.
isideal : bool, optional
    If ``True``, overrides ``noise_std`` and ``bias`` to zero, producing
    an ideal (noise-free, bias-free) GPS. Defaults to ``False``.

See Also
========
.ekf
.seeker

**Functionality**

At each sample the GPS returns a position measurement based on the true
inertial position of the vehicle.  If the true state is

$$
X = [x, y, z, v_x, v_y, v_z, \varphi, \theta, \psi, p, q, r]^T
$$
the ideal position measurement is

$$
z_{ideal} = [x, y, z]^T.
$$
The simulated measurement is

$$
z = z_{ideal} + b + n
$$
where $b$ is the constant bias and $n$ is a zero-mean
Gaussian random variable with standard deviation ``noise_std`` applied
independently to each position coordinate.

**Errors Model**

The GPS measurement is subject to two error sources: bias and noise.

- ``Bias``:
  represents a constant offset in the measured position.  It is set when
  the GPS object is constructed through the ``bias`` parameter and remains
  unchanged between measurements.  When ``bias`` is not provided, the
  bias is ``[0, 0, 0]``.
- ``Noise``:
  represents random variations in the position measurement.  At every
  call to `measure`, an independent normally distributed random
  vector with mean zero and standard deviation ``noise_std`` is added to
  the position.

The errors model can be disabled by setting ``noise_std = 0`` and
``bias = [0, 0, 0]``.  This produces an ideal position measurement.

Unlike the `seeker` model, the GPS implementation does not generate
a random bias during construction and does not include a scale-factor
error.  The supplied ``bias`` is deterministic for a given GPS instance.

**Construction**

A GPS instance is created by making a direct call to the constructor:

    >>> gps_sensor = c4d.sensors.gps()

The measurement noise and constant bias can be specified when creating the
sensor.

Examples
========

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
**True trajectory**

For the examples below, generate a smooth 3D trajectory and store its
position in a 12-state vector.

```python
>>> t = np.arange(0, 20, 0.1)
>>> x_true = np.zeros((len(t), 12))
>>> x_true[:, 0] = 5 * np.sin(0.3 * t)
>>> x_true[:, 1] = 4 * np.cos(0.25 * t)
>>> x_true[:, 2] = -2 + 0.5 * np.sin(0.6 * t)
```
**Ideal GPS**

An ideal GPS can be created by setting both the noise and the bias to
zero:

```python
>>> gps_ideal = c4d.sensors.gps(noise_std=0, bias=[0, 0, 0])
>>> measurements = np.array([gps_ideal.measure(x) for x in x_true])
```
The measured position is then identical to the true position.

```python
>>> np.allclose(measurements, x_true[:, 0:3])
True
```
**Non-ideal GPS**

A non-ideal GPS introduces a constant position bias and white measurement
noise.  Set the random seed to make the example reproducible:

```python
>>> np.random.seed(42)
>>> gps_sensor = c4d.sensors.gps(
...     noise_std=0.5,
...     bias=[1.0, -0.5, 0.2]
... )
>>> measurements = np.array([gps_sensor.measure(x) for x in x_true])
```
The result can be compared with the true position:

```python
>>> fig, ax = plt.subplots(3, 1, figsize=(9, 7), sharex=True)
>>> labels = ['x', 'y', 'z']
>>> for i in range(3):
...     ax[i].plot(t, x_true[:, i], lw=2, label='True')
...     ax[i].plot(t, measurements[:, i], '.', ms=3, label='GPS measurement')
...     ax[i].set_ylabel(f'{labels[i]} [m]')
...     ax[i].grid(True)
...     ax[i].legend()  # doctest: +IGNORE_OUTPUT
>>> ax[-1].set_xlabel('Time [s]')  # doctest: +IGNORE_OUTPUT
>>> fig.suptitle('GPS Position Measurements')  # doctest: +IGNORE_OUTPUT
>>> fig.tight_layout()
```

**Bias**

The bias is constant across all measurements.  For example, a GPS with a
2m bias in the x direction can be created as follows:

```python
>>> gps_bias = c4d.sensors.gps(noise_std=0, bias=[2, 0, 0])
>>> measurement = gps_bias.measure(x_true[0])
>>> print(measurement - x_true[0, 0:3]) # doctest: +NUMPY_FORMAT
[2.  0.  0.]
```
The difference between the measurement and the true position is the
specified bias.

**Measurement noise**

With zero bias, repeated measurements of the same state demonstrate the
random noise generated at every call to `measure`:

```python
>>> np.random.seed(1)
>>> gps_noise = c4d.sensors.gps(noise_std=0.5, bias=[0, 0, 0])
>>> for _ in range(3): # doctest: +IGNORE_OUTPUT
...     print(gps_noise.measure(x_true[0]))
[ 0.812  3.694  -2.264]
[-0.536  4.433  -3.151]
[ 0.872  3.619  -1.840]
```
**Demo**

The built-in `demo` method provides a compact demonstration of the
GPS errors model and plots the true and measured positions:

```python
>>> fig = c4d.sensors.gps.demo(show=True)
```

The same demonstration can be run without displaying the figure by using
``show=False``.

### `demo`

```python
demo(duration=20.0, dt=0.1, seed=1, show=True)
```

Demonstrate GPS position measurements.

Simulates a smooth 3D trajectory and shows the noisy GPS position
measurements in comparison with the true trajectory.

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
    Figure containing the true and measured x, y, and z positions.

**Errors Model**

The demonstration uses ``noise_std=0.5`` and zero bias.  The random
seed controls the generated measurement noise so that the same
demonstration can be reproduced.

### Examples
Run the demonstration and display the result:

```python
>>> fig = gps.demo() # doctest: +ELLIPSIS
```
To create the figure without displaying it:

    >>> fig = gps.demo(show=False) # doctest: +ELLIPSIS

### `measure`

```python
measure(self, x_true)
```

Measure inertial position.

The method extracts the first three elements of ``x_true`` and adds
the GPS bias and a zero-mean Gaussian noise sample to each coordinate.

### Parameters
x_true : array_like
    True position vector
    ``[x, y, z]`` [m].

### Returns
numpy.ndarray
    Measured inertial position ``[x, y, z]``, [m].

**Errors Model**

A single independent noise sample is generated for each position
coordinate. The returned measurement is therefore:

$$
z = x_{true}[0:3] + bias + std \cdot N(0, I)
$$
The bias is constant for the GPS instance, while the noise is
regenerated at every call.

### Examples
```python
>>> import c4dynamics as c4d
>>> import numpy as np
>>> np.random.seed(42)
>>> gps_sensor = c4d.sensors.gps(noise_std=0, bias=[1, -2, 0.5])
>>> x = np.zeros(12)
>>> x[0:3] = [10, 20, 30]
>>> gps_sensor.measure(x) # doctest: +NUMPY_FORMAT
```
    array([11.  18.  30.5])

