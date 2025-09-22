'''

.. currentmodule:: c4dynamics.states.state


This page is an `introduction` to the states module. 
For the different state objects, go to :ref:`objects-header`.     


State Data-Structure
-------------------- 


C4dynamics offers versatile data-structures for managing state variables. 


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
:class:`state` constructor with 
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
retrieved later by calling :attr:`state.X0`:

.. code::

  >>> s.X0  # doctest: +NUMPY_FORMAT 
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
  >>> print(s)
  [ var1  var2  var3 ]



  
**Parameters**


 
All the variables that passed to the :class:`state` constructor are considered 
state variables, and only these variables. Parameters, i.e. data attributes that are 
added to the object outside the constructor (the `__init__` method), as in: 

.. code::

  >>> s.parameter = 0 

are considered part of the object attributes, but are not part of the object state:

.. code::

  >>> print(s)
  [ var1  var2  var3 ]


  
**Predefined states**

Another way to create a state instance is by using one of the pre-defined objects from 
the :mod:`states library <c4dynamics.states.lib>`. These state objects may be useful 
as they are optimized for particular tasks. 

'''


# TODO how come the overall title is not word-capatilized and the smaller are.  


import sys 
sys.path.append('.')
from c4dynamics.states.lib import * 




if __name__ == "__main__":

  # import doctest, contextlib, os
  # from c4dynamics import IgnoreOutputChecker, cprint
  
  # # Register the custom OutputChecker
  # doctest.OutputChecker = IgnoreOutputChecker

  # tofile = False 
  # optionflags = doctest.FAIL_FAST

  # if tofile: 
  #   with open(os.path.join('tests', '_out', 'output.txt'), 'w') as f:
  #     with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
  #       result = doctest.testmod(optionflags = optionflags) 
  # else: 
  #   result = doctest.testmod(optionflags = optionflags)

  # if result.failed == 0:
  #   cprint(os.path.basename(__file__) + ": all tests passed!", 'g')
  # else:
  #   print(f"{result.failed}")

  from c4dynamics import rundoctests
  rundoctests(sys.modules[__name__])




