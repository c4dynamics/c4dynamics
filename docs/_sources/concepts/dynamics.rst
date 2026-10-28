Dynamics
========


:doc:`Kinematics </concepts/kinematics>` propagates the position and the attitude
of a body, given its velocity and its angular rates.
Dynamics closes the loop:
it explains what changes the velocity and the angular rates.
Newton's second law translates the forces on a body into its linear acceleration,
and Euler's equations translate the moments into its angular acceleration.

These laws do not depend on the vehicle.
c4dynamics implements them once, in the :mod:`eqm <c4dynamics.eqm>` module,
and the state objects integrate them for every vehicle.
What makes a quadcopter different from a missile is the physics that
generates the forces and the moments.
These are the subject of the next page, :doc:`Vehicles </concepts/vehicles>`.



Nomenclature
------------

The inputs of the dynamic equations are the total force and the total moment
acting on the body, and its mass properties (see Fig-1 in
:ref:`Kinematics <kinematics-nomenclature>`):

.. list-table::
   :widths: 25 45 30
   :header-rows: 1

   * - Symbol
     - Description
     - Frame
   * - :math:`F = [F_x, F_y, F_z]^T`
     - Total force acting on the body
     - Reference
   * - :math:`M = [M_x, M_y, M_z]^T`
     - Total moment about the center of mass.
       Also known as the rolling, pitching, and yawing moments :math:`(L, M, N)`
     - Body
   * - :math:`m`
     - Mass
     - \-
   * - :math:`I = \operatorname{diag}(I_{xx}, I_{yy}, I_{zz})`
     - Inertia matrix about the center of mass
     - Body

The state variables are those of :ref:`Kinematics <kinematics-nomenclature>`:
the position :math:`r`, the inertial velocity :math:`V = [v_x, v_y, v_z]^T`,
the attitude, and the body rates :math:`\omega = [p, q, r]^T`.

c4dynamics takes the body axes as the principal axes of inertia,
so the inertia matrix is diagonal, and is given by the three moments of inertia
:attr:`I <c4dynamics.states.lib.rigidbody.rigidbody.I>`
(:math:`I_{xx}, I_{yy}, I_{zz}`).

**Moment and torque.** Both words describe the same physical quantity.
This documentation uses *moment* for the quantity :math:`M` in the equations of motion,
and *torque* for what an actuator produces, such as the reaction torque of a rotor
or the torque of a motor. The torques of the actuators are part of the total moment.

**Frames.** The equations below hold relative to an inertial frame.
c4dynamics writes them relative to the reference frame,
which is therefore assumed to be inertial
(see :ref:`Reference Frames <transformations-frames>`).



.. _dynamics-newton-euler:

The Newton-Euler Equations
--------------------------


Translational Motion
~~~~~~~~~~~~~~~~~~~~

**Vector form**

Newton's second law states that the total force acting on a body
equals the rate of change of its linear momentum, :math:`m \cdot V`,
relative to an inertial frame [MI]_.
For a constant mass:

.. math::

  m \cdot \dot{V} = F

The law involves only the center of mass.
It holds for a point mass and for a rigid body alike,
regardless of the rotation of the body.

**Scalar form**

c4dynamics expresses the velocity and the force in the reference frame,
where the components of the vector equation are independent:

.. math::

  \begin{aligned}
  \dot{v}_x &= {F_x \over m} \\
  \dot{v}_y &= {F_y \over m} \\
  \dot{v}_z &= {F_z \over m}
  \end{aligned}

Each acceleration component is driven by the force component along the same axis only.

**Explanation**

The force :math:`F` is the sum of all the external forces:
propulsion, aerodynamics, gravity, contact forces.
Many of them are naturally computed in the body frame,
e.g. the thrust of a motor along the body :math:`x` axis.
Such a force is rotated to the reference frame before it enters the equations
(see :ref:`Rotation Matrices <transformations-notation>`):

.. math::

  F = [RB] \cdot F_B

The equations could also be written with the body components of the velocity,
:math:`V_B = [u, v, w]^T`, as :math:`m \cdot (\dot{V}_B + \omega \times V_B) = F_B`.
The extra term :math:`\omega \times V_B` appears because the body frame rotates,
and couples the translational motion with the angular rates.
Writing the translational equations in the reference frame avoids this coupling.

When the mass changes, as in a rocket that burns its fuel,
:attr:`mass <c4dynamics.states.lib.datapoint.datapoint.mass>`
is updated between the integration steps,
and the effect of the ejected mass is included in the thrust.


Rotational Motion
~~~~~~~~~~~~~~~~~

**Vector form**

The rotational analog of Newton's law states that the total moment about the center of mass
equals the rate of change of the angular momentum, :math:`h`,
relative to an inertial frame.
For a rigid body, the angular momentum is :math:`h = I \cdot \omega`.

The inertia matrix is constant in the body frame, but not in an inertial frame,
where it changes as the body rotates.
Therefore, the law is written in the body frame.
The rate of change of a vector relative to an inertial frame
equals its rate of change relative to the rotating body frame,
plus the cross product of the angular velocity with the vector
(the transport theorem):

.. math::

  M = {dh \over dt} \bigg|_{I} = {dh \over dt} \bigg|_{B} + \omega \times h

Substituting :math:`h = I \cdot \omega`, with a constant :math:`I`,
gives Euler's equations of rotational motion:

.. math::

  I \cdot \dot{\omega} + \omega \times (I \cdot \omega) = M

Or, solved for the angular acceleration:

.. math::

  \dot{\omega} = I^{-1} \cdot (M - \omega \times (I \cdot \omega))

**Scalar form**

With the principal axes of inertia, :math:`I = \operatorname{diag}(I_{xx}, I_{yy}, I_{zz})`,
and :math:`\omega = [p, q, r]^T`,
the three components of Euler's equations are:

.. math::

  \begin{aligned}
  I_{xx} \cdot \dot{p} &= M_x - (I_{zz} - I_{yy}) \cdot q \cdot r \\
  I_{yy} \cdot \dot{q} &= M_y - (I_{xx} - I_{zz}) \cdot p \cdot r \\
  I_{zz} \cdot \dot{r} &= M_z - (I_{yy} - I_{xx}) \cdot p \cdot q
  \end{aligned}

**Explanation**

Each equation has the structure of Newton's law, inertia times acceleration
equals moment, with an additional term:

- :math:`I \cdot \dot{\omega}` is the rotational analog of :math:`m \cdot \dot{v}`.
  A moment about an axis accelerates the rotation about that axis,
  in inverse proportion to the moment of inertia about it.
- :math:`\omega \times (I \cdot \omega)` is the gyroscopic (or inertial coupling) term.
  It has no translational analog.
  It appears because the equations are written in the rotating body frame,
  where the angular momentum changes direction as the body rotates.
  In the scalar form, the coupling term of each axis is the product of the rates
  about the two other axes, times the difference of their moments of inertia.

The coupling term explains several typical behaviors of rotating bodies:

- **Equal moments of inertia.** A body with :math:`I_{xx} = I_{yy} = I_{zz}`,
  such as a sphere or a cube, has no coupling.
  With no moments, its angular rates remain constant.
- **Axial symmetry.** A body with :math:`I_{yy} = I_{zz}`, such as a missile or a rocket,
  has no coupling in the roll equation, :math:`I_{xx} \cdot \dot{p} = M_x`.
  The pitch and the yaw equations remain coupled through the roll rate :math:`p`.
  A rolling airframe turns a pitch rate into a yaw acceleration and vice versa.
- **Spin about a principal axis.** With only one nonzero rate, the coupling terms vanish,
  and with no moments the spin continues.
  The spin is stable about the axes of the maximum and the minimum moments of inertia,
  and unstable about the intermediate axis, where a small disturbance grows
  until the body tumbles (see the example below).
- **Spinning parts.** The same term, applied to the angular momentum of the rotors,
  produces the gyroscopic moments of a quadcopter
  (see :ref:`Quadcopter <vehicles-quadcopter>`).



.. _dynamics-eqm:

The Equations of Motion
-----------------------

The kinematic equations of :doc:`Kinematics </concepts/kinematics>`
and the dynamic equations above form the equations of motion,
a set of first-order differential equations of the state vector,
:math:`\dot{X} = f(X, F, M)`.
c4dynamics provides three such sets, one for each state object.


**Point mass (3DOF)**

A :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` has only
translational degrees of freedom:

.. math::

  X = [x, y, z, v_x, v_y, v_z]^T

.. math::

  \begin{aligned}
  \dot{r} &= V \\
  \dot{V} &= {F \over m}
  \end{aligned}

Where :math:`r = [x, y, z]^T` and :math:`V = [v_x, v_y, v_z]^T`.
The derivatives are given by :func:`eqm3 <c4dynamics.eqm.derivs.eqm3>`.


**Rigid body with Euler angles (6DOF)**

A :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` adds the attitude,
as the 3-2-1 Euler angles, and the body rates:

.. math::

  X = [x, y, z, v_x, v_y, v_z, \varphi, \theta, \psi, p, q, r]^T

.. math::

  \begin{aligned}
  \dot{r} &= V \\
  \dot{V} &= {F \over m} \\
  [\dot{\varphi}, \dot{\theta}, \dot{\psi}]^T &= E(\varphi, \theta) \cdot \omega \\
  \dot{\omega} &= I^{-1} \cdot (M - \omega \times (I \cdot \omega))
  \end{aligned}

Where :math:`E(\varphi, \theta)` is the matrix of the
:ref:`Euler angles rates <kinematics-euler>`.
The derivatives are given by :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`.


**Rigid body with a quaternion (6DOF)**

A :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` replaces the
Euler angles with the attitude quaternion:

.. math::

  X = [x, y, z, v_x, v_y, v_z, q_w, q_x, q_y, q_z, p, q, r]^T

.. math::

  \begin{aligned}
  \dot{r} &= V \\
  \dot{V} &= {F \over m} \\
  \dot{q} &= {1 \over 2} \cdot q \otimes [0, p, q, r] \\
  \dot{\omega} &= I^{-1} \cdot (M - \omega \times (I \cdot \omega))
  \end{aligned}

The quaternion rates are derived in :ref:`Kinematics <kinematics-quaternion>`.
The derivatives are given by :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`.


**Summary**

.. list-table::
   :widths: 22 14 32 32
   :header-rows: 1

   * - State object
     - States
     - Derivatives
     - Integration step
   * - :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`
     - 6
     - :func:`eqm3 <c4dynamics.eqm.derivs.eqm3>`
     - :func:`int3 <c4dynamics.eqm.integrate.int3>`,
       :meth:`datapoint.inteqm <c4dynamics.states.lib.datapoint.datapoint.inteqm>`
   * - :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
     - 12
     - :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`
     - :func:`int6 <c4dynamics.eqm.integrate.int6>`,
       :meth:`rigidbody.inteqm <c4dynamics.states.lib.rigidbody.rigidbody.inteqm>`
   * - :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`
     - 13
     - :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`
     - :func:`int6q <c4dynamics.eqm.integrate.int6q>`,
       :meth:`quatbody.inteqm <c4dynamics.states.lib.quatbody.quatbody.inteqm>`

In all three sets, the force :math:`F` is expressed in the reference frame,
and the moment :math:`M` in the body frame.



.. _dynamics-integration:

Integration
-----------

The equations of motion are integrated in time by one of three ways:

1. **The state object method.**
   :meth:`inteqm <c4dynamics.states.lib.rigidbody.rigidbody.inteqm>`
   advances the state of the object by one step of
   a fourth-order Runge-Kutta method, with the force and the moment held
   constant over the step.
   :meth:`quatbody.inteqm <c4dynamics.states.lib.quatbody.quatbody.inteqm>`
   normalizes the quaternion at the end of the step.
2. **The step functions.**
   :func:`int3 <c4dynamics.eqm.integrate.int3>`,
   :func:`int6 <c4dynamics.eqm.integrate.int6>`, and
   :func:`int6q <c4dynamics.eqm.integrate.int6q>` perform the same step
   and return the integrated state vector, without changing the object.
3. **An external integrator.**
   The derivative functions (:func:`eqm3 <c4dynamics.eqm.derivs.eqm3>`,
   :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`, :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`),
   or a vehicle model such as :func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>`,
   are passed to an integrator such as ``scipy.integrate.solve_ivp``,
   and the result is written back to :attr:`X <c4dynamics.states.state.state.X>`.
   With a quaternion attitude, setting
   :attr:`quat <c4dynamics.states.lib.quatbody.quatbody.quat>` to itself
   normalizes it after the step.

A simulation loop stores the state, computes the forces and the moments
from the current state, and integrates one step:

.. code::

  for t in np.arange(0, tf, dt):
    body.store(t)
    F, M = forces_and_moments(body)     # the vehicle physics
    body.inteqm(F, M, dt)



Examples
--------

Import c4dynamics and numpy:

.. code::

  >>> import c4dynamics as c4d
  >>> import numpy as np


**A point mass under gravity**

A ball is thrown at 20 m/s forward and 20 m/s up,
in a frame with :math:`z` up.
The only force is its weight:

.. code::

  >>> ball = c4d.datapoint(vx = 20, vz = 20)
  >>> ball.mass = 0.5
  >>> dt = 0.01
  >>> t = 0
  >>> while ball.z >= 0:
  ...   ball.store(t)
  ...   ball.inteqm([0, 0, -ball.mass * c4d.g_ms2], dt)
  ...   t += dt

.. code::

  >>> ball.x  # doctest: +NUMPY_FORMAT
  81.8

The analytic range is :math:`2 \cdot v_x \cdot v_z / g`, i.e. 81.6 m.
The difference is the last step, which ends below the ground.


**Spin about a principal axis**

Two bodies with the moments of inertia :math:`I = [1, 2, 3]` kg·m², and no moments.
The first spins about its major axis :math:`(z)`, the second about its intermediate axis :math:`(y)`.
Both are disturbed by a small roll rate:

.. code::

  >>> major = c4d.rigidbody(p = 0.01, r = 2)
  >>> inter = c4d.rigidbody(p = 0.01, q = 2)
  >>> major.I = [1, 2, 3]
  >>> inter.I = [1, 2, 3]
  >>> for t in np.arange(0, 10, dt):
  ...   major.store(t)
  ...   inter.store(t)
  ...   major.inteqm(np.zeros(3), np.zeros(3), dt)
  ...   inter.inteqm(np.zeros(3), np.zeros(3), dt)

The spin about the major axis is stable. The yaw rate stays at 2 rad/s:

.. code::

  >>> major.data('r')[1].min(), major.data('r')[1].max()  # doctest: +NUMPY_FORMAT
  (2.0, 2.0)

The spin about the intermediate axis is unstable.
The coupling terms amplify the disturbance, and the body flips over:
the pitch rate reverses its direction after less than six seconds:

.. code::

  >>> tq, q = inter.data('q')
  >>> q.min()  # doctest: +NUMPY_FORMAT
  -2.023
  >>> tq[np.argmax(q < 0)]  # doctest: +NUMPY_FORMAT
  5.82

No moment acted on either body.
The flip is caused only by the term :math:`\omega \times (I \cdot \omega)`.



References
----------

.. [MI] 17 July 1995, "Missile Flight Simulation, Part One, Surface-to-Air Missiles",
         Ch 4 In: Military Handbook. 1995, MIL-HDBK-1211(MI)



See Also
--------

.. list-table::
  :header-rows: 0

  * - :doc:`Kinematics </concepts/kinematics>`
    - Previous: the propagation of the position and the attitude
  * - :doc:`Vehicles </concepts/vehicles>`
    - Next: the forces and the moments of each vehicle
  * - :func:`eqm3 <c4dynamics.eqm.derivs.eqm3>`
    - Translational motion derivatives of a data point in three-dimensional space
  * - :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`
    - Translational and rotational motion derivatives of a rigid body in three-dimensional space
  * - :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`
    - Translational and rotational motion derivatives of a rigid body with a quaternion attitude
  * - :func:`int3 <c4dynamics.eqm.integrate.int3>`
    - A step integration of the equations of translational motion
  * - :func:`int6 <c4dynamics.eqm.integrate.int6>`
    - A step integration of the equations of translational and rotational motion
  * - :func:`int6q <c4dynamics.eqm.integrate.int6q>`
    - A step integration of the equations of translational and rotational motion with a quaternion attitude
