'''

Rotational Matrix Operations
============================

   

Background Material 
-------------------

A rotation matrix is a mathematical representation of a 
rotation in three-dimensional space. 

It's a 3x3 matrix that, when multiplied with a vector, 
transforms the vector to represent a new orientation. 

Each element of the matrix corresponds to a directional cosine, 
capturing the rotation's effect on the x, y, and z axes.


Euler Angles Order
^^^^^^^^^^^^^^^^^^

Frame based vectors are related through a Direction Cosine Matrix (DCM). [HS]_

When Euler angles are employed in the transformation of
a vector expressed in one reference frame to the expression
of the vector in a different reference frame, any order of the
three Euler rotations is possible, but the resulting transformation
equations depend on the order selected. [MIs]_ 

In aerospace applications for example, 
the common order is that the first Euler rotation is about the z-axis,
the second is about the y-axis, and the third is about the Xaxis.
Such a transformation order is called z-y-x, or 3-2-1. 
With reference to a body orientation, the resulting
order is yaw, pitch, and roll. 
With reference to geographical
orientation, the resulting order is azimuth (heading),
elevation (pitch), and roll (bank angle).


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


.. figure:: /_static/frame_conventions.svg
   
   Fig-1: Coordinate System Conventions 


References
----------

.. [HS] Hanspeter Schaub, "Spacecraft Dynamics and Control" lecture notes, module 2: rigidbody kinematics. 
.. [MIs] Ch 4 in "Missile Flight Simulation Part One Surface-to-Air Missiles", Military Handbook, 1995, MIL-HDBK-1211(MI).    



Examples
--------

For examples, see the various functions.

''' 
# spacecraft dyanmics and control 

# Rotating Reference Frame
# ^^^^^^^^^^^^^^^^^^^^^^^^

# A vector resolved in a given reference frame is said to be 
# **expressed** in that frame (sometimes said **referred to**). 

# The rate of change of a vector, as viewed by an observer fixed to and moving 
# with a given reference frame, 
# is said to be **relative to** or **with respect to** that reference frame. 

# It's important to note here that the rate of change of a vector must be 
# relative to an inertial reference frame, 
# but it can be expressed in any reference frame. 


import sys 
sys.path.append('.')

from c4dynamics.rotmat.rotmat import rotx, roty, rotz, dcm321, dcm321euler
from c4dynamics.rotmat.animate import animate  



if __name__ == "__main__":

  import doctest, contextlib, os
  from c4dynamics import IgnoreOutputChecker, cprint
  
  # Register the custom OutputChecker
  doctest.OutputChecker = IgnoreOutputChecker

  tofile = False 
  optionflags = doctest.FAIL_FAST

  if tofile: 
    with open(os.path.join('tests', '_out', 'output.txt'), 'w') as f:
      with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        result = doctest.testmod(optionflags = optionflags) 
  else: 
    result = doctest.testmod(optionflags = optionflags)

  if result.failed == 0:
    cprint(os.path.basename(__file__) + ": all tests passed!", 'g')
  else:
    print(f"{result.failed}")







