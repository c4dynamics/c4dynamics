API Reference
=============

This API documentation is a comprehensive guide 
to the various modules, classes, and functions 
available in `c4dynamics`. 
It covers everything from core components like **state 
objects**, which encapsulate system states, 
to modules like **sensors**, **detectors**, and **filters**.

The API reference serves as both a learning tool for 
newcomers and a quick lookup for experienced users.

For a quick overview of how to get started, 
see the **Getting Started** section, and for 
detailed use cases, refer to the **Programs** section.


Namespaces 
----------

State objects and utilities should be accessed 
from c4dynamics top-level namespace:

.. code::

  >>> import c4dynamics as c4d 
  >>> s = c4d.state(...)        # Access state objects directly from the top-level namespace
  >>> c4d.d2r                   # Access constants like degrees-to-radians conversion


Other modules and classes are available by preceding the module name:

.. code::

  >>> import c4dynamics as c4d 
  >>> rdr = c4d.sensors.radar(...)            
  >>> kf = c4d.filters.kalman(...)           


Datasets  
--------

Some examples in the following API reference use datasets 
to demonstrate c4dynamics functionality. 
c4dynamics uses `Pooch` to simplify fetching data files. 
By calling: 
:code:`c4dynamics.datasets.module(file)`, 
where ``module`` and ``file`` define the dataset, 
the dataset is downloaded over the network once 
and saved to the cache for later usa.

For more details, see the :mod:`datasets <c4dynamics.datasets>` module.



Modules
-------

.. toctree:: 
  :hidden:
  :maxdepth: 1 

  State Objects <States>
  Sensors 
  Detectors 
  Filters 
  Kinematics <eqm>
  Rotations <rotmat>
  Utils 
  Datasets 



.. list-table:: 
  :header-rows: 0

  * - :doc:`State Objects <States>`
    - Data-structures for state variables
  * - :doc:`Sensors <Sensors>`
    - Sensor models to simulate radar and seeker
  * - :doc:`Detectors <Detectors>`
    - API to object detection models
  * - :doc:`Filters <Filters>`
    - | State observers.
      | Lowpass filter.
  * - :doc:`Kinematics <eqm>`
    - Equations of motion solvers
  * - :doc:`Rotations <rotmat>`
    - Rotation matrix operations
  * - :doc:`Utils <Utils>`
    - Utility Functions and mathematical tools
  * - :doc:`Datasets <Datasets>`
    - An interface for managing datasets and pre-trained models



