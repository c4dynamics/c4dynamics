"""

This page is an `introduction` to the filters module. 
For the different filter objects themselves, go to :ref:`filters-header`.     



The :mod:`filters <c4dynamics.filters>` module in `c4dynamics` provides a collection of 
classes and functions for implementing various types of filters commonly used in control 
systems and state estimation. 



*******************
Background Material
*******************

The background material and the sections concerning the particular filters 
are based on sources in references [AG]_ [SD]_ [ZP]_.  

System Model
============

State-space representation is a mathematical model of a physical system represented 
as a set of input, output, and state variables related by first-order differential 
(or difference) equations. 

The state vector :math:`X` of a state-space model provides a snapshot of the system's current condition, 
encapsulating all the variables necessary to describe its future behavior given the input.
(In `c4dynamics` the state vector is a fundamental data structure, 
represented by the class :class:`state <c4dynamics.states.state.state>`) 
and a snapshot of its values is provided by 
the property :attr:`state.X <c4dynamics.states.state.state.X>`). 

When the coefficients of the state variables in the equations are constant, the 
state model represents a linear system (LTI, linear time invariant). 
If the coefficients are 
linear functions of time, the system is considered linear time varying.  
Otherwise, the system is nonlinear. 


Nonlinear Systems
=================

All systems are naturally nonlinear. When an equilibrium point 
representing the major operation part of the system can be found, then a 
linearization is performed about this point, and the system is regarded 
linear. 
When such a point cannot be easily found, more advanced approaches 
have to be considered to analyze and manipulate the system. Such 
an approach is the extended Kalman filter. 

A nonlinear system is described by:

.. math::
  :label: nonlinearmodel

  \\dot{x}(t) = f(x, u) + \\omega 

  y(t) = h(x) + \\nu 

  x(0) = x_0 



Where: 

- :math:`f(\\cdot)` is an arbitrary vector-valued function representing the system process
- :math:`x` is the system state vector 
- :math:`t` is a time variable 
- :math:`u` is the system input signal
- :math:`\\omega` is the process uncertainty with covariance matrix :math:`Q_c`
- :math:`y` is the system output vector (the measure)
- :math:`h(\\cdot)` is an arbitrary vector-valued function representing the measurement equations 
- :math:`\\nu` is the measure noise with covariance matrix :math:`R_c`
- :math:`x_0` is a vector of initial conditions  

The noise processes :math:`\\omega(t)` and :math:`\\nu(t)` are white, zero-mean, uncorrelated, 
and have known covariance matrices :math:`Q_c` and :math:`R_c`, respectively:

.. math::

  \\omega(t) \\sim (0, Q_c) 

  \\nu(t) \\sim (0, R_c) 

  E[\\omega(t) \\cdot \\omega^T(t)] = Q_c \\cdot \\delta(t) 

  E[\\nu(t) \\cdot \\nu^T(t)] = R_c \\cdot \\delta(t) 

  E[\\nu(t) \\cdot \\omega^T(t)] = 0 
    


Where:

- :math:`\\omega` is the process uncertainty with covariance matrix :math:`Q_c`
- :math:`\\nu` is the measure noise with covariance matrix :math:`R_c`
- :math:`Q_c` is the process covariance matrix 
- :math:`R_c` is the measurement covariance matrix 
- :math:`\\sim` is the distribution operator. :math:`\\sim (\\mu, \\sigma)` means a normal distribution with mean :math:`\\mu` and standard deviation :math:`\\sigma`
- :math:`E(\\cdot)` is the expectation operator 
- :math:`\\delta(\\cdot)` is the Dirac delta function (:math:`\\delta(t) = \\infty` if :math:`t = 0`, and :math:`\\delta(t) = 0` if :math:`t \\neq 0`)
- superscript T is the transpose operator



Linearization 
=============

A linear Kalman filter has a significant advantage in terms of simplicity and 
computing resources, but much more importantly, the `System Covariance`_ 
in a linear Kalman provides exact predictions of the errors in the state estimates. 
The extended Kalman filter offers no such guarantees.  
Therefore it is always a good practice to start by 
an attempt to linearize the system. 

The linearized model of system :eq:`nonlinearmodel` around a nominal trajectory :math:`x_n` is given by [MZ]_:


.. math::
  :label: linearizedmodel

  \\dot{x} = \\Delta{x} \\cdot {\\partial{f} \\over \\partial{x}}\\bigg|_{x_n, u_n}
                + \\Delta{u} \\cdot {\\partial{f} \\over \\partial{u}}\\bigg|_{x_n, u_n} + \\omega
                  
  y = \\Delta{x} \\cdot {\\partial{h} \\over \\partial{x}}\\bigg|_{x_n} + \\nu
                
  \\\\ 

  x(0) = x_0 
  

Where: 

- :math:`\\Delta{x}` is the linear approximation of a small deviation of the state :math:`x` from the nominal trajectory 
- :math:`\\Delta{u}` is the linear approximation of a small deviation of the input control :math:`u` from the nominal trajectory 
- :math:`\\omega` is the process uncertainty  
- :math:`\\Delta{\\nu}` is the linear approximation of a small deviation of the noise :math:`\\nu` from the nominal trajectory 
- :math:`{\\partial{f} \\over \\partial{i}}\\bigg|_{x_n, u_n}` is the partial derivative of :math:`f` with respect to :math:`i (i = x` or :math:`u)` substituted by the nominal point :math:`{x_n, u_n}`
- :math:`{\\partial{h} \\over \\partial{x}}\\bigg|_{x_n}` is the partial derivative of :math:`h` with respect to :math:`x`, substituted by the nominal point :math:`{x_n}`
- :math:`y` is the system output vector (the measure)
- :math:`x_0` is a vector of initial conditions  



Let's denote:

.. math::
  
  A = {\\partial{f} \\over \\partial{x}}\\bigg|_{x_n, u_n, \\omega_n} 

  B = {\\partial{f} \\over \\partial{u}}\\bigg|_{x_n, u_n, \\omega_n} 
  
  C = {\\partial{h} \\over \\partial{x}}\\bigg|_{x_n, \\nu_n} 
  
  

Finally the linear model of system :eq:`nonlinearmodel` is: 

.. math:: 
  :label: linearmodel

  \\dot{x} = A \\cdot x + B \\cdot u + \\omega 

  y = C \\cdot x + \\nu

  x(0) = x_0 

Where: 

- :math:`A` is the process dynamics matrix 
- :math:`x` is the system state vector  
- :math:`b` is the process input matrix
- :math:`u` is the system input signal
- :math:`\\omega` is the process uncertainty with covariance matrix :math:`Q_c`
- :math:`y` is the system output vector (the measure)
- :math:`C` is the output matrix
- :math:`\\nu` is the measure noise with covariance matrix :math:`R_c`
- :math:`x_0` is a vector of initial conditions  
- :math:`Q_c` is the process covariance matrix 
- :math:`R_c` is the measurement covariance matrix 


Sampled Systems
===============

The nonlinear system :eq:`nonlinearmodel` and its linearized form :eq:`linearmodel` 
are given in the continuous-time domain, which is the progressive manifestation of any physical system. 
However, the output of a system is usually sampled by digital devices in discrete time instances.

Hence, in sampled-data systems the dynamics is described by a continuous-time differential equation, 
but the output only changes at discrete time instants.

Nonetheless, for numerical considerations the Kalman filter equations are usually given in the discrete-time domain
not only at the stage of measure updates (`update` or `correct`) but also at the stage of the dynamics propagation (`predict`). 

The discrete-time form of system :eq:`linearmodel` is given by:

.. math:: 
  :label: discretemodel

  x_k = F \\cdot x_{k-1} + G \\cdot u_{k-1} + \\omega_{k-1} 

  y_k = H \\cdot x_k + \\nu_k

  x_{k=0} = x_0 

Where: 

- :math:`x_k` is the discretized system state vector  
- :math:`F` is the discretized process dynamics matrix (actually a first order approximation of the state transition matrix :math:`\\Phi`)
- :math:`G` is the discretized process input matrix
- :math:`u` is the discretized process input signal
- :math:`\\omega_k` is the process uncertainty with covariance matrix :math:`Q`
- :math:`y_k` is the discretized system output vector (the measurement)
- :math:`H` is the discrete measurement matrix 
- :math:`\\nu_k` is the measure noise with covariance matrix :math:`R`
- :math:`x_0` is a vector of initial conditions  

  
The noise processes :math:`\\omega_{k}` and :math:`\\nu_k` are white, zero-mean, uncorrelated, 
and have known covariance matrices :math:`Q` and :math:`R`, respectively:

.. math::

  \\omega_k \\sim (0, Q) 

  \\nu_k \\sim (0, R) 

  E[\\omega_k \\cdot \\omega^T_j] = Q \\cdot \\delta_{k-j} 
  
  E[\\nu_k \\cdot \\nu^T_j] = R \\cdot \\delta_{k-j} 

  E[\\nu_k \\cdot \\omega^T_j] = 0

  
  
The discretization of a system is based on the state-transition matrix :math:`\\Phi(t)`. 
For a matrix :math:`A` the state transition matrix :math:`\\Phi(t)` is given by the matrix exponential :math:`\\Phi = e^{A \\cdot t}` 
which can be expanded as a power series. 

An approximate representation of a continuous-time 
system by a series expansion up to the first-order is given by: 

.. math::

  F = I + A \\cdot dt 

  G = B \\cdot dt 

  Q = Q_c \\cdot dt 

  R = R_c / dt


Where: 

- :math:`x_k` is the discretized system state vector  
- :math:`F` is the discretized process dynamics matrix (actually a first order approximation of the state transition matrix :math:`\\Phi`)
- :math:`G` is the discretized process input matrix
- :math:`u` is the discretized process input signal
- :math:`\\omega_k` is the process uncertainty with covariance matrix :math:`Q`
- :math:`y_k` is the discretized system output vector (the measurement)
- :math:`H` is the discrete measurement matrix 
- :math:`\\nu_k` is the measure noise with covariance matrix :math:`R`
- :math:`x_0` is a vector of initial conditions  
- :math:`I` is the identity matrix
- :math:`dt` is the sampling time 
- :math:`\\sim` is the distribution operator. :math:`\\sim (\\mu, \\sigma)` means a normal distribution with mean :math:`\\mu` and standard deviation :math:`\\sigma`
- :math:`E(\\cdot)` is the expectation operator 
- :math:`\\delta(\\cdot)` is the Kronecker delta function (:math:`\\delta(k-j) = 1` if :math:`k = j`, and :math:`\\delta_{k-j} = 0` if :math:`k \\neq j`)
- superscript T is the transpose operator
- :math:`Q` is the process covariance matrix 
- :math:`R` is the measurement covariance matrix 
- :math:`A, B, Q_c, R_c` are the continuous-time system variables of the system state matrix, system input vector, process covariance matrix, and measurement covariance matrix, respectively




Note that the covariance matrices may have been converted from 
the continuous-time system to discrete-time. 
However, in most cases, these parameters are determined through experimentation 
with the system in its final form.

Additionally, measurements are sampled by digital devices at discrete time steps, 
and the noise properties are typically provided in that form. 
However, if the process noise applies to a kinematic system where the noise properties 
are specified in continuous terms, the above approximation can be used or 
the more exact expression for continuous white noise model 
:math:`Q = \\int_{0}^{dt} F \\cdot Qc \\cdot F^T \\, dt`







System Covariance
=================

Before getting into the Kalman filter itself, it is necessary to consider one more concept, 
that is the system covariance.

Usually denoted by :math:`P`, this variable represents the current uncertainty of the estimate. 

:math:`P` is a matrix that quantifies the estimated accuracy of the state variables, 
with its diagonal elements indicating the variance of each state variable, 
and the off-diagonal elements representing the covariances between different state variables. 

:math:`P` is iteratively refined through the `predict` and the `update` steps. Its 
initial state, :math:`P_0`, 
is chosen based on prior knowledge to reflect the confidence in the initial state estimate (:math:`x_0`).  





******************************************************************
Kalman Filter (:class:`kalman <c4dynamics.filters.kalman.kalman>`)
******************************************************************

A simple way to design a Kalman filter is to separate between two steps: `predict` and `update` (sometimes called `correct`).
The `predict` step is used to project the estimate forward in time. 
The `update` corrects the prediction by using a new measure.  

Predict
=======

In the prediction step the current estimate is projected forward in time to 
obtain a predicted estimate using the system model.

The current state estimate, :math:`x`, is projected into the future using the known system dynamics :eq:`discretemodel`. 
The uncertainty associated with the predicted state, :math:`P`, is calculated by projecting the 
current error covariance forward in time. 

Since the `predict` equations are calculated before a measure is taken (a priori), the new state :math:`x` and the new covariance :math:`P` 
are notated by :math:`(-)` superscript. 

.. math:: 

  x_k^- = F \\cdot x_{k-1}^+ + G \\cdot u_{k-1} 

  P_k^- = F \\cdot P_{k-1}^+ \\cdot F^T + Q

  x_0^+ = x_0

  P_0^+ = E[x_0 \\cdot x_0^T] 

Where:

- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, before a measurement update. 
- :math:`F` is the discretized process dynamics matrix 
- :math:`G` is the discretized process input matrix 
- :math:`u_k` is the process input signal
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, before a measurement update
- :math:`P_{k-1}^+` is the system covariance matrix estimate, :math:`P_k`, from previous measurement update 
- :math:`Q` is the process covariance matrix 
- :math:`R` is the measurement covariance matrix 
- superscript T is the transpose operator
- :math:`x_0` is the initial state estimation
- :math:`P_0` is the covariance matrix consisting of errors of the initial estimation 


Update 
======

In the update step (also called `correct`), the estimate is corrected by using a new measure. 

The Kalman gain, :math:`K`, is computed based on the predicted error covariance and the measurement noise. 
It determines the optimal weighting between the predicted state and the new measurement.

The predicted state estimate is adjusted using the new measurement, weighted by the Kalman Gain.
This update incorporates the latest measurement to refine the state estimate.
Then the error covariance is updated to reflect the reduced uncertainty after incorporating the new measurement. 


The `update` equations are calculated after a measure is taken (a posteriori), and the new state :math:`x` and the new covariance :math:`P` 
are notated by :math:`(+)` superscript. 

.. math:: 

  K = P_k^- \\cdot H^T \\cdot (H \\cdot P_k^- \\cdot H^T + R)^{-1}

  x_k^+ = x_k^- + K \\cdot (y - H \\cdot x_k^-)

  P_k^+ = (I - K \\cdot H) \\cdot P_k^-

Where:

- :math:`K` is the Kalman gain
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, from the previous prediction
- :math:`H` is the discrete measurement matrix 
- :math:`R` is the measurement covariance matrix 
- :math:`x_k^+` is the estimate of the system state, :math:`x_k`, after a measurement update
- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, from the previous prediction
- :math:`y` is the measure 
- :math:`I` is the identity matrix 
- :math:`P_k^+` is the estimate of the system covariance matrix, :math:`P_k`, after a measurement update
- superscript T is the transpose operator


.. _kalman_implementation:

Implementation (C4dynamics)
===========================

:class:`kalman <c4dynamics.filters.kalman.kalman>`
is a discrete linear Kalman filter model. 

Following the concept of separating `predict` 
and `update`, running a Kalman filter is done 
by constructing a Kalman filter with parameters as a 
:class:`state <c4dynamics.states.state.state>` object 
and calling the 
:meth:`predict <c4dynamics.filters.kalman.kalman.predict>` 
and :meth:`update <c4dynamics.filters.kalman.kalman.update>` methods.

The Kalman filter in `c4dynamics` is a class.  
Thus, the user constructs an object that holds the 
attributes required to build the estimates. 
This is crucial to understand because when the user 
calls the `predict` or `update`, 
the object uses parameters and values from previous calls. 


Every filter class in `c4dynamics` is a 
subclass of the state class. 
This means that the filter itself 
encapsulates the estimated state vector:

.. code:: 

  >>> from c4dynamics.filters import kalman 
  >>> import numpy as np       
  >>> z = np.zeros((2, 2)) 
  >>> kf = kalman(X = {'x1': 0, 'x2': 0}, P0 = z, F = z, H = z, Q = z, R = z)
  >>> print(kf)
  [ x1  x2 ]

`z` is an arbitrary matrix used 
to initialize a filter of 
two variables (:math:`x_1, x_2`).


It also means that a filter object 
inherits all the mathematical attributes 
(norm, multiplication, etc.) 
and data attributes (storage, plotting, etc.) 
of a state object 
(for further details, see :mod:`states <c4dynamics.states>`, 
:class:`state <c4dynamics.states.state.state>`, 
and refer to the examples below)
    

Example
-------

An altimeter is measuring the altitude of an aircraft.
The flight path angle of the aircraft, :math:`\\gamma` is controlled 
by a stick which deflects the
elevator that in its turn changes the aircaft altitude :math:`z`:

.. math::

  \\dot{z}(t) = 5 \\cdot \\gamma(t) + \\omega_z(t)

  \\dot{\\gamma}(t) = -0.5 \\cdot \\gamma(t) + 0.1 \\cdot (H_f - u(t)) + \\omega_{\\gamma}(t)

  y(t) = z(t) + \\nu(t)

  
Where:

- :math:`z` is the deviation of the aircraft from the required altitude
- :math:`\\gamma` is the flight path angle
- :math:`H_f` is a constant altitude input required by the pilot 
- :math:`\\omega_z` is the uncertainty in the altitude behavior  
- :math:`\\omega_{\\gamma}` is the uncertainty in the flight path angle behavior 
- :math:`u` is the deflection command 
- :math:`y` is the output measure of `z`
- :math:`\\nu` is the measure noise   

The process uncertainties are given by: :math:`\\omega_z \\sim (0, 0.5)[ft], 
\\omega_{\\gamma} \\sim (0, 0.1)[deg]`.

Let :math:`H_f`, the required altitude by the pilot to be :math:`H_f = 1kft`. 
The initial conditions are: :math:`z_0 = 1010ft` (error of :math:`10ft`), and :math:`\\gamma_0 = 0`. 

The altimeter is sampling in a rate of :math:`50Hz (dt = 20msec)` 
with measure noise of :math:`\\nu \\sim (0, 0.5)[ft]`.



A Kalman filter shall reduce the noise and estimate the state variables. 
But at first it must be verified that the system is observable, otherwise the filter cannot 
fully estimate the state variables based on the output measurements. 


**Setup** 


Import required packages: 

.. code::

  >>> from c4dynamics.filters import kalman 
  >>> from matplotlib import pyplot as plt 
  >>> from scipy.integrate import odeint 
  >>> import c4dynamics as c4d  
  >>> import numpy as np 


Define system matrices:

.. code:: 

  >>> A = np.array([[0, 5], [0, -0.5]])
  >>> B = np.array([0, 0.1])
  >>> C = np.array([1, 0])

Observability test: 

.. code:: 

  >>> n = A.shape[0]
  >>> obsv = C
  >>> for i in range(1, n):
  ...   obsv = np.vstack((obsv, C @ np.linalg.matrix_power(A, i)))
  >>> rank = np.linalg.matrix_rank(obsv)
  >>> print(f'The system is observable (rank = n = {n}).' if rank == n else 'The system is not observable (rank = {rank), n = {n}).')
  The system is observable (rank = n = 2).

  
Some constants and initialization of the scene: 

.. code:: 
  
  >>> dt, tf = 0.01, 50
  >>> tspan = np.arange(0, tf + dt, dt)  
  >>> Hf = 1000
  >>> # reference target 
  >>> tgt = c4d.state(z = 1010, gamma = 0)


The dynamics is defined by an ODE function to be solved using scipy's ode integration:

.. code:: 

  >>> def autopilot(y, t, u = 0, w = np.zeros(2)):
  ...   return A @ y + B * u + w


**Ideal system** 
  
Let's start with a simulation of an ideal system. 
The process has no uncertainties and the radar is clean of measurement errors (`isideal` flag on):  

.. code:: 

  >>> process_noise = np.zeros((2, 2))
  >>> altmtr = c4d.sensors.radar(isideal = True, dt = 2 * dt)

Main loop: 

.. code:: 

  >>> for t in tspan:
  ...   tgt.store(t)
  ...   _, _, Z = altmtr.measure(tgt, t = t, store = True)
  ...   if Z is not None:  
  ...     tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - Z, process_noise @ np.random.randn(2)))[-1]

  
The loop advances the target variables according to the `autopilot` (accurate) dynamics 
and the (ideal) measures of the radar. 

Plot the time histories of the target altitude (:math:`z`) and flight path angle (:math:`\\gamma`):

.. code:: 

  >>> fig, ax = plt.subplots(1, 2)
  >>> # first axis 
  >>> ax[0].plot(*tgt.data('z'), 'm', label = 'true')                   # doctest: +IGNORE_OUTPUT                 
  >>> ax[0].plot(*altmtr.data('range'), '.c', label = 'altimeter')      # doctest: +IGNORE_OUTPUT   
  >>> c4d.plotdefaults(ax[0], 'Altitude', 't', 'ft')
  >>> ax[0].legend()                                                    # doctest: +IGNORE_OUTPUT   
  >>> # second axis
  >>> ax[1].plot(*tgt.data('gamma', c4d.r2d), 'm')                      # doctest: +IGNORE_OUTPUT   
  >>> c4d.plotdefaults(ax[1], 'Path Angle', 't', '')  

.. figure:: /_examples/filters/ap_ideal.png

The ideal altimeter measures the aircraft altitude precisely. 
Its samples use to control the flight angle that started 
at an altitude of :math:`10ft` above the required 
altitude (:math:`Hf = 1000ft`) and is closed after about :math:`18s`.  


**Noisy system** 

Now, let's introduce the process uncertainty and measurement noise:

.. code:: 

  >>> process_noise = np.diag([0.5, 0.1 * c4d.d2r])
  >>> measure_noise = 1 # ft
  >>> altmtr = c4d.sensors.radar(rng_noise_std = measure_noise, dt = 2 * dt) 

Re-running the main loop yields: 

.. figure:: /_examples/filters/ap_noisy.png

Very bad.
The errors corrupt the input that uses to control the altitude.
The point in which the altitude converges to its steady-state is more 
than :math:`10s` later than the ideal case. 


**Filtered system** 

A Kalman filter should find optimized gains to minimize the mean squared error. 
For the estimated state let's define a new object, :math:`kf`, 
and initialize it with the estimated errors: 


.. code:: 

  >>> z_err = 5 
  >>> gma_err = 1 * c4d.d2r 
  >>> tgt = c4d.state(z = 1010, gamma = 0)
  >>> kf = kalman(X = {'z': tgt.z + z_err, 'gamma': tgt.gamma + gma_err}
  ...                 , P0 = [2 * z_err, 2 * gma_err] 
  ...                     , R = measure_noise**2 / dt, Q = process_noise**2 * dt 
  ...                         , F = np.eye(2) + A * dt, G = B * dt, H = C)
 
  

The main loop is changed to: 

.. code:: 

  >>> for t in tspan:
  ...   tgt.store(t)
  ...   kf.store(t)
  ...   tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - kf.z, process_noise @ np.random.randn(2)))[-1]
  ...   kf.predict(u = Hf - kf.z)
  ...   _, _, Z = altmtr.measure(tgt, t = t, store = True)
  ...   if Z is not None: 
  ...     kf.update(Z) # doctest: +IGNORE_OUTPUT

  

Plot the state estimates on the true the target altitude (:math:`z`) and flight path angle (:math:`\\gamma`):

.. code:: 

  >>> fig, ax = plt.subplots(1, 2)
  >>> # first axis 
  >>> ax[0].plot(*tgt.data('z'), 'm', label = 'true')                   # doctest: +IGNORE_OUTPUT                 
  >>> ax[0].plot(*altmtr.data('range'), '.c', label = 'altimeter')      # doctest: +IGNORE_OUTPUT   
  >>> ax[0].plot(*kf.data('z'), 'y', label = 'kf')                      # doctest: +IGNORE_OUTPUT
  >>> c4d.plotdefaults(ax[0], 'Altitude', 't', 'ft')
  >>> ax[0].legend()                                                    # doctest: +IGNORE_OUTPUT   
  >>> # second axis
  >>> ax[1].plot(*tgt.data('gamma', c4d.r2d), 'm')                      # doctest: +IGNORE_OUTPUT   
  >>> ax[1].plot(*kf.data('gamma', c4d.r2d), 'y')                       # doctest: +IGNORE_OUTPUT
  >>> c4d.plotdefaults(ax[1], 'Path Angle', 't', '')  

.. figure:: /_examples/filters/ap_filtered.png

The filtered altitude (`kf.z`) is used as input to control the system and 
generates results almost as good as the ideal case. 

Ultimately, the altimeter measuring the aircraft altitude
operates through a two-step process: prediction and update. 
In the prediction step, the filter projects the current state estimate 
forward using the system model. 
In the update step, it corrects this prediction with new measurements. 

As the Kalman filter implemented as a class, 
its usage is by creating an instance and then calling its 
predict and update methods for state estimation. 















******************************************************************
Extended Kalman Filter (:class:`ekf <c4dynamics.filters.ekf.ekf>`)
******************************************************************

A linear Kalman filter 
(:class:`kalman <c4dynamics.filters.kalman.kalman>`) 
should be the first choice 
when designing a state observer. 
However, when a nominal trajectory cannot be found, 
the solution is to linearize the system
at each cycle about the current estimated state. 

Similarly to the linear Kalman filter, 
a good approach to design an extended Kalman filter 
is to separate it to two steps: `predict` and `update` (`correct`).

Since the iterative solution to the algebraic Riccati equation 
(uses to calculate the optimal covariance matrix :math:`P`) involves 
the matrix representation of the system parameters, the nonlinear equations
of the process and / or the measurement must be linearized 
before executing each stage of the `ekf`. 

Nevertheless, the calculation of the state vector :math:`x` 
both in the predict step (projection in time using the process equations) 
and in the update step (correction using the measure equations) 
does not have to use the approximated linear expressions (:math:`F, H`)
and can use the exact nonlinear equations (:math:`f, h`). 


Recall the mathematical model of a nonlinear system as given in :eq:`nonlinearmodel`:


.. math::

  \\dot{x} = f(x, u, \\omega) 

  y = h(x, \\nu) 

  x(0) = x_0 


Where: 

- :math:`f(\\cdot)` is an arbitrary vector-valued function representing the system dynamics
- :math:`x` is the system state vector 
- :math:`u` is the process input signal
- :math:`\\omega` is the process uncertainty with covariance matrix :math:`Q`
- :math:`y` is the system output vector 
- :math:`h(\\cdot)` is an arbitrary vector-valued function representing the system output
- :math:`\\nu` is the measure noise with covariance matrix :math:`R`
- :math:`x_0` is a vector of initial conditions  

The noise processes :math:`\\omega(t)` and :math:`\\nu(t)` are white, zero-mean, uncorrelated, 
and have known covariance matrices :math:`Q` and :math:`R`, respectively:

.. math::

  \\omega(t) \\sim (0, Q) 

  \\nu(t) \\sim (0, R) 

  E[\\omega(t) \\cdot \\omega^T(t)] = Q \\cdot \\delta(t) 

  E[\\nu(t) \\cdot \\nu^T(t)] = R \\cdot \\delta(t) 

  E[\\nu(t) \\cdot \\omega^T(t)] = 0 
    

Where:

- :math:`\\omega` is the process uncertainty with covariance matrix :math:`Q`
- :math:`\\nu` is the measure noise with covariance matrix :math:`R`
- :math:`Q` is the process covariance matrix 
- :math:`R` is the measurement covariance matrix 
- :math:`\\sim` is the distribution operator. :math:`\\sim (\\mu, \\sigma)` means a normal distribution with mean :math:`\\mu` and standard deviation :math:`\\sigma`
- :math:`E(\\cdot)` is the expectation operator 
- :math:`\\delta(\\cdot)` is the Dirac delta function (:math:`\\delta(t) = \\infty` if :math:`t = 0`, and :math:`\\delta(t) = 0` if :math:`t \\neq 0`)
- superscript T is the transpose operator


The linearized term for :math:`f` is given by its Jacobian with 
respect to :math:`x`: 

.. math::

  A = {\\partial{f} \\over \\partial{x}}\\bigg|_{x, u} 
  

Note however that the derivatives are taken at the last estimate  
(as opposed to a nominal trajectory that is used in a global linearization). 

The linearized term for :math:`h` is given by its Jacobian with 
respect to :math:`x`: 

.. math:: 

  C = {\\partial{h} \\over \\partial{x}}\\bigg|_{x} 
 

A last final step before getting into the filter itself 
is to discretize these terms: 


.. math::

  F = I + A \\cdot dt 

  H = C  


Where:

- :math:`F` is the discretized process dynamics matrix (actually a first order approximation of the state transition matrix :math:`\\Phi`)
- :math:`H` is the discrete measurement matrix 
- :math:`I` is the identity matrix
- :math:`dt` is the sampling time 
- :math:`A, C` are the continuous-time system dynamics and output matrices


Note that :math:`Q` and :math:`R` refer to the covariance matrices 
representing the system noise in its final form, regardless of the time domain.  


Now the execution of the `predict` step and the `update` step is possible. 


Predict
=======

As mentioned earlier, the advancement of the state vector 
is possible by using the exact equations. The second in 
the following equations is an Euler integration to the
nonlinear equations. 

The progression of the covariance matrix must use 
the linear terms that were derived earlier. 
The first equation in the following
set is the linearization of the process 
equations for the covariance calculation (third):


.. math:: 

  F = I + dt \\cdot {\\partial{f} \\over \\partial{x}}\\bigg|_{x_{k-1}^+, u{k-1}}

  x_k^- = x_{k-1}^+ + dt \\cdot f(x_{k-1}^+, u_{k-1})

  P_k^- = F \\cdot P_{k-1}^+ \\cdot F^T + Q

subject to initial conditions: 

.. math:: 
  
  x_0^+ = x_0

  P_0^+ = E[x_0 \\cdot x_0^T] 


Where: 

- :math:`F` is the discretized process dynamics matrix 
- :math:`I` is the identity matrix
- :math:`f(\\cdot)` is a vector-valued function representing the system dynamics
- :math:`dt` is the sampling time 
- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, before a measurement update. 
- :math:`u_k` is the process input signal
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, before a measurement update
- :math:`P_{k-1}^+` is the system covariance matrix estimate, :math:`P_k`, from previous measurement update 
- :math:`Q` is the process covariance matrix 
- superscript T is the transpose operator
- :math:`x_0` is the initial state estimation
- :math:`P_0` is the covariance matrix consisting of errors of the initial estimation 




Update
======

In a similar manner, the measurement equations :math:`h(x)` are 
linearized (:math:`H`) before the `update` to correct the covariance matrix. 
But the correction of the state vector is possible by using 
the nonlinear equations themselves (third equation): 


.. math:: 

  H = {\\partial{h} \\over \\partial{x}}\\bigg|_{x_k^-} 

  K = P_k^- \\cdot H^T \\cdot (H \\cdot P_k^- \\cdot H^T + R)^{-1}

  x_k^+ = x_k^- \\cdot K \\cdot (y - h(x)) 

  P_k^+ = (I - K \\cdot H) \\cdot P_k^-

Where:

- :math:`H` is the discrete measurement matrix 
- :math:`h(\\cdot)` is a vector-valued function representing the measurement equations 
- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, from the previous prediction
- :math:`K` is the Kalman gain
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, from the previous prediction
- :math:`R` is the measurement covariance matrix 
- :math:`x_k^+` is the estimate of the system state, :math:`x_k`, after a measurement update
- :math:`y` is the measure 
- :math:`I` is the identity matrix 
- :math:`P_k^+` is the estimate of the system covariance matrix, :math:`P_k`, after a measurement update
- superscript T is the transpose operator



Implementation (C4dynamics)
===========================

We saw that in both the 
`predict` and `update` stages, 
the state doesn't have 
to rely on approximated nonlinear equations 
but can instead 
use exact models for the process and the measurement. 
However, it is sometimes more convenient to use 
the existing linear for state advancements. 
C4dyanmics provides an interface for each approach:
the `predict` method 
can either take :math:`f(x)` 
as an input argument or use the necessary matrix :math:`F` 
to project the state in time. 
Similarly, the update method can either 
take :math:`h(x)` as an input argument 
or use the necessary matrix :math:`H`
to correct :math:`x`. 

Recall a few additional properties of  
filter implementation in 
c4dynamics, as described in the 
:ref:`linear kalman <kalman_implementation>` section: 

A. An Extended Kalman filter is a class.
The object holds the 
attributes required to build the estimates, and 
every method call relies on the results of previous calls. 

B. The Extended Kalman filter is a 
subclass of the state class. 
The state variables are part of the filter object itself, 
which inherits all the attributes of a state object.    

C. The filter operations
are divided into separate `predict` and `update` methods. 
:meth:`ekf.predict <c4dynamics.filters.ekf.ekf.predict>` 
projects the state into 
the next time. 
:meth:`ekf.update <c4dynamics.filters.ekf.ekf.update>` 
calculates the optimized gain and 
corrects the state based on the input measurement. 



Example
-------

The following example appears in several sources. 
[ZP]_ provides a great deal of detail. Additional sources can be found in [SD]_. 
The problem is to estimate the ballistic coefficient of a target 
in a free fall where a noisy radar is tracking it.

The process equations are: 

.. math:: 

  \\dot{z} = v_z

  \\dot{v}_z = {\\rho_0 \\cdot e^{-z / k} \\cdot v_z^2 \\cdot g \\over 2 \\cdot \\beta} - g

  \\dot{\\beta} = \\omega_{\\beta} 

  y = z + \\nu_k 


Where:


- :math:`\\rho_0 = 0.0034`
- :math:`k = 22,000` 
- :math:`g = 32.2 ft/sec^2`
- :math:`\\omega_{\\beta} \\sim (0, 300)`
- :math:`\\nu_k \\sim (0, 500)` 
- :math:`z` is the target altitude (:math:`ft`)
- :math:`v_z` is the target vertical velocity (:math:`ft/sec`)
- :math:`\\beta` is the target ballistic coefficient (:math:`lb/ft^2`)
- :math:`y` is the system measure 


Let:

.. math::

  \\rho = \\rho_0 \\cdot e^{-z / k}


The lineariztion of the process matrix for the `predict` step:

.. math::

  F = \\begin{bmatrix}
        0 & 1 & 0 \\\\
          -\\rho \\cdot g \\cdot v_z^2 / (44000 \\cdot \\beta) 
          & \\rho \\cdot g \\cdot v_z / \\beta
          & -\\rho \\cdot g \\cdot v_z^2 \\cdot / (2 \\cdot \\beta^2) \\\\ 
            0 & 0 & 0
      \\end{bmatrix}  

  
The measurement is a direct sample of the altitude of the target
so these equations are already a linear function of the state. 

.. math::

  H = \\begin{bmatrix}
        1 & 0 & 0 
      \\end{bmatrix}  
              

We now have all we need to run the extended Kalman filter. 
      

Quick setup for an ideal case: 

.. code:: 

  >>> dt, tf = .01, 30
  >>> tspan = np.arange(0, tf + dt, dt) 
  >>> dtsensor = 0.05  
  >>> rho0, k = 0.0034, 22000 
  >>> tgt = c4d.state(z = 100000, vz = -6000, beta = 500)
  >>> altmtr = c4d.sensors.radar(isideal = True, dt = dt)

Target equations of motion:

.. code:: 

  >>> def ballistics(y, t):
  ...   return [y[1], rho0 * np.exp(-y[0] / k) * y[1]**2 * c4d.g_fts2 / 2 / y[2] - c4d.g_fts2, 0]

  
Main loop: 

.. code::  

  >>> for t in tspan:
  ...   tgt.store(t)
  ...   tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
  ...   _, _, z = altmtr.measure(tgt, t = t, store = True)

.. figure:: /_examples/filters/bal_ideal.png


These figures show the time histories of the altitude, velocity, 
and ballistic coefficient, for a target in a free fall with ideal conditions. 

Let's examine the `ekf` capability to estimate :math:`\\beta` at the presence of errors. 
Errors in initial conditions introduced into each one of the variables: 
:math:`z_{0_{err}} = 25, v_{z_{0_{err}}} = -150, \\beta_{0_{err}} = 300`. 
The uncertainty in the ballistic coefficient is given in terms of 
the spectral density of a continuous system, such that for flight time :math:`t_f`, 
the standard deviation of the ballistic coefficient noise 
is :math:`\\omega_{\\beta} = \\sqrt{\\beta_{err} \\cdot t_f}`. 
The measurement noise is :math:`\\nu = \\sqrt{500}`. These use 
for the noise covariance matrices :math:`Q, R` as for 
the initialization of the state covariance matrix :math:`P`:   


.. code::

  >>> zerr, vzerr, betaerr = 25, -150, 300 
  >>> nu = np.sqrt(500) 
  >>> p0 = np.diag([nu**2, vzerr**2, betaerr**2])
  >>> R = nu**2 / dt
  >>> Q = np.diag([0, 0, betaerr**2 / tf * dt])  
  >>> H = [1, 0, 0]
  >>> tgt = c4d.state(z = 100000, vz = -6000, beta = 500)
  >>> # altmeter and ekf construction: 
  >>> altmtr = c4d.sensors.radar(rng_noise_std = nu, dt = dtsensor) 
  >>> ekf = c4d.filters.ekf(X = {'z': tgt.z + zerr, 'vz': tgt.vz + vzerr
  ...                                     , 'beta': tgt.beta + betaerr}
  ...                                         , P0 = p0, H = H, Q = Q, R = R) 



The main loop includes the simulation of the target motion, the linearization 
and discretization of the process equations, and calling the `predict` method. 
Then linearization and discretization of the measurement equations (not relevant 
here as the measurement is already linear), and calling the `update` method. 

.. code:: 

  >>> for t in tspan:
  ...   tgt.store(t)
  ...   ekf.store(t)
  ...   # target motion simulation  
  ...   tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
  ...   # process linearization 
  ...   rhoexp  = rho0 * np.exp(-ekf.z / k) * c4d.g_fts2 * ekf.vz / ekf.beta
  ...   fx      = [ekf.vz, rhoexp * ekf.vz / 2 - c4d.g_fts2, 0]
  ...   f2i     = rhoexp * np.array([-ekf.vz / 2 / k, 1, -ekf.vz / 2 / ekf.beta])
  ...   # discretization 
  ...   F = np.array([[0, 1, 0], f2i, [0, 0, 0]]) * dt + np.eye(3)
  ...   # ekf predict 
  ...   ekf.predict(F = F, fx = fx, dt = dt)
  ...   # take a measure 
  ...   _, _, Z = altmtr.measure(tgt, t = t, store = True)
  ...   if Z is not None:  
  ...     ekf.update(Z) # doctest: +IGNORE_OUTPUT


Though the `update` requires also the linear 
process matrix (:math:`F`), the `predict` method 
stores the introduced `F` to prove that 
the `update` step always comes after calling the `predict`. 


.. figure:: /_examples/filters/bal_filtered.png



A few steps to consider when designing a Kalman filter: 

- Spend some time understanding the dynamics. It's the basis of great filtering. 
- If the system is nonlinear, identify the nonlinearity; is it in the process? in the measurement? both? 
- Always prioriorotize linear Kalman. If possible, find a nominal trajectory to linearize the system about.
- The major time-consuming activity is researching the balance between the noise matrices `Q` and `R`.
- -> Plan your time in advance.
- Use a framework that provides you with the most flexibility and control.
- Make fun! 





***************
Low-pass Filter
***************

A first-order low-pass filter is a fundamental component in signal processing 
and control systems, designed to allow low-frequency signals to pass while 
attenuating higher-frequency noise. 

This type of filter is represented by a simple differential equation 
and is commonly used for signal smoothing and noise reduction.



A low-pass filter (LPF) can be described by the differential equation:

.. math:: 

   \\alpha \\cdot \\dot{y} + y = x

Where:

- :math:`y` is the output signal
- :math:`x` is the input signal
- :math:`\\alpha` is a shaping parameter that influences the filter's cutoff frequency

In signal processing, the LPF smooths signals by reducing high-frequency noise. 
In control systems, it is often used to model a first-order lag.


Frequency-Domain
================

In the frequency domain, the transfer function of a first-order low-pass filter is given by:

.. math::

   H(s) = \\frac{Y(s)}{X(s)} = \\frac{1}{\\alpha \\cdot s + 1}

Where:

- :math:`H(s)` is the transfer function
- :math:`Y(s)` and :math:`X(s)` are the Laplace transforms of the output and input signals respectively
- :math:`s` is the complex frequency variable in the Laplace transform, defined as :math:`s = j \\cdot 2 \\cdot \\pi \\cdot f`
- :math:`\\alpha` is a constant related to the cutoff frequency



Time-Constant
=============

The cutoff frequency :math:`f_c` is the frequency at which the filter attenuates the signal to approximately 70.7% (-3dB) of its maximum value. It is related to the time constant :math:`\\tau` by:

.. math::

   f_c = \\frac{1}{2 \\cdot \\pi \\cdot \\tau}

and equivalently,

.. math::

   \\tau = \\frac{1}{2 \\cdot \\pi \\cdot f_c}

In practical applications, the desired cutoff frequency determines :math:`\\tau`, which in turn defines the filter behavior.


Discrete-Time
=============

In the discrete-time domain, a first-order low-pass filter is represented as:

.. math::

   y_k = \\alpha \\cdot x_k + (1 - \\alpha) \\cdot y_{k-1}

where :math:`y_k` and :math:`x_k` are the discrete output and input signals at sample index `k`, and :math:`\\alpha` is the filter coefficient derived from the sample rate and cutoff frequency.


Implementation (C4dynamics)
===========================

This filter class can be initialized with a 
cutoff frequency and sample rate, allowing users to simulate 
first-order systems.


References
==========


.. [SD] Simon, Dan, 
   'Optimal State Estimation: Kalman, H Infinity, and Nonlinear Approaches', 
   Hoboken: Wiley, 2006.

   
.. [AG] Agranovich, Grigory, 
   Lecture Notes on Modern and Digital Control Systems, 
   University of Ariel, 2012-2013.

   
.. [ZP] Zarchan, Paul, 
   'Tactical and Strategic Missile Guidance', 
   American Institute of Aeronautics and Astronautics, 1990. 

   
.. [MZ] Meri, Ziv, 
   `Extended Lyapunov Analysis and Simulative Investigations in Stability of Proportional Navigation Guidance Systems 
   <../_static/PN_Stability.pdf>`_,
   MSc. Thesis supervised by prof. Grigory Agranovich, University of Ariel, 2020.

"""


# NOTE 
# the line: 
# "Note that the divider of R is :math:`dt_{measure}` rather than simply :math:`dt` 
#   because often times the sampling-time of the measures is different than 
#   the sampling-time that uses to integrate the dynamics. 
#   However, when the measure times and the integration times are equal,
#   then :math:`dt_{measure} = dt`." 
# required clarification. i think i took it from simon. not sure. 
# anyway it's weird. as for a continuous system with Q = R 
# it's gone have balanced weights. 
# however the translation of it to discrete matrices with Q = Q*dt, R = R/dt 
# violates the balance.  
# I think it's realy wrong. in pg 232 (247) he says explicitly: 
# now let us think about measurement noise. suppose we have a discrete-time 
# measurement of a constant x every T seconds. The measurement times are tk = k*T (k=1,2,..).
# .. 
# the error covariance at time tk is independent of the sample time T if: R = Rc/T. 
# where Rc is some constant. 
# this implis that 
#     lim(R, T->0) = Rc * delta(t)
# where delta(t) is the constinuous time impulse function.
# this estabilshes the equivalence between white meausrement noise 
# in discrete time and continuous time. the effects of white measuremnt noise in discrete time
# and continuous time are the same if:
# vk ~ (0, R)
# v(t) ~ (0, Rc)
# i  think i should simply say that c4d kamlans are discrete kalmans.
# only that the user can provdie also cont. matrices. 
# and now that i think about that its become more clear to me 
# that what i should do is only suggest discrete filter and also 
# provide util for covnerting cont to discr system and then the user 
# provides the disc systems.  
# i rather think that best thing is to separate the covariance matrices from 
# discretization and just present it as given for the final system.
# or to add a remark and say that if also the covarinace matrices are given for 
# cont system then this the way to discretize it. 
# or add a note that in practice the noise of the discrete system should be know ampricialy or by data sheet. 
# or to add that in practice the sensors are taking measurements in discrete times. 
# 
# another problem arises: 
# the kalman is implemented as discrete-time system. 
# if the user provides system matrices A,B,C in the continuous-time domain, 
# then i ask also the time-step parameter and convert them to the discrete-time 
# form and then calculate the filter equations. 
# the problem that if the user provide continuous-time matrices, 
# probably he also provide his noise covariances Q and R in the continuous time domain, 
# which means that the noise descriptions do not match the discrete form of my filter. 
# what do u suggest to do?
# gpt: 
# convert q by yourself according to:  
#     Qd = A^-1 * (e^AT - I) * Qc
# R is in anyway sampled in disc times.
# alternatively change the model to discrete inputs only.   
# 
#
# FIXME 
# the example of the kalman filter must be fixed as there's no reason to 
# divide R here by dt becuase it's the vairance of the radar in the given time step!! 
# see figures in w.doc. 
  
'''
Franklin, G.F., Powell,D.J., and Workman, M.L., Digital Control of Dynamic Systems 
ch 9 
9.4.2 the discrete kf:
w(t) and v(t) have no time correlation.
E(w*w^T)=Rw=Q
E(v*v^T)=Rv=R

9.4.4. noise matrices and discerete equivalents.
the process uncertainty acts on the continuous portion of the system.  




i have a cont system sampled with a 
discrete samples camera. let's say the sensor errors with its algo are 
sig_camera in both position and bounding box. 
i want to show an example where i give the camera and the process the 
same weight and i run them in a steady state mode.
the model in const velocity model.  
then i say i want to overcome an error in the linearity and extend the 
uncertainty of the process with still continuous modeling of the process. 
** remark: how at all can kalman designers 
introduce the uncertainty in the noise? after all kalman 
restrains that factor to be a white noise with mean 0 and
im not sure the model uncertainty behaves in that way.
** any way in the next example i want to show 
that same results could be achieved by using discrete matrices.
'''

import sys, os
sys.path.append('.')

from c4dynamics.filters.kalman import kalman
from c4dynamics.filters.ekf import ekf
from c4dynamics.filters.lowpass import lowpass


if __name__ == "__main__":

  # import doctest, contextlib
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
