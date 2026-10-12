Rigid Body Transformations
==========================


The ``rotmat`` module in c4dynamics provides a collection of
functions for defining and exploring the rotation of bodies from
one frame of reference to another.

This page covers the background:
what a frame of reference is,
the notation c4dynamics uses for rotation matrices,
the three representations of an attitude (Euler angles, rotation matrix, quaternion),
how to convert between them,
and how to rotate vectors from one frame to another.


Background Material
-------------------


.. _transformations-frames:

Reference Frames
^^^^^^^^^^^^^^^^

A frame of reference (or a coordinate system) is an origin and three
mutually perpendicular unit axes, :math:`x, y, z`.
A physical vector, such as a velocity or a force, exists independently of any frame.
Its three components, however, depend on the frame in which it is resolved.
A vector resolved in a given frame is said to be **expressed** in that frame.

For example, an aircraft that flies north at :math:`150 m/s` and pitches up by :math:`30°`
has a single velocity vector.
In an earth frame its components are :math:`[150, 0, 0]`,
while in the aircraft body frame they are :math:`[129.9, 0, 75]`
(see the examples below).

The rate of change of a vector, as viewed by an observer fixed to and moving
with a given frame, is said to be **relative to** (or **with respect to**) that frame.
The laws of motion hold relative to an inertial frame,
but the vectors in them can be expressed in any frame.

The frames that appear throughout c4dynamics:

.. list-table::
   :widths: 10 30 60
   :header-rows: 1

   * - Symbol
     - Frame
     - Description
   * - :math:`R`
     - Reference
     - The frame against which the attitude of a body is defined.
       Usually an inertial earth frame. This is the default frame of the
       position and the velocity of the state objects
       (:math:`x, y, z, v_x, v_y, v_z`).
   * - :math:`I`
     - Inertial
     - A reference frame that does not accelerate or rotate.
       In c4dynamics, :math:`I` and :math:`R` are used interchangeably when the
       reference frame is inertial, e.g. in the navigation sensors and the quadcopter model.
   * - :math:`B`
     - Body
     - A frame fixed to the body and rotating with it. The origin is
       at the center of mass and :math:`x_b` is along the centerline (the nose).
       The body angular rates :math:`(p, q, r)` and the body velocity
       :math:`(u, v, w)` are expressed in this frame.
   * - :math:`S`
     - Sensor
     - A frame fixed to a sensor, such as a :class:`seeker <c4dynamics.sensors.seeker.seeker>`
       or a :class:`radar <c4dynamics.sensors.radar.radar>`.
       Its :math:`x` axis is the sensor boresight.

Two pairs of an inertial frame and a body frame are common for vehicles that fly
above a flat earth.
Both are supported by the quadcopter model and the navigation sensors through the
``frame`` argument (see :ref:`Quadcopter Equations of Motion <kinematics-quadcopter>`):

.. list-table::
   :widths: 15 40 45
   :header-rows: 1

   * - ``frame``
     - Inertial frame
     - Body frame
   * - ``'NED'``
     - :math:`x` north, :math:`y` east, :math:`z` down
     - :math:`x` forward, :math:`y` right, :math:`z` down (FRD)
   * - ``'ENU'``
     - :math:`x` east, :math:`y` north, :math:`z` up
     - :math:`x` forward, :math:`y` left, :math:`z` up (FLU)


Right Hand Frame
^^^^^^^^^^^^^^^^

The positive directions of coordinate system
axes and the directions of positive rotations
about the axes are arbitrary.
In right-handed systems:

::

  i x j = k
  j x k = i
  k x i = j

where i is the unit vector in the direction of the x-axis,
j is the unit vector in the direction of the y-axis,
k is the unit vector in the direction of the z-axis.

Positive rotations are clockwise
when viewed from the origin, looking out along the
positive direction of the axis.

These conventions are illustrated
in Fig-1.


.. figure:: /_architecture/frame_conventions.svg

   Fig-1: Coordinate System Conventions


.. _transformations-notation:

Rotation Matrix Notation
^^^^^^^^^^^^^^^^^^^^^^^^

Vectors that are expressed in different frames are related through a
Direction Cosine Matrix (DCM), a :math:`3 \times 3` rotation matrix. [HS]_

c4dynamics names a rotation matrix by two letters in square brackets.
The letters state the direction of the transformation, read from right to left:

.. math::

  [BR] \quad \text{- a rotation matrix from the frame } R \text{ to the frame } B

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
     - Body from Inertial, used in the IMU, the magnetometer, and the quadcopter model
   * - :math:`[SB]`
     - Sensor from Body, e.g. the gimbal of a seeker

**Direction cosines.** The element :math:`[BR]_{ij}` is the cosine of the angle between
the :math:`i`-th axis of :math:`B` and the :math:`j`-th axis of :math:`R`.
Hence the rows of :math:`[BR]` are the body axes expressed in :math:`R`,
and its columns are the reference axes expressed in :math:`B`.

**Inverse.** A rotation matrix is orthonormal, :math:`[BR] \cdot [BR]^T = I_3`,
and its determinant is :math:`+1`. Its inverse is its transpose,
which is the transformation in the opposite direction:

.. math::

  [RB] = [BR]^{-1} = [BR]^T

  v_R = [RB] \cdot v_B

**Composition.** A chain of transformations is composed by cancelling adjacent letters.
For three frames :math:`A, B, C`:

.. math::

  [CA] = [CB] \cdot [BA]

For example, a seeker that is mounted on a gimbal sees the reference frame through
:math:`[SR] = [SB] \cdot [BR]`.

**Passive rotation.** The rotation matrices in c4dynamics are *passive*:
they rotate the frame of coordinates rather than the vector.
The vector itself is unchanged; only the frame in which its components
are expressed changes.
To rotate a vector *actively* by a positive angle within the same frame,
use the transpose. E.g. :math:`R_z(\psi)^T \cdot v` rotates :math:`v` by :math:`\psi`
about :math:`z`.


Elementary Rotations
^^^^^^^^^^^^^^^^^^^^

A rotation of a frame through an angle about one of its axes is given by an
elementary rotation matrix:

.. math::

  R_x(\varphi) = \begin{bmatrix}
      1 & 0 & 0 \\
      0 & cos(\varphi) & sin(\varphi) \\
      0 & -sin(\varphi) & cos(\varphi)
    \end{bmatrix}
  , \quad
  R_y(\theta) = \begin{bmatrix}
      cos(\theta) & 0 & -sin(\theta) \\
      0 & 1 & 0 \\
      sin(\theta) & 0 & cos(\theta)
    \end{bmatrix}
  , \quad
  R_z(\psi) = \begin{bmatrix}
      cos(\psi) & sin(\psi) & 0 \\
      -sin(\psi) & cos(\psi) & 0 \\
      0 & 0 & 1
    \end{bmatrix}

These are implemented by :func:`rotx <c4dynamics.rotmat.rotmat.rotx>`,
:func:`roty <c4dynamics.rotmat.rotmat.roty>`, and
:func:`rotz <c4dynamics.rotmat.rotmat.rotz>`.
Any attitude is reached by a sequence of three elementary rotations.


Euler Angles Order
^^^^^^^^^^^^^^^^^^

When Euler angles are employed in the transformation of
a vector expressed in one reference frame to the expression
of the vector in a different reference frame, any order of the
three Euler rotations is possible, but the resulting transformation
equations depend on the order selected. [MIs]_

In aerospace applications for example,
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

where :math:`c \equiv cos` and :math:`s \equiv sin`.
This matrix is computed by :func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`.

The Euler angles are extracted back from the matrix by:

.. math::

  \varphi = atan2([BR]_{23}, [BR]_{33})

  \theta = -asin([BR]_{13})

  \psi = atan2([BR]_{12}, [BR]_{11})

The 3-2-1 Euler angles are singular at :math:`\theta = \pm 90°` (gimbal lock),
where :math:`\varphi` and :math:`\psi` are not uniquely defined.


Quaternions
^^^^^^^^^^^

A rotation can also be represented by a unit quaternion.
According to Euler's rotation theorem, any orientation is reached from the
reference frame by a single rotation through an angle :math:`\alpha`
about a unit axis :math:`n`. The attitude quaternion stores this rotation,
scalar first:

.. math::

  q = [q_w, q_x, q_y, q_z] = [cos(\alpha / 2), \; n \cdot sin(\alpha / 2)], \qquad \|q\| = 1

Unlike the three Euler angles, the quaternion has no singular attitude,
which makes it the representation of choice for vehicles that may reach any attitude.
:math:`q` and :math:`-q` describe the same rotation.

In c4dynamics, a quaternion describes the same attitude as the 3-2-1 Euler angles
:math:`(\varphi, \theta, \psi)` of the convention above,
and the Body from Reference DCM computed from the quaternion is identical to
:func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>` of those angles.

The :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>` state object
carries its attitude as such a quaternion. For the quaternion kinematics, see the
:ref:`Kinematics <kinematics-quaternion>` concept page.


.. _transformations-conversions:

Converting Between Representations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An attitude has three equivalent representations in c4dynamics.
The functions of the ``rotmat`` module convert between them:

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


See Also
--------

The rotation matrices in the equations of motion, and the quaternion kinematics,
are on the :doc:`Kinematics </concepts/kinematics>` concept page.

.. list-table::
  :header-rows: 0

  * - :func:`rotx <c4dynamics.rotmat.rotmat.rotx>`
    - Direction Cosine Matrix for a rotation about the x
  * - :func:`roty <c4dynamics.rotmat.rotmat.roty>`
    - Direction Cosine Matrix for a rotation about the y
  * - :func:`rotz <c4dynamics.rotmat.rotmat.rotz>`
    - Direction Cosine Matrix for a rotation about the z
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
