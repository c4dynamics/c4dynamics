import numpy as np
# from scipy.integrate import solve_ivp 

import C4dynamics as c4d
from .eqm6 import eqm6 

class rigidbody(c4d.datapoint):  # 
  """ 
    the rigidbody object is the most basic element in the rotational dynamics domain.
    a rigidbody object is also a datapoint. 
  """
  
  # 
  # euler angles 
  #   rad 
  ##
  phi   = 0
  theta = 0
  psi   = 0
  
  # 
  # angular rates 
  #   rad / sec 
  ##
  p     = 0
  q     = 0
  r     = 0
  
  # 
  # abgular accelerations
  #   rad / sec^2
  ## 
  p_dot = 0
  q_dot = 0
  r_dot = 0
  
  # 
  # initial attitude
  #   rad 
  ##
  phi0   = 0
  theta0 = 0
  psi0   = 0
  
  
  # 
  # inertia properties 
  ## 
  ixx = 0   # moment of inertia aboux x
  iyy = 0   # moment of inertia aboux y
  izz = 0   # moment of inertia aboux z
  xcm = 0   # distance from nose to center of mass (m) 
  
  
  
  # 
  # body from inertial direction cosine matrix   
  ## 
  dcm = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])


  # 
  # variables for storage
  ##
  _data = np.zeros((1, 19))
  _didx = {'t': 0, 'x': 1, 'y': 2, 'z': 3, 'vx': 4, 'vy': 5, 'vz': 6, 'ax': 7, 'ay': 8, 'az': 9 
           , 'phi': 10, 'theta': 11, 'psi': 12, 'p': 13, 'q': 14, 'r': 15, 'p_dot': 16, 'q_dot': 17, 'r_dot': 18}
  
  # 
  # properties for integration
  ##  
  # _xs = np.zeros((1, 10))   # current state for integration
  _dt = 1e-2 # when running free fall dt of .01sec is inaccurate. besides it seems like have no use. 





  # 
  # bounded methods 
  ##
  def __init__(obj, **kwargs):
    obj.__dict__.update(kwargs)

    obj.phi0   = obj.phi
    obj.theta0 = obj.theta
    obj.psi0   = obj.psi
    
    obj._xs = [obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r]
   
   
  def IB(obj): 
    # inertial from body dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return np.transpose(c4d.dcm321(obj.phi, obj.theta, obj.psi))
  
  def BI(obj): 
    # body from inertial dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return c4d.dcm321(obj.phi, obj.theta, obj.psi)


  def store(obj, t = -1):
    obj._data = np.vstack((obj._data
                           , np.array([t, obj.x, obj.y,  obj.z      # 0 : 3
                                       , obj.vx, obj.vy, obj.vz      # 4 : 6
                                       , obj.ax, obj.ay, obj.az       # 7 : 9
                                       , obj.phi, obj.theta, obj.psi   # 10 : 12
                                       , obj.p, obj.q, obj.r            # 13 : 15
                                       , obj.p_dot, obj.q_dot, obj.r_dot # 16 : 18                                      
                                       ]))).copy()



  def get_phi(obj):
      return obj._data[1:, 10]
  # data_phi = property(get_phi, super(c4d.rigidbody).set_t,  super(rigidbody, obj).set_t)
  def get_theta(obj):
      return obj._data[1:, 11]
  def get_psi(obj):
      return obj._data[1:, 12]

  def run(obj, dt, forces, moments):
    # 
    # integration 
    # $ runge kutta 
    #     ti = tspan(i); yi = Y(:,i);
    #     k1 = f(ti, yi);
    #     k2 = f(ti+dt/2, yi+dt*k1/2);
    #     k3 = f(ti+dt/2, yi+dt*k2/2);
    #     k4 = f(ti+dt  , yi+dt*k3);
    #     dy = 1/6*(k1+2*k2+2*k3+k4);
    #     Y(:,i+1) = yi + dy;
    ## 
    
    y = np.array([obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r])
    
    # step 1
    dydx = eqm6(y, forces, moments, obj.m, obj.ixx, obj.iyy, obj.izz)
    yt = y + dt / 2 * dydx 
    
    # step 2 
    dyt = eqm6(yt, forces, moments, obj.m, obj.ixx, obj.iyy, obj.izz)
    yt = y + dt / 2 * dyt 
    
    # step 3 
    dym = eqm6(yt, forces, moments, obj.m, obj.ixx, obj.iyy, obj.izz)
    yt = y + dt * dym 
    dym += dyt 
    
    # step 4
    dyt = eqm6(yt, forces, moments, obj.m, obj.ixx, obj.iyy, obj.izz)
    yout = y + dt / 6 * (dydx + dyt + 2 * dym) 
    
    # 
    obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r = yout
    yderivs = eqm6(yout, forces, moments, obj.m, obj.ixx, obj.iyy, obj.izz)
    obj.ax, obj.ay, obj.az, obj.p_dot, obj.q_dot, obj.r_dot = yderivs[[3, 4, 5, 9, 10, 11]]
    ##

 