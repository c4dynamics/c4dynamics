Vehicles
========


:doc:`Dynamics </concepts/dynamics>` gave the equations of motion
that turn a force and a moment into the motion of a body.
These equations do not depend on the vehicle.
The use cases of c4dynamics, however, fly, drive, and steer different vehicles:
a quadcopter, a missile, a car, and a helicopter.

What makes a quadcopter different from a missile is not the equations of motion,
but the physics that generates the forces and the moments:
rotors that push along one body axis,
a rocket motor and a body that produces lift as it meets the air at an angle,
tires that hold the car on its path,
or a pivot that constrains the helicopter to two rotations.
The control inputs act on the vehicle only through these forces and moments.
This page describes the force and moment model of each vehicle:
what produces the forces and the moments,
and how the control inputs shape them.

The workflow is shared by all the vehicles:

1. Define a :doc:`state object </concepts/states>` with the state variables of the vehicle.
2. Compute the forces and the moments from the vehicle physics and the control inputs.
3. Integrate the :ref:`equations of motion <dynamics-eqm>` over a time step and update the state.
4. Store the state and analyze the results.

The state object is the common interface between the vehicle and the algorithm.
The vehicle model changes, but the state object keeps the same interface:
:attr:`X <c4dynamics.states.state.state.X>` to get and set the state vector,
:meth:`store <c4dynamics.states.state.state.store>` and
:meth:`data <c4dynamics.states.state.state.data>` to record and retrieve the history,
and :meth:`plot <c4dynamics.states.state.state.plot>` to view it.
Therefore, a guidance law, a controller, or a filter that is developed on one vehicle
moves to another vehicle smoothly, by replacing the state object and the force model,
while the rest of the program remains intact.


.. list-table::
   :widths: 13 17 35 17 18
   :header-rows: 1

   * - Vehicle
     - Control inputs
     - Force and moment sources
     - Attitude
     - Model
   * - Quadcopter
     - Four rotor speeds
     - Rotor thrust and reaction torque, drag, gravity
     - Quaternion (or Euler angles)
     - :func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>`,
       :func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>`
   * - Missile
     - Fin deflections
     - Rocket thrust, aerodynamic lift and drag, aerodynamic moments, gravity
     - Euler angles
     - :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`
       with the aerodynamics of the use case
   * - Car
     - Steering rate
     - Tire forces, assumed to follow the steering (kinematic model)
     - Heading
     - Kinematic (unicycle) model
   * - Helicopter (2-DOF)
     - Two rotor voltages
     - Rotor torques, gravity about the pivot, friction
     - Pitch and yaw angles
     - Lagrangian pitch-yaw model



.. _vehicles-quadcopter:

Quadcopter
----------

A quadcopter has no control surfaces.
Every force and moment, other than gravity and drag, comes from four fixed rotors
that all point along the body *up* axis.
The control input is the vector of the four rotor speeds:

.. math::

  \mathbf{u} = [\Omega_1, \Omega_2, \Omega_3, \Omega_4]^T


**Frames**

The model supports the two common pairs of an earth frame and a body frame,
``'NED'`` and ``'ENU'``
(see :ref:`Reference Frames <transformations-frames>`).
The earth frame is treated as inertial, and is denoted :math:`I`.
Both conventions use the 3-2-1 rotation, and the Body from Inertial matrix is :math:`[BI]`.
The two conventions differ in the direction of *up* along the body :math:`z` axis,
denoted by the sign :math:`s`:

.. list-table::
   :widths: 20 40 40
   :header-rows: 1

   * - ``frame``
     - Body frame
     - :math:`s`
   * - ``'NED'``
     - :math:`x` forward, :math:`y` right, :math:`z` down (FRD)
     - :math:`-1`
   * - ``'ENU'``
     - :math:`x` forward, :math:`y` left, :math:`z` up (FLU)
     - :math:`+1`

The sign :math:`s` appears wherever the model depends on the frame:
the rotors thrust along :math:`s \cdot z_b`, and gravity acts along :math:`-s \cdot z`.

.. figure:: /_architecture/quad_frame_enu_flu.png
   :width: 60%

   Reference systems and rotor layout in the ``'ENU'`` convention.
   Earth (inertial) frame: ENU (east, north, up).
   Body frame: FLU (forward, left, up).
   Positive rotation about an axis is given by curling the right-hand fingers.
   Rotors rotation: 1: CCW (counterclockwise), 2: CCW, 3: CW (clockwise), 4: CW.


**Rotors**

Rotor :math:`i` is located at the body position :math:`(x_i, y_i)`
and spins at the speed :math:`\Omega_i` in the direction :math:`d_i`
(:math:`+1` counterclockwise seen from above, :math:`-1` clockwise).
It produces a thrust and a reaction torque, both proportional to the square of its speed:

.. math::

  \begin{aligned}
  F_i &= k_T \cdot \Omega_i^2 \\
  Q_i &= k_Q \cdot \Omega_i^2
  \end{aligned}

Where :math:`k_T` is the thrust coefficient, in N/(rad/s)²,
and :math:`k_Q` is the torque coefficient, in N·m/(rad/s)².

The default rotor layout is an :math:`X` configuration with the moment arm :math:`l`,
in the motor order of ArduPilot:

.. list-table::
   :widths: 15 25 35 25
   :header-rows: 1

   * - Rotor
     - Position
     - :math:`(x_i, y_i)`
     - :math:`d_i`
   * - 1
     - front-right
     - :math:`(l, -s \cdot l)`
     - :math:`+1` (CCW)
   * - 2
     - rear-left
     - :math:`(-l, s \cdot l)`
     - :math:`+1` (CCW)
   * - 3
     - front-left
     - :math:`(l, s \cdot l)`
     - :math:`-1` (CW)
   * - 4
     - rear-right
     - :math:`(-l, -s \cdot l)`
     - :math:`-1` (CW)

The factor :math:`s` in :math:`y_i` follows the body :math:`y` axis,
which points to the right in FRD and to the left in FLU.
Any other layout is given by the explicit attributes ``rotor_pos``
(the body :math:`(x_i, y_i)` of each rotor) and ``rotor_dir`` (the :math:`d_i`).


**Forces**

The body force is the total thrust along the body *up* axis
and a linear aerodynamic drag that opposes the air-relative velocity:

.. math::

  F_b = \begin{bmatrix} -A_x \cdot u_a \\ -A_y \cdot v_a \\ s \cdot \sum F_i - A_z \cdot w_a \end{bmatrix}

Where :math:`A_x, A_y, A_z` are the drag coefficients along the body axes,
and :math:`(u_a, v_a, w_a)` are the body components of the air-relative velocity
(see :doc:`Kinematics </concepts/kinematics>`):

.. math::

  [u_a, v_a, w_a]^T = [BI] \cdot (V - V_{wind})

:math:`V` is the inertial velocity of the state, and :math:`V_{wind}` is the wind velocity
in the earth frame (the optional attribute ``wind``).
In still air, :math:`(u_a, v_a, w_a)` equal the body components of the inertial velocity,
:math:`(u, v, w)`.

The force in the inertial frame, which enters the
:ref:`translational equations <dynamics-newton-euler>`, adds gravity:

.. math::

  F = [BI]^T \cdot F_b + \begin{bmatrix} 0 \\ 0 \\ -s \cdot m \cdot g \end{bmatrix}

The collective thrust is the only control force, and it acts along the body *up* axis.
To accelerate sideways, the vehicle must first tilt.
:math:`F_b / m` is the specific force, i.e. what an accelerometer at the center of mass measures.


**Moments**

Three mechanisms produce the body moment:

- The thrust of each rotor acts at its position, :math:`(x_i, y_i, 0) \times (0, 0, s \cdot F_i)`,
  and produces roll and pitch moments.
- The reaction torque of each rotor turns the body against the rotor's spin:
  a counterclockwise rotor turns the body clockwise seen from above.
  The reaction torques produce the yaw moment.
- The rotors spin, and their angular momentum,
  :math:`h = s \cdot I_R \cdot \sum d_i \cdot \Omega_i` along the body :math:`z` axis,
  rotates with the body. This adds the gyroscopic term :math:`-\omega \times h`,
  which is the :ref:`coupling term <dynamics-newton-euler>` of Euler's equations
  applied to the rotors.

With a rotational drag :math:`A_r` that opposes the angular rates, the body moment is:

.. math::

  \begin{aligned}
  M_x &= s \cdot \sum y_i \cdot F_i - A_r \cdot p - q \cdot h \\
  M_y &= -s \cdot \sum x_i \cdot F_i - A_r \cdot q + p \cdot h \\
  M_z &= -s \cdot \sum d_i \cdot Q_i - A_r \cdot r
  \end{aligned}

Where :math:`I_R` is the rotor moment of inertia.
The gyroscopic terms couple the roll and the pitch dynamics:
a pitch rate generates a roll moment, and a roll rate generates a pitch moment.
:math:`[M_x, M_y, M_z]` is the moment :math:`M` of the
:ref:`rotational equations <dynamics-newton-euler>`.


**Mixing**

A controller usually commands the total thrust and the three control torques,
:math:`[T, \tau_x, \tau_y, \tau_z]`,
i.e. the rotor parts of the force and the moments above.
For the :math:`X` layout, they are a linear function of the rotor thrusts:

.. math::

  \begin{bmatrix} T \\ \tau_x \\ \tau_y \\ \tau_z \end{bmatrix}
  = \begin{bmatrix}
      1 & 1 & 1 & 1 \\
      -l & l & l & -l \\
      -s \cdot l & s \cdot l & -s \cdot l & s \cdot l \\
      -s \cdot k_Q / k_T & -s \cdot k_Q / k_T & s \cdot k_Q / k_T & s \cdot k_Q / k_T
    \end{bmatrix}
    \begin{bmatrix} F_1 \\ F_2 \\ F_3 \\ F_4 \end{bmatrix}

The controller maps the commands to the rotor thrusts by the inverse of this mixing matrix,
and to the rotor speeds by :math:`\Omega_i = \sqrt{F_i / k_T}`.

Each of the four outputs has a physical meaning:

- **Collective thrust** :math:`T`: the sum of the rotor thrusts.
- **Roll torque** :math:`\tau_x`: a thrust difference between the left rotors (2, 3)
  and the right rotors (1, 4). It has the same sign in both conventions:
  positive roll lowers the right side, and is driven by the left rotors.
- **Pitch torque** :math:`\tau_y`: a thrust difference between the front rotors (1, 3)
  and the rear rotors (2, 4). Positive pitch raises the nose in FRD, and lowers it in FLU,
  hence the factor :math:`s`.
- **Yaw torque** :math:`\tau_z`: the sum of the reaction torques.
  When the counterclockwise pair spins faster than the clockwise pair,
  the torques do not cancel, and the vehicle turns clockwise seen from above,
  with little change in the total thrust.
  Clockwise seen from above is a negative rotation about the FLU :math:`z` (up),
  and a positive rotation about the FRD :math:`z` (down), hence the factor :math:`s`.


**Attitude**

A quadcopter can flip, roll, and point its *up* axis in any direction,
so it is a natural candidate for the quaternion representation
(see :ref:`Kinematics <kinematics-quaternion>`).
The attitude representation is independent of the force model:
:func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>` accepts a 13-state
:class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` as well as a 12-state
:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`.


**Implementation**

:func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>` returns the
body force (thrust and drag) and the body moment.
:func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>` rotates the force to the inertial frame,
adds gravity, and evaluates the equations of motion,
:func:`eqm6 <c4dynamics.eqm.derivs.eqm6>` for a 12-state vector
or :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>` for a 13-state vector,
with the signature of ``scipy.integrate.solve_ivp``.
The vehicle parameters (:math:`m, g, l, k_T, k_Q, I_{xx}, I_{yy}, I_{zz}, A_x, A_y, A_z, A_r, I_R`)
are attributes of the state object.
The parameters of the reference vehicle are given by
``c4dynamics.models.quad.default_quad_config()``.


**Example**

Define the quadcopter, speed up the counterclockwise rotors by 10%,
slow down the clockwise rotors by 10%, and integrate the equations of motion:

.. code::

  >>> import numpy as np
  >>> import c4dynamics as c4d
  >>> from scipy.integrate import solve_ivp
  >>> from c4dynamics.models.quad import default_quad_config

.. code::

  >>> quad = c4d.quatbody()
  >>> for k, v in default_quad_config().items():
  ...   setattr(quad, k, v)
  >>> w_hover = np.sqrt(quad.m * quad.g / 4 / quad.kT)          # rotor speed that carries the weight
  >>> rotor_speeds = w_hover * np.array([1.1, 1.1, 0.9, 0.9])   # ccw pair faster, cw pair slower

.. code::

  >>> F_b, M_b = c4d.eqm.quadforces(quad.X, quad, rotor_speeds, 'ENU')
  >>> F_b      # thrust along body up
  array([0, 0, 4.63...])
  >>> M_b      # a yaw moment only
  array([0, 0, -0.035...])

.. code::

  >>> dt = 0.01
  >>> for t in np.arange(0, 2, dt):
  ...   quad.store(t)
  ...   sol = solve_ivp(c4d.eqm.quadeqm, [t, t + dt], quad.X, args = (quad, rotor_speeds, 'ENU'))
  ...   quad.X = sol.y[:, -1]
  ...   quad.quat = quad.quat    # normalize to a unit quaternion

.. code::

  >>> print(quad)
  [ x  y  z  vx  vy  vz  qw  qx  qy  qz  p  q  r ]
  >>> quad.quat
  array([ 0.985...,  0.        ,  0.        , -0.170...])
  >>> quad.psi * c4d.r2d     # turns clockwise seen from above
  -19.6...

The reaction torques turn the vehicle about its *up* axis.
The quaternion is a rotation of :math:`\alpha = -19.6°` about :math:`z`:
:math:`q_w = \cos(\alpha / 2)`, :math:`q_z = \sin(\alpha / 2)`.
The total thrust is slightly above the weight, and the vehicle climbs slowly.
Replacing ``c4d.quatbody()`` by ``c4d.rigidbody()`` selects the Euler angles model
with no other change in the code.


**Use cases**

- :doc:`Cascade PID Control </programs/pid_cascade/quadcopter_pid>`:
  a cascade PID controller flies the quadcopter on a figure-eight trajectory.
- :doc:`EKF Estimation </programs/ekf_estimation/quad_ekf>`:
  an extended Kalman filter estimates the quadcopter state in closed loop with the controller.
- :doc:`ArduPilot Simulation </programs/ardupilot_sim/ardupilot_fig8>`:
  the ArduPilot flight controller flies a :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`
  quadcopter in a figure-eight.



.. _vehicles-missile:

Missile
-------

**State vector**

The missile is a rigid body with six degrees of freedom,
represented by a :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` object:

.. math::

  X = [x, y, z, v_x, v_y, v_z, \varphi, \theta, \psi, p, q, r]^T

The mass and the moments of inertia are attributes of the object,
:attr:`mass <c4dynamics.states.lib.datapoint.datapoint.mass>` and
:attr:`I <c4dynamics.states.lib.rigidbody.rigidbody.I>`,
and may be updated during the run, as the rocket motor burns its fuel.
A missile is axially symmetric, :math:`I_{yy} = I_{zz}`,
so its roll is decoupled from the pitch and the yaw
(see :ref:`Rotational Motion <dynamics-newton-euler>`).

The target is a point mass with three degrees of freedom, represented by a
:class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` object:

.. math::

  X = [x, y, z, v_x, v_y, v_z]^T


**Forces and moments**

The forces on the missile are the propulsion along the body :math:`x` axis,
the aerodynamic lift and drag, and gravity.
The propulsion and the aerodynamic forces are computed in the body frame and rotated to the
inertial frame by :attr:`RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>`.
The aerodynamic moments are computed in the body frame from the angles of attack
and the fins deflections.
The control input, the fins deflections, acts on the missile only through these
aerodynamic moments.

The forces and the moments enter the 6DOF equations of motion with Euler angles,
:func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`
(see :ref:`The Equations of Motion <dynamics-eqm>`),
integrated by :meth:`rigidbody.inteqm <c4dynamics.states.lib.rigidbody.rigidbody.inteqm>`.
The target is integrated by :meth:`datapoint.inteqm <c4dynamics.states.lib.datapoint.datapoint.inteqm>`
(:func:`eqm3 <c4dynamics.eqm.derivs.eqm3>`).


**Example**

Launch the missile at :math:`30°` pitch in a NED frame (:math:`z` down)
with a constant thrust, and propagate a non-maneuvering target:

.. code::

  >>> missile = c4d.rigidbody(vx = 30 * np.cos(30 * c4d.d2r), vz = -30 * np.sin(30 * c4d.d2r), theta = 30 * c4d.d2r)
  >>> missile.mass = 85               # kg
  >>> missile.I = [0.5, 61, 61]       # kg·m²
  >>> target = c4d.datapoint(x = 4000, z = -1000, vx = -250)

.. code::

  >>> dt = 0.01
  >>> for t in np.arange(0, 3, dt):
  ...   missile.store(t)
  ...   target.store(t)
  ...   thrust  = missile.RB @ [3000, 0, 0]               # body x to inertial
  ...   gravity = [0, 0, missile.mass * c4d.g_ms2]        # z down
  ...   missile.inteqm(thrust + gravity, [0, 0, 0], dt)   # forces, moments, dt
  ...   target.inteqm([0, 0, 0], dt)

.. code::

  >>> missile.vel_mag()
  123.8...
  >>> target.x
  3250.0...

In the use case, the moments of the aerodynamics and the control fins
replace the zero moments vector, and the guidance law closes the loop.


**Use cases**

- :doc:`Proportional Navigation Guidance </programs/pn_guidance/dof6sim>`:
  a 6DOF missile, guided by proportional navigation, intercepts a target.



.. _vehicles-car:

Car
---

**State vector**

The car is modeled in the plane, by its position and its heading.
It is represented by a :class:`state <c4dynamics.states.state.state>` object
with the state variables:

.. math::

  X = [x, y, \psi]^T

Where:

- :math:`x, y` are the position coordinates in the plane
- :math:`\psi` is the heading angle with respect to the :math:`x` axis


**Model**

The car is the one vehicle on this page that is modeled without forces.
The tires are assumed to hold the car on the path that the steering dictates,
with no slip.
Under this assumption, the motion is fully described by kinematics,
and the force and moment models are not needed.

At a constant speed :math:`V` (here a scalar, the magnitude of the velocity),
the kinematic (unicycle) model of the car is given by:

.. math::

  \begin{aligned}
  \dot{x} &= V \cdot \cos(\psi) \\
  \dot{y} &= V \cdot \sin(\psi) \\
  \dot{\psi} &= \delta
  \end{aligned}

Where :math:`\delta` is the steering input, the rate of change of the heading.

For a straight reference line along the :math:`x` axis,
the model is linearized about :math:`\psi = 0`.
The longitudinal motion decouples, and the lateral dynamics reduce to two state variables,
:math:`X = [\psi, y]^T`, with :math:`\dot{\psi} = \delta` and :math:`\dot{y} = V \cdot \psi`.
This is the prediction model of the MPC use case.


**Example**

Define the car with an initial lateral offset of 1 m,
steer it back to the line with a simple feedback,
and store the steering input as a parameter of the state:

.. code::

  >>> V = 22.3   # m/s
  >>> def car_model(t, X, delta):
  ...   x, y, psi = X
  ...   return [V * np.cos(psi), V * np.sin(psi), delta]

.. code::

  >>> car = c4d.state(x = 0, y = 1, psi = 0)
  >>> car.delta = 0

.. code::

  >>> dt = 0.2
  >>> for t in np.arange(0, 8, dt):
  ...   car.store(t)
  ...   car.storeparams('delta', t = t)
  ...   car.delta = -0.5 * car.y - 2 * car.psi
  ...   sol = solve_ivp(car_model, [t, t + dt], car.X, args = (car.delta,))
  ...   car.X = sol.y[:, -1]

.. code::

  >>> print(car)
  [ x  y  ψ ]
  >>> car.y      # back on the line
  -0.02...

The same car seen by a camera is a point in the image plane.
The car tracker use cases represent it by a
:class:`pixelpoint <c4dynamics.states.lib.pixelpoint.pixelpoint>`,
:math:`X = [x, y, w, h]^T` (the center pixel and the bounding box size),
and propagate it with a constant velocity model in a
:class:`kalman <c4dynamics.filters.kalman.kalman>` filter.


**Use cases**

- :doc:`MPC Steering </programs/mpc_steering/mpc_steering>`:
  a model predictive controller steers the car to a straight reference line.
- :doc:`Car Tracker (YOLOv3) </programs/car_tracker/car_tracker>` and
  :doc:`Car Tracker (YOLO11) </programs/car_tracker_yolo11/car_tracker_yolo11>`:
  a Kalman filter tracks a car detected in a video, with constant velocity dynamics.



.. _vehicles-helicopter:

Helicopter
----------

**State vector**

The helicopter is a laboratory-scale model with two degrees of freedom.
It is mounted on a fixed base, and rotates in pitch and yaw only, with no translational motion.
It is represented by the ``helicopter`` environment, a subclass of
:class:`state <c4dynamics.states.state.state>`
(``c4dynamics.envs.environments.helicopter``), with the state variables:

.. math::

  X = [\theta, \psi, \dot{\theta}, \dot{\psi}]^T

Where:

- :math:`\theta, \psi` are the pitch (elevation) and yaw (azimuth) angles
- :math:`\dot{\theta}, \dot{\psi}` are the pitch and yaw angular rates


**Model**

The pivot constrains the body to two rotations.
Rather than the Newton-Euler equations with the constraint forces of the pivot,
the equations of motion are derived by Lagrangian mechanics,
directly in terms of the two free angles.
Two rotors, driven by the voltages :math:`V_p` and :math:`V_y`, generate the pitch and the yaw torques:

.. math::

  \begin{aligned}
  (J_p + M \cdot L_{cm}^2) \cdot \ddot{\theta} &= K_{pp} \cdot V_p + K_{py} \cdot V_y \\
  &\quad - M \cdot g \cdot L_{cm} \cdot \cos(\theta) - D_p \cdot \dot{\theta} \\
  &\quad - M \cdot L_{cm}^2 \cdot \dot{\psi}^2 \cdot \sin(\theta) \cdot \cos(\theta) \\
  (J_y + M \cdot L_{cm}^2 \cdot \cos^2(\theta)) \cdot \ddot{\psi} &= K_{yp} \cdot V_p + K_{yy} \cdot V_y \\
  &\quad - D_y \cdot \dot{\psi} \\
  &\quad + 2 \cdot M \cdot L_{cm}^2 \cdot \dot{\psi} \cdot \dot{\theta} \cdot \sin(\theta) \cdot \cos(\theta)
  \end{aligned}

Where:

- :math:`J_p, J_y` are the pitch and yaw moments of inertia
- :math:`M, L_{cm}` are the mass and the center of mass distance from the pivot
- :math:`D_p, D_y` are the pitch and yaw viscous damping
- :math:`K_{pp}, K_{py}, K_{yp}, K_{yy}` are the torque gains from each rotor to each axis
- :math:`g` is the gravity acceleration

The yaw-pitch coupling terms (centrifugal and Coriolis) and the cross rotor gains
make the system a nonlinear multi-input multi-output plant.
The equations are written in the control-affine form:

.. math::

  \begin{aligned}
  \dot{X}_1 &= X_2 \\
  \dot{X}_2 &= F(X) + G(X) \cdot u
  \end{aligned}

with :math:`X_1 = [\theta, \psi]^T`, :math:`X_2 = [\dot{\theta}, \dot{\psi}]^T`,
and :math:`u = [V_p, V_y]^T`.
The ``helicopter`` object provides ``F(X)``, ``G(X)``, and ``dynamics(t, X, u)``,
the full state derivative with the signature of ``scipy.integrate.solve_ivp``.


**Example**

Find the trim voltages, :math:`G \cdot u = -F`, that hold the helicopter at rest,
add a step to the pitch voltage, and integrate the equations of motion:

.. code::

  >>> from c4dynamics.envs.environments import helicopter
  >>> heli = helicopter(theta = 0, psi = 0)
  >>> u_trim = np.linalg.solve(heli.G(), -heli.F())
  >>> u = u_trim + [2, 0]   # V

.. code::

  >>> dt = 0.01
  >>> for t in np.arange(0, 2, dt):
  ...   heli.store(t)
  ...   sol = solve_ivp(heli.dynamics, [t, t + dt], heli.X, args = (u,))
  ...   heli.X = sol.y[:, -1]

.. code::

  >>> print(heli)
  [ θ  ψ  dtheta  dpsi ]
  >>> heli.theta * c4d.r2d, heli.psi * c4d.r2d   # pitch up, and a coupled yaw
  (10.4..., -2.5...)


**Use cases**

- :doc:`Neural Learning Control </programs/learning_controller/learning_controller>`:
  a backstepping controller with a neural network estimator of the uncertain dynamics
  tracks a pitch-yaw reference.



See Also
--------

.. list-table::
  :header-rows: 0

  * - :doc:`Dynamics </concepts/dynamics>`
    - Previous: the equations of motion that all the vehicles share
  * - :doc:`State Objects </concepts/states>`
    - The state data-structure and its operations
  * - :doc:`Rigid Body Transformations </concepts/transformations>`
    - Frames, rotation matrices, Euler angles, and quaternions
  * - :func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>`, :func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>`
    - Quadcopter forces and moments, and equations of motion shaped for ``scipy.integrate.solve_ivp``
  * - :mod:`eqm <c4dynamics.eqm>`
    - Equations of motion and integration functions
