Dynamics
========


The use cases of c4dynamics fly, drive, and steer different vehicles:
a quadcopter, a missile, a car, and a helicopter.
They look different, but the mechanics that move them are the same.
Newton's second law translates the forces on a body into its linear acceleration,
and Euler's equations translate the moments into its angular acceleration.
These equations do not depend on the vehicle,
and c4dynamics implements them once, for all vehicles
(:func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`, :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`,
:meth:`rigidbody.inteqm <c4dynamics.states.lib.rigidbody.rigidbody.inteqm>`).

What makes a quadcopter different from a missile is not the equations of motion,
but the physics that generates the forces and the moments:
rotors that push along one body axis,
a rocket motor and a body that produces lift as it meets the air at an angle,
tires that hold the car on its path,
or a pivot that constrains the helicopter to two rotations.
The control inputs act on the vehicle only through these forces and moments.
Therefore, this page focuses on the force and moment model of each vehicle:
what produces the forces and the moments,
and how the control inputs shape them.

The workflow is shared by all the vehicles:

1. Define a state object with the state variables of the vehicle.
2. Compute the forces and the moments from the vehicle physics and the control inputs.
3. Integrate the equations of motion over a time step and update the state.
4. Store the state and analyze the results.

The state object is the common interface between the vehicle and the algorithm.
The vehicle model changes, but the state object keeps the same interface:
:attr:`X <c4dynamics.states.state.state.X>` to get and set the state vector,
:meth:`store <c4dynamics.states.state.state.store>` and
:meth:`data <c4dynamics.states.state.state.data>` to record and retrieve the history,
and :meth:`plot <c4dynamics.states.state.state.plot>` to view it.
Therefore, a guidance law, a controller, or a filter that is developed on one system
moves to another system smoothly, by replacing the state object and the force model,
while the rest of the program remains intact.



The Common Core
---------------

For a rigid body of mass :math:`m` and inertia matrix :math:`I`,
the Newton-Euler equations are:

.. math::

  \dot{r} &= v \\
  m \cdot \dot{v} &= F \\
  I \cdot \dot{\omega} &= M - \omega \times I \cdot \omega

Where:

- :math:`r, v` are the position and the velocity in the inertial frame
- :math:`F` is the total force, resolved in the inertial frame
- :math:`\omega = [p, q, r]` is the angular rate of the body, resolved in the body frame
- :math:`M` is the total moment about the center of mass, resolved in the body frame

To close the loop, the attitude is propagated from the body rates :math:`\omega`.
The attitude can be represented in different ways,
and the representation sets the attitude part of the state vector:

- Euler angles :math:`[\varphi, \theta, \psi]`: intuitive,
  but singular at :math:`\theta = \pm 90°`
  (:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`, 12 states).
- A quaternion :math:`[q_w, q_x, q_y, q_z]`: free of singularities at any attitude
  (:class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`, 13 states).
- A rotation matrix: used to move vectors between the body and the inertial frames
  (:attr:`BR <c4dynamics.states.lib.rigidbody.rigidbody.BR>`,
  :attr:`RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>`).

The kinematics of the Euler angles and of the quaternion are derived in
:doc:`Kinematics </concepts/kinematics>`
(see :ref:`Quaternion Kinematics <kinematics-quaternion>`),
and the conversions between the representations are given in
:ref:`Rigid Body Transformations <transformations-conversions>`.
Below, the quadcopter section shows the quaternion form,
and the missile section shows the Euler angles form.

The vehicle physics supplies :math:`F` and :math:`M`.
The following table summarizes the force and moment models used across the use cases.
Each model is described in a dedicated section below.


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



Quadcopter
----------

**Forces and moments**

A quadcopter has no control surfaces.
Every force and moment, other than gravity and drag, comes from four fixed rotors
that all point along the body *up* axis.
The inputs are the four rotor speeds :math:`\Omega_i`.
Each rotor produces a thrust and a reaction torque,
both proportional to the square of its speed:

.. math::

  T_i &= k_T \cdot \Omega_i^2 \\
  Q_i &= k_Q \cdot \Omega_i^2

The rotors are arranged in an *x* configuration, at a distance :math:`l` from the center,
with two rotors turning clockwise and two counterclockwise.
The four speeds map into one force and three moments:

- **Collective thrust**: the sum :math:`\sum T_i` acts along the body *up* axis.
  It is the only control force. To accelerate sideways, the vehicle must first tilt.
- **Roll and pitch moments**: a thrust difference between the left and the right rotors,
  or between the front and the rear rotors, acting on the arm :math:`l`.
- **Yaw moment**: the reaction torques :math:`Q_i`.
  A rotor turning counterclockwise pushes the body clockwise.
  When the counterclockwise pair spins faster than the clockwise pair,
  the torques do not cancel, and the vehicle yaws,
  with little change in the total thrust.

Further terms complete the model:
a linear drag on the air-relative velocity (with an optional wind),
a rotational drag on the body rates,
and the gyroscopic coupling of the spinning rotors.
:func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>` returns the
body force (thrust and drag) and the body moment.
:func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>` rotates the force to the inertial frame,
adds gravity, and evaluates the Newton-Euler equations,
for the ``'NED'`` and ``'ENU'`` frame conventions,
with the signature of ``scipy.integrate.solve_ivp``.
The rotor model, the drag terms, and the frames are detailed in
:ref:`Quadcopter Equations of Motion <kinematics-quadcopter>`.
The physical parameters of the reference vehicle are given by
``c4dynamics.models.quad.default_quad_config()``.


**Quaternion attitude**

A quadcopter can flip, roll, and point its *up* axis in any direction.
The Euler angles become singular at :math:`\theta = \pm 90°`,
so the quadcopter is a natural candidate for the quaternion representation.
A :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` object holds 13 state variables:

.. math::

  X = [x, y, z, v_x, v_y, v_z, q_w, q_x, q_y, q_z, p, q, r]^T

Where:

- :math:`x, y, z` are the position coordinates in the inertial frame
- :math:`v_x, v_y, v_z` are the velocity components in the inertial frame
- :math:`q_w, q_x, q_y, q_z` are the attitude quaternion components (scalar first)
- :math:`p, q, r` are the body roll, pitch, and yaw rates

The translational and the angular rates equations are those of the common core.
The quaternion :math:`\mathbf{q} = [q_w, q_x, q_y, q_z]` is propagated by the body rates:

.. math::

  \dot{\mathbf{q}} = {1 \over 2} \cdot \mathbf{q} \otimes [0, p, q, r]

These rates contain no trigonometric functions and no division,
and are regular at any attitude.
Numerical integration does not preserve the unit norm exactly,
so the quaternion is normalized after each step.
The rotation matrices and the Euler angles
(:attr:`phi <c4dynamics.states.lib.quatbody.quatbody.phi>`,
:attr:`theta <c4dynamics.states.lib.quatbody.quatbody.theta>`,
:attr:`psi <c4dynamics.states.lib.quatbody.quatbody.psi>`)
are computed from the quaternion, for the force model and for presentation.

The attitude representation is independent of the force model.
:func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>` accepts a 12-state
:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` as well,
with the Euler angles kinematics shown in the missile section below.
See :ref:`Quaternion Kinematics <kinematics-quaternion>` for the derivation and
:ref:`Rigid Body Transformations <transformations-conversions>` for the
conversions between the representations.


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
:math:`q_w = cos(\alpha / 2)`, :math:`q_z = sin(\alpha / 2)`.
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



Missile
-------

**State vector**

The missile is a rigid body with six degrees of freedom,
represented by a :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` object:

.. math::

  X = [x, y, z, v_x, v_y, v_z, \varphi, \theta, \psi, p, q, r]^T

The variables are as defined for the quadcopter.
The mass and the moments of inertia are attributes of the object,
:attr:`mass <c4dynamics.states.lib.datapoint.datapoint.mass>` and
:attr:`I <c4dynamics.states.lib.rigidbody.rigidbody.I>`,
and may be updated during the run, as the rocket motor burns its fuel.

The target is a point mass with three degrees of freedom, represented by a
:class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` object:

.. math::

  X = [x, y, z, v_x, v_y, v_z]^T


**Dynamics**

The forces on the missile are the propulsion along the body :math:`x` axis,
the aerodynamic lift and drag, and gravity.
The propulsion and the aerodynamic forces are computed in the body frame and rotated to the
inertial frame by :attr:`RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>`.
The aerodynamic moments are computed in the body frame from the angles of attack
and the fins deflections.

The translational equations are Newton's second law in the inertial frame:

.. math::

  \dot{r} &= v \\
  \dot{v} &= {F \over m}

The rotational equations relate the moments to the body rates,
and the body rates to the Euler angles rates:

.. math::

  \dot{\varphi} &= p + (q \cdot sin(\varphi) + r \cdot cos(\varphi)) \cdot tan(\theta) \\
  \dot{\theta} &= q \cdot cos(\varphi) - r \cdot sin(\varphi) \\
  \dot{\psi} &= {q \cdot sin(\varphi) + r \cdot cos(\varphi) \over cos(\theta)} \\
  \dot{p} &= {M[0] - q \cdot r \cdot (I_{zz} - I_{yy}) \over I_{xx}} \\
  \dot{q} &= {M[1] - p \cdot r \cdot (I_{xx} - I_{zz}) \over I_{yy}} \\
  \dot{r} &= {M[2] - p \cdot q \cdot (I_{yy} - I_{xx}) \over I_{zz}}

The derivatives are given by :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`.
:meth:`rigidbody.inteqm <c4dynamics.states.lib.rigidbody.rigidbody.inteqm>`
integrates them by a fourth-order Runge-Kutta step,
and :meth:`datapoint.inteqm <c4dynamics.states.lib.datapoint.datapoint.inteqm>`
integrates the translational equations of the target
(:func:`eqm3 <c4dynamics.eqm.derivs.eqm3>`).
The full derivation is given in :doc:`Kinematics </concepts/kinematics>`.


**Example**

Launch the missile at :math:`30°` pitch in a NED frame (:math:`z` down)
with a constant thrust, and propagate a non-maneuvering target:

.. code::

  >>> missile = c4d.rigidbody(vx = 30 * np.cos(30 * c4d.d2r), vz = -30 * np.sin(30 * c4d.d2r), theta = 30 * c4d.d2r)
  >>> missile.mass = 85               # kg
  >>> missile.I = [0.5, 61, 61]       # kg.m^2
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


**Dynamics**

At a constant speed :math:`V`, the kinematic (unicycle) model of the car is given by:

.. math::

  \dot{x} &= V \cdot cos(\psi) \\
  \dot{y} &= V \cdot sin(\psi) \\
  \dot{\psi} &= \delta

Where :math:`\delta` is the steering input, the rate of change of the heading.

For a straight reference line along the :math:`x` axis,
the model is linearized about :math:`\psi = 0`.
The longitudinal motion decouples, and the lateral dynamics reduce to two state variables,
:math:`X = [\psi, y]^T`, with :math:`\dot{\psi} = \delta` and :math:`\dot{y} = V \cdot \psi`.
This is the prediction model of the MPC use case.


**Example**

Define the car with an initial lateral offset of :math:`1m`,
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


**Dynamics**

Two rotors, driven by the voltages :math:`V_p` and :math:`V_y`, generate the pitch and the yaw torques.
The equations of motion, derived by Lagrangian mechanics, are:

.. math::

  (J_p + M \cdot L_{cm}^2) \cdot \ddot{\theta} &= K_{pp} \cdot V_p + K_{py} \cdot V_y
    - M \cdot g \cdot L_{cm} \cdot cos(\theta) - D_p \cdot \dot{\theta} \\
    &\quad - M \cdot L_{cm}^2 \cdot \dot{\psi}^2 \cdot sin(\theta) \cdot cos(\theta) \\
  (J_y + M \cdot L_{cm}^2 \cdot cos^2(\theta)) \cdot \ddot{\psi} &= K_{yp} \cdot V_p + K_{yy} \cdot V_y
    - D_y \cdot \dot{\psi} \\
    &\quad + 2 \cdot M \cdot L_{cm}^2 \cdot \dot{\psi} \cdot \dot{\theta} \cdot sin(\theta) \cdot cos(\theta)

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

  \dot{X}_1 &= X_2 \\
  \dot{X}_2 &= F(X) + G(X) \cdot u

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

  * - :doc:`State Objects </concepts/states>`
    - The state data-structure and its operations
  * - :doc:`Kinematics </concepts/kinematics>`
    - Background material on the equations of motion of points and rigid bodies
  * - :doc:`Rigid Body Transformations </concepts/transformations>`
    - Rotation matrices, Euler angles, and quaternions
  * - :mod:`eqm <c4dynamics.eqm>`
    - Equations of motion and integration functions
