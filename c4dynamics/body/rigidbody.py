import numpy as np
# from scipy.integrate import solve_ivp 

import c4dynamics as c4d
# from c4dynamics.src.main.py.eqm.eqm6 import eqm6
from c4dynamics.eqm import eqm6
from c4dynamics.rotmat import dcm321

class rigidbody(c4d.datapoint):  # 
  ''' 
  The :class:`rigidbody` extends the :class:`datapoint`
  to form an elementary rigidbody object in space.  

  The rigidbody is a class defining a rigid body in space, i.e. 
  an object with length and attitude.

  The rigidbody class extends the functionality of the datapoint class. 
  It introduces additional attributes related to rotational dynamics, 
  such as angular position, angular velocity, and moment of inertia. 

  The class leverages the capabilities of the datapoint class for handling
  translational dynamics and extends it to include rotational aspects.

  '''
  
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
  ''' float; Angular rate around the x-axis (rad/sec). '''
  q     = 0
  ''' float; Angular rate around the y-axis (rad/sec). '''
  r     = 0
  ''' float; Angular rate around the z-axis (rad/sec). '''
  
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
  ''' float; Moment of inertia about the z-axis.  '''
  xcm = 0   
  ''' float; Distance from nose to center of mass (m). '''
  
  # 
  # body from inertial direction cosine matrix   
  ## 
  dcm = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
  ''' 
  numpy array; Direction Cosine Matrix (DCM) representing the orientation of the body.
  '''



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
    ''' Inertial from body direction cosine matrix. '''
    # inertial from body dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return np.transpose(dcm321(obj))
  

  @property
  def BI(obj): 
    ''' Body from inertial direction cosine matrix. '''
    # body from inertial dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return dcm321(obj)


  def inteqm(obj, forces, moments, dt):
    '''
    Integrates equations of motion using the 4th Order Runge-Kutta method.

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



