.. currentmodule:: c4dynamics.sensors.seeker 

.. _sensors.seeker:

************************
Seeker (:class:`seeker`)
************************

:class:`seeker` is a general purpose seeker.


The seeker models an electro-optical or electro-magnetical sensor
that returns precise range measure and azimuth-elevation 
angles with the following errors model: scale factor, bias, noise.


Functionality 
=============

At each sample the seeker returns measures based on the true geometry 
with the target.

Let: 

.. math::

  dx = seeker.x - target.x

  dy = seeekr.y - target.y

  dz = seeker.z - target.z

Range: the range measure is a precise geometric distance between the 
seeker and the target:

.. math:: 

  range = 
  \sqrt{dx^2 + dy^2 + dz^2}


Angles: the azimuth and elevation measures are the spatial angles (see the Angles Convention section)

.. math:: 

  az = tan^{-1}{dy \over dx}

  el = tan^{-1}{dz \over \sqrt{dx^2 + dy^2}}


Angles Convention
=================

.. figure:: /_static/figures/seeker.svg
  
  Fig-1: Azimuth and elevation angles definition   



Errors Model
============

The azimuth and elevation angles are subject to errors: scale factor, bias, and noise.

- Bias: represents a constant offset or deviation from the true value in the seeker's measurements. 
  It is a systematic error that consistently affects the measured values. 
  The bias of :class:`seeker` is a normally distributed variable with `mean = 0` 
  and `std = :attr:`bias_std <seeker.bias_std>`

- Scale Factor: a multiplier applied to the true value of a measurement. 
  It represents a scaling error in the measurements made by the seeker. 
  The scale factor of :class:`seeker` is a normally distributed variable 
  with `mean = 0` and `std = :attr:`scale_factor_std <seeker.scale_factor_std>`
- Noise: represents random variations or fluctuations in the measurements 
  that are not systematic. It introduces randomness into the measurements. 
  The noise of :class:`seeker` is represented by :attr:`noise_std <seeker.noise_std>` 
  and is added at each measure by multiplication with a `randn()` function. 


Parameters 
==========

.. autosummary:: 
  :toctree: generated/

  seeker.bias_std
  seeker.scale_factor_std
  seeker.noise_std



Attributes
==========

.. autosummary:: 
  :toctree: generated/

  seeker.bias 
  seeker.scale_factor
  seeker.measure



Examples 
========


Target
------

Generate target trajectory for the following examples  

.. code::

  >>> tgt = c4d.datapoint(x = 1000, y = 0, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
  >>> for t in np.arange(0, 60, 0.01):
  ...   tgt.inteqm(np.zeros(3), .01)
  ...   tgt.store(t)

.. figure:: /_static/figures/seeker_target.png

Measure the target position with an *ideal* seeker. 
The seeker origin is a pedestal with position and attitude. 


Ideal Seeker
------------

.. code::

  >>> pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
  >>> skr = c4d.sensors.seeker(origin = pedestal, isideal = True)
  >>> truth_angles = []
  >>> for x in tgt.get_data():
  ...   truth_angles.append(skr.measure(c4d.create(x[1:]))[:2])

.. figure:: /_static/figures/ideal_seeker.png


Non-ideal Seeker 
----------------

Measure the target position with a *non-ideal* seeker. 

.. code::

  >>> skr = c4d.sensors.seeker(origin = pedestal)
  >>> measured_angles = []
  >>> for x in tgt.get_data():
  ...   measured_angles.append(skr.measure(c4d.create(x[1:]))[:2])

.. figure:: /_static/figures/nonideal_seeker.png


Get the bias, scale factor, and noise that used to generate these measures:

.. code::

  >>> print(f'{ skr.bias * c4d.r2d :.2f}')
  0.02
  >>> print(f'{ skr.scale_factor :.2f}')
  0.99
  >>> print(f'{ skr.noise_std :.2f}')
  0.01


Moving Seeker
-------------

Measure the target position with a rotating non-ideal seeker. 
The seeker origin is yawing in the direction of the target motion. 

.. code::
  
  >>> skr = c4d.sensors.seeker(origin = pedestal)
  >>> measured_angles_2 = []
  >>> for x in tgt.get_data():
  ...   skr.psi += .01 * c4d.d2r 
  ...   measured_angles_2.append(skr.measure(c4d.create(x[1:]), store = True, t = x[0])[:2])
  ...   skr.store(x[0])


.. figure:: /_static/figures/yawing_seeker.png


