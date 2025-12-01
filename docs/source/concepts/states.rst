State Objects 
=============

Modeling dynamic systems through state objects provides a unifying abstraction: 
every system, regardless of its complexity, evolves through changes in its state. 

By encapsulating state variables in dedicated objects, we gain:

- Clarity - separating system variables from equations and algorithms.
- Consistency - a common interface for kinematics, sensors, filters, and environments.
- Flexibility - seamless extension to new models and operations without rewriting the core logic.

This approach turns the state into a first-class entity, making simulation and algorithm development both intuitive and scalable.


In ``c4dynamics``, state objects stand at the core of the framework, serving as the foundation upon which all models, algorithms, and simulations are built.


State Data-Structure
-------------------- 


C4dynamics offers versatile data-structures for managing state variables. 


Users from a range of disciplines, particularly those involving mathematical modeling, 
simulations, and dynamic systems, can define a state with any desired variables, for example: 



**Control Systems** 
 
- `Pendulum`
- :math:`X = [\theta, \omega]^T`
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
- :math:`X = [x, y, z, v_x, v_y, v_z, \varphi, \theta, \psi, p, q, r]^T`
- Position, velocity, angles, angular velocities. 
- :code:`s = c4d.state(x = 0, y = 0, z = 0, vx = 0, vy = 0, vz = 0, phi = 0, theta = 0, psi = 0, p = 0, q = 0, r = 0)`



**Autonomous Systems**  
  
- `Self-driving car`
- :math:`X = [x, y, z, \theta, \omega]^T`
- Position and velocity, heading and angular velocity. 
- :code:`s = c4d.state(x = 0, y = 0, v = 0, theta = 0, omega = 0)`



**Robotics**  

- `Robot arm`
- :math:`X = [\theta_1, \theta_2, \omega_1, \omega_2]^T`
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
To perform these operations, `c4dynamics` provides a variety of methods under the :class:`state object <c4dynamics.states.state.state>`.   


The following tables summarize the mathematical and data management operations 
on a state vector. 

Let an arbitrary state vector with variables :math:`x = 1, y = 0, z = 0`:

Import c4dynamics: 

.. code:: 

  >>> import c4dynamics as c4d 

.. code:: 

  >>> s = c4d.state(x = 1, y = 0, z = 0)
  >>> print(s)
  [ x  y  z ]
  >>> s.X   # doctest: +NUMPY_FORMAT
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
     - | :code:`>>> for t in np.linspace(0, 1, 3):`
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
:class:`state <c4dynamics.states.state.state>` constructor with 
pairs of variables that compose the state and their initial conditions. 
For example, a state of two 
variables, :math:`var1` and :math:`var2`, is created by:

.. code::

  >>> s = c4d.state(var1 = 0, var2 = 0)


The list of the variables that form the state is given by :code:`print(s)`. 

.. code::

  >>> print(s)
  [ var1  var2 ]

  
**Initial conditions**
  
The variables must be passed with initial values. These values may be 
retrieved later by calling :attr:`X0 <c4dynamics.states.state.state.X0>`:

.. code::

  >>> s.X0  # doctest: +NUMPY_FORMAT 
  [0  0]

When the initial values are not known at the stage of constructing 
the state object, it's possible to pass zeros and override them later 
by direct assignment of the state variable with a `0` suffix, :code:`s.var10 = 100`, :code:`s.var20 = 200`. 
See more at :attr:`state.X0 <c4dynamics.states.state.state.X0>`. 


**Assignment Length Must Match**

Assignments to `X` must match the current state vector length:

.. code:: 

  s = c4d.state(v1 = 0, v2 = 0, v3 = 0)     # Initialize s with 3 variables
  s.X = [1, 2, 3]                           # Assign 3 new values → Ok 
  s.X = [1, 2]                              # Length mismatch → ValueError   
  s.X[:2] = [1, 2]                          # Slicing assignment → Ok (updates part of the vector)  


     
**Adding variables**

    
Adding state variables outside the  
constructor is possible by using :meth:`addvars(**kwargs) <c4dynamics.states.state.state.addvars>`, 
where `kwargs` represent the pairs of variables and their initial conditions as calling the
`state` constructor:  

.. code:: 

  >>> s.addvars(var3 = 0)
  >>> print(s)
  [ var1  var2  var3 ]


  
**Parameters**

 
All the variables that passed to the :class:`state <c4dynamics.states.state.state>` constructor are considered 
state variables, and only these variables. Parameters, i.e. data attributes that are 
added to the object outside the constructor (the `__init__` method), as in: 

.. code::

  >>> s.parameter = 0 

are considered part of the object attributes, but are not part of the object state:

.. code::

  >>> print(s)
  [ var1  var2  var3 ]





State Type 
----------

The state object always uses a `fixed floating-point type` for the state vector :code:`X`. 
This ensures consistent numerical precision, predictable behavior, and compatibility with scientific computations.

All state variables are stored internally as `float64` (`np.float64`), regardless of the type used at initialization:

.. code::

  s1 = state(x = 0,  y = 0 )   # integers provided
  s2 = state(x = 0., y = 0.)   # floats provided

Both :code:`s1.X` and :code:`s2.X` are stored as `float64`.

When any value is assigned to the state vector, it is automatically converted to `float64`:

.. code::

  s.X[0] = 1      # integers → float64
  s.X[0] = 1.0    # float64 → stays float64

This ensures all internal computations operate on a consistent floating-point type,
preventing silent type mismatches and numerical inconsistencies.





See Also
^^^^^^^^

.. list-table:: 
  :header-rows: 0

  * - :class:`State <c4dynamics.states.state.state>`
    - The state class


  

=================

Predefined States
=================

C4dynamics includes several pre-defined state objects optimized for particular tasks. 


Each one of the states in the library is inherited from the 
:class:`state <c4dynamics.states.state.state>` 
class and has the benefit of its attributes, like 
:meth:`store() <c4dynamics.states.state.state.store>` 
:meth:`data() <c4dynamics.states.state.state.data>` 
etc. 

-----------------

1. Data Point 
-------------

C4dynamics provides built-in entities for developing 
and analyzing algorithms of objects in space and time:

:class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`: 
a class defining a point in space: position, velocity, and mass.

:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`: 
a class rigidbody a class defining a rigid body in space, i.e. 
an object with length and angular position.


.. figure:: /_architecture/body_states.svg
  :width: 482px
  :height: 534px   

  **Figure:** 
  Conceptual diagram showing the relationship between the two 
  fundamental objects used to describe bodies in space: 1) the
  datapoint, 2) the rigidbody. A rigidbody object extends the 
  datapoint by adding on it body rotational motion. 


The :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` 
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

  >>> from c4dynamics import datapoint 
  >>> dp = datapoint()

.. code::

  >>> print(dp)
  [ x  y  z  vx  vy  vz ]





Initialization of an instance does not require any mandatory parameters. 
However, 
setting values to any of the state variables uses as initial conditions: 

.. code::

  >>> dp = datapoint(x = 1000, vx = -100)

  
Functionality 
^^^^^^^^^^^^^  

The :meth:`inteqm() <c4dynamics.states.lib.datapoint.datapoint.inteqm>` method uses 
the Runge-Kutta integration technique 
to evolve the state in response to external forces. 
The mechanics underlying the equations of motion can be found 
:mod:`here <c4dynamics.eqm>`. 

The method :meth:`plot() <c4dynamics.states.lib.datapoint.datapoint.plot>` adds on 
the standard :meth:`state.plot() <c4dynamics.states.state.state.plot>` 
the option to draw trajectories from side view and from top view.  
  



-----------------

2. Rigid Body
-------------

The :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` 
class extends the functionality of the :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`. 

It introduces additional attributes related to rotational 
dynamics, such as angular position, angular velocity, and moment of inertia. 
The class leverages the capabilities of the datapoint 
class for handling translational dynamics and extends 
it to include rotational aspects. See the figure above. 



Data Attributes
^^^^^^^^^^^^^^^ 

State variables:

.. math:: 

  X = [x, y, z, v_x, v_y, v_z, {\varphi}, {\theta}, {\psi}, p, q, r]^T 

- Position, velocity, angles, angle rates. 


Parameters: 

- `mass`: point mass.
- `I`: vector of moments of inertia about 3 axes.

Construction
^^^^^^^^^^^^

A `rigidbody` instance is created by making a direct call to the rigidbody constructor:

.. code::

  >>> from c4dynamics import rigidbody 
  >>> rb = rigidbody()


.. code::

  >>> print(rb)
  [ x  y  z  vx  vy  vz  φ  θ  ψ  p  q  r ]


  


  
Similar to the datapoint, 
initialization of an instance does not require any mandatory parameters. 
Setting values to any of the state variables uses as initial conditions: 

.. code::

  >>> from c4dynamics import d2r  
  >>> rb = rigidbody(theta = 10 * d2r, q = -1 * d2r)
  


Functionality 
^^^^^^^^^^^^^  

The :meth:`inteqm() <c4dynamics.states.lib.rigidbody.rigidbody.inteqm>` method uses 
the Runge-Kutta integration technique 
to evolve the state in response to external forces and moments. 
The mechanics underlying the equations of motion can be found 
:mod:`here <c4dynamics.eqm>` and :mod:`here <c4dynamics.rotmat>`. 

:attr:`BR <c4dynamics.states.lib.rigidbody.rigidbody.BR>` and 
:attr:`RB <c4dynamics.states.lib.rigidbody.rigidbody.RB>` return 
Direction Cosine Matrices, Body from Reference (`[BR]`) 
and Reference from Body (`[RB]`), with respect to the 
instantaneous Euler angles (:math:`\varphi, \theta, \psi`). 

When a 3D model is provided, the method 
:meth:`animate() <c4dynamics.states.lib.rigidbody.rigidbody.animate>` 
animates the object with respect to the histories of 
the rigidbody attitude.  



-----------------

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

  >>> from c4dynamics import pixelpoint 
  >>> pp = pixelpoint(x = 50, y = 50, w = 15, h = 25) # (50, 50) detected object center, (15, 25) object bounding box  
  >>> pp.fsize = (100, 100)   # frame width and frame height
  >>> pp.class_id = 'fox'



.. code::

  >>> print(pp)
  [ x  y  w  h ]

  
  
Functionality 
^^^^^^^^^^^^^  

:attr:`box <c4dynamics.states.lib.pixelpoint.pixelpoint.box>` 
returns the bounding box in terms of top-left and bottom-right coordinates. 




See Also
^^^^^^^^

.. list-table:: 
  :header-rows: 0

  * - :class:`State <c4dynamics.states.state.state>`
    - The state class


**Pre-defined state objects**

.. list-table:: 
  :header-rows: 0

  * - :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`
    - A point in space
  * - :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
    - Rigid body object
  * - :class:`pixelpoint <c4dynamics.states.lib.pixelpoint.pixelpoint>`
    - A pixel point in an image




