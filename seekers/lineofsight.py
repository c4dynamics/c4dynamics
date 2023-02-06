import numpy as np

import C4dynamics as c4d 

# np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)                 

class lineofsight:
  """ 
    the lineofsight is measure line of sight vector rate 
    the seeker head lags the true angular rate. 
    this lag is represented by a first order transfer function with time constant tau1 
    there are assumed to be delays involved in processing the seeker head angular rate singal. 
    the filter delays are represented by a first order transfer function with time constant tau2
  """
  
  tau1 = 0
  tau2 = 0
  dt = 0
  
  omega = np.array([0, 0, 0])     # truth los rate
  omega_ach = np.array([0, 0, 0]) # achieved los rate after first order filter
  omega_f = np.array([0, 0, 0])     # filtered los rate after first order filter 
  
  _data = np.zeros((1, 7))
    
  def __init__(obj, dt, tau1 = 0.05, tau2 = 0.05): #**kwargs):
    # obj.__dict__.update(kwargs)
    obj.dt = dt
    obj.tau1 = tau1 
    obj.tau2 = tau2 
  
  def measure(obj, r, v):
    # r: range to target (line of sight vector)
    # v: relative velocity with target 
    
    # usa = r / np.linalg.norm(r) # seeker boresight axis vector 
    # gimbal = np.arccos(usa @ ucl) # gimbal angle 
    obj.omega = np.cross(r, v) / np.linalg.norm(r)**2 # true angular rate of the los vector  
    # obj.omega_ach = obj.omega_ach + obj.dt * (-1 / obj.tau1 * obj.omega_ach + 1 / obj.tau1 * obj.omega)  # lag 
    # obj.omega_f = obj.omega_f + obj.dt * (-1 / obj.tau2 * obj.omega_f + 1 / obj.tau2 * obj.omega_ach) # filter 
    
    obj.omega_ach = obj.omega_ach * np.exp(-obj.dt / obj.tau1) + obj.omega * (1 - np.exp(-obj.dt / obj.tau1)) # lag 
    obj.omega_f = obj.omega_f * np.exp(-obj.dt / obj.tau2) + obj.omega_ach * (1 - np.exp(-obj.dt / obj.tau2)) # filter 
    
    return obj.omega_f

  
  def store(obj, t = -1):
    obj._data = np.vstack((obj._data
                           , np.concatenate(([t], obj.omega, obj.omega_f)))).copy()

  