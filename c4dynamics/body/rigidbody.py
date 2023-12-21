import numpy as np
# from scipy.integrate import solve_ivp 

import c4dynamics as c4d
# from c4dynamics.src.main.py.eqm.eqm6 import eqm6
from c4dynamics.eqm import eqm6
from c4dynamics.rotmat import dcm321

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
  # _data = [] # np.zeros((1, 19))
  # _didx = {'t': 0, 'x': 1, 'y': 2, 'z': 3, 'vx': 4, 'vy': 5, 'vz': 6, 'ax': 7, 'ay': 8, 'az': 9 
  #          , 'phi': 10, 'theta': 11, 'psi': 12, 'p': 13, 'q': 14, 'r': 15, 'p_dot': 16, 'q_dot': 17, 'r_dot': 18}
  
  # 
  # properties for integration
  ##  
  # _xs = np.zeros((1, 10))   # current state for integration
  # _dt = 1e-2 # when running free fall dt of .01sec is inaccurate. besides it seems like have no use. 





  # 
  # bounded methods 
  ##
  def __init__(obj, **kwargs):
    #
    # reset mutable attributes:
    # 
    # variables for storage
    ##
    super().__init__()  # Dummy values
    obj.__dict__.update(kwargs)
    obj._data = [] # np.zeros((1, 19))
    obj._didx.update({'phi': 7, 'theta': 8, 'psi': 9
                        , 'p': 10, 'q': 11, 'r': 12})  
                          # , 'p_dot': 16, 'q_dot': 17, 'r_dot': 18})

    obj.x0 = obj.x
    obj.y0 = obj.y
    obj.z0 = obj.z

    obj.phi0   = obj.phi
    obj.theta0 = obj.theta
    obj.psi0   = obj.psi
    
    # obj._xs = [obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r]
   

  @property 
  def IB(obj): 
    # inertial from body dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return np.transpose(dcm321(obj))
  

  @property
  def BI(obj): 
    # body from inertial dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return dcm321(obj)



  # @property
  # def X(obj):
  #   return super().X 
  

  # @X.setter
  # def X(obj, x):
    
  #   obj.x   = x[0]
  #   obj.y   = x[1]
  #   obj.z   = x[2]

  #   if len(x) > 3:
  #     obj.vx  = x[3]
  #     obj.vy  = x[4]
  #     obj.vz  = x[5]

  #   if len(x) > 6:
  #     obj.ax  = x[6]
  #     obj.ay  = x[7]
  #     obj.az  = x[8]

  #   if len(x) > 9: 

  #     obj.phi   = x[9]
  #     obj.theta = x[10]
  #     obj.psi   = x[11]

  #     obj.p     = x[12]
  #     obj.q     = x[13]
  #     obj.r     = x[14]

      # obj.p_dot = x[15]
      # obj.q_dot = x[16]
      # obj.r_dot = x[17]






  # def store(obj, t = -1):
  #   # obj._data = np.vstack((obj._data
  #   #                        , np.array([t, obj.x, obj.y,  obj.z      # 0 : 3
  #   #                                    , obj.vx, obj.vy, obj.vz      # 4 : 6
  #   #                                    , obj.ax, obj.ay, obj.az       # 7 : 9
  #   #                                    , obj.phi, obj.theta, obj.psi   # 10 : 12
  #   #                                    , obj.p, obj.q, obj.r            # 13 : 15
  #   #                                    , obj.p_dot, obj.q_dot, obj.r_dot # 16 : 18                                      
  #   #                                    ]))).copy()
  #   obj._data.append([t, obj.x, obj.y,  obj.z      # 0 : 3
  #                     , obj.vx, obj.vy, obj.vz      # 4 : 6
  #                       , obj.ax, obj.ay, obj.az       # 7 : 9
  #                         , obj.phi, obj.theta, obj.psi   # 10 : 12
  #                           , obj.p, obj.q, obj.r            # 13 : 15
  #                             , obj.p_dot, obj.q_dot, obj.r_dot])


  # def get_phi(obj):
  #     return np.array(obj._data)[:, 10] if obj._data else np.empty(1)
  # # data_phi = property(get_phi, super(c4d.rigidbody).set_t,  super(rigidbody, obj).set_t)
  # def get_theta(obj):
  #     return np.array(obj._data)[:, 11] if obj._data else np.empty(1)
  # def get_psi(obj):
  #     return np.array(obj._data) if obj._data else np.empty(1)

  def inteqm(obj, forces, moments, dt):
    '''
    4th Order Runge-Kutta method for solving ODEs

    Parameters:
        f: function representing the ODE, f(x, y)
        y0: initial value of y
        x0: initial value of x
        xn: final value of x
        h: step size

    Returns:
        x_values: List of x values
        y_values: List of corresponding y values
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
     
    '''

    # x, y, z, vx, vy, vz, phi, theta, psi, p, q, r 
    x0 = obj.X
        
    # print('t: ' + str(t) + ', f: ' + str(forces) + ', m: ' + str(moments))

    # step 1
    h1 = eqm6(obj, forces, moments)
    # yt = 
    # obj.update(np.concatenate((yt[0 : 6], np.zeros(3), yt[6 : 12], np.zeros(3)), axis = 0))
    obj.X = x0 + dt / 2 * h1 
    
    # print('dydx: ' + str(dydx))
    # print('yt: ' + str(yt))

    # step 2 
    h2 = eqm6(obj, forces, moments)
    # yt = 
    # obj.update(np.concatenate((yt[0 : 6], np.zeros(3), yt[6 : 12], np.zeros(3)), axis = 0))
    obj.X = x0 + dt / 2 * h2 
    
    # print('dyt: ' + str(dyt))
    # print('yt: ' + str(yt))
    
    # step 3 
    h3 = eqm6(obj, forces, moments)
    # yt =
    # obj.update(np.concatenate((yt[0 : 6], np.zeros(3), yt[6 : 12], np.zeros(3)), axis = 0))
    obj.X = x0 + dt * h3 
    
    # print('dym: ' + str(dym))
    # print('yt: ' + str(yt))
    
    # print('dym: ' + str(dym))
    
    # step 4
    h4 = eqm6(obj, forces, moments)
    # print('dyt: ' + str(dyt))
    # print('yout: ' + str(yout))

    if (h1[10] - h2[10]) != 0:
      print(np.linalg.norm((h2[10] - h3[10]) / (h1[10] - h2[10])))

    # obj.update(np.concatenate((yout[0 : 6], dyt[3 : 6], yout[6 : 12], dyt[9 : 12]), axis = 0))
    
    obj.X = x0 + dt / 6 * (h1 + 2 * h2 + 2 * h3 + h4) 
     
    # obj.ax, obj.ay, obj.az = dxdt4[3 : 6] # dyt[-3:]
    # obj.p_dot, obj.q_dot, obj.r_dot = dxdt4[9 : 12] # dyt[-3:]
    return h4[3 : 6] + h4[9 : 12]
    ##



