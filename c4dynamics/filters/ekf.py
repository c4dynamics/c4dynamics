import numpy as np
import c4dynamics as c4d 

class ekf(c4d.state):
  '''  
  Extended Kalman Filter.

  Extended Kalman Filter class for state estimation.
    
  
  Parameters
  ==========
  X : dict
      Initial state variables and their values.
  P0 : numpy.ndarray
      Initial covariance matrix or standard deviations.
  dt : float, optional
      Time step for the filter. Defaults to None.
  G : numpy.ndarray, optional
      Control matrix. Defaults to None.

   
  See Also
  ========
  .filters
  .kalman  
  .lowpass
  .seeker 
  .eqm 


  Example
  =======
  TODO complete

  '''

  # Phi \ F   transition matrix 
  # P         covariance matrix
  # Q         process noise matrix
  # H         measurement matrix 
  # R         measurement noise matrix 
  
  def __init__(self, X, P0, dt = None, G = None): 

    if not isinstance(X, dict):
      raise TypeError('X must be a dictionary containig pairs of variables and initial conditions, e.g.: {''x'': 0, ''y'': 0}')
    super().__init__(**X)

    self.dt = dt
    if self.dt is None:
      c4d.cprint(f'dt is not provided. '
                    'dt can be provided once when constructing the filter '
                      'or on every call to predict()', 'y')

    self.G = G
    
    P0 = np.atleast_2d(P0)
    if P0.shape[0] == P0.shape[1]:
      # square matrix
      self.P = P0
    else:
      # only standard deviations are provided 
      self.P = np.diag(P0.flatten()**2)
      
    self._Pdata = [] 

    self.F = None   


  def predict(self, F, Qk, fx = None, dt = None, u = None):
    '''
    Predicts the next state and covariance based on the given parameters.
    
    Parameters
    ----------

    F : numpy.ndarray
        State transition matrix.
    Qk : numpy.ndarray
        Process noise covariance matrix.
    fx : numpy.ndarray, optional
        State transition function. Defaults to None.
    dt : float, optional
        Time step. Defaults to None.
    u : numpy.ndarray, optional
        Control input. Defaults to None.
    
    Raises
    ------
    AttributeError
        If dt is not provided.

    Example
    -------
    TODO complete

    '''
    # TODO test the size of the objects. test the type. make sure the user is working with c4d modules. 
    
    if dt is not None: 
      self.dt = dt 
    elif self.dt is None: 
      raise AttributeError(f'dt is not provided. '
                              'dt can be provided once when constructing the filter '
                                'or on every call to predict().')

    self.F = np.atleast_2d(F) 
    Qk = np.atleast_2d(Qk) 

    # covariance matrix propagation 
    self.P = self.F @ self.P @ self.F.T + Qk 

    # state vector propagation 
    if fx is not None:
      Fxdt = self.X + np.array(fx) * self.dt 
    else:
      #      (I + A*dt)*x = x + A*x*dt  
      Fxdt = self.F @ self.X  
              
    self.X = Fxdt

    if u is not None and self.G is not None:
        self.X += self.G.reshape(self.X.shape) * u * self.dt
    
  
 
  def update(self, z, H, Rk, hx = None): 
    '''
    Updates the state estimate based on the given measurements.
        

    Parameters
    ----------
    z : numpy.ndarray
        Measurement vector.
    H : numpy.ndarray
        Measurement matrix.
    Rk : numpy.ndarray
        Measurement noise covariance matrix.
    hx : numpy.ndarray, optional
        Measurement prediction function. Defaults to None.
        
    Raises
    ------
    ValueError
        If predict() has not been called before update().
    ValueError
        If the size of hx does not match the size of z.

    
    '''

    if self.F is None: 
      raise ValueError('update() must be preceded by predict()') 

    Rk = np.atleast_2d(Rk)

    H = np.atleast_2d(H) 
    # H is mxn where m measure number. 
    # the H.shape[0] = len(z)
    if hx is None:
      hx = H @ self.X 
    hx = np.atleast_1d(hx)    

    z = np.atleast_1d(z)

    if np.size(hx) != np.size(z):
      raise ValueError(f'Number of measure variables in z must match the shape[0] of H or len(hx)')

    
    K = self.P @ H.T @ np.linalg.inv(H @ self.P @ H.T + Rk)
    self.P = self.P - K @ H @ self.P


    self.X += K @ (z - hx)

    self.F = None






  def store(self, t = -1):
    '''
    Stores the current state and diagonal elements of the covariance matrix.
        
    Parameters
    ----------

    t : int, optional
        Time step for storing the state. Defaults to -1.
    
    '''
    # state 
    super().store(t) # store state 
    # store covariance: 
    for i, p in enumerate(np.diag(self.P)): 
      pstr = f'P{i}{i}'
      setattr(self, pstr, p) # set 
      self.storeparams(pstr, t) # store 
    





