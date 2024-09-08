import numpy as np
from scipy.linalg import solve_discrete_are
import c4dynamics as c4d 


class kalman(c4d.state):
  ''' 
  Kalman Filter.

  Kalman Filter class for state estimation. 
  :class:`kalman` provides methods for prediction and update
  phases of the Kalman filter, including both discrete and continuous systems.
  
  Parameters
  ==========
        
  X : dict
      Initial state variables and their values.
  dt : float
      Time step for the filter.
  P0 : numpy.ndarray, optional
      Initial covariance matrix or standard deviations. Mandatory if steadystate is False.
  steadystate : bool, optional
      Flag to indicate if the filter is in steady-state mode. Defaults to False.
  A : numpy.ndarray, optional
      Continuous-time state transition matrix. Defaults to None.
  C : numpy.ndarray, optional
      Continuous-time measurement matrix. Defaults to None.
  Q : numpy.ndarray, optional
      Continuous-time process noise covariance matrix. Defaults to None.
  R : numpy.ndarray, optional
      Continuous-time measurement noise covariance matrix. Defaults to None.
  B : numpy.ndarray, optional
      Continuous-time control matrix. Defaults to None.
  F : numpy.ndarray, optional
      Discrete-time state transition matrix. Defaults to None.
  H : numpy.ndarray, optional
      Discrete-time measurement matrix. Defaults to None.
  Qk : numpy.ndarray, optional
      Discrete-time process noise covariance matrix. Defaults to None.
  Rk : numpy.ndarray, optional
      Discrete-time measurement noise covariance matrix. Defaults to None.
  G : numpy.ndarray, optional
      Discrete-time control matrix. Defaults to None.
        
  Raises:
  TypeError: If X is not a dictionary.
  ValueError: If P0 is not provided when steadystate is False.
  ValueError: If neither continuous nor discrete system matrices are fully provided.


      
  See Also
  ========
  .filters
  .ekf 
  .lowpass
  .seeker 
  .eqm 


  Example
  =======
  TODO complete
  

  '''
  
  Kinf = None 


  def __init__(self, X, dt, P0 = None, steadystate = False
                  , A = None, C = None, Q = None, R = None, B = None 
                      , F = None, H = None, Qk = None, Rk = None, G = None): 
    # 
    # P0 is mandatory and it is either the initial state covariance matrix itself or 
    # a vector of the diagonal standard deviations. 
    # dt is for the predict integration.
    # F and H are linear transition matrix and linear measure matrix for
    # a linear kalman filter.
    # Q and R are process noise and measure noise matrices when they are time invariant. 
    ##  

    if not isinstance(X, dict):
      raise TypeError('X must be a dictionary containig pairs of variables '
                      'and initial conditions, e.g.: {''x'': 0, ''y'': 0}')
    super().__init__(**X)

    if steadystate is False and P0 is None: 
      raise ValueError(r'P0 is a necessary variable (optional only in steadystate mode)')


    self.dt = dt
    self.G = None 
    # if continuous, check all mats provided.
    # if discrete, check all mats provided. 
     
    if A is not None and C is not None and Q is not None and R is not None:
      # assume continuous system  
      
      self.F  = np.eye(len(A)) + A * dt 
      self.H  = np.atleast_2d(C) 
      self.Qk = np.atleast_2d(Q) * dt 
      self.Rk = np.atleast_2d(R) / dt 

      
      if B is not None: 
        self.G = np.atleast_2d(B) * dt 


    elif F is not None and H is not None and Qk is not None and Rk is not None:
      # not continuous

      self.F  = np.atleast_2d(F) 
      self.H  = np.atleast_2d(H) 
      self.Qk = np.atleast_2d(Qk)  
      self.Rk = np.atleast_2d(Rk)  

      if G is not None: 
        self.G = np.atleast_2d(G) 

    else: 
        
      raise ValueError('At least one set of matrices has to be entirely provided: ' 
                         '\nFor a continuous system: A, C, Q, R, (B is optional). where: x'' = A*x + B*u + w, y = C*x + v, E(w*w^T) = Q*delta(t), E(v*v^T) = Q*delta(t). '
                         '\nFor a dicscrete system: F, H, Qk, Rk, (G is optional). where x(k) = F*x(k-1) + G*u(k-1) + wk, y(k) = H*x(k), E(wk*wk^T) = Qk*delta(k), E(vk*vk^T) = Rk * delta(k)')

    if steadystate: 
      self.P = solve_discrete_are(self.F.T, self.H.T, self.Qk, self.Rk)
      self.Kinf = self.P @ self.H.T @ np.linalg.inv(self.H @ self.P @ self.H.T + self.Rk)
      

    else:
      P0 = np.atleast_2d(P0)

      if P0.shape[0] == P0.shape[1]:
        # square matrix
        self.P = P0
      else:
        # only standard deviations are provided 
        self.P = np.diag(P0.flatten()**2)

    self._Pdata = []   


  def predict(self, u = None):
    '''
    Predicts the next state and covariance based on the current state and process model.
    
    Parameters
    ----------
    u : numpy.ndarray, optional
        Control input. Defaults to None.

    '''
    # TODO test the size of the objects. 
    # test the type. 
    # make sure the user is working with c4d modules. 

    # this F must be linear, but it can be linearized once for the entire
    # process (regular kalman), or linearized and delivered at each step (extended kalman)
    if self.Kinf is None:
      self.P = self.F @ self.P @ self.F.T + self.Qk 
      # self.P = self.F @ self.P @ self.F.T + self.Q
         
    # this F can be either linear or nonlinear function of x. 
    # print(f'{x=}')
    self.X = self.F @ self.X 
    # print(f'{x=}')

    if u is not None and self.G is not None:
        # print(f'{self.B.shape = } {u = } {np.array(u) = } {np.array(u).shape = }')
        self.X += self.G.reshape(self.X.shape) * u 

    
 
  def update(self, z): 
    '''
    Updates the state estimate based on the given measurements.
    
    Parameters
    ----------
    z : numpy.ndarray
        Measurement vector.

    '''

    
    # this H must be linear, but as F may it be linearized once about an equilibrium point for 
    # the entire process (regular kalman) or at each 
    # iteration about the current state (ekf). 
    if self.Kinf is None:
      K = self.P @ self.H.T @ np.linalg.inv(self.H @ self.P @ self.H.T + self.Rk)
      self.P = self.P - K @ self.H @ self.P
    else: 
      K = self.Kinf

    # this H can be expressed as either linear or nonlinear function of x.  
    # print(f'\n correct \n')
    # print(f'{x=} {K=} {z=} {hx=}')
    self.X += K @ (z - self.H @ self.X)
    
    




  def store(self, t = -1):
    ''' 
    Stores the current state and diagonal elements of the covariance matrix.
        
    Parameters
    ----------

    t : int, optional
        Time step for storing the state. Defaults to -1.
      
    '''
    
    super().store(t) # store state 
    # store covariance: 
    for i, p in enumerate(np.diag(self.P)): 
      pstr = f'P{i}{i}'
      setattr(self, pstr, p) # set 
      self.storeparams(pstr, t) # store 
    





