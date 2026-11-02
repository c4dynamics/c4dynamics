# quatbody

A rigid-body object with a quaternion attitude

The `quatbody` is the quaternion replicate of the
`rigidbody`.
It extends the
`datapoint`
class to form an elementary rigidbody object in space, i.e.
an object with length and attitude,
where the attitude is represented by a unit quaternion
rather than by Euler angles.

The dynamics model is the same model of the
`rigidbody`.
However, the Euler angles kinematics are singular at
$\theta = \pm 90°$ (gimbal lock), while the quaternion
kinematics are not. This makes the `quatbody` suitable
for agile vehicles, such as drones, that may
reach any attitude (e.g. flips).

Its state vector consists of the following variables:

$$
X = [x, y, z, v_x, v_y, v_z, q_w, q_x, q_y, q_z, p, q, r]^T
$$
- Position coordinates, velocity coordinates.
- Attitude quaternion (scalar first), angular rates.

The quaternion $[q_w, q_x, q_y, q_z]$ represents
the same attitude as the 3-2-1 Euler angles
$[\varphi, \theta, \psi]$ of the
`rigidbody`
(see `euler2quat`).
The Euler angles `phi`, `theta`, `psi`
are available as properties that are derived from the quaternion.

**Arguments**

x : float or int, optional
    The x-position of the datapoint. Default value $x = 0$.
y : float or int, optional
    The y-position of the datapoint. Default value $y = 0$.
z : float or int, optional
    The z-position of the datapoint. Default value $z = 0$.
vx : float or int, optional
    Component of velocity along the x-axis. Default value $v_x = 0$.
vy : float or int, optional
    Component of velocity along the y-axis. Default value $v_y = 0$.
vz : float or int, optional
    Component of velocity along the z-axis. Default value $v_z = 0$.
phi : float or int, optional
    Initial Euler angle representing rotation around the x-axis (rad). Default value
    $\varphi = 0$.
theta : float or int, optional
    Initial Euler angle representing rotation around the y-axis (rad). Default value
    $\theta = 0$.
psi : float or int, optional
    Initial Euler angle representing rotation around the z-axis (rad). Default value
    $\psi = 0$.
p : float or int, optional
    Angular rate around the x-axis (roll). (rad/sec). Default value $p = 0$.
q : float or int, optional
    Angular rate around the y-axis (pitch). (rad/sec). Default value $q = 0$.
r : float or int, optional
    Angular rate around the z-axis (yaw). (rad/sec). Default value $r = 0$.
quat : array_like, optional
    Initial attitude quaternion $[q_w, q_x, q_y, q_z]$.
    If provided, it overrides `phi`, `theta`, and `psi`. The
    quaternion is normalized. Default value: `None`.

The initial attitude is provided either by Euler angles,
as in the `rigidbody`,
or directly by a quaternion.
The vector of initial conditions can be retrieved by calling
`quatbody.X0`:

```python
>>> from c4dynamics import quatbody
```

```python
>>> qb = quatbody(z = 10, psi = 90 * c4d.d2r, r = 0.5)
>>> qb.X0 # doctest: +NUMPY_FORMAT
[0  0  10  0  0  0  0.707  0  0  0.707  0  0  0.5]
```
### Note
The quaternion components are named $q_w, q_x, q_y, q_z$
(`qw`, `qx`, `qy`, `qz`) rather than $q_0, ..., q_3$,
since the `0` suffix of a state variable is reserved for its
initial value (e.g. `q0` is the initial pitch rate,
see `state.X0`).

Parameters
==========

mass : float
    The mass of the datapoint
I : [float, float, float]
    An array of moments of inertia

See Also
========
.lib
.rigidbody
.rotmat
.state
.eqm

Example
=======

A quadcopter performs a back flip: it starts at a level attitude
with a pitch rate of one revolution per second, and
rotates freely (no external forces nor moments) for one second.

The Euler angles kinematics of a
`rigidbody`
cross the singularity at $\theta = 90°$.
The quaternion kinematics of the `quatbody` remain regular
along the entire maneuver.

import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial conditions:

```python
>>> dt = 0.001
>>> drone = c4d.quatbody(z = 10, q = 2 * np.pi)
>>> drone.I = [0.0082, 0.0082, 0.0149]
>>> drone.mass = 1.2
```
Main loop:

```python
>>> for t in np.arange(0, 1, dt):
...   drone.store(t)
...   drone.inteqm(np.zeros(3), np.zeros(3), dt)  # doctest: +IGNORE_OUTPUT
```
After a full revolution the quaternion returns to
the level attitude (up to the sign):

```python
>>> drone.store(1)
>>> np.abs(drone.quat)  # doctest: +NUMPY_FORMAT
[1  0  0  0]
```
The pitch component of the quaternion,
$q_y = sin(q \cdot t / 2)$, goes smoothly through the
entire revolution:

```python
>>> _, ax = plt.subplots(2, 1)
>>> drone.plot('qw', ax = ax[0])
>>> ax[0].set(xlabel = '')  # doctest: +IGNORE_OUTPUT
>>> drone.plot('qy', ax = ax[1])
```

The `animate` method allows the user to play the attitude
histories given a 3D model (requires installation of `open3D`),
exactly as with the
`rigidbody.animate`.

### `BR`

```python
BR(self)
```

Returns a Body-from-Reference Direction Cosine Matrix (DCM).

Based on the current attitude quaternion $[q_w, q_x, q_y, q_z]$,
`BR` returns the DCM that is calculated by the
`quat2dcm` function
and is given by:

$$
R = \begin{bmatrix}
1 - 2(q_y^2 + q_z^2)
& 2(q_x q_y + q_w q_z)
& 2(q_x q_z - q_w q_y) \\
2(q_x q_y - q_w q_z)
& 1 - 2(q_x^2 + q_z^2)
& 2(q_y q_z + q_w q_x) \\
2(q_x q_z + q_w q_y)
& 2(q_y q_z - q_w q_x)
& 1 - 2(q_x^2 + q_y^2)
\end{bmatrix}
$$
The matrix is identical to the DCM in a 3-2-1 order
(`dcm321`) of the same attitude.

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
>>> qb = c4d.quatbody(psi = 45 * c4d.d2r)
>>> v_body = qb.BR @ v_inertial
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
The moments of inertia determine how much torque is
required for a desired angular acceleration about a rotational axis.

In this example, two drones with the same yaw torque
and different moments of inertia about the z axis
are compared.
The drone with the larger moment of inertia accelerates slower:

$$
\dot{r} = {M_z \over I_{zz}}
$$
Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial condtions:

```python
>>> dt = 0.01
>>> torque = [0, 0, 0.01]
>>> light = c4d.quatbody()
>>> light.I = [0.0082, 0.0082, 0.0149]
>>> heavy = c4d.quatbody()
>>> heavy.I = [0.0164, 0.0164, 0.0298]
```
Main loop

```python
>>> for ti in np.arange(0, 2, dt):
...   light.inteqm(np.zeros(3), torque, dt)  # doctest: +IGNORE_OUTPUT
...   light.store(ti)
...   heavy.inteqm(np.zeros(3), torque, dt)  # doctest: +IGNORE_OUTPUT
...   heavy.store(ti)
```
Plot results:

```python
>>> light.plot('psi')
>>> heavy.plot('psi', ax = plt.gca(), color = 'c')
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

Based on the current attitude quaternion, `RB` returns the
transpose matrix of `BR`,
where `BR`
is the Body from Reference DCM:

$$
R = \begin{bmatrix}
1 - 2(q_y^2 + q_z^2)
& 2(q_x q_y - q_w q_z)
& 2(q_x q_z + q_w q_y) \\
2(q_x q_y + q_w q_z)
& 1 - 2(q_x^2 + q_z^2)
& 2(q_y q_z - q_w q_x) \\
2(q_x q_z - q_w q_y)
& 2(q_y q_z + q_w q_x)
& 1 - 2(q_x^2 + q_y^2)
\end{bmatrix}
$$
For the background material regarding the rotational matrix operations,
see `rotmat`.

### Returns
out : numpy.ndarray
    A 3x3 DCM matrix uses to rotate a vector from a body frame
    to a reference frame of coordinates.

### Example
```python
>>> v_body = [np.sqrt(3), 0, 1]
>>> qb = c4d.quatbody(theta = 30 * c4d.d2r)
>>> v_inertial = qb.RB @ v_body
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
>>> qb = c4d.quatbody(q = q0)
>>> qb.ang_rates # doctest: +NUMPY_FORMAT
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
The 3-2-1 Euler angles are derived from the attitude quaternion
(see `quat2euler`).

### Returns
out : numpy.array
    An array of three Euler angles, about each one of the axes
    $([\varphi, \theta, \psi])$

### Examples
```python
>>> qb = c4d.quatbody(phi = 135 * c4d.d2r)
>>> qb.angles * c4d.r2d # doctest: +NUMPY_FORMAT
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

### `data`

```python
data(self, var=None, scale=1.0)
```

Returns arrays of stored time and data.

Extends `state.data()`
with the Euler angles `phi`, `theta`, `psi`, which are
derived from the stored quaternion histories
(see `quat2euler`).
For every other variable, the behavior is identical to
`state.data()`.

### Parameters
var : str, optional
    The name of the variable or parameter of the required histories.
    In addition to the state variables and the parameters,
    `phi`, `theta`, `psi` are supported.
scale : float or int, optional
    A scaling factor to apply to the variable values. Defaults to `1`.

### Returns
out : tuple of numpy.array or numpy.array
    A tuple of the time and the variable histories,
    or the entire state histories if `var` is not provided.

### Examples
```python
>>> qb = c4d.quatbody()
>>> for t in [0, 1, 2]:
...   qb.psi = t * 10 * c4d.d2r
...   qb.store(t)
>>> qb.data('psi', c4d.r2d)  # doctest: +NUMPY_FORMAT
```
  (array([0, 1, 2]), array([0, 10, 20]))

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

Advances the state vector, `quatbody.X`,
with respect to the input
forces and moments on a single step of time, `dt`.

Integrates equations of six degrees motion using the Runge-Kutta method.

This method numerically integrates the equations of motion for a dynamic system
using the fourth-order Runge-Kutta method as given by
`eqm.int6q`.

The derivatives of the equations are of six dimensional motion
with quaternion attitude kinematics as given by
:py`eqm.eqm6q`.
The quaternion is normalized at the end of each step.

### Parameters
forces : numpy.array or list
    An external forces vector acting on the body, `forces = [Fx, Fy, Fz]`
moments : numpy.array or list
    An external moments vector acting on the body, `moments = [Mx, My, Mz]`
dt : float or int
    Interval time step for integration.

### Returns
out : numpy.float64
    An acceleration array at the final time step,
    $[dv_x, dv_y, dv_z, dp, dq, dr]$.

### Warning
This method is not recommanded when the vectors
of forces or moments depend on the state variables.
Since the vectors of forces and moments are provided once at the
entrance to the integration, they remain constant
for the entire steps.
Therefore, when the forces or moments depend on the state variables
the results of this method are not accurate and may lead to instability.

### Examples
A drone applies a roll torque to perform a half roll
and then stops the rotation by an opposite torque,
ending up inverted ($q_x \approx 1$, i.e. $\varphi \approx 180°$).

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```
Settings and initial conditions:

```python
>>> dt = 0.001
>>> drone = c4d.quatbody()
>>> drone.I = [0.0082, 0.0082, 0.0149]
```
Main loop:

```python
>>> for ti in np.arange(0, 1, dt):
...   torque = [0.1, 0, 0] if ti < 0.5 else [-0.1, 0, 0]
...   drone.inteqm(np.zeros(3), torque, dt)  # doctest: +IGNORE_OUTPUT
...   drone.store(ti)
```
Plot results:

```python
>>> _, ax = plt.subplots(2, 1, gridspec_kw = {'hspace': 0.5})
>>> drone.plot('p', ax = ax[0])
>>> ax[0].set(xlabel = '')  # doctest: +IGNORE_OUTPUT
>>> drone.plot('qx', ax = ax[1])
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

### `phi`

```python
phi(self)
```

Gets and sets the Euler roll angle, $\varphi$ (rad).

The angle is derived from the attitude quaternion.
Setting the angle updates the quaternion while
the other two Euler angles are kept.

### Examples
```python
>>> qb = c4d.quatbody(theta = 10 * c4d.d2r)
>>> qb.phi = 20 * c4d.d2r
>>> qb.angles * c4d.r2d  # doctest: +NUMPY_FORMAT
```
  [20  10  0]

### `plot`

```python
plot(self, var, scale=1, ax=None, filename=None, darkmode=True, **kwargs)
```

Draws plots of trajectories or variable evolution over time.

`var` can be each one of the state variables, the Euler angles
`phi`, `theta`, `psi`, or `top`, `side`, for trajectories.

### Parameters
var : str
    The variable to be plotted.
    Possible variables for trajectories: `top`, `side`.
    For time evolution, any one of the state variables is possible:
    `x`, `y`, `z`, `vx`, `vy`, `vz`, `qw`, `qx`, `qy`, `qz`, `p`, `q`, `r`,
    and the Euler angles `phi`, `theta`, `psi`
    (derived from the quaternion histories).

scale : float or int, optional
    A scaling factor to apply to the variable values. Defaults to `1`.

ax : matplotlib.axes.Axes, optional
    An existing Matplotlib axis to plot on.
    If None, a new figure and axis will be created. By default None.

filename : str, optional
    Full file name to save the plot image.
    If None, the plot will not be saved, by default None.

darkmode : bool, optional
    Plot in a dark background style. By default True.

**kwargs : dict, optional
    Additional key-value arguments passed to `matplotlib.pyplot.plot`.
    These can include any keyword arguments accepted by `plot`,
    such as `color`, `linestyle`, `marker`, etc.

### Notes
- The method overrides the
  `datapoint.plot`.
- As in the `rigidbody`,
  Euler angles and angular rates are plotted in degrees
  and degrees per second, respectively.
- The quaternion components are plotted unitless.

### Examples
```python
>>> import c4dynamics as c4d
>>> import numpy as np
```

```python
>>> dt = 0.01
>>> drone = c4d.quatbody(r = 90 * c4d.d2r)
>>> drone.I = [0.0082, 0.0082, 0.0149]
>>> for ti in np.arange(0, 1, dt):
...   drone.inteqm(np.zeros(3), np.zeros(3), dt)  # doctest: +IGNORE_OUTPUT
...   drone.store(ti)
>>> drone.plot('psi')
```

### `psi`

```python
psi(self)
```

Gets and sets the Euler yaw angle, $\psi$ (rad).

The angle is derived from the attitude quaternion.
Setting the angle updates the quaternion while
the other two Euler angles are kept.

### Examples
```python
>>> qb = c4d.quatbody()
>>> qb.psi = 45 * c4d.d2r
>>> qb.quat  # doctest: +NUMPY_FORMAT
```
  [0.924  0  0  0.383]

### `quat`

```python
quat(self)
```

Gets and sets the attitude quaternion.

$$
quat = [q_w, q_x, q_y, q_z]
$$
The quaternion is scalar first (Hamilton convention).
A set quaternion is normalized to a unit quaternion.

### Parameters
quat : numpy.array or list
    A quaternion $[q_w, q_x, q_y, q_z]$.

### Returns
out : numpy.array
    The attitude quaternion $[q_w, q_x, q_y, q_z]$.

### Examples
```python
>>> qb = c4d.quatbody(phi = 90 * c4d.d2r)
>>> qb.quat  # doctest: +NUMPY_FORMAT
[0.707  0.707  0  0]
```

```python
>>> qb.quat = [1, 0, 0, 1]
>>> qb.quat  # doctest: +NUMPY_FORMAT
[0.707  0  0  0.707]
>>> qb.angles * c4d.r2d  # doctest: +NUMPY_FORMAT
```
  [0  0  90]

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

### `theta`

```python
theta(self)
```

Gets and sets the Euler pitch angle, $\theta$ (rad).

The angle is derived from the attitude quaternion.
Setting the angle updates the quaternion while
the other two Euler angles are kept.

### Examples
```python
>>> qb = c4d.quatbody()
>>> qb.theta = 30 * c4d.d2r
>>> qb.theta * c4d.r2d  # doctest: +NUMPY_FORMAT
```
  30

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

