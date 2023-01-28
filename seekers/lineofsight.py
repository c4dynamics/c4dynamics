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
  
  tau1 = 0.05
  tau2 = 0.05
  omega_ach = np.array([[0], [0], [0]]) # ahieved rate after first order filter
  omega = np.array([[0], [0], [0]])     # actual rate after first order filter 
  
    
  def __init__(obj, **kwargs):
    obj.__dict__.update(kwargs)
  
  def measure(obj, r, v):
    # r: range to target (line of sight vector)
    # v: relative velocity with target 
    
    usa = r / np.linalg.norm(r) # seeker boresight axis vector 
    # gimbal = np.arccos(usa @ ucl) # gimbal angle 
    omega = np.cross(r, v) / np.linalg.norm(r)**2 # true angular rate of the los vector  
    obj.omega_ach = -1 / obj.tau1 * obj.omega_ach + 1 / obj.tau1 * omega # lag 
    obj.omega = -1 / obj.tau2 * obj.omega + 1 / obj.tau2 * obj.omega_ach # lag 
    
    return obj.omega
  
  