Kinematics
==========


:doc:`Rigid Body Transformations </concepts/transformations>` described
the position and the attitude of a body at a single instant:
the frames, the rotation matrices, and the representations of an attitude.
Kinematics lets these quantities evolve in time.
It describes the motion without its causes:
given the velocity and the body angular rates,
it tells how the position and the attitude change.

The forces and the moments that change the velocity and the angular rates
are the subject of the next page, :doc:`Dynamics </concepts/dynamics>`.
Together, the kinematic equations of this page and the dynamic equations of the next one
form the equations of motion of the :mod:`eqm <c4dynamics.eqm>` module.



.. _kinematics-nomenclature:

Nomenclature
------------

The position of the center of mass of a body is the vector :math:`r`,
with the Cartesian coordinates :math:`(x, y, z)` in the reference frame.
Its velocity relative to the reference frame, which the equations of motion assume to be
inertial (see :ref:`Reference Frames <transformations-frames>`),
is the vector :math:`V`, with the components :math:`(v_x, v_y, v_z)` in the reference frame.
(The position vector :math:`r` is distinct from the yaw rate :math:`r` below;
the context, a vector or a scalar, tells them apart.)

The motion of the body frame is described by the components of the
velocity and the angular rate on the body axes (Fig-1).
The six projections of the linear and angular velocity vectors on the moving
body frame axes are the six degrees of freedom.
The attitude is given by the 3-2-1 Euler angles,
listed as roll, pitch, yaw :math:`(\varphi, \theta, \psi)`
and applied in the order yaw, pitch, roll
(see :ref:`Euler Angles <transformations-euler>`),
or by a quaternion (see :ref:`Quaternion <transformations-quaternion>`).

.. figure:: /_architecture/rigidbody.svg

   Fig-1: Forces, velocities, moments, and angular rates in the body frame.
   The forces and the moments are discussed in :doc:`Dynamics </concepts/dynamics>`.

.. list-table::
   :widths: 16 28 28 28
   :header-rows: 1

   * - Axis
     - Inertial velocity :math:`V`
     - Angular displacement
     - Angular velocity :math:`\omega`
   * - :math:`x_b`
     - :math:`u`
     - :math:`\varphi` (roll)
     - :math:`p` (roll rate)
   * - :math:`y_b`
     - :math:`v`
     - :math:`\theta` (pitch)
     - :math:`q` (pitch rate)
   * - :math:`z_b`
     - :math:`w`
     - :math:`\psi` (yaw)
     - :math:`r` (yaw rate)

The same inertial velocity :math:`V` has the components :math:`(u, v, w)` on the body axes
and :math:`(v_x, v_y, v_z)` on the reference axes.
The angular velocity of the body relative to the reference frame,
:math:`\omega = [p, q, r]^T`, is expressed in the body frame.

Note that :math:`(u, v, w)` are the body components of the **inertial** velocity,
the velocity relative to the ground.
They differ from the body components of the **air-relative** velocity
when there is wind (see `Translational Kinematics`_).



Translational Kinematics
------------------------

The rate of change of the position is the velocity:

.. math::

  \begin{aligned}
  \dot{x} &= v_x \\
  \dot{y} &= v_y \\
  \dot{z} &= v_z
  \end{aligned}

Or, in a vector form, :math:`\dot{r} = V`.
c4dynamics integrates the position in the reference frame,
where the components of the velocity are simply the derivatives of the coordinates.

**Body components of the inertial velocity**

When the inertial velocity is needed in the body frame,
it is rotated by the Body from Reference matrix:

.. math::

  [u, v, w]^T = [BR] \cdot [v_x, v_y, v_z]^T

**Air-relative velocity**

Aerodynamic forces depend on the motion of the body relative to the air,
not relative to the ground.
With a wind velocity :math:`V_{wind}`, expressed in the reference frame,
the air-relative velocity and its body components are:

.. math::

  \begin{aligned}
  V_a &= V - V_{wind} \\
  [u_a, v_a, w_a]^T &= [BR] \cdot V_a
  \end{aligned}

In still air, :math:`V_a = V` and :math:`(u_a, v_a, w_a) = (u, v, w)`.
The position is always integrated from the inertial velocity :math:`V`.
The air-relative velocity enters only the force models,
e.g. the drag of the :ref:`quadcopter <vehicles-quadcopter>`.

These equations are the complete kinematics of a point mass
(a :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`).
A rigid body adds the attitude.



.. _kinematics-euler:

Attitude Kinematics: Euler Angles
---------------------------------

As a rigid body changes its orientation, the Euler angles change.
The rates of the Euler angles are related to the body angular rates :math:`(p, q, r)`.

**Derivation**

Each Euler rate is a rotation about the axis of its own elementary rotation:
:math:`\dot{\psi}` about the reference :math:`z` axis,
:math:`\dot{\theta}` about the intermediate :math:`y` axis after the yaw rotation,
and :math:`\dot{\varphi}` about the body :math:`x` axis.
Expressing the three in the body frame by the elementary rotations
of :ref:`Euler Angles <transformations-euler>` and summing them gives the body rates:

.. math::

  \begin{bmatrix} p \\ q \\ r \end{bmatrix}
  = \begin{bmatrix} \dot{\varphi} \\ 0 \\ 0 \end{bmatrix}
  + R_x(\varphi) \begin{bmatrix} 0 \\ \dot{\theta} \\ 0 \end{bmatrix}
  + R_x(\varphi) R_y(\theta) \begin{bmatrix} 0 \\ 0 \\ \dot{\psi} \end{bmatrix}
  = \begin{bmatrix}
      1 & 0 & -\sin\theta \\
      0 & \cos\varphi & \sin\varphi \cdot \cos\theta \\
      0 & -\sin\varphi & \cos\varphi \cdot \cos\theta
    \end{bmatrix}
    \begin{bmatrix} \dot{\varphi} \\ \dot{\theta} \\ \dot{\psi} \end{bmatrix}

Note that the matrix is not a rotation matrix.
The three Euler rates are about three axes that are not mutually perpendicular,
therefore :math:`[\dot{\varphi}, \dot{\theta}, \dot{\psi}]` is not a vector,
and it is not simply a rotated version of :math:`\omega`.

**The Euler angles rates**

Inverting the matrix gives the rates of the Euler angles,
which are the attitude part of the rigid body state equations:

.. math::

  \begin{aligned}
  \dot{\varphi} &= p + (q \cdot \sin\varphi + r \cdot \cos\varphi) \cdot \tan\theta \\
  \dot{\theta} &= q \cdot \cos\varphi - r \cdot \sin\varphi \\
  \dot{\psi} &= {q \cdot \sin\varphi + r \cdot \cos\varphi \over \cos\theta}
  \end{aligned}

**The singularity**

The determinant of the matrix above is :math:`\cos\theta`.
As the pitch angle approaches :math:`\theta = \pm 90°`, the matrix becomes singular,
the terms :math:`\tan\theta` and :math:`1 / \cos\theta` grow without bound,
and so do :math:`\dot{\varphi}` and :math:`\dot{\psi}`.
This is the time domain face of the gimbal lock of
:ref:`Euler Angles <transformations-euler>`:
at this attitude, roll and yaw are the same rotation,
and a finite body rate maps into infinite Euler rates.
Near the singularity, the numerical integration loses accuracy (see the example below).

For vehicles that never approach it, such as a transport aircraft in level flight
or a car on the road, the Euler angles are a natural and intuitive choice.
Agile vehicles, however, such as drones performing flips,
aerobatic aircraft, missiles in a vertical launch, or tumbling spacecraft,
may reach any attitude.
For those, the attitude is better propagated as a quaternion.



.. _kinematics-quaternion:

Attitude Kinematics: Quaternion
-------------------------------

The rate of change of the attitude quaternion
:math:`q = [q_w, q_x, q_y, q_z]` (see :ref:`Quaternion <transformations-quaternion>`)
is related to the body rates by the quaternion product (:math:`\otimes`)
of the quaternion and the angular velocity [DI]_:

.. math::

  \dot{q} = {1 \over 2} \cdot q \otimes [0, p, q, r]

Or equivalently, in a matrix form:

.. math::

  \begin{bmatrix} \dot{q}_w \\ \dot{q}_x \\ \dot{q}_y \\ \dot{q}_z \end{bmatrix}
  = {1 \over 2}
  \begin{bmatrix}
    0 & -p & -q & -r \\
    p &  0 &  r & -q \\
    q & -r &  0 &  p \\
    r &  q & -p &  0
  \end{bmatrix}
  \begin{bmatrix} q_w \\ q_x \\ q_y \\ q_z \end{bmatrix}

And in a scalar form, which is the attitude part of the quaternion state equations:

.. math::

  \begin{aligned}
  \dot{q}_w &= -{1 \over 2} (q_x \cdot p + q_y \cdot q + q_z \cdot r) \\
  \dot{q}_x &= {1 \over 2} (q_w \cdot p + q_y \cdot r - q_z \cdot q) \\
  \dot{q}_y &= {1 \over 2} (q_w \cdot q - q_x \cdot r + q_z \cdot p) \\
  \dot{q}_z &= {1 \over 2} (q_w \cdot r + q_x \cdot q - q_y \cdot p)
  \end{aligned}

Note the two different meanings of the symbol :math:`q`:
the quaternion :math:`q = [q_w, q_x, q_y, q_z]`, and the pitch rate :math:`q`,
the second component of the angular rates :math:`(p, q, r)`.

Compared to the Euler angles rates, the quaternion rates:

- Contain no trigonometric functions and no division, and are therefore
  free of singularities at any attitude.
- Are linear in the quaternion components, which makes them cheap to evaluate
  and well behaved in numerical integration.

**Normalization**

The exact solution of the quaternion rates preserves the unit norm.
Numerical integration, however, does not preserve it exactly.
Small errors accumulate, and the quaternion drifts from a unit quaternion.
A standard remedy is to normalize the quaternion after each integration step:

.. math::

  q \leftarrow {q \over \|q\|}

:meth:`quatbody.inteqm <c4dynamics.states.lib.quatbody.quatbody.inteqm>` and
:func:`int6q <c4dynamics.eqm.integrate.int6q>` normalize at the end of each step.
Setting :attr:`quatbody.quat <c4dynamics.states.lib.quatbody.quatbody.quat>`
normalizes as well, which is the way to normalize after an external integrator
such as ``scipy.integrate.solve_ivp``.



Choosing a Representation
-------------------------

The two rigid body state objects of c4dynamics differ only in the attitude representation.
The translational kinematics, and the dynamics of the next page, are the same.

.. list-table::
   :widths: 22 39 39
   :header-rows: 1

   * -
     - :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
     - :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`
   * - Attitude states
     - :math:`\varphi, \theta, \psi`
     - :math:`q_w, q_x, q_y, q_z`
   * - State vector
     - 12 variables
     - 13 variables
   * - Singular attitude
     - :math:`\theta = \pm 90°`
     - None
   * - Constraint
     - None
     - :math:`\|q\| = 1`, normalized after each step
   * - Euler angles
     - The states themselves
     - Computed from the quaternion
       (:attr:`phi <c4dynamics.states.lib.quatbody.quatbody.phi>`,
       :attr:`theta <c4dynamics.states.lib.quatbody.quatbody.theta>`,
       :attr:`psi <c4dynamics.states.lib.quatbody.quatbody.psi>`)
   * - Typical use
     - Vehicles that stay away from a vertical attitude
     - Vehicles that may reach any attitude

Both objects provide the rotation matrices of their current attitude,
:attr:`BR <c4dynamics.states.lib.rigidbody.rigidbody.BR>` and
:attr:`RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>`.
Away from the singularity, both produce the same motion.



Example
-------

Import c4dynamics and numpy:

.. code::

  >>> import c4dynamics as c4d
  >>> import numpy as np


**Euler rates near the singularity**

A body pitched up by :math:`89.9°`, with a small yaw rate of 0.1 rad/s.
The Euler angles rates :math:`(\dot{\varphi}, \dot{\theta}, \dot{\psi})`
of :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>` explode,
while the quaternion rates :math:`(\dot{q}_w, \dot{q}_x, \dot{q}_y, \dot{q}_z)`
of :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>` stay small:

.. code::

  >>> rb = c4d.rigidbody(theta = 89.9 * c4d.d2r, r = 0.1)
  >>> c4d.eqm.eqm6(rb, np.zeros(3), np.zeros(3))[6:9]  # doctest: +NUMPY_FORMAT
  [57.3  0  57.3]

.. code::

  >>> qb = c4d.quatbody(theta = 89.9 * c4d.d2r, r = 0.1)
  >>> c4d.eqm.eqm6q(qb, np.zeros(3), np.zeros(3))[6:10]  # doctest: +NUMPY_FORMAT
  [0  0.035  0  0.035]


**Propagation through a near vertical attitude**

Two bodies with the same constant body rates, :math:`\omega = [0, 1, 0.1]` rad/s.
With no moments and equal moments of inertia, the body rates stay constant
(see :doc:`Dynamics </concepts/dynamics>`), so only the kinematics act.
During the run, the pitch angle passes within :math:`5°` of the vertical:

.. code::

  >>> rb = c4d.rigidbody(q = 1, r = 0.1)
  >>> qb = c4d.quatbody(q = 1, r = 0.1)
  >>> rb.I = [1, 1, 1]
  >>> qb.I = [1, 1, 1]
  >>> dt = 0.01
  >>> for t in np.arange(0, 3, dt):
  ...   rb.inteqm(np.zeros(3), np.zeros(3), dt)
  ...   qb.inteqm(np.zeros(3), np.zeros(3), dt)

A constant :math:`\omega` is a rotation about a fixed axis :math:`n = \omega / \|\omega\|`
through the angle :math:`\alpha = \|\omega\| \cdot t`,
so the exact final attitude follows from the definition of the quaternion:

.. code::

  >>> w = np.array([0, 1, 0.1])
  >>> alpha, n = np.linalg.norm(w) * 3, w / np.linalg.norm(w)
  >>> q_exact = np.hstack([np.cos(alpha / 2), n * np.sin(alpha / 2)])
  >>> c4d.rotmat.quat2euler(q_exact) * c4d.r2d  # doctest: +NUMPY_FORMAT
  [168.53  7.22  179.27]

The quaternion body lands on the exact attitude.
The Euler angles body accumulated an error of more than :math:`1°` in roll
while passing near the singularity:

.. code::

  >>> np.array([qb.phi, qb.theta, qb.psi]) * c4d.r2d  # doctest: +NUMPY_FORMAT
  [168.53  7.22  179.27]
  >>> np.array([rb.phi, rb.theta, rb.psi]) * c4d.r2d  # doctest: +NUMPY_FORMAT
  [169.82  7.27  179.43]



References
----------

See [HS]_ for the derivation of the Euler angles kinematics,
and [DI]_ for the quaternion kinematics
(on the :doc:`Rigid Body Transformations </concepts/transformations>` page).



See Also
--------

.. list-table::
  :header-rows: 0

  * - :doc:`Rigid Body Transformations </concepts/transformations>`
    - Previous: frames, rotation matrices, and attitude representations
  * - :doc:`Dynamics </concepts/dynamics>`
    - Next: the forces and the moments that drive the velocity and the body rates
  * - :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
    - A rigid body state object with an Euler angles attitude
  * - :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`
    - A rigid body state object with a quaternion attitude
  * - :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`, :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`
    - Rigid body state derivatives, with an Euler angles or a quaternion attitude
