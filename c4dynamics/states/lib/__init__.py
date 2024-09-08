'''
This page is an `introduction` to the states library. 
For the different pre-defined states themselves, go to :ref:`states-header`.     

.. currentmodule:: c4dynamics.states.lib

Each one of the states in the library is inherited from the 
:class:`state <c4dynamics.states.state.state>` 
class and has the benefit of its attributes, like 
:meth:`store() <c4dynamics.states.state.state.store>` 
:meth:`data() <c4dynamics.states.state.state.data>` 
etc. 


1. Data Point 
-------------

C4dynamics provides built-in entities for developing 
and analyzing algorithms of objects in space and time:

:class:`datapoint <datapoint.datapoint>`: 
a class defining a point in space: position, velocity, and mass.

:class:`rigidbody <rigidbody.rigidbody>`: 
a class rigidbody a class defining a rigid body in space, i.e. 
an object with length and angular position.


.. figure:: /_static/figures/bodies.svg
  :width: 482px
  :height: 534px   

  **Figure** 
  Conceptual diagram showing the relationship between the two 
  fundamental objects used to describe bodies in space: 1) the
  datapoint, 2) the rigidbody. A rigidbody object extends the 
  datapoint by adding on it body rotational motion. 


The :class:`datapoint <datapoint.datapoint>` 
is the most basic element in translational dynamics; it's a point in space. 

A `datapoint` serves as the building block for modeling and simulating 
the motion of objects in a three-dimensional space. 
In the context of translational dynamics, a datapoint represents 
a point mass in space with defined Cartesian coordinates :math:`(x, y, z)` 
and associated velocities :math:`(v_x, v_y, v_z)`. 


Data Attributes
^^^^^^^^^^^^^^^ 

State variables: 

.. math:: 

  X = [x, y, z, v_x, v_y, v_z]^T 

- Position coordinates, velocity coordinates. 

Parameters: 

- `mass`: point mass.

  
Construction
^^^^^^^^^^^^

A `datapoint` instance is created by making a direct call to the datapoint constructor:

.. code::

  >>> dp = c4d.datapoint()

.. code::

  >>> dp
  [ x  y  z  vx  vy  vz ]





Initialization of an instance does not require any mandatory parameters. 
However, 
setting values to any of the state variables uses as initial conditions: 

.. code::

  >>> dp = c4d.datapoint(x = 1000, vx = -100)

  
Functionality 
^^^^^^^^^^^^^  

The :meth:`inteqm() <datapoint.datapoint.inteqm>` method uses 
the Runge-Kutta integration technique 
to evolve the state in response to external forces. 
The mechanics underlying the equations of motion can be found 
:mod:`here <c4dynamics.eqm>`. 

The method :meth:`plot() <datapoint.datapoint.plot>` adds on 
the standard :meth:`state.plot() <c4dynamics.states.state.state.plot>` 
the option to draw trajectories from side view and from top view.  
  



See Also
^^^^^^^^
.datapoint
.eqm

 

2. Rigid Body
-------------

The :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` 
class extends the functionality of the :class:`datapoint <datapoint.datapoint>`. 

It introduces additional attributes related to rotational 
dynamics, such as angular position, angular velocity, and moment of inertia. 
The class leverages the capabilities of the datapoint 
class for handling translational dynamics and extends 
it to include rotational aspects. See the figure above. 



Data Attributes
^^^^^^^^^^^^^^^ 

State variables:

.. math:: 

  X = [x, y, z, v_x, v_y, v_z, {\\varphi}, {\\theta}, {\\psi}, p, q, r]^T 

- Position, velocity, angles, angle rates. 


Parameters: 

- `mass`: point mass.
- `I`: vector of moments of inertia about 3 axes.

Construction
^^^^^^^^^^^^

A `rigidbody` instance is created by making a direct call to the rigidbody constructor:

.. code::

  >>> rb = c4d.rigidbody()


.. code::

  >>> rb
  [ x  y  z  vx  vy  vz  φ  θ  ψ  p  q  r ]


  


  
Similar to the datapoint, 
initialization of an instance does not require any mandatory parameters. 
Setting values to any of the state variables uses as initial conditions: 

.. code::

  >>> rb = c4d.rigidbody(theta = 10 * c4d.d2r, q = -1 * c4d.d2r)
  


Functionality 
^^^^^^^^^^^^^  

The :meth:`inteqm() <rigidbody.rigidbody.inteqm>` method uses 
the Runge-Kutta integration technique 
to evolve the state in response to external forces and moments. 
The mechanics underlying the equations of motion can be found 
:mod:`here <c4dynamics.eqm>` and :mod:`here <c4dynamics.rotmat>`. 

:attr:`BR <rigidbody.rigidbody.BR>` and 
:attr:`RB <rigidbody.rigidbody.RB>` return 
Direction Cosine Matrices, Body from Reference (`[BR]`) 
and Reference from Body (`[RB]`), with respect to the 
instantaneous Euler angles (:math:`\\varphi, \\theta, \\psi`). 

When a 3D model is provided, the method 
:meth:`animate() <rigidbody.rigidbody.animate>` 
animates the object with respect to the histories of 
the rigidbody attitude.  


See Also
^^^^^^^^
.rigidbody
.eqm
.rotmat



3. Pixel Point
-------------- 

The :class:`pixelpoint <c4dynamics.states.lib.pixelpoint.pixelpoint>` 
class representing a data point in a video frame with a 
bounding box. 

This class is particularly useful for applications in computer vision, 
such as object detection and tracking.


Data Attributes
^^^^^^^^^^^^^^^

State variables: 

.. math:: 

  X = [x, y, w, h]^T 

- Center pixel, box size. 

Parameters: 

- `fsize`: frame size.
- `class_id`: object classification. 


Construction
^^^^^^^^^^^^

Usually, the `pixelpoint` instance is created immediately after an object 
detection: 

.. code::

  >>> pp = c4d.pixelpoint(x = detect[0], y = detect[1], w = detect[2], h = detect[3])
  >>> pp.fsize = (framewidth, frameheight)
  >>> pp.class_id = classID

where `detect` represents the detection coordinates, 
framewidth and frameheight are the video frame dimensions, 
and classID is the object classification. 



.. code::

  >>> pp
  [ x  y  w  h ]

  
  
Functionality 
^^^^^^^^^^^^^  

:attr:`box <c4dynamics.states.lib.pixelpoint.pixelpoint.box>` 
returns the bounding box in terms of top-left and bottom-right coordinates. 




See Also
^^^^^^^^
.pixelpoint 
.yolov3  







'''





# :class:`pixelspoint <c4dynamics.states.lib.pixelpoint.pixelpoint>` has 
# two types of coordinate :attr:`units <c4dynamics.states.lib.pixelpoint.pixelpoint.units>`: 
# `pixels` (default) and `normalized`. 
# When `normalized` mode is selected, the method 
# :attr:`Xpixels <c4dynamics.states.lib.pixelpoint.pixelpoint.Xpixels>` 
# uses to retrun the state vector in pixel coordinates. 




