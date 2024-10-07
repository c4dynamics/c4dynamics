# TODO add small photo for expreicne next to each state?
# TODO how come the overall title is not word-capatilized and the smaller are.  
'''

.. currentmodule:: c4dynamics.states.state


This page is an `introduction` to the states module. 
For the different state objects, go to :ref:`objects-header`.     


State Data-Structure
-------------------- 


C4dynamics offers a versatile data-structures for managing state variables. 


Users from a range of disciplines, particularly those involving mathematical modeling, 
simulations, and dynamic systems, can define a state with any desired variables, for example: 



**Control Systems** 
 
- `Pendulum`
- :math:`X = [\\theta, \\omega]^T`
- Angle, angular velocity. 
- :code:`s = c4d.state(theta = 10 * c4d.d2r, omega = 0)`



**Navigation**
  
- `Strapdown navigation system` 
- :math:`X = [x, y, z, v_x, v_y, v_z, q_0, q_1, q_2, q_3, b_{ax}, b_{ay}, b_{az}]^T`
- Position, velocity, quaternions, biases. 
- :code:`s = c4d.state(x = 0, y = 0, z = 0, vx = 0, vy = 0, vz = 0, q0 = 0, q1 = 0, q2 = 0, q3 = 0, bax = 0, bay = 0, baz = 0)`



**Computer Vision**  
  
- `Objects tracker` 
- :math:`X = [x, y, w, h]^T`
- Center pixel, bounding box size. 
- :code:`s = c4d.state(x = 960, y = 540, w = 20, h = 10)`



**Aerospace**  

- `Aircraft`
- :math:`X = [x, y, z, v_x, v_y, v_z, \\varphi, \\theta, \\psi, p, q, r]^T`
- Position, velocity, angles, angular velocities. 
- :code:`s = c4d.state(x = 0, y = 0, z = 0, vx = 0, vy = 0, vz = 0, phi = 0, theta = 0, psi = 0, p = 0, q = 0, r = 0)`



**Autonomous Systems**  
  
- `Self-driving car`
- :math:`X = [x, y, z, \\theta, \\omega]^T`
- Position and velocity, heading and angular velocity. 
- :code:`s = c4d.state(x = 0, y = 0, v = 0, theta = 0, omega = 0)`



**Robotics**  

- `Robot arm`
- :math:`X = [\\theta_1, \\theta_2, \\omega_1, \\omega_2]^T`
- Joint angles, angular velocities. 
- :code:`s = c4d.state(theta1 = 0, theta2 = 0, omega1 = 0, omega2 = 0)`



And many others. 


These data-structures encapsulate the variables into a state vector :math:`X` (a numpy array), 
allows for seamless execution of vector operations on the state, 
enabling efficient and intuitive manipulations of the state data. 




Operations 
----------

Operations on state vectors are categorized into two main types: 
`mathematical operations` and `data management operations`.

The mathematical operations involve direct manipulation of the state vectors 
using mathematical methods. These operations include multiplication, addition, and normalization, 
and can be performed by standard `numpy` methods. 

The data management operations involve managing the state vector data, 
such as storing and retrieving states at different times or handling time series data. 
To perform these operations, `c4dynamics` provides a variety of methods under the :class:`state object <state>`.   


The following tables summarize the mathematical and data management operations 
on a state vector. 

Let an arbitrary state vector with variables :math:`x = 1, y = 0, z = 0`:


.. code:: 

  >>> s = c4d.state(x = 1, y = 0, z = 0)
  >>> s
  [ x  y  z ]
  >>> s.X
  [1  0  0]

.. list-table:: Mathematical Operations
   :widths: 30 70
   :header-rows: 1

   * - Operation 
     - Example

   * - Scalar Multiplication	
     - | :code:`>>> s.X * 2`
       | :code:`[2  0  0]` 

   * - Matrix Multiplication	
     - | :code:`>>> R = c4d.rotmat.dcm321(psi = c4d.pi / 2)` 
       | :code:`>>> s.X @ R`
       | :code:`[0  1  0]` 

   * - Norm Calculation	
     - | :code:`>>> np.linalg.norm(s.X)`
       | :code:`1` 

   * - Addition/Subtraction	
     - | :code:`>>> s.X + [-1, 0, 0]`
       | :code:`[0  0  0]` 

   * - Dot Product	
     - | :code:`>>> s.X @ s.X`
       | :code:`1` 

   * - Normalization
     - | :code:`>>> s.X / np.linalg.norm(s.X)`
       | :code:`[1  0  0]` 
    
     


.. list-table:: Data Management Operations
   :widths: 30 70
   :header-rows: 1

   * - Operation 
     - Example

   * - Store the current state  	
     - :code:`>>> s.store()`

   * - Store with time-stamp  	
     - :code:`>>> s.store(t = 0)`

   * - Store the state in a for-loop   	
     - | :code:`>>> for t in np.linspace(0, 1, 3)):`
       | :code:`...   s.X = np.random.rand(3)`
       | :code:`...   s.store(t)`

   * - Get the stored data  	
     - | :code:`>>> s.data()`
       | :code:`[[0     0.37  0.76  0.20]`
       | :code:`[0.5    0.93  0.28  0.59]`
       | :code:`[1      0.79  0.39  0.33]]`

   * - Get the time-series of the data	
     - | :code:`>>> s.data('t')`
       | :code:`[0  0.5  1]`

   * - Get data of a variable	
     - | :code:`>>> s.data('x')[1]`
       | :code:`[0.37  0.93  0.79]`

   * - Get time-series and data of a variable	
     - | :code:`>>> time, y_data = s.data('y')`
       | :code:`>>> time`
       | :code:`[0  0.5  1]`
       | :code:`>>> y_data`
       | :code:`[0.76  0.28  0.39]`

   * - Get the state at a given time	
     - | :code:`>>> s.timestate(t = 0.5)`
       | :code:`[0.93  0.28  0.59]`

   * - Plot the histories of a variable	
     - | :code:`>>> s.plot('z')`
       | ...





State Construction 
------------------

A state instance is created by calling the 
:class:`state` constructor with 
pairs of variables that compose the state and their initial conditions. 
For example, a state of two 
variables, :math:`var1` and :math:`var2`, is created by:

.. code::

  >>> s = c4d.state(var1 = 0, var2 = 0)


The list of the variables that form the state is given by :code:`print(s)`. 

.. code::

  >>> s
  [ var1  var2 ]

  
**Initial conditions**
  
The variables must be passed with initial values. These values may be 
retrieved later by calling :attr:`state.X0`:

.. code::

  >>> s.X0
  [0  0]

When the initial values are not known at the stage of constructing 
the state object, it's possible to pass zeros and override them later 
by direct assignment of the state variable with a `0` suffix, :code:`s.var10 = 100`, :code:`s.var20 = 200`. 
See more at :attr:`state.X0`. 

  
**Adding variables**

    
Adding state variables outside the  
constructor is possible by using :meth:`addvars(**kwargs) <c4dynamics.states.state.state.addvars>`, 
where `kwargs` represent the pairs of variables and their initial conditions as calling the
`state` constructor:  

.. code:: 

  >>> s.addvars(var3 = 0)
  >>> s
  [ var1  var2  var3 ]



  
**Parameters**


 
All the variables that passed to the :class:`state` constructor are considered 
state variables, and only these variables. Parameters, i.e. data attributes that are 
added to the object outside the constructor (the `__init__` method), as in: 

.. code::

  >>> s.parameter = 0 

are considered part of the object attributes, but are not part of the object state:

.. code::

  >>> s
  [ var1  var2  var3 ]


  
**Predefined states**

Another way to create a state instance is by using one of the pre-defined objects from 
the :mod:`states library <c4dynamics.states.lib>`. These state objects may be useful 
as they are optimized for particular tasks. 





'''
# 
# TODO BUG FIXME HACK NOTE XXX 
# TODO IMPROVMEMNT
# BUG LOGICAL FAILURE PROBABLY COMES WITH XXX
# FIXME NOT SEVERE BUT A BETTER IDEA IS TO DO SO
# HACK I KNOW ITS NOT BEST SOLUTION TREAT IF U HAVE SPARE TIME
# NOTE MORE IMPORTANT THAN A CASUAL COMMENT
# XXX TREAT THIS BEFORE OTHERS
# 

from .lib import * 










# \\ 2 or 3 examples and then discription. 
#   6 degrees
#   kaman
#   control
#   object tracking
#   navigation/ guidance
#   signal processing 


# ``control``
# .. raw:: html

#   <strong>control</control>


# .. code::

#   >>> plane = c4.state(z = 1000, gamma = 10)
#   >>> plane
#   [z  γ]
#   >>> plane.X
#   [1000  0]


# ``objects trackging``


# .. code::

#   >>> pixel = c4.state(x = cv2.im[0, 0], y = cv2.im[0, 1])
#   >>> pixle
#   [x,  y]

# ``6 degrees of freedom``


# .. code:: 

#   pass


# ``data science`` 

# .. code:: 
#   pass 


# ``more examples``
# see the complete quickstart page for states definition. 


# ****************
# state operations
# ****************

# The state is the fundamental entity in dynamic systems.
# It is a snapshot representation of the system at a given time. 

# In various fields such as control theory, quantum mechanics, 
# and signal processing, the state vector use to design and analysis, 
# system investigation and manipluation. 


# In control systems, the state vector represents the system's status 
# in terms of its variables, such as position, velocity, and other relevant parameters. 
# It is fundamental for designing controllers and observers.
  
# Quantum Mechanics: The state vector, often referred to as a wavefunction, 
# describes the quantum state of a particle or system. 
# It is used to compute probabilities of outcomes of measurements.

# In signal processing, state vectors are used to model and analyze 
# time-varying signals. They help in designing filters and predicting signal behavior.

# Economics and Finance: State vectors model economic indicators 
# and financial instruments, assisting in forecasting and decision-making processes.

# Computer Science: In areas like robotics and artificial intelligence, 
# state vectors represent the status of systems and environments, 
# enabling complex decision-making and control algorithms.


# The operations performed on state vectors depend on the 
# specific application and the nature of the system being modeled. 
# Common operations include:

# State Transition: 
# This operation involves updating 
# the state vector based on a dynamic model of the system. 
# It is essential for predicting future states.


# Measurement Update: 
# Integrating new data or measurements to refine the state vector, 
# reducing uncertainty and improving accuracy.

# Linear Transformations: 
# Applying matrices to state vectors to perform operations such as rotations, 
# scaling, and projections. 
# These transformations are fundamental in both control theory and quantum mechanics.

# Normalization: 
# In quantum mechanics, state vectors must be normalized to 
# ensure that the total probability is one. 
# This operation is crucial for accurate probabilistic interpretations.

# Filtering: 
# Techniques like Kalman filtering are used to 
# estimate the state vector in the presence of noise 
# and uncertainty, combining predictions and measurements.

# State Estimation: 
# Methods such as the observer design in control theory 
# or the particle filter in robotics are used to estimate 
# the state vector from incomplete or noisy data.


# State vectors provide a structured and efficient 
# way to represent and manipulate the state of complex systems. 
# They enable:

# Predictive Modeling: Forecasting future states based on current information and dynamic models.
# Optimization: Enhancing system performance through control strategies and feedback mechanisms.
# Robustness: Improving system resilience to disturbances and uncertainties through 
# adaptive techniques.
# Decision Making: Facilitating informed decisions in automated systems and intelligent agents.

# In summary, state vectors are a foundational concept across multiple disciplines, 
# providing a powerful framework for representing, analyzing, and manipulating 
# the states of dynamic systems. Whether in engineering, physics, or computational sciences, 
# understanding and effectively utilizing state vectors is key to advancing technology 
# and scientific knowledge.



# *****************
# c4dynamics states
# *****************

# =====
# state
# =====

# the simplest way to construct a state object is by calling :mod:`state` with 
# the required arguments: 

# .. code:: 

#   >>> s = c4d.state(x = 0, y = 0)

# s now is a state object with two variables: x, and y:

# .. code::

#   >>> s
#   [x  y]

# getting and viewing the current state is possible by the `X` property:

# .. code::

#   >>> s.X
#   [0  0]

# operating on the state is possible also with the X property:


# .. code::

#   >>> s.X += 1 

# to advance the whole state vector by 1

# the state always encapsulates the state at a given time. 
# when storing the current state it may be with explicit time:

# .. code::

#   >>> s.store(t = 10.445)
#   >>> s.data('x')
#   [[0  0.001  0.002...]
#     , [12  12  12...]]

# otherwise the samples are just stored in a serial order without a timetag.


# ==========
# states lib
# ==========

# another way to use c4dynamics states is to use one of the predefined 
# state objects as appear in **



  






# '''




