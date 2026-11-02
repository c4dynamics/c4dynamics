# lowpass

A first-order low-pass filter for smoothing signals,
supporting both discrete and continuous systems.

### Parameters
alpha : float, optional
    Smoothing factor for a discrete system. Must be in the range (0, 1). Defaults to None.
dt : float, optional
    Time step for a continuous system. Must be positive. Defaults to None.
tau : float, optional
    Time constant for a continuous system. Must be positive. Defaults to None.
y0 : float, optional
    Initial value of the state. Defaults to 0.

### Raises
ValueError
    If neither `alpha` nor both `dt` and `tau` are provided.
    If `alpha` is out of the range (0, 1) for a discrete system.
    If `dt` or `tau` is non-positive for a continuous system.

### Notes
- For a continuous system, `dt` and `tau` are required, and `alpha` is calculated as `dt / tau`.
- For a discrete system, `alpha` alone is required and directly specifies the smoothing factor.

### Example
```python
>>> filter_continuous = lowpass(dt=0.01, tau=0.1, y0=0)
>>> filter_discrete = lowpass(alpha=0.5, y0=1)
>>> filter_continuous.sample(1.0) # doctest: +ELLIPSIS
0.09...
>>> filter_discrete.sample(2.0)
```
  1.5

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

### `sample`

```python
sample(self, x: float) -> float
```

Applies the low-pass filter to the input value and returns the filtered output.

### Parameters
x : float
    Input value to be filtered.

### Returns
float
    The filtered output value after applying the low-pass filter.

### Notes
- For a continuous system: `y'(t) = -y(t) / tau + x(t) / tau`
- For a discrete system: `y[k] = (1 - alpha) * y[k-1] + alpha * x[k]`
- The filter's state (`self.y`) is updated in place.

### Example
```python
>>> lp_filter = lowpass(alpha=0.5)
>>> lp_filter.sample(2.0)
1.0
>>> lp_filter.sample(3.0)
```
  2.0

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

