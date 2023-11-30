.. _bodyobjects:

************
Body Objects
************

.. currentmodule:: c4dynamics 

C4dynamics provides two basic entities for developing and analyzing algorithms of objects in space and time:

datapoint: a class defining a point in space: position, velocity, acceleration, and mass.
rigidbody: a class defining a rigid body in space, i.e. an object with length and angular position.

The rigidbody class extends the functionality of the datapoint class. 
It introduces additional attributes related to rotational dynamics, such as angular position, angular velocity, and moment of inertia. 
The class leverages the capabilities of the datapoint class for handling translational dynamics and extends it to include rotational aspects.


.. .. figure:: figures/threefundamental.png

..    **Figure**
..    Conceptual diagram showing the relationship between the three
..    fundamental objects used to describe the data in an array: 1) the
..    ndarray itself, 2) the data-type object that describes the layout
..    of a single fixed-size element of the array, 3) the array-scalar
..    Python object that is returned when a single element of the array
..    is accessed.



.. toctree::
   :maxdepth: 2

   bodyobjects.datapoint
   bodyobjects.rigidbody
