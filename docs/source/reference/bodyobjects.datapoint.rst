.. currentmodule:: c4dynamics 

.. _bodyobjects.datapoint:

******************************
Datapoint (:class:`datapoint`)
******************************

The :class:`datapoint` is the most basic element 
in translational dynamics; it's a point in space. 

:class:`datapoint` serves as the building block for modeling and simulating 
the motion of objects in a three-dimensional space. 
In the context of translational dynamics, a datapoint represents 
a point mass in space with defined Cartesian coordinates (x, y, z) 
and associated velocities (vx, vy, vz) and accelerations (ax, ay, az). 


Functionality 
=============

The class incorporates functionality for storing time 
histories of these state variables, 
facilitating analysis and visualization of dynamic simulations.

The class supports the integration of equations of motion 
using the Runge-Kutta method, allowing users to model the behavior 
of datapoints under the influence of external forces. 

Additionally, it provides methods for storing and retrieving data, 
enabling users to track and analyze the evolution of system variables over time.

Furthermore, the class includes plotting functions to visualize 
the trajectories and behaviors of datapoints. 
Users can generate top-view and side-view plots, 
as well as visualize the time evolution of specific variables.


Flexibility 
===========

To enhance flexibility, the class allows users to store 
additional variables of interest, facilitating the expansion of the basic datapoint model.
The code encourages modularity by emphasizing the separation of concerns, 
suggesting the move of certain functionalities to abstract classes or interfaces.


The 'State'
===========

The concept of 'state' in the context of the datapoint and rigidbody 
objects refers to the representation of a body object (datapoint or rigidbody) 
at any given time during a process. 

In the datapoint class, the state is defined by the position and
velocity attributes:


.. math:: 
  X = [x, y, z, v_x, v_y, v_z]

In the rigidbody class, the state is extended with 
the angular position and angular 
velocity attributes:

.. math:: 
  X = [x, y, z, v_x, v_y, v_z, {\varphi}, {\theta}, {\psi}, p, q, r]


A special attention is attributed to the concept of the state, 
as the datapoint and the rigidbody classes  
provide methods for storing, retrieving, and updating these 
state variables over time. 

Reading and writing of the state vairables is allowed by using the 
:attr:`X <datapoint.X>` property. 


The :attr:`inteqm <datapoint.inteqm>` method uses the Runge-Kutta integration technique 
to evolve the state in response to external forces.

A call to the :attr:`store <datapoint.store>` method saves 
the state variables at the current time, with time-stamp, if given. 


Constructing a datapoint
========================

A datapoint instance is created by making a direct call 
to the datapoint constructor:

`pt = c4d.datapoint()`

Initialization of the instance does not require any 
mandatory parameters, but each datapoint parameter can be 
determined using the \**kwargs keyword, for example:

.. code:: 

  pt = c4d.datapoint(x = 1000, vx = 200)


Regardless of the values with which the parameters of the datapoint
were constructed, the initial state is assigned 
to the initial variables: 

.. code:: 

  self.x0 = self.x
  self.y0 = self.y
  self.z0 = self.z
  self.vx0 = self.vx
  self.vy0 = self.vy
  self.vz0 = self.vz


Parameters 
----------

Optional keyword arguments: 

.. autosummary:: 
  :toctree: generated/

  datapoint.x 
  datapoint.y 
  datapoint.z 
  datapoint.vx
  datapoint.vy 
  datapoint.vz 
  datapoint.ax
  datapoint.ay 
  datapoint.az 
  datapoint.mass 


Attributes
==========

As mentioned earlier, reading and writing of the state vairables is allowed by using the 
:attr:`X <datapoint.X>` property. The entire attributes which support 
the reading and the updating of a datapoint instance are given in the following list:  


.. autosummary:: 
  :toctree: generated/

  datapoint.X 
  datapoint.X0 
  datapoint.pos 
  datapoint.vel 
  datapoint.P
  datapoint.V 
  datapoint.store 
  datapoint.storevar 
  datapoint.get_data 
  datapoint.timestate 
  datapoint.dist 
  datapoint.inteqm 
  datapoint.draw 



  
Additional Notes
================

- The class provides a foundation for modeling and simulating 
  translational dynamics in 3D space.
- Users can customize initial conditions, store additional variables, 
  and visualize simulation results.
- The integration method allows the datapoint to evolve based on external forces.
- The plotting method supports top-view, side-view, and variable-specific plots.



.. admonition:: Example 

  Simulate the flight of an aircraft starting with some given
  initial conditions and draw trajectories: 

  >>> target = c4d.datapoint(x = 4000, y = 1000, z = -3000, vx = -200, vy = -150)    
  >>> dt = 0.01 
  >>> time = np.arange(0, 10, dt)
  >>> for t in time: 
  ...  target.inteqm(np.zeros(3), dt = dt)
  ...  target.store(t)
  >>> target.draw('top')

.. figure:: /_static/figures/datapoint_top.png


Summary
=======

Overall, the :class:`datapoint` class serves as a versatile 
foundation for implementing and simulating translational dynamics, 
offering a structured approach to modeling and analyzing the motion 
of objects in three-dimensional space.
