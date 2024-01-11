'''
Equations of Motion (:mod:`c4dynamics.eqm`)
=======================================================

.. currentmodule:: c4dynamics.eqm


EQM
---

.. autosummary::
   :toctree: generated/

   eqm3
   eqm6
   int3 
   int6


Background Material [MI]_
-------------------------

Introduction
^^^^^^^^^^^^

Motion models for points (particles) and rigid bodies in space and time are based on mathematical
equations. 

Three degrees of freedom models employ translational
equations of motion.
Six degrees of freedom models 
incorporate both translational 
and rotational equations of motion. 

The inputs to the equations of motion are the 
forces and moments acting on the body; 
yielding body accelerations as outputs.


Nomenclature and Convention
^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


.. figure:: /_static/figures/rigidbody.svg
   
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
     - :math:`\\varphi`
     - :math:`p`
     - :math:`I_{xx}`
   * - :math:`y_b`
     - :math:`{F_y}_b`
     - :math:`M`
     - :math:`v`
     - :math:`\\theta`
     - :math:`q`
     - :math:`I_{yy}`
   * - :math:`z_b`
     - :math:`{F_z}_b`
     - :math:`N`
     - :math:`w`
     - :math:`\\psi`
     - :math:`r`
     - :math:`I_{zz}`


The position of the mass center of the body is given by
its Cartesian coordinates expressed in an inertial frame of
reference, such as the fixed-earth frame :math:`(x, y, z)`. 

The body's angular orientation is defined by three rotations :math:`(\\psi, \\theta, \\varphi)` 
relative to the inertial frame of reference. 
These are
called Euler rotations, and the order of the successive rotations
is important. 
Starting with the body coordinate frame
aligned with the earth coordinate frame, the adopted order here is 3-2-1, i.e.: 

(1) Rotate the body frame about the :math:`z_b` axis through the heading angle :math:`\\psi`, 
(2) Rotate about the :math:`y_b` axis through the pitch angle :math:`\\theta`, and 
(3) Rotate about the :math:`x_b` axis through the roll angle :math:`\\varphi`

The total inertial velocity :math:`V` has components :math:`u, v`, and :math:`w` on the body frame axes, 
and :math:`(v_x, v_y, v_z)` on the earth-frame axes.


Newton's Second Law 
^^^^^^^^^^^^^^^^^^^

Newton’s second law of motion establishes the foundational 
equation governing the relationship among 
force, mass, and acceleration.
 

in the context of Newton's second law, the force :math:`(F)` 
acting on an object is the derivative of its momentum :math:`(m \\cdot v)` 
with respect to time :math:`(t)`:

.. math:: 
   F = {d(m \cdot v) \\over dt}

where:

- :math:`F` is the total force acting on the object

- :math:`m` is the mass of the object

- :math:`v` is the velocity 

- :math:`t` is time 

This equation yields the final form of the equations of linear motion.
In the final form, acceleration is represented by the rate of change of the velocity:

.. math::
   F = m \cdot \\dot{v}

where:

- :math:`F` is the total force acting on the object

- :math:`m` is the mass of the object

- :math:`\\dot{v}` is the acceleration of the object


A direct extension of Newton's second law to rotational motion 
reveals that the moment of force (torque) on a body 
about a given axis equals the time rate of change of the 
angular momentum of the paricle about that axis. 


.. math::
   M = {dh \\over dt} 

where:

- :math:`M` is the total moment (torque) acting on the object

- :math:`h` is the angular momentum vector of the object



Hence, the final form of the equations of angular motion is given by: 

.. math::
   M = [I] \\cdot \\dot{\omega}

where:

- :math:`M` is the total moment (torque) acting on the object

- :math:`[I]` is the inertia matrix of the body relative to the axis of rotation

- :math:`\\dot{\omega}` is the absolute angular acceleration vector of the body



   
Translational Equations of Motion
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

   dv_x = {F[0] \\over m}

   dv_y = {F[1] \\over m}

   dv_z = {F[2] \\over m}

where:

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
Euler angles, :math:`\\psi, \\theta, \\varphi`. 

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

   d\\varphi = p + (q \\cdot sin(\\varphi) + r \\cdot cos(\\varphi)) \\cdot tan(\\theta)

   d\\theta = q \\cdot cos(\\varphi) - r \\cdot sin(\\varphi)
   
   d\\psi = {q \\cdot sin(\\varphi) + r \\cdot cos(\phi) \\over cos(\\theta)}

   dp = {M[0] - q \\cdot r \\cdot (I_{zz} - I_{yy}) \\over I_{xx}}

   dq = {M[1] - p \\cdot r \\cdot (I_{xx} - I_{zz}) \\over I_{yy}}

   dr = {M[2] - p \\cdot q \\cdot (I_{yy} - I_{xx}) \\over I_{zz}}

where: 

- :math:`d\\varphi, d\\theta, d\\psi` are the changes in Euler roll, Euler pitch, and Euler yaw angles, respectively 

- :math:`dp, dq, dr` are the changes in body roll rate, pitch rate, and yaw rate, respectively

- :math:`\\varphi, \\theta, \\psi` are the Euler roll, Euler pitch, and uler yaw angles, respectively 

- :math:`p, q, r` are the body roll rate, pitch rate, and yaw rate, respcetively
   
- :math:`M[0], M[1], M[2]` are the input moment of force components about the :math:`x, y, z` in the body direction, respectively

- :math:`I_{xx}, I_{yy}, I_{zz}` are the moments of inertia about the :math:`x, y,` and :math:`z` in body direction, respectively


These equations describe the angular dynamics of a rigid body. 
Together with the equations that describe the translational 
motion of the body they form the six-dimensional motion in space (**6DOF**). 


References
----------

.. [MI] 17 July 1995, "Missile Flight Simulation Part One Surface-to-Air Missiles", 
         Ch 4 In: Military Handbook. 1995, MIL-HDBK-1211(MI)


         
Examples
--------

For examples, see the various functions.

'''


from .derivs import * 
from .integrate import * 
