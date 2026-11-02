# kalman

Kalman Filter.

Discrete linear Kalman filter class for state estimation.

`kalman` provides methods for prediction and update (correct)
phases of the filter.

For background material, implementation, and examples,
please refer to `filters`.

Parameters
==========
X : dict
    Initial state variables and their values.
F : numpy.ndarray
    Discrete-time state transition matrix. Defaults to None.
H : numpy.ndarray
    Discrete-time measurement matrix. Defaults to None.
steadystate : bool, optional
    Flag to indicate if the filter is in steady-state mode. Defaults to False.
G : numpy.ndarray, optional
    Discrete-time control matrix. Defaults to None.
P0 : numpy.ndarray, optional
    Covariance matrix, or standard deviations array, of the
    initial estimation error. Mandatory if `steadystate` is False.
    If P0 is one-dimensional array, standard deviation values are
    expected. Otherwise, variance values are expected.
Q : numpy.ndarray, optional
    Process noise covariance matrix. Defaults to None.
R : numpy.ndarray, optional
    Measurement noise covariance matrix. Defaults to None.
P_jitter : float, optional
    If provided, `P` is symmetrized and floored by `P_jitter` times
    the identity after every `predict`/`update` that modifies it
    (skipped in `steadystate` mode, where `P` never changes). This
    guards against floating-point roundoff eroding `P`'s symmetry or
    positive-definiteness over many cycles; it is not a substitute for
    a correct process/measurement model. Defaults to `None` (off).

Notes
=====
1. `kalman` is a subclass of `state`,
as such the variables provided within the parameter `X` form its state variables.
Hence, `X` is a dictionary of variables and their initial values, for example:
``X = {'x': x0, 'y': y0, 'z': z0}``.

2. Steady-state mode: if the underlying system is linear time-invariant (`LTI`),
and the noise covariance matrices are time-invariant,
then a steady-state mode of the Kalman filter can be employed.
In steady-state mode the Kalman gain (`K`) and the estimation covariance matrix
(`P`) are computed once and remain constant ('steady-state') for the entire run-time,
performing as well as the time-varying filter.
Note however that also in steady-state mode the predict and the update steps are separated
and the user must call each of them at a time.

Raises
======
TypeError:
    If X is not a dictionary.
ValueError:
    If P0 is not provided when steadystate is False.
ValueError:
    If system matrices are not fully provided.

See Also
========
.filters
.ekf
.lowpass
.seeker
.eqm

Examples
========

The examples in the introduction to the
`filters`
module demonstrate the operations of
the Kalman filter for inputs from
electromagnetic devices, such as an altimeter,
which measures the altitude.

An accurate Japaneese train travels 150 meters in one second
($F = 1, u = 1, G = 150, Q = 0.05$).
A sensor measures the train position with noise
variance of $200m^2$ ($H = 1, R = 200$).
The initial position of the train is known with uncertainty
of $0.5m$ ($P0 = 0.5^2$).

**Note**

The system may be interpreted as follows:

- $F = 1$             - constant position

- $u = 1, G = 150$    - constant velocity control input

The advantage of this model is in its being first order.
However, a slight difference between the actual dynamics and
the modeled process will result in a lag with the tracked object.

Import required packages:

```python
>>> from c4dynamics.filters import kalman
>>> from matplotlib import pyplot as plt
>>> import c4dynamics as c4d
```
Let's run a filter.

First, since the covariance matrices are
constant we can utilize the steady state mode of the filter.
This requires initalization with the respective flag:

```python
>>> v = 150
>>> sensor_noise = 200
>>> kf = kalman({'x': 0}, P0 = 0.5**2, F = 1, G = v, H = 1
...                         , Q = 0.05, R = sensor_noise**2, steadystate = True)
```

```python
>>> for t in range(1, 26): #  seconds.
...   # store for later
...   kf.store(t)
...   # predict + correct
...   kf.predict(u = 1)
...   kf.detect = v * t + np.random.randn() * sensor_noise
...   kf.storeparams('detect', t)
```
Recall that a `kalman` object, as subclass of
the `state`,
encapsulates the process state vector:

```python
>>> print(kf)
[ x ]
```
It can also employ the
`plot`
or any other method of the `state` class:

```python
>>> kf.plot('x')  # doctest: +IGNORE_OUTPUT
>>> plt.gca().plot(*kf.data('detect'), 'co', label = 'detection')   # doctest: +IGNORE_OUTPUT
>>> plt.gca().legend()    # doctest: +IGNORE_OUTPUT
>>> plt.show()
```

Let's now assume that as the
train moves farther from the station,
the sensor measurements degrade.

The measurement covariance matrix therefore increases accordingly,
and the steady state mode cannot be used:

```python
>>> v = 150
>>> kf = kalman({'x': 0}, P0 = 0.5*2, F = 1, G = v, H = 1, Q = 0.05)
>>> for t in range(1, 26): #  seconds.
...   kf.store(t)
...   sensor_noise = 200 + 8 * t
...   kf.predict(u = 1)
...   kf.detect = v * t + np.random.randn() * sensor_noise
...   kf.K = kf.update(kf.detect, R = sensor_noise**2)
...   kf.storeparams('detect', t)
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

### `nees`

```python
nees(kf, true_obj)
```

normalized estimated error squared

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
plot(self, var, scale=1, ax=None, filename=None, darkmode=True, block=False, **kwargs)
```

Draws plots of variable evolution over time.

This method plots the evolution of a state variable over time.
The resulting plot can be saved to a directory if specified.

### Parameters
var : str
    The name of the variable or parameter to be plotted.

scale : float or int, optional
    A scaling factor to apply to the variable values. Defaults to `1`.

ax : matplotlib.axes.Axes, optional
    An existing Matplotlib axis to plot on.
    If None, a new figure and axis will be created, by default None.

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

### Returns
ax : matplotlib.axes.Axes.
    Matplotlib axis of the derived plot.

### Note
- The default `color` is set to `'m'` (magenta).
- The default `linewidth` is set to `1.2`.

### Examples
Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Plot an arbitrary state variable and save:

```python
>>> s = c4d.state(x = 0, y = 0)
>>> s.store()
>>> for _ in range(100):
...   s.x = np.random.randint(0, 100, 1)
...   s.store()
>>> s.plot('x', filename = 'x.png')   # doctest: +IGNORE_OUTPUT
>>> plt.show()
```

**Interactive mode:**

```python
>>> s.plot('x')   # doctest: +IGNORE_OUTPUT
>>> plt.show(block = True)
```
**Dark mode off:**

  >>> s = c4d.state(x = 0)
  >>> s.xstd = 0.2
  >>> for t in np.linspace(-2 * c4d.pi, 2 * c4d.pi, 1000):
  ...   s.x = c4d.sin(t) + np.random.randn() * s.xstd
  ...   s.store(t)
  >>> s.plot('x', darkmode = False)    # doctest: +IGNORE_OUTPUT
  >>> plt.show()

**Scale plot:**

```python
>>> s = c4d.state(phi = 0)
>>> for y in c4d.tan(np.linspace(-c4d.pi, c4d.pi, 500)):
...   s.phi = c4d.atan(y)
...   s.store()
>>> s.plot('phi', scale = c4d.r2d)  # doctest: +IGNORE_OUTPUT
>>> plt.gca().set_ylabel('deg') # doctest: +IGNORE_OUTPUT
>>> plt.show()
```

**Given axis:**

```python
>>> plt.subplots(1, 1)  # doctest: +IGNORE_OUTPUT
>>> plt.plot(np.linspace(-c4d.pi, c4d.pi, 500) * c4d.r2d, 'm')   # doctest: +IGNORE_OUTPUT
>>> s.plot('phi', scale = c4d.r2d, ax = plt.gca(), color = 'c')  # doctest: +IGNORE_OUTPUT
>>> plt.gca().set_ylabel('deg')  # doctest: +IGNORE_OUTPUT
>>> plt.legend(['θ', 'φ'])  # doctest: +IGNORE_OUTPUT
>>> plt.show()
```

Top view + side view - options of
`datapoint`
and `rigidbody` objects:

```python
>>> dt = 0.01
>>> floating_balloon = c4d.datapoint(vx = 10 * c4d.k2ms)
>>> floating_balloon.mass = 0.1
>>> for t in np.arange(0, 10, dt):
...   floating_balloon.inteqm(forces = [0, 0, .05], dt = dt)   # doctest: +IGNORE_OUTPUT
...   floating_balloon.store(t)
>>> floating_balloon.plot('side')
>>> plt.gca().invert_yaxis()
>>> plt.show()
```

### `predict`

```python
predict(self, u: Optional[numpy.ndarray] = None, Q: Optional[numpy.ndarray] = None)
```

Predicts the filter's next state and covariance matrix based
on the current state and the process model.

### Parameters
u : numpy.ndarray, optional
    Control input. Defaults to None.
Q : numpy.ndarray, optional
    Process noise covariance matrix. Defaults to None.

### Raises
ValueError
    If `Q` is not missing (neither provided
    during construction nor passed to `predict`).
ValueError
    If a control input is provided, but the number of elements in `u`
    does not match the number of columns of the input matrix `G`.

### Examples
For more detailed usage,
see the examples in the introduction to
the `filters` module and
the `kalman` class.

Import required packages:

```python
>>> from c4dynamics.filters import kalman
```
Plain `predict` step
(predict in steady-state mode where the process variance matrix
remains constant
and is provided once to initialize the filter):

```python
>>> kf = kalman({'x': 0},
...       P0 = 0.5**2,
...       F = 1,
...       H = 1,
...       Q = 0.05,
...       R = 200,
...       steadystate = True
... )
>>> print(kf)
[ x ]
>>> kf.X          # doctest: +NUMPY_FORMAT
[0]
>>> kf.P          # doctest: +NUMPY_FORMAT
[[3.187...]]
>>> kf.predict()
>>> kf.X          # doctest: +NUMPY_FORMAT
[0]
>>> kf.P          # doctest: +NUMPY_FORMAT
[[3.187...]]
```
Predict with control input:

```python
>>> kf = kalman({'x': 0}, P0 = 0.5**2, F = 1, G = 150, H = 1, R = 200, Q = 0.05)
>>> kf.X  # doctest: +NUMPY_FORMAT
[0]
>>> kf.P          # doctest: +NUMPY_FORMAT
[[0.25...]]
>>> kf.predict(u = 1)
>>> kf.X      # doctest: +NUMPY_FORMAT
[150]
>>> kf.P  # doctest: +NUMPY_FORMAT
[[0.3]]
```
Predict with updated process noise covariance matrix:

```python
>>> kf = kalman({'x': 0}, P0 = 0.5**2, F = 1, G = 150, H = 1, R = 200, Q = 0.05)
>>> kf.X  # doctest: +NUMPY_FORMAT
[0]
>>> kf.P # doctest: +NUMPY_FORMAT
[[0.25]]
>>> kf.predict(u = 1, Q = 0.01)
>>> kf.X  # doctest: +NUMPY_FORMAT
[150]
>>> kf.P # doctest: +NUMPY_FORMAT
```
  [[0.26]]

### `store`

```python
store(self, t: int = -1)
```

Stores the current state and diagonal elements of the covariance matrix.

The `store` method captures the current state of the Kalman filter,
storing the state vector (`X`) and the error covariance matrix (`P`)
at the specified time.

### Parameters
t : int, optional
    The current time at which the state is being stored. Defaults to -1.

### Notes
1. The stored data can be accessed via `data`
   or other methods for
   post-analysis or visualization.
2. The elements on the main diagonal of the covariance matrix are named
   according to their position, starting with 'P' followed by their row and column indices.
   For example, the first element is named 'P00', and so on.
3. See also `store`
   and `data`
   for more details.

### Examples
For more detailed usage,
see the examples in the introduction to
the `filters` module and
the `kalman` class.

Import required packages:

```python
>>> from c4dynamics.filters import kalman
```

```python
>>> kf = kalman({'x': 0}, P0 = 0.5**2, F = 1, H = 1, Q = 0.05, R = 200)
>>> # store initial conditions
>>> kf.store()
>>> kf.predict()
>>> # store X after prediction
>>> kf.store()
>>> kf.update(z = 100)    # doctest: +NUMPY_FORMAT
[[0.00149...]]
>>> # store X after correct
>>> kf.store()
```
Access stored data:

```python
>>> kf.data('x')[1]  # doctest: +NUMPY_FORMAT
[0  0  0.15])
>>> kf.data('P00')[1]  # doctest: +NUMPY_FORMAT
```
  [0.25  0.3  0.299])

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

### `update`

```python
update(self, z: Optional[numpy.ndarray] = None, R: Optional[numpy.ndarray] = None, hx: Optional[numpy.ndarray] = None, innov: Optional[numpy.ndarray] = None, gate: Optional[float] = None)
```

Updates (corrects) the state estimate based on the given measurements.

### Parameters
z : numpy.ndarray, optional
    Measurement vector. Required unless `innov` is provided directly.
R : numpy.ndarray, optional
    Measurement noise covariance matrix. Defaults to None.
hx : numpy.ndarray, optional
    Predicted measurement, i.e. h(x), used to form the innovation
    as ``z - hx``. Defaults to the linear prediction ``H @ X``.
    Useful for a nonlinear measurement function whose output does
    not equal ``H @ X`` (as in `ekf`).
    Ignored if `innov` is provided directly.
innov : numpy.ndarray, optional
    The innovation (measurement residual) itself, overriding the
    default ``z - hx``. Use this when the residual is not a plain
    subtraction, for example a circular (angle-wrapped) measurement.
    `z` is not required when `innov` is given.
gate : float, optional
    Chi-squared gating threshold on the normalized innovation
    squared (NIS = ``innov.T @ inv(S) @ innov``, with
    ``S = H @ P @ H.T + R``). If the NIS exceeds `gate`, the update
    is rejected: `X` and `P` are left unchanged and `update`
    returns `None`. Defaults to `None` (no gating).

### Returns
K : numpy.ndarray or None
    Kalman gain, or `None` if the update was rejected by `gate`,
    or if ``S = H @ P @ H.T + R`` is numerically singular (in
    which case `X` and `P` are likewise left unchanged, exactly
    as for a gate rejection).

### Raises
ValueError
    If neither `z` nor `innov` is provided.
ValueError
    If the number of elements in `z` (or `innov`) does not match
    the number of rows in the measurement matrix H.
ValueError
    If `R` is missing (neither provided
    during construction
    nor passed to `update`).

### Examples
For more detailed usage,
see the examples in the introduction to
the `filters` module and
the `kalman` class.

Import required packages:

```python
>>> from c4dynamics.filters import kalman
```
Plain update step
(update in steady-state mode
where the measurement covariance matrix remains
and is provided once during filter initialization):

```python
>>> kf = kalman({'x': 0},
...       P0 = 0.5**2,
...       F = 1,
...       H = 1,
...       Q = 0.05,
...       R = 200,
...       steadystate = True
... )
>>> print(kf)
[ x ]
>>> kf.X   # doctest: +NUMPY_FORMAT
[0]
>>> kf.P                # doctest: +NUMPY_FORMAT
[[3.187...]]
>>> kf.update(z = 100)  # returns Kalman gain   # doctest: +NUMPY_FORMAT
[[0.0156...]]
>>> kf.X                # doctest: +NUMPY_FORMAT
[1.568...]
>>> kf.P                # doctest: +NUMPY_FORMAT
[[3.187...]]
```
Update with modified measurement noise covariance matrix:

```python
>>> kf = kalman({'x': 0}, P0 = 0.5**2, F = 1, G = 150, H = 1, R = 200, Q = 0.05)
>>> kf.X   # doctest: +NUMPY_FORMAT
[0]
>>> kf.P   # doctest: +NUMPY_FORMAT
[[0.25]]
>>> K = kf.update(z = 150, R = 0)
>>> K   # doctest: +NUMPY_FORMAT
[[1]]
>>> kf.X  # doctest: +NUMPY_FORMAT
[150]
>>> kf.P  # doctest: +NUMPY_FORMAT
```
  [[0]]

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

### `velocitymodel`

```python
velocitymodel(dt: float, process_noise: float, measure_noise: float)
```

Defines a linear Kalman filter model for tracking position and velocity.

### Parameters
dt : float
    Time step for the system model.
process_noise : float
    Standard deviation of the process noise.
measure_noise : float
    Standard deviation of the measurement noise.

### Returns
kf : kalman
    A Kalman filter object initialized with the linear system model.

X = [x, y, w, h, vx, vy]
#    0  1  2  3  4   5

x'  = vx
y'  = vy
w'  = 0
h'  = 0
vx' = 0
vy' = 0

H = [1 0 0 0 0 0
    0 1 0 0 0 0
    0 0 1 0 0 0
    0 0 0 1 0 0]

