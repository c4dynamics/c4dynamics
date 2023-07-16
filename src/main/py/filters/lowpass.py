import numpy as np

class lowpass:
  """ 
  low pass filter
  zarchan noise analysis
  """

  tau = 0 # filter time constant 
  ts = 0  # integration step size
  x = 0
  
  def __init__(obj, tau, ts, x): 
    obj.tau = tau
    obj.ts = ts
    obj.x = np.reshape(x, ((3, 1)))
      
  def predict(*args):
    pass
    
  def update(obj, f, xin):
    dx = -obj.x[0] / obj.tau + xin / obj.tau
    obj.x[0] = obj.x[0] + dx * obj.ts
    return obj.x
    