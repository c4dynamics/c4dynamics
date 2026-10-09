Kinematics
========== 


The ``eqm`` module in c4dynamics provides a collection of 
functions for integrating the equations of motion of data points and 
rigid bodies in the three-dimensional space. 


Background Material
-------------------

Introduction
~~~~~~~~~~~~

Motion models for points (particles) and rigid bodies in space and time are based on mathematical
equations. 

Three degrees of freedom models employ translational
equations of motion.
Six degrees of freedom models 
incorporate both translational 
and rotational equations of motion. 

The inputs to the equations of motion are the 
forces and moments acting on the body; 
yielding body accelerations as outputs [MI]_.


Nomenclature and Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typically, the forces and moments on a body are
resolved into components in the body coordinate system. 
Fig-1 shows the components of
force, moment velocity, and angular rate of a body
resolved in the body coordinate system. 
The six projections
of the linear and angular velocity vectors on the moving
body frame axes are the six degrees of freedom. 
The nomenclature and conventions for positive directions
are as shown in Fig-1 and in the following Table:


.. figure:: /_architecture/rigidbody.svg
   
   Fig-1: Forces, velocities, moments, and angular rates in body reference frame 



.. list-table::
   :widths: 10 20 20 20 20 20 20 
   :header-rows: 1

   * - Axis
     - Force along axis
     - Moment about axis
     - Linear velocity
     - Angular displacement 
     - Angular velocity 
     - Moment of Inertia
   * - :math:`x_b`
     - :math:`{F_x}_b`
     - :math:`L`
     - :math:`u`
     - :math:`\varphi`
     - :math:`p`
     - :math:`I_{xx}`
   * - :math:`y_b`
     - :math:`{F_y}_b`
     - :math:`M`
     - :math:`v`
     - :math:`\theta`
     - :math:`q`
     - :math:`I_{yy}`
   * - :math:`z_b`
     - :math:`{F_z}_b`
     - :math:`N`
     - :math:`w`
     - :math:`\psi`
     - :math:`r`
     - :math:`I_{zz}`


The position of the mass center of the body is given by
its Cartesian coordinates expressed in an inertial frame of
reference, such as the fixed-earth frame :math:`(x, y, z)`. 

The body's angular orientation is defined by three rotations :math:`(\psi, \theta, \varphi)` 
relative to the inertial frame of reference. 
These are
called Euler rotations, and the order of the successive rotations
is important. 
Starting with the body coordinate frame
aligned with the earth coordinate frame, the adopted order here is 3-2-1, i.e.: 

(1) Rotate the body frame about the :math:`z_b` axis through the heading angle :math:`\psi`, 
(2) Rotate about the :math:`y_b` axis through the pitch angle :math:`\theta`, and 
(3) Rotate about the :math:`x_b` axis through the roll angle :math:`\varphi`

The total inertial velocity :math:`V` has components :math:`u, v`, and :math:`w` on the body frame axes,
and :math:`(v_x, v_y, v_z)` on the earth-frame axes.


Rotation Matrix Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~

The relation between the body frame and the reference frame is described by a
Direction Cosine Matrix (DCM), a 3x3 rotation matrix.
c4dynamics names rotation matrices by two letters, which state the
direction of the transformation:

.. math::

  [BR] \quad \text{- a rotation matrix from the frame } R \text{ to the frame } B

Where :math:`R` stands for the reference (inertial, e.g. earth) frame and
:math:`B` stands for the body frame.
Read from right to left, :math:`[BR]` takes a vector that is expressed
in :math:`R` and returns the same vector expressed in :math:`B`:

.. math::

  v_B = [BR] \cdot v_R

The matrix is orthonormal, hence its inverse is its transpose,
and the opposite direction is given by:

.. math::

  [RB] = [BR]^{-1} = [BR]^T

  v_R = [RB] \cdot v_B

The rotation matrices are *passive*, i.e. they rotate the frame of
coordinates rather than the vector. The vector itself is unchanged;
only the frame in which its components are expressed changes.

With this naming, a chain of transformations is composed by cancelling
adjacent letters. For example, for three frames :math:`A, B, C`:

.. math::

  [CA] = [CB] \cdot [BA]

For the 3-2-1 Euler rotations defined above, the matrix from the reference
frame to the body frame is a product of three elementary rotations, where the
first rotation (:math:`\psi` about :math:`z`) is the rightmost:

.. math::

  [BR] = R_x(\varphi) \cdot R_y(\theta) \cdot R_z(\psi)

Where :math:`R_x, R_y, R_z` are the elementary rotation matrices about :math:`x, y, z`,
respectively (see :ref:`the rotmat module <kinematics-rotmat>` below).

In the equations of motion, these matrices are used to move forces, moments,
and velocities between the frames.
For example, the translational equations below take the forces in the
reference frame. A force that is given in the body frame, :math:`F_B`
(e.g. the thrust of a motor), is first rotated to the reference frame:

.. math::

  F_R = [RB] \cdot F_B

Similarly, the inertial velocity is resolved in the body frame by:

.. math::

  [u, v, w]^T = [BR] \cdot [v_x, v_y, v_z]^T

Both rigid body state objects, :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
and :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`, provide their current
rotation matrices as the properties
:attr:`BR <c4dynamics.states.lib.rigidbody.rigidbody.BR>` and
:attr:`RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>`.


Newton's Second Law 
~~~~~~~~~~~~~~~~~~~

Newton's second law of motion establishes the foundational 
equation governing the relationship among 
force, mass, and acceleration.
 

in the context of Newton's second law, the force :math:`(F)` 
acting on an object is the derivative of its momentum :math:`(m \cdot v)` 
with respect to time :math:`(t)`:

.. math:: 
   F = {d(m \cdot v) \over dt}

Where:

- :math:`F` is the total force acting on the object
- :math:`m` is the mass of the object
- :math:`v` is the velocity 
- :math:`t` is time 

This equation yields the final form of the equations of linear motion.
In the final form, acceleration is represented by the rate of change of the velocity:

.. math::
   F = m \cdot \dot{v}

Where:

- :math:`F` is the total force acting on the object
- :math:`m` is the mass of the object
- :math:`\dot{v}` is the acceleration of the object


A direct extension of Newton's second law to rotational motion 
reveals that the moment of force (torque) on a body 
about a given axis equals the time rate of change of the 
angular momentum of the paricle about that axis. 


.. math::
   M = {dh \over dt} 

Where:

- :math:`M` is the total moment (torque) acting on the object
- :math:`h` is the angular momentum vector of the object



Hence, the final form of the equations of angular motion is given by: 

.. math::
   M = [I] \cdot \dot{\omega}

Where:

- :math:`M` is the total moment (torque) acting on the object

- :math:`[I]` is the inertia matrix of the body relative to the axis of rotation

- :math:`\dot{\omega}` is the absolute angular acceleration vector of the body



   
Translational Equations of Motion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The basis of the translational equation of motion was introduced 
above. 
The usual procedure used to solve this
equation is to sum the external forces
:math:`F` acting on the body, express them in an 
inertial frame, and substitute :math:`F` into 
the equation.
Once the acceleration, namely the forces 
divided by the mass, is expressed in inertial coordinates, 
it is integrated twice to yield the
translational displacement. 


.. math::

  dx = v_x

  dy = v_y

  dz = v_z

  dv_x = {F[0] \over m}

  dv_y = {F[1] \over m}

  dv_z = {F[2] \over m}

Where:

- :math:`dx, dy, dz` are the changes in position in the :math:`x, y, z` inertial directions, respectively  
- :math:`dv_x, dv_y, dv_z` are the changes in velocity in the :math:`x, y, z` inertial directions, respectively 
- :math:`v_x, v_y, v_z` are the velocities in the :math:`x, y, z` inertial directions, respectively
- :math:`f[0], f[1], f[2]` are the input force components in the :math:`x, y, z` inertial directions, respectively
- :math:`m` is the mass of the body.


These equations describe the dynamics of a datapoint in three-dimensional space (**3DOF**). 
Which is 
the rate of change of position 
:math:`(x, y, z)` with respect to time equals to the velocity, 
and the rate of change of velocity 
:math:`(v_x, v_y, v_z)` with respect to time
equals to the force divided by the mass :math:`(m)`.




Rotational Equations of Motion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As mentioned earlier, the rotational analog
of Newton's law describes the relationship between torque, 
moment of inertia, and angular acceleration. 
We also saw that a double integration on the translational 
acceleration produces the change of the body in position.

However, the angular accelerations
are typically expressed with respect to a body frame and 
must be adjusted in order to produce the attitude of the
body. 
For that purpose we introduced the euler angles (see Nomenclature and Conventions)
which describe the 
body attitude with respect to an inertial frame of reference.

The orientation of the body reference frame is specified by the three
Euler angles, :math:`\psi, \theta, \varphi`. 

As a rigid body changes its orientation
in space, the Euler angles change. 
The rates of change
of the Euler angles are related to the angular rates :math:`(p, q, r)` of the
body frame.

The rate of change of the Euler angles together with the rotational analog 
of Newton's law provide the set of differential equations 
that 
describe the equations governing the motion of a rigid body: 


.. math::

  d\varphi = p + (q \cdot sin(\varphi) + r \cdot cos(\varphi)) \cdot tan(\theta)

  d\theta = q \cdot cos(\varphi) - r \cdot sin(\varphi)
  
  d\psi = {q \cdot sin(\varphi) + r \cdot cos(\phi) \over cos(\theta)}

  dp = {M[0] - q \cdot r \cdot (I_{zz} - I_{yy}) \over I_{xx}}

  dq = {M[1] - p \cdot r \cdot (I_{xx} - I_{zz}) \over I_{yy}}

  dr = {M[2] - p \cdot q \cdot (I_{yy} - I_{xx}) \over I_{zz}}


Where: 

- :math:`d\varphi, d\theta, d\psi` are the changes in Euler roll, Euler pitch, and Euler yaw angles, respectively 
- :math:`dp, dq, dr` are the changes in body roll rate, pitch rate, and yaw rate, respectively
- :math:`\varphi, \theta, \psi` are the Euler roll, Euler pitch, and uler yaw angles, respectively 
- :math:`p, q, r` are the body roll rate, pitch rate, and yaw rate, respcetively
- :math:`M[0], M[1], M[2]` are the input moment of force components about the :math:`x, y, z` in the body direction, respectively
- :math:`I_{xx}, I_{yy}, I_{zz}` are the moments of inertia about the :math:`x, y,` and :math:`z` in body direction, respectively


These equations describe the angular dynamics of a rigid body.
Together with the equations that describe the translational
motion of the body they form the six-dimensional motion in space (**6DOF**).



Quaternion Kinematics
~~~~~~~~~~~~~~~~~~~~~

**The Euler angles singularity**

The Euler angles rates above contain the terms :math:`tan(\theta)` and :math:`1 / cos(\theta)`.
As the pitch angle approaches :math:`\theta = \pm 90°`, these terms grow without bound
and the equations become singular.
At this attitude the roll axis and the yaw axis are aligned,
:math:`\varphi` and :math:`\psi` describe the same rotation,
and they are not uniquely defined.
This phenomenon is known as *gimbal lock*.

Any set of three angles has such a singular attitude.
For vehicles that never approach it, such as a transport aircraft in level flight,
the Euler angles are a natural and intuitive choice.
Agile vehicles, however, such as drones performing flips,
aerobatic aircraft, missiles in a vertical launch, or tumbling spacecraft,
may reach any attitude.
For those, the attitude is better represented by a quaternion [DI]_.


**The attitude quaternion**

According to Euler's rotation theorem, any attitude can be reached from
the reference frame by a single rotation through an angle :math:`\alpha`
about a unit axis :math:`n = [n_x, n_y, n_z]`.
The attitude quaternion encodes this rotation by four parameters:

.. math::

  q = [q_w, q_x, q_y, q_z] = [cos{\alpha \over 2}, \; n_x \cdot sin{\alpha \over 2}, \; n_y \cdot sin{\alpha \over 2}, \; n_z \cdot sin{\alpha \over 2}]

Where:

- :math:`q_w` is the scalar part of the quaternion
- :math:`q_x, q_y, q_z` are the vector part of the quaternion

c4dynamics uses the scalar-first (Hamilton) convention.

Four parameters describe three degrees of freedom, therefore the quaternion
is subject to one constraint. An attitude quaternion is a unit quaternion:

.. math::

  q_w^2 + q_x^2 + q_y^2 + q_z^2 = 1

Note that :math:`q` and :math:`-q` represent the same attitude
(a rotation of :math:`\alpha` about :math:`n` equals a rotation of
:math:`\alpha - 360°` about the same axis).


**Relation to the Euler angles**

The quaternion of the attitude that is defined by the 3-2-1
Euler angles :math:`(\psi, \theta, \varphi)` is given by:

.. math::

  q_w = c{\varphi \over 2} c{\theta \over 2} c{\psi \over 2} + s{\varphi \over 2} s{\theta \over 2} s{\psi \over 2}

  q_x = s{\varphi \over 2} c{\theta \over 2} c{\psi \over 2} - c{\varphi \over 2} s{\theta \over 2} s{\psi \over 2}

  q_y = c{\varphi \over 2} s{\theta \over 2} c{\psi \over 2} + s{\varphi \over 2} c{\theta \over 2} s{\psi \over 2}

  q_z = c{\varphi \over 2} c{\theta \over 2} s{\psi \over 2} - s{\varphi \over 2} s{\theta \over 2} c{\psi \over 2}

where :math:`c \equiv cos` and :math:`s \equiv sin`.

The inverse relation, from a quaternion to the Euler angles, is given by:

.. math::

  \varphi = atan2(2(q_w q_x + q_y q_z), \; 1 - 2(q_x^2 + q_y^2))

  \theta = asin(2(q_w q_y - q_x q_z))

  \psi = atan2(2(q_w q_z + q_x q_y), \; 1 - 2(q_y^2 + q_z^2))

The extracted Euler angles are, of course, still singular at :math:`\theta = \pm 90°`.
The quaternion itself is not. It is therefore common to propagate the quaternion
and to compute the Euler angles only for presentation.

The rotation matrix from the reference frame to the body frame, :math:`[BR]`
(see Rotation Matrix Convention),
is given in terms of the quaternion by the following matrix,
which is identical to the matrix of the 3-2-1 Euler angles of the same attitude:

.. math::

  [BR] = \begin{bmatrix}
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


**The quaternion rates**

The rate of change of the attitude quaternion is related to the angular
rates :math:`(p, q, r)` of the body frame by the quaternion product
(:math:`\otimes`) of the quaternion and the angular velocity vector:

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

Compared to the Euler angles rates, the quaternion rates:

- Contain no trigonometric functions and no division, and are therefore
  free of singularities at any attitude.
- Are linear in the quaternion components, which makes them cheap to evaluate
  and well behaved in numerical integration.

Numerical integration, however, does not preserve the unit norm exactly.
Small errors accumulate, and the quaternion drifts from a unit quaternion.
A standard remedy is to normalize the quaternion after each integration step:

.. math::

  q \leftarrow {q \over \|q\|}


**The quaternion equations of motion**

Replacing the Euler angles rates by the quaternion rates yields the
quaternion form of the rotational equations of motion.
The angular rates equations remain unchanged:

.. math::

  dq_w = -{1 \over 2} (q_x \cdot p + q_y \cdot q + q_z \cdot r)

  dq_x = {1 \over 2} (q_w \cdot p + q_y \cdot r - q_z \cdot q)

  dq_y = {1 \over 2} (q_w \cdot q - q_x \cdot r + q_z \cdot p)

  dq_z = {1 \over 2} (q_w \cdot r + q_x \cdot q - q_y \cdot p)

  dp = {M[0] - q \cdot r \cdot (I_{zz} - I_{yy}) \over I_{xx}}

  dq = {M[1] - p \cdot r \cdot (I_{xx} - I_{zz}) \over I_{yy}}

  dr = {M[2] - p \cdot q \cdot (I_{yy} - I_{xx}) \over I_{zz}}

Where:

- :math:`dq_w, dq_x, dq_y, dq_z` are the changes in the attitude quaternion components
- :math:`q_w, q_x, q_y, q_z` are the attitude quaternion components
- the rest of the variables are as defined for the Euler angles equations above.

Note the two different meanings of the symbol :math:`q`:
the quaternion :math:`q = [q_w, q_x, q_y, q_z]`, and the pitch rate :math:`q`,
the second component of the angular rates :math:`(p, q, r)`.

Together with the translational equations, these equations form a
singularity-free 6DOF model with 13 state variables:

.. math::

  X = [x, y, z, v_x, v_y, v_z, q_w, q_x, q_y, q_z, p, q, r]^T

In c4dynamics, this model is implemented by the
:class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` state object,
whose equations of motion are given by
:func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>` and integrated by
:func:`int6q <c4dynamics.eqm.integrate.int6q>`.
The Euler angles model is implemented by the
:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` state object
with :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>` and
:func:`int6 <c4dynamics.eqm.integrate.int6>`.
Away from the singularity, both models produce the same motion.



.. _kinematics-quadcopter:

Quadcopter Equations of Motion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The 6DOF equations above take the forces and the moments as inputs.
For a quadcopter, these come from four rotors, aerodynamic drag, and gravity.
:func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>` computes them, and
:func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>` passes them through the
rigid body equations: the Euler angles model of
:func:`eqm6 <c4dynamics.eqm.derivs.eqm6>` for a 12-state vector,
or the quaternion model of :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`
for a 13-state vector.


**Frames**

The model supports the two common pairs of an inertial frame and a body frame.
Both use the 3-2-1 rotation of the convention above,
so the body-from-inertial matrix is :math:`[BI]` with no extra rotation:

.. list-table::
   :widths: 15 30 30 25
   :header-rows: 1

   * - ``frame``
     - Inertial frame
     - Body frame
     - :math:`s`
   * - ``'NED'``
     - :math:`x` north, :math:`y` east, :math:`z` down
     - :math:`x` forward, :math:`y` right, :math:`z` down (FRD)
     - :math:`-1`
   * - ``'ENU'``
     - :math:`x` east, :math:`y` north, :math:`z` up
     - :math:`x` forward, :math:`y` left, :math:`z` up (FLU)
     - :math:`+1`

The sign :math:`s` is the direction of *up* along the body :math:`z` axis.
It appears wherever the model depends on the frame:
the rotors thrust along :math:`s \cdot z_b`, and gravity acts along :math:`-s \cdot z`.


**Rotors**

Rotor :math:`i` at the body position :math:`(x_i, y_i)` spins at :math:`\Omega_i`
in the direction :math:`d_i` (:math:`+1` counterclockwise seen from above,
:math:`-1` clockwise). It produces a thrust and a reaction torque:

.. math::

  F_i = k_T \cdot \Omega_i^2, \qquad Q_i = k_Q \cdot \Omega_i^2

The default rotor layout is an :math:`X` configuration with the moment arm :math:`l`,
in the motor order front-right, rear-left, front-left, rear-right,
and :math:`d = [1, 1, -1, -1]`.
Any other layout is given by explicit rotor positions and directions.


**Forces**

The body force is the total thrust along the body *up* axis
and a linear drag that opposes the body velocity relative to the air:

.. math::

  F_b = \begin{bmatrix} -A_x \cdot u \\ -A_y \cdot v \\ s \cdot \sum F_i - A_z \cdot w \end{bmatrix},
  \qquad
  \begin{bmatrix} u \\ v \\ w \end{bmatrix} = [BI] \cdot (V - V_{wind})

The force in the inertial frame, which enters the translational equations of motion, adds gravity:

.. math::

  F = [BI]^T \cdot F_b + \begin{bmatrix} 0 \\ 0 \\ -s \cdot m \cdot g \end{bmatrix}

:math:`F_b / m` is the specific force, i.e. what an accelerometer at the center of mass measures.


**Moments**

The thrust of each rotor acts at its position and produces roll and pitch moments.
The reaction torques produce the yaw moment: a counterclockwise rotor
turns the body clockwise seen from above.
A rotational drag opposes the angular rates, and the angular momentum of the rotors,
:math:`h = s \cdot I_R \cdot \sum d_i \cdot \Omega_i` along the body :math:`z` axis,
adds a gyroscopic coupling :math:`-\omega \times h`:

.. math::

  M[0] = s \cdot \sum y_i \cdot F_i - A_r \cdot p - q \cdot h

  M[1] = -s \cdot \sum x_i \cdot F_i - A_r \cdot q + p \cdot h

  M[2] = -s \cdot \sum d_i \cdot Q_i - A_r \cdot r

Where:

- :math:`k_T, k_Q` are the rotor thrust and torque coefficients
- :math:`A_x, A_y, A_z` are the linear drag coefficients along the body axes
- :math:`A_r` is the rotational drag coefficient
- :math:`I_R` is the rotor moment of inertia
- :math:`V, V_{wind}` are the inertial velocity of the body and the wind velocity
- :math:`m, g` are the mass and the gravity acceleration
- the rest of the variables are as defined above.

:math:`F` and :math:`M` are the inputs of the translational and the rotational
equations of motion of the previous sections.


**Integration**

:func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>` has the signature of
``scipy.integrate.solve_ivp``. The vehicle parameters are attributes of the
state object, and the rotor speeds are held constant over a step:

.. code::

  from scipy.integrate import solve_ivp
  from c4dynamics.models.quad import default_quad_config

  quad = c4d.rigidbody()
  for k, v in default_quad_config().items():
      setattr(quad, k, v)

  sol = solve_ivp(c4d.eqm.quadeqm, [t, t + dt], quad.X, args = (quad, rotor_speeds, 'ENU'))
  quad.X = sol.y[:, -1]

A :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` instead of a
:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` selects the quaternion model.
The `Cascade-PID <https://c4dynamics.github.io/c4dynamics/programs/pid_cascade/quadcopter_pid.html>`_
and the `EKF <https://c4dynamics.github.io/c4dynamics/programs/ekf_estimation/quad_ekf.html>`_
quadcopter examples fly this model.



.. _kinematics-rotmat:

The rotmat Module
~~~~~~~~~~~~~~~~~

The :mod:`rotmat <c4dynamics.rotmat>` module implements the rotation operations
described on this page, following the convention above.
All the angles are in radians, unless stated otherwise.

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Function
     - Description
   * - :func:`rotx <c4dynamics.rotmat.rotmat.rotx>`,
       :func:`roty <c4dynamics.rotmat.rotmat.roty>`,
       :func:`rotz <c4dynamics.rotmat.rotmat.rotz>`
     - Elementary rotation matrices :math:`R_x, R_y, R_z`: a frame rotation
       through an angle about the :math:`x, y`, or :math:`z` axis
   * - :func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`
     - :math:`[BR]` of the 3-2-1 Euler angles,
       :math:`R_x(\varphi) \cdot R_y(\theta) \cdot R_z(\psi)`
   * - :func:`dcm321euler <c4dynamics.rotmat.rotmat.dcm321euler>`
     - The 3-2-1 Euler angles of a :math:`[BR]` matrix (returned in degrees)
   * - :func:`euler2quat <c4dynamics.rotmat.rotmat.euler2quat>`
     - The attitude quaternion of the 3-2-1 Euler angles
   * - :func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>`
     - The 3-2-1 Euler angles of an attitude quaternion (also for an array of quaternions)
   * - :func:`quat2dcm <c4dynamics.rotmat.rotmat.quat2dcm>`
     - :math:`[BR]` of an attitude quaternion
   * - :func:`animate <c4dynamics.rotmat.animate.animate>`
     - Animates the attitude histories of a rigid body with a 3D model

To get :math:`[RB]` from any of the functions above, transpose the result.


**Examples**

Import c4dynamics:

.. code::

  >>> import c4dynamics as c4d

A frame that is rotated by :math:`90°` about :math:`z`. The :math:`x` axis of the
reference frame is the :math:`-y` axis of the rotated frame:

.. code::

  >>> c4d.rotmat.rotz(90 * c4d.d2r) @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  -1  0]

A body with heading :math:`\psi = 90°` and pitch :math:`\theta = 30°`.
:math:`[BR]` expresses the reference :math:`x` axis in body coordinates,
and :math:`[RB] = [BR]^T` expresses the body :math:`x` axis (the nose)
in reference coordinates:

.. code::

  >>> BR = c4d.rotmat.dcm321(phi = 0, theta = 30 * c4d.d2r, psi = 90 * c4d.d2r)
  >>> BR @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  -1  0]
  >>> BR.T @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  0.866  -0.5]

Going back from the matrix to the Euler angles (in degrees):

.. code::

  >>> c4d.rotmat.dcm321euler(BR)  # doctest: +NUMPY_FORMAT
  (0  30  90)

The same attitude as a quaternion. Its rotation matrix is identical to
the one of the Euler angles, and the Euler angles are recovered from it:

.. code::

  >>> q = c4d.rotmat.euler2quat(phi = 0, theta = 30 * c4d.d2r, psi = 90 * c4d.d2r)
  >>> q  # doctest: +NUMPY_FORMAT
  [0.683  -0.183  0.183  0.683]
  >>> c4d.rotmat.quat2dcm(q) @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  -1  0]
  >>> c4d.rotmat.quat2euler(q) * c4d.r2d  # doctest: +NUMPY_FORMAT
  [0  30  90]

The state objects use these functions to provide their rotation matrices.
:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` computes
:math:`[BR]` by :func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`, and
:class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` by
:func:`quat2dcm <c4dynamics.rotmat.rotmat.quat2dcm>`:

.. code::

  >>> rb = c4d.rigidbody(theta = 30 * c4d.d2r, psi = 90 * c4d.d2r)
  >>> rb.RB @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  0.866  -0.5]

For the background material on rotation matrices, Euler angles orders,
and the right hand frame convention, see the
:doc:`Rigid Body Transformations </concepts/transformations>` concept page.



References
~~~~~~~~~~

.. [MI] 17 July 1995, "Missile Flight Simulation, Part One, Surface-to-Air Missiles",
         Ch 4 In: Military Handbook. 1995, MIL-HDBK-1211(MI)

.. [DI] Diebel, J., 2006, "Representing Attitude: Euler Angles, Unit Quaternions,
         and Rotation Vectors", Stanford University.


         
Examples
~~~~~~~~

For examples, see the various functions.



See Also
~~~~~~~~

.. list-table:: 
  :header-rows: 0

  * - :func:`eqm3 <c4dynamics.eqm.derivs.eqm3>`
    - Translational motion derivatives of a data point in three-dimensional space
  * - :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`
    - Translational and rotational motion derivatives of a rigid body in three-dimensional space
  * - :func:`int3 <c4dynamics.eqm.integrate.int3>`
    - A step integration of the equations of translational motion
  * - :func:`int6 <c4dynamics.eqm.integrate.int6>`
    - A step integration of the equations of translational and rotational motion
  * - :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>`
    - Translational and rotational motion derivatives of a rigid body with a quaternion attitude
  * - :func:`int6q <c4dynamics.eqm.integrate.int6q>`
    - A step integration of the equations of translational and rotational motion with a quaternion attitude
  * - :func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>`, :func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>`
    - Quadcopter equations of motion (rotor forces and moments through ``eqm6`` / ``eqm6q``), shaped for ``scipy.integrate.solve_ivp``
  * - :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`
    - A rigid body state object with a quaternion attitude
  * - :func:`euler2quat <c4dynamics.rotmat.rotmat.euler2quat>`, :func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>`, :func:`quat2dcm <c4dynamics.rotmat.rotmat.quat2dcm>`
    - Conversions between quaternions, Euler angles, and DCMs
  * - :mod:`rotmat <c4dynamics.rotmat>`
    - Rotation matrices and rotational operations
  * - :doc:`Rigid Body Transformations </concepts/transformations>`
    - Background material on rotation matrices and frame conventions

