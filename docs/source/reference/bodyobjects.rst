.. _bodyobjects:

************
Body Objects
************

.. currentmodule:: c4dynamics 

C4dynamics provides two basic entities for developing and analyzing algorithms of objects in space and time:

datapoint: a class defining a point in space: position, velocity, acceleration, and mass.
rigidbody: a class defining a rigid body in space, i.e. an object with length and angular position.


.. figure:: /_static/figures/bodies.svg
   :width: 482px
   :height: 534px   

   **Figure** 
   Conceptual diagram showing the relationship between the two 
   fundamental objects used to describe bodies in space: 1) the
   datapoint, 2) the rigidbody. A rigidbody object extends the 
   datapoint by adding on it body rotational motion. 

The rigidbody class extends the functionality of the datapoint class. 
It introduces additional attributes related to rotational dynamics, such as angular position, angular velocity, and moment of inertia. 
The class leverages the capabilities of the datapoint class for handling translational dynamics and extends it to include rotational aspects.


.. autosummary::
   :toctree: generated/

   datapoint
   rigidbody


.. .. toctree::
..    :maxdepth: 2

..    bodyobjects.datapoint
..    bodyobjects.rigidbody



