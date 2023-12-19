import numpy as np

class e_kalman:
  ''' 
  extended kalman filter 
  zarchan 374 
  see also   
  https://arxiv.org/ftp/arxiv/papers/1204/1204.0375.pdf#:~:text=A%20Kalman%20Filtering%20is%20carried,in%20wireless%20networks%20is%20given.
  
  '''
  # x = 0 # state vector. 
  # # Phi = 0 # transition matrix 
  # P = 0   # covariance matrix
  # # Q = 0   # process noise matrix
  # H = 0   # measurement matrix 
  # R = 0   # measurement noise matrix 
  
  tau = 0

  def __init__(obj, x0, p0noise, tau): # vp, 
    '''    '''
    
    obj.x = np.reshape(x0, ((3, 1)))
    
    n = len(x0)
    
    # obj.Phi = np.zeros(n)
    obj.P = np.zeros((n, n))         # the initial covariance matrix
    for i in range(n):
      # the variance of the error in the initial estimate of position and is taken to be the variance of the measurement noise.
      # the variance of the error in the initial estimate of velocity
      # the variance of the error in the initial estimate of ballistic coefficient
      # others: assumed that there is no process noise.
      obj.P[i, i] = p0noise[i]**2         
    # obj.Q = np.zeros(n)         
    
    obj.H = np.zeros((n))
    obj.H[0] = 1
    obj.R = p0noise[0]**2 
    obj.tau = tau 
    
      
      
  def predict(obj, f, Phi, Q):
    '''
    predict the mean X and the covariance P of the system state at time k.
    x input mean state estimate of the previous step (k - 1)
    P state covariance at k - 1
    A transition matrix
    Q process noise covariance matrix
    b input matrix 
    u control input 
    '''
    obj.x = obj.x + f(obj.x) * obj.tau
    obj.P = np.linalg.multi_dot([Phi, obj.P, Phi.T]) + Q   
    
    return obj.x
 
 
  def update(obj, f, y_in): 
    '''
    computes the posterior mean x and covariance P of the state given new measurement y.
    corrects x and P given the predicted x and P matrices, measurement vector y, the measurement 
    matrix H and the measurement covariance matrix R
    K kalman gains
    '''
    
    S = obj.R + np.linalg.multi_dot([obj.H, obj.P, obj.H.T])
    
    invs = 1 / S if S.ndim < 2 else np.linalg.inv(S)
    K = np.reshape(np.dot(obj.P @ obj.H.T, invs), (len(obj.P), -1))
    
    obj.x = obj.x + np.dot(K, (y_in - np.dot(obj.H, obj.x))).reshape((len(K), 1))
    obj.P = (np.eye(len(obj.P)) - K * obj.H) @ obj.P
    
    return obj.x

