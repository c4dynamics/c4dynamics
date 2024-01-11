.. currentmodule:: c4dynamics 

.. _bodyobjects.rigidbody:

**********************************
the Rigidbody (:class:`rigidbody`)
**********************************

The :class:`rigidbody` extends the :class:`datapoint`
to form an elementary rigidbody object in space.  

The rigidbody is a class defining a rigid body in space, i.e. 
an object with length and attitude.

The rigidbody introduces attributes related to rotational dynamics, 
such as angular position, angular velocity, and moment of inertia. 

The class leverages the capabilities of the datapoint class for handling
translational dynamics and extends it to include rotational aspects.


Notes
=====
The following parameters and attributes extend
the super class, the datapoint. 



Parameters 
==========

.. autosummary:: 
  :toctree: generated/

  rigidbody.phi
  rigidbody.theta
  rigidbody.psi
  rigidbody.p
  rigidbody.q
  rigidbody.r
  rigidbody.p_dot
  rigidbody.q_dot
  rigidbody.r_dot
  rigidbody.ixx
  rigidbody.iyy
  rigidbody.izz
  rigidbody.xcm



Attributes
==========

.. autosummary:: 
  :toctree: generated/

  rigidbody.angles
  rigidbody.ang_rates
  rigidbody.IB 
  rigidbody.BI 



  




