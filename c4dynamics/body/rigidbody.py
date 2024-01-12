import numpy as np
# from scipy.integrate import solve_ivp 

import c4dynamics as c4d
# from c4dynamics.src.main.py.eqm.eqm6 import eqm6
from c4dynamics.eqm import eqm6
from c4dynamics.rotmat import dcm321

class rigidbody(c4d.datapoint):  # 
  
  # 
  # euler angles 
  #   rad 
  ##
  phi   = 0
  ''' float; Euler angle representing rotation around the x-axis (rad). '''
  theta = 0
  ''' float; Euler angle representing rotation around the y-axis (rad). '''
  psi   = 0
  ''' float; Euler angle representing rotation around the z-axis (rad). '''
  
  # 
  # angular rates 
  #   rad / sec 
  ##
  p     = 0
  ''' float; Angular rate around the x-axis (roll). (rad/sec). '''
  q     = 0
  ''' float; Angular rate around the y-axis (pitch). (rad/sec). '''
  r     = 0
  ''' float; Angular rate around the z-axis (yaw). (rad/sec). '''
  
  # 
  # abgular accelerations
  #   rad / sec^2
  ## 
  p_dot = 0
  ''' float; Angular acceleration around the x-axis (rad/sec^2). '''
  q_dot = 0
  ''' float; Angular acceleration around the y-axis (rad/sec^2). '''
  r_dot = 0
  ''' float; Angular acceleration around the z-axis (rad/sec^2). '''


  
  # 
  # inertia properties 
  ## 
  ixx = 0   
  ''' float; Moment of inertia about the x-axis. '''
  iyy = 0  
  ''' float; Moment of inertia about the y-axis. '''
  izz = 0   
  ''' float; Moment of inertia about the z-axis. '''
  xcm = 0   
  ''' float; Distance from nose to center of mass. '''
  



  # 
  # bounded methods 
  ##
  def __init__(self, **kwargs):
    #
    # reset mutable attributes:
    # 
    # variables for storage
    ##
    super().__init__()  # Dummy values
    self.__dict__.update(kwargs)
    self._data = [] # np.zeros((1, 19))
    self._didx.update({'phi': 7, 'theta': 8, 'psi': 9
                        , 'p': 10, 'q': 11, 'r': 12})  

    self.x0 = self.x
    self.y0 = self.y
    self.z0 = self.z
    self.vx0 = self.vx
    self.vy0 = self.vy
    self.vz0 = self.vz

    self.phi0   = self.phi
    self.theta0 = self.theta
    self.psi0   = self.psi
    self.p0   = self.p
    self.q0   = self.q
    self.r0   = self.r
    

   

  @property
  def angles(self):
    ''' 
    Returns an Euler angles array. 
     
    .. math:: 
        X = [\\varphi, \\theta, \\psi]


    Returns
    -------
    out : numpy.array 
        :math:`[\\varphi, \\theta, \\psi]` 
  
        
    Examples
    --------

    .. code:: 
    
      >>> rb = c4d.rigidbody(phi = 135 * c4d.d2r)
      >>> print(rb.angles * c4d.r2d)
      [135.   0.   0.]
    
    '''

    return np.array([self.phi, self.theta, self.psi])


  @property
  def ang_rates(self):
    ''' 
    Returns an angular rates array. 
     
    .. math:: 

      X = [p, q, r]


    Returns
    -------
    out : numpy.array 
        :math:`[p, q, r]` 
  
        
    Examples
    --------

    .. code:: 

      >>> q0 = 30 * c4d.d2r
      >>> rb = c4d.rigidbody(q = q0)
      >>> print(rb.ang_rates * c4d.r2d)
      [ 0. 30.  0.]

    '''
    return np.array([self.p, self.q, self.r])


  @property 
  def IB(self): 
    ''' 
    Returns an Inertial from Body Direction Cosine Matrix (DCM). 

    Based on the current Euler angles, generates a DCM in a 3-2-1 order.
    i.e. first rotation about the z axis (yaw), then a rotation about the 
    y axis (pitch), and finally a rotation about the x axis (roll).
 
    For the background material regarding the rotational matrix operations, 
    see :mod:`rotmat <c4dynamics.rotmat>`. 

    Returns
    -------

    out : numpy.ndarray
        A 3x3 DCM matrix uses to rotate a vector from a body frame 
        to an inertial frame of coordinates.


    Example
    -------

    .. code::

      >>> v_body = [np.sqrt(3), 0, 1]
      >>> rb = c4d.rigidbody(theta = 30 * c4d.d2r)
      >>> v_inertial = rb.IB @ v_body
      >>> print(v_inertial.round(decimals = 2))
      [2. 0. 0.]


    '''
    # inertial from body dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return np.transpose(dcm321(self))
  

  @property
  def BI(self): 
    ''' 

    Returns a Body from Inertial Direction Cosine Matrix (DCM). 

    Based on the current Euler angles, generates a DCM in a 3-2-1 order.
    i.e. first rotation about the z axis (yaw), then a rotation about the 
    y axis (pitch), and finally a rotation about the x axis (roll).
 
    For the background material regarding the rotational matrix operations, 
    see :mod:`rotmat <c4dynamics.rotmat>`. 

    Returns
    -------

    out : numpy.ndarray
        A 3x3 DCM matrix uses to rotate a vector from an inertial frame 
        to a body frame of coordinates.


    Example
    -------

    .. code::

      >>> v_inertial = [1, 0, 0]
      >>> rb = c4d.rigidbody(psi = 45 * c4d.d2r)
      >>> v_body = rb.BI @ v_inertial 
      >>> print(v_body.round(decimals = 3))
      [ 0.707 -0.707  0.   ]


    '''
    # body from inertial dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return dcm321(self)


  def inteqm(self, forces, moments, dt):
    '''
    Advances the state vector, `rigidbody.X`, with respect to the input
    forces and moments on a single step of time, `dt`.

    Integrates equations of six degrees motion using the Runge-Kutta method. 

    This method numerically integrates the equations of motion for a dynamic system
    using the fourth-order Runge-Kutta method as given by 
    :func:`int6 <int6>`. 

    The derivatives of the equations are of six dimensional motion as 
    given by 
    :py:func:`eqm6 <c4dynamics.eqm.eqm6>` 
    
    
    Parameters
    ----------
    forces : numpy.array or list
        An external forces vector acting on the body, `forces = [Fx, Fy, Fz]`  
    moments : numpy.array or list
        An external moments vector acting on the body, `moments = [Mx, My, Mz]`
    dt : float
        Interval time step for integration.


    Returns
    -------
    out : numpy.float64
        An acceleration array at the final time step.


    Note
    ----
    The integration steps follow the Runge-Kutta method:

    1. Compute k1 = f(ti, yi)

    2. Compute k2 = f(ti + dt / 2, yi + dt * k1 / 2)

    3. Compute k3 = f(ti + dt / 2, yi + dt * k2 / 2)

    4. Compute k4 = f(ti + dt, yi + dt * k3)

    5. Update yi = yi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    

    
    Examples
    --------


    .. code::

      >>> dt = .5e-3 
      >>> t = np.arange(0, 10, dt) # np.linspace(0, 10, 1000)
      >>> theta0 =  80 * c4d.d2r       # deg 
      >>> q0     =  0 * c4d.d2r        # deg to sec
      >>> Iyy    =  .4                  # kg * m^2 
      >>> length =  1                  # meter 
      >>> mass   =  0.5                # kg 
      >>> rb = c4d.rigidbody(theta = theta0, q = q0, iyy = Iyy, mass = mass)
      >>> for ti in t: 
      ...    tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
      ...    rb.X = c4d.eqm.int6(rb, np.zeros(3), [0, tau_g, 0], dt)
      ...    rb.store(ti)
      >>> rb.draw('theta')

    .. figure:: /_static/figures/eqm6_theta.png
        
    
    '''
    self.X, acc = c4d.eqm.int6(self, forces, moments, dt, derivs_out = True)
    return acc 



