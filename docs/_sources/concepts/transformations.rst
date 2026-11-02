Rigid Body Transformations
==========================


A :doc:`state object </concepts/states>` holds the variables of a body:
its position, its velocity, and, for a rigid body, its attitude.
Before these variables can change in time, they need a geometric meaning:
in which frame a vector is expressed, and how the orientation of one frame
relative to another is described.

This page covers that geometry, with no time involved:
the frames of reference, the rotation matrices that move vectors between them,
and the three representations of an attitude
(Euler angles, rotation matrix, quaternion).
The next page, :doc:`Kinematics </concepts/kinematics>`,
lets these quantities change in time.

In c4dynamics, the geometry is implemented by the :mod:`rotmat <c4dynamics.rotmat>` module,
and by the :attr:`BR <c4dynamics.states.lib.rigidbody.rigidbody.BR>` and
:attr:`RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>` properties of the rigid body
state objects.



.. _transformations-frames:

Reference Frames
----------------

A frame of reference (or a coordinate system) is an origin and three
mutually perpendicular unit axes, :math:`x, y, z`.
A physical vector, such as a velocity or a force, exists independently of any frame.
Its three components, however, depend on the frame in which it is resolved.
A vector resolved in a given frame is said to be **expressed** in that frame.

For example, an aircraft that flies north at 150 m/s and pitches up by :math:`30°`
has a single velocity vector.
In an earth frame (north, east, down) its components are :math:`[150, 0, 0]`,
while in the aircraft body frame they are :math:`[129.9, 0, 75]`
(see the examples below).

The rate of change of a vector, as viewed by an observer fixed to and moving
with a given frame, is said to be **relative to** (or **with respect to**) that frame.
The laws of motion hold relative to an inertial frame,
but the vectors in them can be expressed in any frame.


**The frames of c4dynamics**

.. list-table::
   :widths: 10 30 60
   :header-rows: 1

   * - Symbol
     - Frame
     - Description
   * - :math:`R`
     - Reference
     - The frame in which the state objects express the position and the velocity
       (:math:`x, y, z, v_x, v_y, v_z`), and against which the attitude of a body is defined.
   * - :math:`I`
     - Inertial
     - A frame that does not accelerate or rotate. The laws of motion hold relative to it.
   * - :math:`B`
     - Body
     - A frame fixed to the body and rotating with it. The origin is
       at the center of mass and :math:`x_b` is along the centerline (the nose).
       The body angular rates :math:`(p, q, r)` and the body components of the velocity
       :math:`(u, v, w)` are expressed in this frame.
   * - :math:`S`
     - Sensor
     - A frame fixed to a sensor, such as a :class:`seeker <c4dynamics.sensors.seeker.seeker>`
       or a :class:`radar <c4dynamics.sensors.radar.radar>`.
       Its :math:`x` axis is the sensor boresight.


**Reference, inertial, and earth frames**

The reference frame is a modeling choice, and is not necessarily inertial.
The equations of motion of c4dynamics, however, are written relative to the reference frame
(see :doc:`Dynamics </concepts/dynamics>`), and therefore assume that it is inertial.
In the use cases, the reference frame is an *earth frame*:
a frame fixed to a flat earth, such as NED or ENU below.
The earth rotation and curvature are negligible over the time and the range of these
use cases, so the earth frame is treated as inertial,
and :math:`R` and :math:`I` denote the same frame.
:math:`I` is used where the inertial property matters, e.g. in the navigation sensors
and the quadcopter model, and :math:`R` elsewhere.


**NED and ENU**

Two pairs of an earth frame and a body frame are common for vehicles that move
above a flat earth.
Both are supported by the quadcopter model and the navigation sensors through the
``frame`` argument (see :ref:`Quadcopter <vehicles-quadcopter>`):

.. list-table::
   :widths: 15 40 45
   :header-rows: 1

   * - ``frame``
     - Earth frame
     - Body frame
   * - ``'NED'``
     - :math:`x` north, :math:`y` east, :math:`z` down
     - :math:`x` forward, :math:`y` right, :math:`z` down (FRD)
   * - ``'ENU'``
     - :math:`x` east, :math:`y` north, :math:`z` up
     - :math:`x` forward, :math:`y` left, :math:`z` up (FLU)


**Right-handed frames**

All the frames in c4dynamics are right-handed:

.. math::

  \begin{aligned}
  i \times j &= k \\
  j \times k &= i \\
  k \times i &= j
  \end{aligned}

where :math:`i, j, k` are the unit vectors along the :math:`x, y, z` axes.
Positive rotations are clockwise
when viewed from the origin, looking out along the
positive direction of the axis (Fig-1).

.. figure:: /_architecture/frame_conventions.svg

   Fig-1: Coordinate system conventions



.. _transformations-notation:

Rotation Matrices
-----------------

Vectors that are expressed in different frames are related through a
Direction Cosine Matrix (DCM), a :math:`3 \times 3` rotation matrix [HS]_.


**Notation**

c4dynamics names a rotation matrix by two letters in square brackets.
The letters state the direction of the transformation, read from right to left:
:math:`[BR]` (*Body from Reference*) takes a vector that is expressed in :math:`R`
and returns the same vector expressed in :math:`B`:

.. math::

  v_B = [BR] \cdot v_R

The same notation applies to any pair of frames, for example:

.. list-table::
   :widths: 15 85
   :header-rows: 0

   * - :math:`[BR]`
     - Body from Reference. Provided by
       :attr:`rigidbody.BR <c4dynamics.states.lib.rigidbody.rigidbody.BR>` and
       :attr:`quatbody.BR <c4dynamics.states.lib.quatbody.quatbody.BR>`
   * - :math:`[RB]`
     - Reference from Body. Provided by
       :attr:`rigidbody.RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>` and
       :attr:`quatbody.RB <c4dynamics.states.lib.quatbody.quatbody.RB>`
   * - :math:`[BI]`
     - Body from Inertial, i.e. :math:`[BR]` when the reference frame is inertial.
       Used in the IMU, the magnetometer, and the quadcopter model
   * - :math:`[SB]`
     - Sensor from Body, e.g. the gimbal of a seeker


**Properties**

*Direction cosines.* The element :math:`[BR]_{ij}` is the cosine of the angle between
the :math:`i`-th axis of :math:`B` and the :math:`j`-th axis of :math:`R`.
Hence the rows of :math:`[BR]` are the body axes expressed in :math:`R`,
and its columns are the reference axes expressed in :math:`B`.

*Inverse.* A rotation matrix is orthonormal, :math:`[BR] \cdot [BR]^T = I_3`,
and its determinant is :math:`+1`. Its inverse is its transpose,
which is the transformation in the opposite direction:

.. math::

  \begin{aligned}
  [RB] &= [BR]^{-1} = [BR]^T \\
  v_R &= [RB] \cdot v_B
  \end{aligned}

*Composition.* A chain of transformations is composed by cancelling adjacent letters.
For three frames :math:`A, B, C`:

.. math::

  [CA] = [CB] \cdot [BA]

For example, a seeker that is mounted on a gimbal sees the reference frame through
:math:`[SR] = [SB] \cdot [BR]`.

*Passive rotation.* The rotation matrices in c4dynamics are *passive*:
they rotate the frame of coordinates rather than the vector.
The vector itself is unchanged; only the frame in which its components
are expressed changes.
To rotate a vector *actively* by a positive angle within the same frame,
use the transpose. E.g. :math:`R_z(\psi)^T \cdot v` rotates :math:`v` by :math:`\psi`
about :math:`z`.


**Elementary rotations**

A rotation of a frame through an angle about one of its axes is given by an
elementary rotation matrix:

.. math::

  R_x(\varphi) = \begin{bmatrix}
      1 & 0 & 0 \\
      0 & \cos(\varphi) & \sin(\varphi) \\
      0 & -\sin(\varphi) & \cos(\varphi)
    \end{bmatrix}
  , \quad
  R_y(\theta) = \begin{bmatrix}
      \cos(\theta) & 0 & -\sin(\theta) \\
      0 & 1 & 0 \\
      \sin(\theta) & 0 & \cos(\theta)
    \end{bmatrix}
  , \quad
  R_z(\psi) = \begin{bmatrix}
      \cos(\psi) & \sin(\psi) & 0 \\
      -\sin(\psi) & \cos(\psi) & 0 \\
      0 & 0 & 1
    \end{bmatrix}

These are implemented by :func:`rotx <c4dynamics.rotmat.rotmat.rotx>`,
:func:`roty <c4dynamics.rotmat.rotmat.roty>`, and
:func:`rotz <c4dynamics.rotmat.rotmat.rotz>`.
Any attitude is reached by a sequence of three elementary rotations.



Attitude Representations
------------------------

The attitude of a body is the orientation of its body frame :math:`B`
relative to the reference frame :math:`R`.
It has three degrees of freedom, and c4dynamics represents it in three equivalent ways:
three Euler angles, a rotation matrix :math:`[BR]`, and a unit quaternion.
The rotation matrix is the one that moves vectors between the frames.
The Euler angles and the quaternion are the compact forms that are stored in the
state vector and propagated in time
(see :doc:`Kinematics </concepts/kinematics>`).


.. _transformations-euler:

Euler Angles
~~~~~~~~~~~~

When Euler angles are employed in the transformation of
a vector expressed in one reference frame to the expression
of the vector in a different reference frame, any order of the
three Euler rotations is possible, but the resulting transformation
equations depend on the order selected [MIs]_.

In aerospace applications,
the common order is that the first Euler rotation is about the z-axis,
the second is about the y-axis, and the third is about the x-axis.
Such a transformation order is called z-y-x, or 3-2-1.
With reference to a body orientation, the resulting
order is yaw, pitch, and roll.
With reference to geographical
orientation, the resulting order is azimuth (heading),
elevation (pitch), and roll (bank angle).

c4dynamics adopts the 3-2-1 order.
Starting with the body frame aligned with the reference frame:

(1) Rotate about :math:`z_b` through the yaw (heading) angle :math:`\psi`,
(2) Rotate about :math:`y_b` through the pitch angle :math:`\theta`,
(3) Rotate about :math:`x_b` through the roll angle :math:`\varphi`.

The rotations are applied in the order yaw, pitch, roll.
The angles, however, are listed in the opposite order, roll, pitch, yaw,
:math:`(\varphi, \theta, \psi)`, wherever they appear as a group:
in the state vector of a :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`,
in the arguments of :func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`
and :func:`euler2quat <c4dynamics.rotmat.rotmat.euler2quat>`,
and in the outputs of :func:`dcm321euler <c4dynamics.rotmat.rotmat.dcm321euler>`
and :func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>`.
This documentation follows the same order.

The first rotation is the rightmost in the product:

.. math::

  [BR] = R_x(\varphi) \cdot R_y(\theta) \cdot R_z(\psi)
  = \begin{bmatrix}
        c\theta \cdot c\psi
      & c\theta \cdot s\psi
      & -s\theta \\
            s\varphi \cdot s\theta \cdot c\psi - c\varphi \cdot s\psi
          & s\varphi \cdot s\theta \cdot s\psi + c\varphi \cdot c\psi
          & s\varphi \cdot c\theta \\
                c\varphi \cdot s\theta \cdot c\psi + s\varphi \cdot s\psi
              & c\varphi \cdot s\theta \cdot s\psi - s\varphi \cdot c\psi
              & c\varphi \cdot c\theta
      \end{bmatrix}

where :math:`c \equiv \cos` and :math:`s \equiv \sin`.
This matrix is computed by :func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`.

The Euler angles are extracted back from the matrix by:

.. math::

  \begin{aligned}
  \varphi &= \operatorname{atan2}([BR]_{23}, [BR]_{33}) \\
  \theta &= -\arcsin([BR]_{13}) \\
  \psi &= \operatorname{atan2}([BR]_{12}, [BR]_{11})
  \end{aligned}

**Gimbal lock.** At :math:`\theta = \pm 90°`,
:math:`[BR]_{11}, [BR]_{12}, [BR]_{23}, [BR]_{33}` all vanish,
the roll axis is aligned with the yaw axis,
and :math:`\varphi` and :math:`\psi` describe the same rotation.
Only their sum (or difference) is defined, not each one alone.
Any set of three angles has such a singular attitude.
The consequence for the propagation of the angles in time is discussed in
:ref:`Kinematics <kinematics-euler>`.


.. _transformations-quaternion:

Quaternion
~~~~~~~~~~

According to Euler's rotation theorem, any attitude is reached from
the reference frame by a single rotation through an angle :math:`\alpha`
about a unit axis :math:`n = [n_x, n_y, n_z]`.
The attitude quaternion encodes this rotation by four parameters, scalar first
(the Hamilton convention):

.. math::

  q = [q_w, q_x, q_y, q_z] = [\cos{\alpha \over 2}, \; n_x \cdot \sin{\alpha \over 2}, \; n_y \cdot \sin{\alpha \over 2}, \; n_z \cdot \sin{\alpha \over 2}]

Where:

- :math:`q_w` is the scalar part of the quaternion
- :math:`q_x, q_y, q_z` are the vector part of the quaternion

Four parameters describe three degrees of freedom, therefore the quaternion
is subject to one constraint. An attitude quaternion is a unit quaternion:

.. math::

  q_w^2 + q_x^2 + q_y^2 + q_z^2 = 1

:math:`q` and :math:`-q` represent the same attitude
(a rotation of :math:`\alpha` about :math:`n` equals a rotation of
:math:`\alpha - 360°` about the same axis).
Unlike the three Euler angles, the quaternion has no singular attitude [DI]_.


**Rotation matrix**

The quaternion describes the rotation that carries the reference frame onto the body frame.
The matrix that c4dynamics computes from a quaternion is the Body from Reference DCM, :math:`[BR]`:
it takes a vector expressed in the reference frame and returns
the same vector expressed in the body frame, :math:`v_B = [BR] \cdot v_R`:

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

Some references give instead the matrix that rotates a vector by :math:`\alpha` about :math:`n`.
That matrix is the transpose, :math:`[RB]`, and its off-diagonal terms that contain :math:`q_w`
have opposite signs. The difference is in the direction of the transformation, not a sign error.
In quaternion products, :math:`v_B = [BR] \cdot v_R` is
:math:`[0, v_B] = q^* \otimes [0, v_R] \otimes q`, where :math:`q^* = [q_w, -q_x, -q_y, -q_z]`
is the conjugate of :math:`q`.

For example, the quaternion of a yaw of :math:`90°`,
:math:`q = [\cos 45°, 0, 0, \sin 45°]`,
gives :math:`[BR] = R_z(90°)`, the elementary rotation above.
In general, a quaternion describes the same attitude as the 3-2-1 Euler angles
of the convention above, and its :math:`[BR]` is identical to
:func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>` of those angles.
It is computed by :func:`quat2dcm <c4dynamics.rotmat.rotmat.quat2dcm>`.


**Relation to the Euler angles**

The quaternion of the attitude that is defined by the 3-2-1
Euler angles :math:`(\varphi, \theta, \psi)` is given by:

.. math::

  \begin{aligned}
  q_w &= c{\varphi \over 2} c{\theta \over 2} c{\psi \over 2} + s{\varphi \over 2} s{\theta \over 2} s{\psi \over 2} \\
  q_x &= s{\varphi \over 2} c{\theta \over 2} c{\psi \over 2} - c{\varphi \over 2} s{\theta \over 2} s{\psi \over 2} \\
  q_y &= c{\varphi \over 2} s{\theta \over 2} c{\psi \over 2} + s{\varphi \over 2} c{\theta \over 2} s{\psi \over 2} \\
  q_z &= c{\varphi \over 2} c{\theta \over 2} s{\psi \over 2} - s{\varphi \over 2} s{\theta \over 2} c{\psi \over 2}
  \end{aligned}

The inverse relation, from a quaternion to the Euler angles, is given by:

.. math::

  \begin{aligned}
  \varphi &= \operatorname{atan2}(2(q_w q_x + q_y q_z), \; 1 - 2(q_x^2 + q_y^2)) \\
  \theta &= \arcsin(2(q_w q_y - q_x q_z)) \\
  \psi &= \operatorname{atan2}(2(q_w q_z + q_x q_y), \; 1 - 2(q_y^2 + q_z^2))
  \end{aligned}

The extracted Euler angles are, of course, still singular at :math:`\theta = \pm 90°`.
The quaternion itself is not.
The :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` state object therefore
stores the quaternion, and computes the Euler angles only for presentation.


.. _transformations-conversions:

Conversions
~~~~~~~~~~~

The functions of the ``rotmat`` module convert between the three representations:

.. list-table::
   :widths: 22 26 26 26
   :header-rows: 1

   * - From \\ To
     - Euler angles :math:`(\varphi, \theta, \psi)`
     - DCM :math:`[BR]`
     - Quaternion :math:`q`
   * - Euler angles
     - \-
     - :func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`
     - :func:`euler2quat <c4dynamics.rotmat.rotmat.euler2quat>`
   * - DCM
     - :func:`dcm321euler <c4dynamics.rotmat.rotmat.dcm321euler>` (degrees)
     - \-
     - ``euler2quat(*dcm321euler(BR) * d2r)``
   * - Quaternion
     - :func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>`
     - :func:`quat2dcm <c4dynamics.rotmat.rotmat.quat2dcm>`
     - \-

Notes:

- All the functions take and return angles in radians, except
  :func:`dcm321euler <c4dynamics.rotmat.rotmat.dcm321euler>`, which returns degrees.
- All the matrices are :math:`[BR]`. To get :math:`[RB]`, transpose the result.
- A conversion that passes through the Euler angles inherits their
  singularity at :math:`\theta = \pm 90°`.


**Between ENU and NED**

The ENU and the NED frames swap :math:`x` and :math:`y` and flip :math:`z`.
The matrix that does it is its own inverse, so the same matrix converts both ways:

.. math::

  v_{NED} = \begin{bmatrix} 0 & 1 & 0 \\ 1 & 0 & 0 \\ 0 & 0 & -1 \end{bmatrix} \cdot v_{ENU}

A heading measured from east (ENU) becomes a heading measured from north (NED):
:math:`\psi_{NED} = \pi / 2 - \psi_{ENU}`.
This conversion is used at the MAVLink boundary of the
:doc:`ArduPilot simulation </programs/ardupilot_sim/ardupilot_fig8>`.



Examples
--------

Import c4dynamics and numpy:

.. code::

  >>> import c4dynamics as c4d
  >>> import numpy as np


**Elementary rotations**

A frame that is rotated by :math:`90°` about :math:`z`.
The :math:`x` axis of the original frame is the :math:`-y` axis of the rotated frame:

.. code::

  >>> c4d.rotmat.rotz(90 * c4d.d2r) @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  -1  0]

The transpose rotates the vector itself (active rotation) by :math:`90°` about :math:`z`,
from :math:`x` to :math:`y`:

.. code::

  >>> c4d.rotmat.rotz(90 * c4d.d2r).T @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  1  0]

The 3-2-1 matrix is the product of the three elementary rotations:

.. code::

  >>> phi, theta, psi = 10 * c4d.d2r, 20 * c4d.d2r, 30 * c4d.d2r
  >>> BR = c4d.rotmat.dcm321(phi, theta, psi)
  >>> np.allclose(BR, c4d.rotmat.rotx(phi) @ c4d.rotmat.roty(theta) @ c4d.rotmat.rotz(psi))
  True

It is orthonormal, so its transpose is its inverse:

.. code::

  >>> np.allclose(BR @ BR.T, np.eye(3))
  True
  >>> np.linalg.det(BR)  # doctest: +NUMPY_FORMAT
  1


**From reference to body and back**

The inertial velocity of an aircraft flying north, expressed in an earth frame,
and its attitude, a pitch of :math:`30°`:

.. code::

  >>> v_R = [150, 0, 0]
  >>> BR = c4d.rotmat.dcm321(theta = 30 * c4d.d2r)

The velocity expressed in the body frame, :math:`v_B = [BR] \cdot v_R`:

.. code::

  >>> v_B = BR @ v_R
  >>> v_B  # doctest: +NUMPY_FORMAT
  [129.9  0  75]

And back to the earth frame, :math:`v_R = [RB] \cdot v_B = [BR]^T \cdot v_B`:

.. code::

  >>> BR.T @ v_B  # doctest: +NUMPY_FORMAT
  [150  0  0]


**The body axes in the reference frame**

A body with heading :math:`\psi = 90°` and pitch :math:`\theta = 30°`.
:math:`[BR]` expresses the reference :math:`x` axis in body coordinates,
and :math:`[RB] = [BR]^T` expresses the body :math:`x` axis (the nose)
in reference coordinates. The latter is also the first row of :math:`[BR]`:

.. code::

  >>> BR = c4d.rotmat.dcm321(theta = 30 * c4d.d2r, psi = 90 * c4d.d2r)
  >>> BR @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  -1  0]
  >>> BR.T @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  0.866  -0.5]
  >>> BR[0]  # doctest: +NUMPY_FORMAT
  [0  0.866  -0.5]

The state objects provide these matrices for their current attitude:

.. code::

  >>> rb = c4d.rigidbody(theta = 30 * c4d.d2r, psi = 90 * c4d.d2r)
  >>> rb.RB @ [1, 0, 0]  # doctest: +NUMPY_FORMAT
  [0  0.866  -0.5]


**Composing transformations**

A target position relative to a seeker, expressed in the reference frame,
and a seeker body with a heading of :math:`30°`:

.. code::

  >>> dx = [1000, 1000, 0]
  >>> skr = c4d.rigidbody(psi = 30 * c4d.d2r)

The relative position in the body frame and the azimuth angle to the target:

.. code::

  >>> x_b = skr.BR @ dx
  >>> x_b  # doctest: +NUMPY_FORMAT
  [1366  366  0]
  >>> np.arctan2(x_b[1], x_b[0]) * c4d.r2d  # doctest: +NUMPY_FORMAT
  15

A gimbal that turns the sensor by another :math:`15°` about :math:`z` gives :math:`[SB]`.
The sensor sees the reference frame through :math:`[SR] = [SB] \cdot [BR]`,
which puts the target on its boresight:

.. code::

  >>> SB = c4d.rotmat.rotz(15 * c4d.d2r)
  >>> SR = SB @ skr.BR
  >>> SR @ dx  # doctest: +NUMPY_FORMAT
  [1414.2  0  0]

The two :math:`z` rotations add up:

.. code::

  >>> np.allclose(SR, c4d.rotmat.rotz(45 * c4d.d2r))
  True


**Converting between representations**

From the Euler angles to the DCM and back. Note that
:func:`dcm321euler <c4dynamics.rotmat.rotmat.dcm321euler>` returns degrees:

.. code::

  >>> BR = c4d.rotmat.dcm321(10 * c4d.d2r, 20 * c4d.d2r, 30 * c4d.d2r)
  >>> c4d.rotmat.dcm321euler(BR)  # doctest: +NUMPY_FORMAT
  (10  20  30)

From the Euler angles to a quaternion, and from the quaternion to the DCM and
to the Euler angles (in radians):

.. code::

  >>> q = c4d.rotmat.euler2quat(10 * c4d.d2r, 20 * c4d.d2r, 30 * c4d.d2r)
  >>> q  # doctest: +NUMPY_FORMAT
  [0.952  0.038  0.189  0.239]
  >>> np.allclose(c4d.rotmat.quat2dcm(q), BR)
  True
  >>> c4d.rotmat.quat2euler(q) * c4d.r2d  # doctest: +NUMPY_FORMAT
  [10  20  30]

From the DCM to a quaternion, through the Euler angles:

.. code::

  >>> np.allclose(c4d.rotmat.euler2quat(*np.array(c4d.rotmat.dcm321euler(BR)) * c4d.d2r), q)
  True

The matrix of a quaternion is the Body from Reference DCM.
A yaw of :math:`90°` gives the elementary rotation :math:`R_z(90°)`:

.. code::

  >>> q90 = [np.cos(45 * c4d.d2r), 0, 0, np.sin(45 * c4d.d2r)]
  >>> np.allclose(c4d.rotmat.quat2dcm(q90), c4d.rotmat.rotz(90 * c4d.d2r))
  True

:math:`q` and :math:`-q` are the same attitude:

.. code::

  >>> np.allclose(c4d.rotmat.quat2dcm(-q), c4d.rotmat.quat2dcm(q))
  True

:func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>` also converts an array of quaternions,
e.g. the attitude history of a :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`:

.. code::

  >>> c4d.rotmat.quat2euler(np.array([q, -q])) * c4d.r2d  # doctest: +NUMPY_FORMAT
  [[10  20  30]
   [10  20  30]]


**Between ENU and NED**

.. code::

  >>> enu2ned = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]])
  >>> enu2ned @ [3, 4, 5]  # doctest: +NUMPY_FORMAT
  [4  3  -5]
  >>> np.allclose(enu2ned @ enu2ned, np.eye(3))
  True



References
----------

.. [HS] Hanspeter Schaub, "Spacecraft Dynamics and Control" lecture notes, module 2: rigidbody kinematics.
.. [MIs] Ch 4 in "Missile Flight Simulation Part One Surface-to-Air Missiles", Military Handbook, 1995, MIL-HDBK-1211(MI).
.. [DI] Diebel, J., 2006, "Representing Attitude: Euler Angles, Unit Quaternions,
        and Rotation Vectors", Stanford University.



See Also
--------

.. list-table::
  :header-rows: 0

  * - :doc:`Kinematics </concepts/kinematics>`
    - Next: the propagation of the position and the attitude in time
  * - :func:`rotx <c4dynamics.rotmat.rotmat.rotx>`,
      :func:`roty <c4dynamics.rotmat.rotmat.roty>`,
      :func:`rotz <c4dynamics.rotmat.rotmat.rotz>`
    - Direction Cosine Matrices for a rotation about the :math:`x`, :math:`y`, :math:`z` axes
  * - :func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`
    - Direction Cosine Matrix for a sequence of rotations in following order: :math:`z`, then :math:`y`, then :math:`x`
  * - :func:`dcm321euler <c4dynamics.rotmat.rotmat.dcm321euler>`
    - Extract Euler angles (roll, pitch, yaw) from a Direction Cosine Matrix (DCM) of 3-2-1 order
  * - :func:`euler2quat <c4dynamics.rotmat.rotmat.euler2quat>`
    - Attitude quaternion of 3-2-1 Euler angles
  * - :func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>`
    - 3-2-1 Euler angles of an attitude quaternion (radians)
  * - :func:`quat2dcm <c4dynamics.rotmat.rotmat.quat2dcm>`
    - Body from Reference Direction Cosine Matrix of an attitude quaternion
  * - :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
    - Rigid body object with an Euler angles attitude
  * - :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`
    - Rigid body object with a quaternion attitude
  * - :func:`animate <c4dynamics.rotmat.animate.animate>`
    - Animates the rigid body's motion using a 3D model according to the 3-2-1 Euler angles histories.
