'''
This page is an `introduction` to the filters module. 
For the different filter objects themselves, go to :ref:`filters-header`.     



The :mod:`c4dynamics:filters` module in the `c4dynamics` framework provides a collection of 
classes and functions for implementing various types of filters commonly used in control 
systems and signal processing. 
This includes Kalman Filters (both linear and extended), Luenberger Filters, and Lowpass Filters.


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
(In `c4dynamics` the state vector is the fundamental data structure, provided 
by the property :attr:`state.X <c4dynamics.states.state.X>`). 

When the coefficients of the state variables in the equations are constant, the 
state model represents a linear system. Otherwise, the system is nonlinear. 


Nonlinear Systems
=================

All systems are naturally nonlinear. When an equilibrium point 
representing the major operation part of the system can be found, then a 
linearization is performed about this point, and the system is regarded 
as linear. 
When such a point cannot be easily found, more advanced approaches 
have to be considered to analyze and manipulate the system. Such 
an approach is the extended Kalman filter. 

A nonlinear system is described by:

.. math::
  :label: nonlinearmodel

  \\dot{x} = f(x, u, \\omega) 

  y = h(x, \\nu) 

  x(0) = x_0 



where: 

- :math:`f(\\cdot)` is an arbitrary vector-valued function representing the system process
- :math:`x` is the system state vector 
- :math:`u` is the system input signal
- :math:`t` is a time variable 
- :math:`\\omega` is the process noise with covariance matrix :math:`Q`
- :math:`y` is the system output vector (the measure)
- :math:`h(\\cdot)` is an arbitrary vector-valued function representing the measurement equations 
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
    


where:

- :math:`\\omega` is the process noise with covariance matrix :math:`Q`
- :math:`\\nu` is the measure noise with covariance matrix :math:`R`
- :math:`Q` is the process covariance matrix 
- :math:`R` is the measurement covariance matrix 
- :math:`\\sim` is the distribution operator. :math:`\\sim (\\mu, \\sigma)` means a normal distribution with mean :math:`\\mu` and standard deviation :math:`\\sigma`
- :math:`E(\\cdot)` is the expectation operator 
- :math:`\\delta(\\cdot)` is the Dirac delta function (:math:`\\delta(t) = \\infty` if :math:`t = 0`, and :math:`\\delta(t) = 0` if :math:`t \\neq 0`)
- superscript T is the transpose operator



Linearization 
=============

A linear Kalman filter has a significant advantage in terms of simplicity and 
computing resources, but much more importantly the `System Covariance`_ 
in a linear Kalman provides exact predictions of the errors in the state estimates. 
The extended Kalman filter offers no such guarantees.  
Therefore it is always a good practice to start by 
an attempt to linearize the system. 

The linearized model of system :eq:`nonlinearmodel` around a nominal trajectory :math:`x_n` is given by [MZ]_:


.. math::
  :label: linearizedmodel

  \\dot{x} = \\Delta{x} \\cdot {\\partial{f} \\over \\partial{x}}\\bigg|_{x_n, u_n, \\omega_n}
                + \\Delta{u} \\cdot {\\partial{f} \\over \\partial{u}}\\bigg|_{x_n, u_n, \\omega_n}
                  + \\Delta{\\omega} \\cdot {\\partial{f} \\over \\partial{\\omega}}\\bigg|_{x_n, u_n, \\omega_n}
                  
  y = \\Delta{x} \\cdot {\\partial{h} \\over \\partial{x}}\\bigg|_{x_n, \\nu_n}
                + \\Delta{\\nu} \\cdot {\\partial{h} \\over \\partial{\\nu}}\\bigg|_{x_n, \\nu_n}

  \\\\ 

  x(0) = x_0 
  
Let's denote:

.. math::
  
  A = {\\partial{f} \\over \\partial{x}}\\bigg|_{x_n, u_n, \\omega_n} 

  B = {\\partial{f} \\over \\partial{u}}\\bigg|_{x_n, u_n, \\omega_n} 
  
  L = {\\partial{f} \\over \\partial{\\omega}}\\bigg|_{x_n, u_n, \\omega_n} 

  C = {\\partial{h} \\over \\partial{x}}\\bigg|_{x_n, \\nu_n} 
  
  M = {\\partial{h} \\over \\partial{\\nu}}\\bigg|_{x_n, \\nu_n} 
  

Practically, the noise is assumed to be an additive disturbance rather 
than a term that propagates through the dynamics in a complex manner. 
Hence it's a common practice to omit the noise coefficients :math:`L, M` 
and to express the discretization properties of the noise directly 
through the covariance matrices :math:`Qk, Rk`. 



Finally the linear model of system :eq:`nonlinearmodel` is: 

.. math:: 
  :label: linearmodel

  \\dot{x} = A \cdot x + B \cdot u + \\omega 

  y = C \cdot x + \\nu

  x(0) = x_0 

where: 

- :math:`A` is the process dynamics matrix 
- :math:`x` is the system state vector  
- :math:`b` is the process input matrix
- :math:`u` is the system input signal
- :math:`\\omega` is the process noise with covariance matrix :math:`Q`
- :math:`y` is the system output vector (the measure)
- :math:`C` is the output matrix
- :math:`\\nu` is the measure noise with covariance matrix :math:`R`
- :math:`x_0` is a vector of initial conditions  
- :math:`Q` is the process covariance matrix 
- :math:`R` is the measurement covariance matrix 


Sampled Systems
===============

The nonlinear system :eq:`nonlinearmodel` and its linearized form :eq:`linearmodel` 
are given in the continuous-time domain, which is the progressive manifestation of any physical system. 
However, the output of systems is sampled by digital devices in discrete time instances.

Hence, In sampled-data systems the dynamics is described by a continuous-time differential equation, 
but the output only changes at discrete time instants.

Nonetheless, for numerical considerations the Kalman filter equations are usually given in the discrete-time domain
not only at the stage of measure updates but also at the stage of the dynamics propagation (`predict`). 

The discrete-time form of system :eq:`linearmodel` is given by:

.. math:: 
  :label: discretemodel

  x_k = F \cdot x_{k-1} + G \cdot u_{k-1} + \\omega_{k-1} 

  y_k = H \cdot x_k + \\nu_k

  x_{k=0} = x_0 

The noise processes :math:`\\omega_{k}` and :math:`\\nu_k` are white, zero-mean, uncorrelated, 
and have known covariance matrices :math:`Q_k` and :math:`R_k`, respectively:

.. math::

  \\omega_k \\sim (0, Q_k) 

  \\nu_k \\sim (0, R_k) 

  E[\\omega_k \\cdot \\omega^T_j] = Q_k \\cdot \\delta_{k-j} 
  
  E[\\nu_k \\cdot \\nu^T_j] = R_k \\cdot \\delta_{k-j} 

  E[\\nu_k \\cdot \\omega^T_j] = 0

The discretization of a system is based on the state-transition matrix :math:`\\Phi(t)`. 
For a matrix :math:`A` the state transition matrix :math:`\\Phi(t)` is given by the matrix exponential :math:`\\Phi = e^{A \\cdot t}` 
which can be expanded as a power series. 

An approximate representation of a continuous-time system by a series expansion up to the first-order is given by: 

.. math::

  F = I + A \\cdot dt 

  G = B \\cdot dt 

  Q_k = Q \\cdot dt 

  R_k = R / dt_{measure}

Note that the divider of R is :math:`dt_{measure}` rather than simply :math:`dt` 
because often times the sampling-time of the measures is different than 
the sampling-time that uses to integrate the dynamics system. 
However when the measure times and the integration times are equal
than :math:`dt_{measure} = dt`. 

where: 

- :math:`x_k` is the discretized system state vector  
- :math:`F` is the discretized process dynamics matrix (actually a first order approximation of the state transition matrix :math:`\\Phi`)
- :math:`G` is the discretized process input matrix
- :math:`u` is the discretized process input signal
- :math:`\\omega_k` is the process noise with covariance matrix :math:`Q_k`
- :math:`y_k` is the discretized system output vector (the measurement)
- :math:`H` is the discrete measurement matrix 
- :math:`\\nu_k` is the measure noise with covariance matrix :math:`R_k`
- :math:`x_0` is a vector of initial conditions  
- :math:`I` is the identity matrix
- :math:`dt` is the sampling time 
- :math:`dt_measure` is the sampling time of the measures 
- :math:`\\sim` is the distribution operator. :math:`\\sim (\\mu, \\sigma)` means a normal distribution with mean :math:`\\mu` and standard deviation :math:`\\sigma`
- :math:`E(\\cdot)` is the expectation operator 
- :math:`\\delta(\\cdot)` is the Kronecker delta function (:math:`\\delta(k-j) = 1` if :math:`k = j`, and :math:`\\delta_{k-j} = 0` if :math:`k \\neq j`)
- superscript T is the transpose operator
- :math:`Q_k` is the process covariance matrix 
- :math:`R_k` is the measurement covariance matrix 
- :math:`A, B, Q, R` are the continuous-time system variables of the system state matrix, system input vector, process covariance matrix, and measurement covariance matrix, respectively



System Covariance
=================

Before getting into the Kalman filter itself, it is necessary to consider one more concept, that is the system covariance.

Usually denoted by :math:`P`, this variable represents the current uncertainty of the estimate. 

:math:`P` is a matrix that quantifies the estimated accuracy of the state variables, 
with its diagonal elements indicating the variance of each state variable, 
and the off-diagonal elements representing the covariances between different state variables. 

:math:`P` is iteratively refined through the `predict` and the `update` steps and its 
initial state, :math:`P_0`, is chosen based on prior knowledge to reflect the confidence in the initial state estimate (:math:`x_0`).  


*******************************
Kalman Filter (:class:`kalman`)
*******************************

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
are notated by :math:`-` superscript. 

.. math:: 

  x_k^- = F \\cdot x_{k-1}^+ + G \\cdot u_{k-1} 

  P_k^- = F \\cdot P_{k-1}^+ \\cdot F^T + Q_k

  x_0^+ = x_0

  P_0^+ = E[x_0 \\cdot x_0^T] 

where:

- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, before a measurement update. 
- :math:`F` is the discretized process dynamics matrix 
- :math:`G` is the discretized process input matrix 
- :math:`u_k` is the process input signal
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, before a measurement update
- :math:`P_{k-1}^+` is the system covariance matrix estimate, :math:`P_k`, from previous measurement update 
- :math:`Q_k` is the process covariance matrix 
- :math:`R_k` is the measurement covariance matrix 
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
are notated by :math:`+` superscript. 

.. math:: 

  K = P_k^- \\cdot H^T \\cdot (H \\cdot P_k^- \\cdot H^T + R_k)^{-1}

  x_k^+ = x_k^- \\cdot K \\cdot (y - H \\cdot x_k^-)

  P_k^+ = (I - K \\cdot H) \\cdot P_k^-

where:

- :math:`K` is the Kalman gain
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, from the previous prediction
- :math:`H` is the discrete measurement matrix 
- :math:`R_k` is the measurement covariance matrix 
- :math:`x_k^+` is the estimate of the system state, :math:`x_k`, after a measurement update
- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, from the previous prediction
- :math:`y` is the measure 
- :math:`I` is the identity matrix 
- :math:`P_k^+` is the estimate of the system covariance matrix, :math:`P_k`, after a measurement update
- superscript T is the transpose operator


Implementation (C4dynamics)
===========================

Following the above concept of separation between the `predict` 
and `update`, running a Kalman filter with `c4dynamics` is performed on a `state` object 
by constructing a Kalman filter with parameters and calling the `predict()` and `update()` methods.

The Kalman filter in `C4dynamics` is a class.  
As such the user constructs an object that holds the 
attributes used to build the estimates. 
This is crucial because when the user calls the :meth:`kalman.predict` or 
the :meth:`kalman.update`, the object uses parameters and values from previous calls. 



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

  
where:

- :math:`z` is the deviation of the aircraft from the required altitude
- :math:`\\gamma` is the flight path angle
- :math:`H_f` is a constant altitude input required by the pilot 
- :math:`\\omega_z` is the uncertainty in the altitude behavior  
- :math:`\\omega_{\\gamma}` is the uncertainty in the flight path angle behavior 
- :math:`u` is the deflection command 
- :math:`y` is the output measure
- :math:`\\nu` is the measure noise   

The process uncertainties are given by: :math:`\\omega_z \\sim (0, 0.5)[ft]
, \\omega_{\\gamma} \\sim (0, 0.1)[deg]`.

Let :math:`H_f`, the required altitude by the pilot to be :math:`H_f = 1kft`. 
The initial conditions are: :math:`z_0 = 1010ft` (error of :math:`10ft`), and :math:`\\gamma_0 = 0`. 

The altimeter is sampling in a rate of :math:`50Hz (dt = 20msec)` 
with measure noise of :math:`\\nu \\sim (0, 0.5)[ft]`.

A Kalman filter shall reduce the noise and estimate the state variables.  
But at first it must be verified that the system is observable, otherwise the filter cannot 
fully estimate the state variables based on the output measurements. 

.. code:: 

  >>> n = A.shape[0]
  >>> obsv = c
  >>> for i in range(1, n):
  ...   obsv = np.vstack((obsv, c @ np.linalg.matrix_power(A, i)))
  >>> rank = np.linalg.matrix_rank(obsv)
  >>> c4d.cprint(f'The system is observable (rank = n = {n}).' if rank == n else 'The system is not observable (rank = {rank), n = {n}).', 'y')
  The system is observable (rank = n = 2). 

  
Let's start with a simulation of an ideal system. 

Variable initialization and dynamics definition:

.. code:: 
  
  >>> dt, tf = 0.01, 10
  >>> tspan = np.arange(0, tf, dt)  
  >>> A = np.array([[0, 5], [0, -0.5]])
  >>> B = np.array([0, 0.1])
  >>> c = np.array([1, 0])
  >>> Q = np.zeros((2, 2))
  >>> Hf = 1000
  >>> # target and altimeter definitions 
  >>> tgt = c4d.state(z = 1010, gamma = 0)
  >>> altmtr = c4d.sensors.seeker(isideal = True)


The dynamics is defined by an ODE function to be solved using scipy's ode integration:

.. code:: 

  >>> def autopilot(y, t, u = 0, Q = np.zeros((2, 1))):
  ...   return A @ y + B * u + Q



Main loop: 

.. code:: 

  >>> for t in tspan:
  ...   tgt.store(t)
  ...   altmtr.store(t)
  ...   _, _, Z = altmtr.measure(tgt, t = t, store = True)
  ...   if Z is None: continue 
  ...   tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (F - Z, np.sqrt(Q) @ np.random.randn(2, 1)))[-1]

Plot the time histories of :math:`z` and :math:`\\gamma`:

.. code:: 

  >>> fig, ax = plt.subplots(1, 2)
  >>> # first axis 
  >>> ax[0].plot(*tgt.data('z'), 'c', linewidth = 2, label = 'true') 
  >>> ax[0].plot(*altmtr.data('range'), 'm', linewidth = 1, label = 'altimeter')
  >>> c4d.plotdefaults(ax[0], 'Altitude', 't', 'ft')
  >>> ax[0].legend(fontsize = 'small', facecolor = None) 
  >>> # second axis
  >>> ax[1].plot(*tgt.data('gamma', c4d.r2d), 'c', linewidth = 1.5, label = 'true')
  >>> c4d.plotdefaults(ax[1], 'Path Angle', 't', '')
  >>> ax[1].legend(fontsize = 'small', facecolor = None)

.. figure:: /_static/figures/filters_kalman_ideal.png

The ideal altimeter measures precisely the aircraft altitude. 
Its samples used to control the flight that started 
at an altitude of :math:`10ft` above the required 
altitude and is closed after about :math:`18s`.  

Now, let's introduce the process noise and the measurement noise:

.. code:: 

  >>> Q = np.diag([0.5**2, (0.1 * c4d.d2r)**2])
  >>> tgt = c4d.state(z = 1010, gamma = 0)
  >>> altmtr = c4d.sensors.seeker(rng_noise_std = 0.5, dt = 20e-3) 

Re-running the main loop yields: 

.. figure:: /_static/figures/filters_kalman_noisy.png

Very bad.
The errors corrupt the input that uses to control the altitude.
The point in which the altitude converges to its steady-state is more 
than :math:`10s` later than the ideal case. 

The Kalman filter should find optimized gains to minimize the mean squared error. 
For the estimated state let's define a new target, :math:`htgt`, where `h` stands for the 
hat estimation symbol. Let's also add to the estimated target a Kalman filter object 
that consists of the Kalman attributes: 

.. code:: 

  >>> htgt = c4d.state(z = tgt.z + 5, gamma = tgt.gamma + 0.05 * c4d.d2r) 
  >>> htgt.kf = c4d.filters.kalman(P0 = [2 * 5, 2 * 0.05 * c4d.d2r] 
  ...                               , R = v**2, Q = Q, dt = dt   
  ...                                 , A = A, B = B, c = c) 

Note that the Kalman filter was initialized here with continuous system matrices. 
However, it could be initialized with discrete system matrices. The only limit
is that all the four necessary parameters, i.e. :math:`A, B, Q, R` or :math:`F, G, Qk, Rk` 
will be provided consistently and as a complete set:

.. code:: 

  >>> htgt.kf = c4d.filters.kalman(P0 = [2 * 5, 2 * 0.05 * c4d.d2r] 
  ...                                , Rk = v**2 / 20e-3, Qk = Q * dt, dt = dt   
  ...                                    , F = np.eye(2) + A * dt, G = B * dt, H = c) 




The main loop is changed to: 

.. code:: 

  >>> for t in tspan:
  ...  tgt.store(t)
  ...  htgt.store(t)
  ...  htgt.p11, htgt.p22 = htgt.kf.P[0, 0], htgt.kf.P[1, 1]
  ...  htgt.storeparams(['state', 'p11', 'p22'], t)
  ...  altmtr.store(t)
  ...  tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - htgt.z, np.sqrt(Q) @ np.random.randn(2, 1)))[-1]
  ...  # predict
  ...  htgt.X = htgt.kf.predict(htgt.X, u = Hf - htgt.z)
  ...  _, _, Z = altmtr.measure(tgt, t = t, store = True)
  ...  if Z is None: continue 
  ...  # update 
  ...  htgt.X = htgt.kf.update(htgt.X, Z)


.. figure:: /_static/figures/filters_kalman_filtered.png

The filtered altitude (`htgt.z`) is used as input to control the system and 
generates results almost as good as the ideal case. 

Ultimately, the altimeter measuring the aircraft altitude
operates through a two-step process: prediction and update. 
In the prediction step, the filter projects the current state estimate 
forward using the system model. 
In the update step, it corrects this prediction with new measurements. 

As the Kalman filter implemented as a class, 
its usage is by creating an instance and then calling its 
predict and update methods for state estimation. 















*************************************
Extended Kalman Filter (:class:`ekf`)
*************************************

A linear Kalman filter (:class:`kalman`) should be the first choice 
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


where: 

- :math:`f(\\cdot)` is an arbitrary vector-valued function representing the system dynamics
- :math:`x` is the system state vector 
- :math:`u` is the process input signal
- :math:`\\omega` is the process noise with covariance matrix :math:`Q`
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
    

where:

- :math:`\\omega` is the process noise with covariance matrix :math:`Q`
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
is to discretize these terms and the noise covariance matrices: 


.. math::

  F = I + A \\cdot dt 

  H = C  

  Q_k = Q \\cdot dt 

  R_k = R / dt_{measure}

where:

- :math:`F` is the discretized process dynamics matrix (actually a first order approximation of the state transition matrix :math:`\\Phi`)
- :math:`G` is the discretized process input matrix
- :math:`H` is the discrete measurement matrix 
- :math:`\\nu_k` is the measure noise with covariance matrix :math:`R_k`
- :math:`I` is the identity matrix
- :math:`dt` is the sampling time 
- :math:`dt_{measure}` is the sampling time of the measures 
- :math:`Q_k` is the process covariance matrix 
- :math:`R_k` is the measurement covariance matrix 
- :math:`A, C, Q, R` are the continuous-time system variables of the system state matrix, system outrput vector, process covariance matrix, and measurement covariance matrix, respectively

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

  P_k^- = F \\cdot P_{k-1}^+ \\cdot F^T + Q_k

subject to initial conditions: 

.. math:: 
  
  x_0^+ = x_0

  P_0^+ = E[x_0 \\cdot x_0^T] 


where: 

- :math:`F` is the discretized process dynamics matrix 
- :math:`I` is the identity matrix
- :math:`f(\\cdot)` is a vector-valued function representing the system dynamics
- :math:`dt` is the sampling time 
- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, before a measurement update. 
- :math:`u_k` is the process input signal
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, before a measurement update
- :math:`P_{k-1}^+` is the system covariance matrix estimate, :math:`P_k`, from previous measurement update 
- :math:`Q_k` is the process covariance matrix 
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

  K = P_k^- \\cdot H^T \\cdot (H \\cdot P_k^- \\cdot H^T + R_k)^{-1}

  x_k^+ = x_k^- \\cdot K \\cdot (y - h(x)) 

  P_k^+ = (I - K \\cdot H) \\cdot P_k^-

where:

- :math:`H` is the discrete measurement matrix 
- :math:`h(\\cdot)` is a vector-valued function representing the measurement equations 
- :math:`x_k^-` is the estimate of the system state, :math:`x_k`, from the previous prediction
- :math:`K` is the Kalman gain
- :math:`P_k^-` is the estimate of the system covariance matrix, :math:`P_k`, from the previous prediction
- :math:`R_k` is the measurement covariance matrix 
- :math:`x_k^+` is the estimate of the system state, :math:`x_k`, after a measurement update
- :math:`y` is the measure 
- :math:`I` is the identity matrix 
- :math:`P_k^+` is the estimate of the system covariance matrix, :math:`P_k`, after a measurement update
- superscript T is the transpose operator



Implementation (C4dynamics)
===========================

We saw that the state in the `predict` stage and in the `update` stage 
doesn't have to use the approximated nonlinear equations and instead 
can make use of the exact models for the process and for the measurement.
However, sometimes it is more convenient to use 
the already linear terms also for the state advancements. 
C4dyanmics offers interface for each approach, i.e. the predict method 
can take :math:`f(x)` and if it is not provided, it uses :math:`F` (necessary) 
to project the state. So for the update method, it can take :math:`h(x)` but if it is not provided it uses :math:`H` (necessary)
to correct :math:`x`. 


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


where


- :math:`\\rho_0 = 0.0034`
- :math:`k = 22,000` 
- :math:`g = 32.2 ft/sec^2`
- :math:`\\omega_{\\beta} \\sim ()`
- :math:`\\nu_k \\sim (0, 500)` 
- :math:`z` is the target altitude (ft)
- :math:`v_z` is the target vertical velocity (ft/sec)
- :math:`\\beta` is the target ballistic coefficient (lb/ft^2)
- :math:`y` is the system measure 


Let:

.. math::

  \\rho = \\rho_0 \\cdot e^{-z / k}


The lineariztion of the process matrix for the `predict` step:

.. math::

  M = \\begin{bmatrix}
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
  >>> tspan = np.arange(dt, tf, dt) 
  >>> dtsensor = 0.05  
  >>> rho0, k = 0.0034, 22000 
  >>> tgt = c4d.state(z = 100000, vz = -6000, beta = 500)
  >>> altmtr = c4d.sensors.seeker(isideal = True, dt = dt)

Target equations of motion:

.. code:: 

  >>> def ballistics(y, t):
  ...   return [y[1], rho0 * np.exp(-y[0] / k) * y[1]**2 * c4d.g_fts2 / 2 / y[2] - c4d.g_fts2, 0]

  
Main loop: 

.. code::  

  >>> for t in tspan:
  ...   tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
  ...   altmtr.measure(tgt, t = t, store = True)
  ...   tgt.store(t)

.. figure:: /_static/figures/filters_ekf_ideal.png

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
for the noise covariance matrices :math:`Q_k, R_k` as for 
the initialization of the state covariance matrix :math:`P`:   


.. code::

  >>> zerr, vzerr, betaerr = 25, -150, 1000 
  >>> nu = np.sqrt(500) 
  >>> p0 = np.diag([nu**2, vzerr**2, betaerr**2])
  >>> Rk = nu**2 / dt
  >>> Qk = np.diag([0, 0, betaerr**2 / tf * dt])  
  >>> # altmeter and ekf construction: 
  >>> altmtr = c4d.sensors.seeker(rng_noise_std = nu, dt = dtsensor) 
  >>> ekf = c4d.filters.ekf(X = {'z': tgt.z + zerr, 'vz': tgt.vz + vzerr
  ...                                     , 'beta': tgt.beta + betaerr}
  ...                                         , P0 = p0, dt = dt) 



The main loop includes the simulation of the target motion, the linearization 
and discretization of the process equations, and calling the `predict` method. 
Then linearization and discretization of the measurement equations (not relevant 
here as the measurement is already linear), and calling the `update` method. 

.. code:: 

  >>> for t in tspan:
  ...   # target motion simulation  
  ...   tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
  ...   # process linearization 
  ...   rhoexp = rho0 * np.exp(-ekf.z / k) * c4d.g_fts2 * ekf.vz / ekf.beta
  ...   fx = [ekf.vz, rhoexp * ekf.vz / 2 - c4d.g_fts2, 0]
  ...   f2i = rhoexp * np.array([-ekf.vz / 2 / k, 1, -ekf.vz / 2 / ekf.beta])
  ...   # discretization 
  ...   F = np.array([[0, 1, 0], f2i, [0, 0, 0]]) * dt + np.eye(3)
  ...   # ekf predict 
  ...   ekf.predict(F, Qk, fx = fx)
  ...   # take a measure 
  ...   _, _, Z = altmtr.measure(tgt, t = t, store = True)
  ...   if Z is not None:  
  ...     H = [1, 0, 0]
  ...     # ekf update 
  ...     ekf.update(Z, H, Rk)
  ...   # store states
  ...   tgt.store(t)
  ...   ekf.store(t)

Though the `update` requires also the linear process matrix (:math:`F`), the `predict` method 
stores the introduced `F` to prove that the `update` step always comes after calling the `predict`. 


.. figure:: /_static/figures/filters_ekf_filtered.png



A few steps to consider when designing a Kalman filter: 

- If possible, find a nominal trajectory to linearize the system about.
- Identify the nonlinearity; there may be mixed situations:
- The process equations are nonlinear.
- The measurement equations are nonlinear.
- Both are nonlinear.
- -> Design your filter accordingly.
- The two major time-consuming activities are:
- Proving the dynamic model.
- Researching the weights for the noise matrices Q, R.
- -> Plan your time in advance.
- Use a framework that provides you with the most flexibility and control.
- Make fun. 








***************
Low-pass Filter
***************

A first-order lowpass filter. 

The differential equation: 

.. math:: 

  \\alpha \\cdot \\dot{y} + y = x

represents a first-order lowpass filter, which allows low-frequency 
signals to pass while attenuating higher-frequency signals.

In singal processing applications, it smooths signals by reducing high-frequency noise.

In control systems applications, it can use to describe 
a first-order lag.

In the frequency-domain, the above diffential equation is represented by: 

.. math::

  H(s) = {Y(s) \\over X(s)} = {1 \\over \\alpha \\cdot s}

where 

- :math:`H` is the transfer function
- :math:`Y` is the output signal
- :math:`X` is the input signal
- :math:`\\alpha` is the shaping parameter  
- :math:`s` is the complex frequency variable in the Laplace transform, :math:`s = j \\cdot 2 \\cdot \\pi \\cdot f` 


Depending on the interpretation that \\alpha is given, the 

when :math:`\\alpha` represents the cutoff frequency: 

.. math::

  s


The frequency separating beween passing frequencies and attenuated 
frequencies is called the cutoff frequency.


In the context of a first-order low-pass filter (LPF), 
the relationship between the time constant 𝜏
τ and the cutoff frequency 𝑓𝑐f c​
is important. The cutoff frequency is the frequency at which the 
output signal is attenuated to 122​ 1
​
(or approximately 0.707) of its maximum value. 
This frequency is also known as the -3dB point.

The cutoff frequency 𝑓𝑐f c
​
(in Hertz) is related to the time constant 𝜏τ by the formula:
𝑓𝑐=12𝜋𝜏f c​ = 2πτ1
​
Alternatively, the time constant can be expressed in terms of the cutoff frequency:
𝜏=12𝜋𝑓𝑐τ 2πfc​1
​
 

When designing or simulating a first-order low-pass filter, 
you often start with a desired cutoff frequency and then calculate the 
corresponding time constant 
𝜏τ. In a discrete-time implementation, the filter's 
behavior is determined by the sample rate and the cutoff frequency, which 
together define the filter coefficient 𝛼α.

Let's add tests for this additional context, ensuring that the 
lowpass class can initialize using a cutoff frequency and sample rate, 
and then use it to simulate a first-order system.



There are different types of lowpass filters, 
including RC (resistor-capacitor) filters, 
LC (inductor-capacitor) filters, 
and active lowpass filters using operational amplifiers.



A first-order lowpass filter is defined by:

.. math:: 

  \\dot{y}(t) = -{1 \\over \\tau} \\cdot y(t) + {1 \\over \\tau} \\cdot x(t) 

in the continuous-time domain, and by:

.. math:: 

  y_k = \\alpha \\cdot x_k + (1 - \\alpha) \\cdot y_{k-1}

in the discrete-time domain. 

The differential equation of the continuous-time filter 
can be Euler-integrated with time constant :math:`dt` as:

.. math::

  y(t + dt) = y(t) + dt \\cdot (-{1 \\over \\tau} \\cdot y(t) + {1 \\over \\tau} \\cdot x(t))


We can substitute 

.. math::

  k = t + dt 

  \\alpha = {dt \\over \\tau}

  
we can derive one representation from the other. 

As such, `c4dynamics` allows each 




  
  
 
  

.. [SD] Simon, Dan, 'Optimal State Estimation: Kalman, H Infinity, and Nonlinear Approaches', Hoboken: Wiley, 2006.

.. [AG] Agranovich, Grigory, Lecture Notes on Modern and Digital Control Systems, University of Ariel, 2012-2013.

.. [ZP] Zarchan, Paul, 'Tactical and Strategic Missile Guidance', American Institute of Aeronautics and Astronautics, 1990. 

.. [MZ] Meri, Ziv, 'Extended Lyapunov Analysis and Simulative Investigations in Stability of Proportional Navigation Guidance Systems', MSc. Thesis supervised by prof. Grigory Agranovich, University of Ariel, 2020.
  





'''


# **********
# References
# **********

# .. [SD] Simon, Dan, 'Optimal State Estimation: Kalman, H Infinity, and Nonlinear Approaches', Hoboken: Wiley, 2006.

# .. [AG] Agranovich, Grigory, Lecture Notes on Modern and Digital Control Systems, University of Ariel, 2012-2013.

# .. [ZP] Zarchan, Paul, 'Tactical and Strategic Missile Guidance', American Institute of Aeronautics and Astronautics, 1990. 

# .. [MZ] Meri, Ziv, 'Extended Lyapunov Analysis and Simulative Investigations in Stability of Proportional Navigation Guidance Systems', MSc. Thesis supervised by prof. Grigory Agranovich, University of Ariel, 2020.
  


from .kalman import kalman 
from .ekf import ekf 
# from .luenberger import luenberger
from .lowpass import lowpass 

