# eqm

## `eqm3`

```python
eqm3(dp: 'datapoint', F: Union[numpy.ndarray, list]) -> numpy.ndarray
```

Translational motion derivatives.

These equations represent a set of first-order ordinary
differential equations (ODEs) that describe the motion
of a datapoint in three-dimensional space under the influence
of external forces.

### Parameters
dp : `datapoint`
    C4dynamics' datapoint object for which the equations of motion are calculated.

F : array_like
    Force vector $[F_x, F_y, F_z]$

### Returns
out : numpy.array
    $[dx, dy, dz, dv_x, dv_y, dv_z]$
    6 derivatives of the equations of motion, 3 position derivatives,
    and 3 velocity derivatives.

### Examples
Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import numpy as np
```

```python
>>> dp = c4d.datapoint()
>>> dp.mass = 10                    # mass 10kg     # doctest: +IGNORE_OUTPUT
>>> F  = [0, 0, c4d.g_ms2]          # g_ms2 = 9.8m/s^2
>>> c4d.eqm.eqm3(dp, F)             # doctest: +NUMPY_FORMAT
array([0  0  0  0  0  0.980665])
```
Euler integration on the equations of motion of
mass in a free fall:

```python
>>> h0 = 10000
>>> pt = c4d.datapoint(z = 10000)
>>> while pt.z > 0:
...   pt.store()
...   dx = c4d.eqm.eqm3(pt, [0, 0, -c4d.g_ms2])
...   pt.X += dx  # (dt = 1)
>>> pt.plot('z')
>>> # comapre to anayltic solution
>>> t = np.arange(len(pt.data('t')))
>>> z = h0 - .5 * c4d.g_ms2 * t**2
>>> plt.gca().plot(t[z > 0], z[z > 0], 'c', linewidth = 1) # doctest: +IGNORE_OUTPUT
```

## `eqm6`

```python
eqm6(rb: 'rigidbody', F: Union[numpy.ndarray, list], M: Union[numpy.ndarray, list]) -> numpy.ndarray
```

Translational and angular motion derivatives.

A set of first-order ordinary
differential equations (ODEs) that describe the motion
of a rigid body in three-dimensional space under the influence
of external forces and moments.

### Parameters
rb : `rigidbody`
    C4dynamics' rigidbody object for which the
    equations of motion are calculated on.
F : array_like
    Force vector $[F_x, F_y, F_z]$
M : array_like
    Moments vector $[M_x, M_y, M_z]$

### Returns
out : numpy.array
    $[dx, dy, dz, dv_x, dv_y, dv_z, d\varphi, d\theta, d\psi, dp, dq, dr]$

    12 total derivatives; 6 of translational motion, 6 of rotational motion.

### Examples
Euler integration on the equations of motion of
a stick fixed at one edge:

(mass: 0.5 kg, moment of inertia about y: 0.4 kg*m^2,
Length: 1m, initial Euler pitch angle: 80° (converted to radians))

Import required packages:

```python
>>> import c4dynamics as c4d
>>> import numpy as np
```
Settings and initial conditions

```python
>>> dt = 0.5e-3
>>> t = np.arange(0, 10, dt)
>>> length =  1  # metter
>>> rb = c4d.rigidbody(theta = 80 * c4d.d2r)
>>> rb.mass = 0.5 # kg
>>> rb.I = [0, 0.4, 0]
```
Main loop:

```python
>>> for ti in t:
...    rb.store(ti)
...    tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
...    dx = c4d.eqm.eqm6(rb, np.zeros(3), [0, tau_g, 0])
...    rb.X += dx * dt
>>> rb.plot('theta')
```

## `eqm6q`

```python
eqm6q(qb: 'quatbody', F: Union[numpy.ndarray, list], M: Union[numpy.ndarray, list]) -> numpy.ndarray
```

Translational and angular motion derivatives, quaternion attitude.

The same six degrees of freedom model as
`eqm6`,
where the attitude kinematics are given by the
quaternion $q = [q_w, q_x, q_y, q_z]$
rather than by Euler angles:

$$
\dot{q} = {1 \over 2} \cdot q \otimes [0, p, q, r]
$$
i.e.:

$$
\dot{q}_w = -{1 \over 2} (q_x p + q_y q + q_z r)
\dot{q}_x = {1 \over 2} (q_w p + q_y r - q_z q)
\dot{q}_y = {1 \over 2} (q_w q - q_x r + q_z p)
\dot{q}_z = {1 \over 2} (q_w r + q_x q - q_y p)
$$
Unlike the Euler angles derivatives, the quaternion
derivatives are free of singularities (e.g. at $\theta = \pm 90°$).

### Parameters
qb : `quatbody`
    C4dynamics' quatbody object for which the
    equations of motion are calculated on.
F : array_like
    Force vector $[F_x, F_y, F_z]$
M : array_like
    Moments vector $[M_x, M_y, M_z]$

### Returns
out : numpy.array
    $[dx, dy, dz, dv_x, dv_y, dv_z, dq_w, dq_x, dq_y, dq_z, dp, dq, dr]$

    13 total derivatives; 6 of translational motion, 7 of rotational motion.

### Examples
Euler integration on the equations of motion of
a stick fixed at one edge:

(mass: 0.5 kg, moment of inertia about y: 0.4 kg*m^2,
Length: 1m, initial pitch angle: 80° (converted to radians))

Import required packages:

```python
>>> import c4dynamics as c4d
>>> import numpy as np
```
Settings and initial conditions

```python
>>> dt = 0.5e-3
>>> t = np.arange(0, 10, dt)
>>> length =  1  # metter
>>> qb = c4d.quatbody(theta = 80 * c4d.d2r)
>>> qb.mass = 0.5 # kg
>>> qb.I = [0, 0.4, 0]
```
Main loop:

```python
>>> for ti in t:
...    qb.store(ti)
...    tau_g = -qb.mass * c4d.g_ms2 * length / 2 * c4d.cos(qb.theta)
...    dx = c4d.eqm.eqm6q(qb, np.zeros(3), [0, tau_g, 0])
...    qb.X += dx * dt
>>> qb.plot('theta')
```

## `int3`

```python
int3(dp: 'datapoint', forces: Union[numpy.ndarray, list], dt: float, derivs_out: bool = False) -> Union[NDArray[numpy.float64], Tuple[NDArray[numpy.float64], NDArray[numpy.float64]]]
```

A step integration of the equations of translational motion.

This method makes a numerical integration using the
fourth-order Runge-Kutta method.

The integrated derivatives are of three dimensional translational motion as
given by
`eqm3`.

The result is an integrated state in a single interval of time where the
size of the step is determined by the parameter `dt`.

### Parameters
dp : `datapoint`
    The datapoint which state vector is to be integrated.
forces : numpy.array or list
    An external forces array acting on the body.
dt : float
    Time step for integration.
derivs_out : bool, optional
    If true, returns the last three derivatives as an estimation for
    the acceleration of the datapoint.

### Returns
X : numpy.float64
    An integrated state.
dxdt4 : numpy.float64, optional
    The last three derivatives of the equations of motion.
    These derivatives can use as an estimation for the acceleration of the datapoint.
    Returned if `derivs_out` is set to `True`.

**Algorithm**

The integration steps follow the Runge-Kutta method:

1. Compute k1 = f(ti, yi)

2. Compute k2 = f(ti + dt / 2, yi + dt * k1 / 2)

3. Compute k3 = f(ti + dt / 2, yi + dt * k2 / 2)

4. Compute k4 = f(ti + dt, yi + dt * k3)

5. Update yi = yi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

### Examples
Runge-Kutta integration of the equations of motion on a mass in a free fall
(compare to the same example in `eqm3`
with Euler integration):

Import required packages

```python
>>> import c4dynamics as c4d
```

```python
>>> pt = c4d.datapoint(z = 10000)
>>> while pt.z > 0:
...   pt.store()
...   pt.X = c4d.eqm.int3(pt, [0, 0, -c4d.g_ms2], dt = 1)
```

## `int6`

```python
int6(rb: 'rigidbody', forces: Union[numpy.ndarray, list], moments: Union[numpy.ndarray, list], dt: float, derivs_out: bool = False) -> Union[NDArray[numpy.float64], Tuple[NDArray[numpy.float64], NDArray[numpy.float64]]]
```

A step integration of the equations of motion.

This method makes a numerical integration using the
fourth-order Runge-Kutta method.

The integrated derivatives are of three dimensional translational motion as
given by
`eqm6`.

The result is an integrated state in a single interval of time where the
size of the step is determined by the parameter `dt`.

### Parameters
dp : `datapoint`
    The datapoint which state vector is to be integrated.
forces : numpy.array or list
    An external forces array acting on the body.
dt : float
    Time step for integration.
derivs_out : bool, optional
    If true, returns the last three derivatives as an estimation for
    the acceleration of the datapoint.

### Returns
X : numpy.float64
    An integrated state.
dxdt4 : numpy.float64, optional
    The last six derivatives of the equations of motion.
    These derivatives can use as an estimation for the
    translational and angular acceleration of the datapoint.
    Returned if `derivs_out` is set to `True`.

**Algorithm**

The integration steps follow the Runge-Kutta method:

1. Compute k1 = f(ti, yi)

2. Compute k2 = f(ti + dt / 2, yi + dt * k1 / 2)

3. Compute k3 = f(ti + dt / 2, yi + dt * k2 / 2)

4. Compute k4 = f(ti + dt, yi + dt * k3)

5. Update yi = yi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

### Examples
In the following example, the equations of motion of a
cylinderical body are integrated by using the
`int6`.

The results are compared to the results of the same equations
integrated by using `scipy.odeint`.

1. `int6`

Import required packages

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> from scipy.integrate import odeint
>>> import numpy as np
```
Settings and initial conditions

```python
>>> dt = 0.5e-3
>>> t  = np.arange(0, 10, dt)
>>> theta0 =  80 * c4d.d2r       # deg
>>> q0     =  0 * c4d.d2r        # deg to sec
>>> Iyy    =  .4                 # kg * m^2
>>> length =  1                  # meter
>>> mass   =  0.5                # kg
```
Define the cylinderical-rigidbody object

```python
>>> rb = c4d.rigidbody(theta = theta0, q = q0)
>>> rb.I = [0, Iyy, 0]
>>> rb.mass = mass
```
Main loop:

```python
>>> for ti in t:
...   rb.store(ti)
...   tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
...   rb.X = c4d.eqm.int6(rb, np.zeros(3), [0, tau_g, 0], dt)
```

```python
>>> rb.plot('theta')
```

2. `scipy.odeint`

```python
>>> def pend(y, t):
...  theta, omega = y
...  dydt = [omega, -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(theta) / Iyy]
...  return dydt
>>> sol = odeint(pend, [theta0, q0], t)
```
Compare to `int6`:

```python
>>> plt.plot(*rb.data('theta', c4d.r2d),
...       'm',
...       label = 'c4dynamics.int6'
... )  # doctest: +IGNORE_OUTPUT
>>> plt.plot(t, sol[:, 0] * c4d.r2d, 'c', label = 'scipy.odeint') # doctest: +IGNORE_OUTPUT
>>> c4d.plotdefaults(plt.gca(),
...       'Equations of Motion Integration ($\theta$)',
...       'Time',
...       'degrees',
...       fontsize = 12
... )
>>> plt.legend() # doctest: +IGNORE_OUTPUT
```

**Note - Differences Between Scipy and C4dynamics Integration**

The difference in the results derive from the method of delivering the
forces and moments.
scipy.odeint gets as input the function that caluclates the derivatives,
where the forces and moments are included in it:

`dydt = [omega, -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(theta) / Iyy]`

This way, the forces and moments are recalculated for each step of
the integration.

c4dynamics.eqm.int6 on the other hand, gets the vectors of forces and moments
only once when the function is called and therefore refer to them as constant
for the four steps of integration.

When external factors may vary quickly over time and a high level of
accuracy is required, using other methods, like scipy.odeint, is recommanded.
If computational resources are available, a decrement of the step-size
may be a workaround to achieve high accuracy results.

## `int6q`

```python
int6q(qb: 'quatbody', forces: Union[numpy.ndarray, list], moments: Union[numpy.ndarray, list], dt: float, derivs_out: bool = False) -> Union[NDArray[numpy.float64], Tuple[NDArray[numpy.float64], NDArray[numpy.float64]]]
```

A step integration of the equations of motion, quaternion attitude.

This method makes a numerical integration using the
fourth-order Runge-Kutta method.

The integrated derivatives are of six dimensional motion
with quaternion attitude kinematics as given by
`eqm6q`.

The result is an integrated state in a single interval of time where the
size of the step is determined by the parameter `dt`.
At the end of the step, the quaternion is normalized
to a unit quaternion to prevent numerical drift.

### Parameters
qb : `quatbody`
    The quatbody which state vector is to be integrated.
forces : numpy.array or list
    An external forces array acting on the body.
moments : numpy.array or list
    An external moments array acting on the body.
dt : float
    Time step for integration.
derivs_out : bool, optional
    If true, returns the translational and angular accelerations
    of the last step.

### Returns
X : numpy.float64
    An integrated state.
dxdt4 : numpy.float64, optional
    The translational and angular accelerations
    $[dv_x, dv_y, dv_z, dp, dq, dr]$ of the last step.
    Returned if `derivs_out` is set to `True`.

**Algorithm**

The integration steps follow the Runge-Kutta method:

1. Compute k1 = f(ti, yi)

2. Compute k2 = f(ti + dt / 2, yi + dt * k1 / 2)

3. Compute k3 = f(ti + dt / 2, yi + dt * k2 / 2)

4. Compute k4 = f(ti + dt, yi + dt * k3)

5. Update yi = yi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

6. Normalize the quaternion.

### Examples
The equations of motion of a
cylinderical body are integrated by using
`int6q`.

Import required packages

```python
>>> import c4dynamics as c4d
>>> import numpy as np
```
Settings and initial conditions

```python
>>> dt = 0.5e-3
>>> t  = np.arange(0, 10, dt)
>>> theta0 =  80 * c4d.d2r       # deg
>>> Iyy    =  .4                 # kg * m^2
>>> length =  1                  # meter
>>> mass   =  0.5                # kg
```
Define the cylinderical-quatbody object

```python
>>> qb = c4d.quatbody(theta = theta0)
>>> qb.I = [0, Iyy, 0]
>>> qb.mass = mass
```
Main loop:

```python
>>> for ti in t:
...   qb.store(ti)
...   tau_g = -qb.mass * c4d.g_ms2 * length / 2 * c4d.cos(qb.theta)
...   qb.X = c4d.eqm.int6q(qb, np.zeros(3), [0, tau_g, 0], dt)
```

```python
>>> qb.plot('theta')
```

## `quadeqm`

```python
quadeqm(t, X, quad, rotor_speeds, frame='NED')
```

Quadcopter equations of motion.

Computes the force and the moment of
`quadforces`, adds gravity,
and returns the state derivatives of
`eqm6` for a 12-state (euler angles)
vector or of `eqm6q` for a 13-state
(quaternion) vector. The signature fits
`scipy.integrate.solve_ivp`:

```python
sol = solve_ivp(c4d.eqm.quadeqm, [t, t + dt], quad.X, args = (quad, rotor_speeds, 'ENU'))
quad.X = sol.y[:, -1]
```
### Parameters
t : float
    Time [s]. Unused (the model is time invariant), kept for
    `scipy.integrate.solve_ivp`.
X : array_like
    State vector, 12 entries (euler angles) or 13 (quaternion). See
    `quadforces`.
quad : object
    The vehicle parameters as attributes: ``m`` mass [kg], ``g``
    gravity [m/s^2], ``Ixx, Iyy, Izz`` principal moments of inertia
    [kg.m^2], and the parameters of
    `quadforces`.
rotor_speeds : array_like
    The four rotor speeds [rad/s], held constant over the call.
frame : {'NED', 'ENU'}, optional
    Inertial frame convention: ``'NED'`` with a forward-right-down body
    frame (gravity along +z), ``'ENU'`` with a forward-left-up body frame
    (gravity along -z). Defaults ``'NED'``.

### Returns
dX : numpy.ndarray
    State derivatives, the same length as `X`.

### Examples
At hover, the thrust carries the weight and the vehicle stays put:

```python
>>> import c4dynamics as c4d
>>> import numpy as np
>>> quad = c4d.struct(m=0.468, g=9.81, Ixx=4.856e-3, Iyy=4.856e-3, Izz=8.801e-3,
...                   kT=2.98e-6, kQ=1.14e-7, l=0.225, Ax=0.3, Ay=0.3, Az=0.25, Ar=0.2)
>>> w_hover = np.sqrt(quad.m * quad.g / 4 / quad.kT)
>>> dX = c4d.eqm.quadeqm(0, np.zeros(12), quad, [w_hover] * 4, 'ENU')
>>> np.allclose(dX, 0)
True
```
The same vehicle with a quaternion attitude:

```python
>>> X = np.zeros(13)
>>> X[6] = 1   # identity quaternion
>>> np.allclose(c4d.eqm.quadeqm(0, X, quad, [w_hover] * 4, 'ENU'), 0)
```
    True

## `quadforces`

```python
quadforces(X, quad, rotor_speeds, frame='NED')
```

Body-frame force and moment acting on a quadcopter.

The force is the rotor thrust plus the linear aerodynamic drag, without
gravity. The moment is the rotor thrust and reaction torques, the
rotational drag and the rotor gyroscopic coupling.
`quadeqm` adds gravity and
integrates both through the rigid-body equations of motion.

### Parameters
X : array_like
    State vector. 12 entries for an euler-angles body
    (`rigidbody`):
    ``[x, y, z, vx, vy, vz, phi, theta, psi, p, q, r]``,
    or 13 entries for a quaternion body
    (`quatbody`):
    ``[x, y, z, vx, vy, vz, qw, qx, qy, qz, p, q, r]``.
quad : object
    The vehicle parameters as attributes:
    ``kT`` thrust coefficient [N/(rad/s)^2],
    ``kQ`` torque coefficient [N.m/(rad/s)^2],
    ``Ax, Ay, Az`` linear drag along the body axes [N/(m/s)],
    ``Ar`` rotational drag [N.m/(rad/s)],
    ``IR`` rotor inertia [kg.m^2] (optional, default 0),
    ``wind`` wind velocity in the inertial frame [m/s] (optional,
    default still air; the drag acts on the air-relative velocity),
    and the rotor geometry: either ``rotor_pos`` (4 x 2, body x, y of
    each rotor [m], in the body frame of `frame`) with ``rotor_dir``
    (4, +1 counterclockwise seen from above, -1 clockwise, default
    ``[1, 1, -1, -1]``), or ``l`` [m] for an x configuration in the motor
    order front-right, rear-left, front-left, rear-right.
rotor_speeds : array_like
    The four rotor speeds [rad/s].
frame : {'NED', 'ENU'}, optional
    Inertial frame convention. ``'NED'`` with a forward-right-down body
    frame, ``'ENU'`` with a forward-left-up body frame. Defaults ``'NED'``.

### Returns
F_b : numpy.ndarray
    Body-frame force, thrust plus drag [N].
M_b : numpy.ndarray
    Body-frame moment [N.m].

### Note
``F_b / m`` is the specific force an accelerometer at the center of
mass measures.

### Examples
```python
>>> import c4dynamics as c4d
>>> import numpy as np
>>> quad = c4d.struct(kT=3e-6, kQ=1e-7, l=0.2, Ax=0.3, Ay=0.3, Az=0.25, Ar=0.2)
>>> X = np.zeros(12)
>>> F_b, M_b = c4d.eqm.quadforces(X, quad, [600, 600, 600, 600])
>>> F_b   # doctest: +NUMPY_FORMAT
[0  0  -4.32]
>>> M_b   # doctest: +NUMPY_FORMAT
```
    [0  0  0]

