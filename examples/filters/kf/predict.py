from scipy.linalg import solve_discrete_are
from typing import Dict, Optional
import sys 
sys.path.append('.')
import c4dynamics as c4d 
import numpy as np
import warnings 


def _noncontwarning(x): 
  warnings.warn(f"""The system is not continuous."""
                  f"""\nDid you mean {x}?""" 
                    , c4d.c4warn)


class kalman(c4d.state):

  Kinf = None 


  def __init__(self, X: dict, dt: Optional[float] = None, P0: Optional[np.ndarray] = None, steadystate: bool = False
                , A: Optional[np.ndarray] = None, B: Optional[np.ndarray] = None, C: Optional[np.ndarray] = None
                  , Q: Optional[np.ndarray] = None, R: Optional[np.ndarray] = None
                    , F: Optional[np.ndarray] = None, G: Optional[np.ndarray] = None, H: Optional[np.ndarray] = None 
                      , Qk: Optional[np.ndarray] = None, Rk: Optional[np.ndarray] = None):



    if not isinstance(X, dict):
      raise TypeError("""X must be a dictionary containig pairs of variables 
                          and initial conditions, e.g.: {''x'': 0, ''y'': 0}""")
    super().__init__(**X)


    # initialize cont or discrete system 
    self.isdiscrete = True 
    self.G = None 
    if A is not None and C is not None:
      # continuous system 
      # 
      self.isdiscrete = False  
      if dt is None:
        raise ValueError("""dt is necessary for a continuous system""")

      self.dt = dt
      #         
      self.F  = np.eye(len(A)) + A * dt 
      self.H  = np.atleast_2d(C) 
      if B is not None: 
        self.G = np.atleast_2d(B) * dt 
      if Q is not None:
        self.Qk = np.atleast_2d(Q) * dt 
      if R is not None:
        self.Rk = np.atleast_2d(R) / dt 

    elif F is not None and H is not None:
      # discrete
      self.F  = np.atleast_2d(F) 
      self.H  = np.atleast_2d(H) 
      if G is not None: 
        self.G = np.atleast_2d(G) 
      if Qk is not None:
        self.Qk = np.atleast_2d(Qk)  
      if Rk is not None:
        self.Rk = np.atleast_2d(Rk)  

    else: 
      raise ValueError("""At least one set of matrices has to be entirely provided:                           
                          \nFor a continuous system: A, C (B is optional). 
                          \nWhere: x'' = A*x + B*u + w, y = C*x + v, E(w*w^T) = Q*delta(t), E(v*v^T) = Q*delta(t). 
                            \nFor a dicscrete system: F, H (G is optional). 
                            \nWhere: x(k) = F*x(k-1) + G*u(k-1) + wk, y(k) = H*x(k), E(wk*wk^T) = Qk*delta(k), E(vk*vk^T) = Rk * delta(k)""")
      
    
    if steadystate: 
      # in steady state mode Q and R or Qk and Rk must be provided: 
      if self.Qk is None or self.Rk is None:
        raise ValueError("""In steady-state mode at least one set of noise matrices must be entirely provided:"""
                          """\nFor a continuous system: Q, R. """
                            """\nWhere: x'' = A*x + B*u + w, y = C*x + v, E(w*w^T) = Q*delta(t), E(v*v^T) = Q*delta(t). """
                              """\nFor a dicscrete system: Qk, Rk.""" 
                                """\nWhere: x(k) = F*x(k-1) + G*u(k-1) + wk, y(k) = H*x(k), E(wk*wk^T) = Qk*delta(k), E(vk*vk^T) = Rk * delta(k)""")

      self.P = solve_discrete_are(self.F.T, self.H.T, self.Qk, self.Rk)
      self.Kinf = self.P @ self.H.T @ np.linalg.inv(self.H @ self.P @ self.H.T + self.Rk)

    else: # steady state is off 
      if P0 is None: 
        raise ValueError(r'P0 is a necessary variable (optional only in steadystate mode)')

      P0 = np.atleast_2d(P0)      

      if P0.shape[0] == P0.shape[1]:  
        # square matrix
        self.P = P0
      else:
        # only standard deviations are provided 
        # self.P = np.diag(P0.flatten()**2)
        self.P = np.diag(P0.ravel()**2)

    self._Pdata = []   



  @property
  def A(self):
    if self.isdiscrete: 
      _noncontwarning('F')
      return None
    
    a = (self.F - np.eye(len(self.F))) / self.dt 
    return a 

  @A.setter
  def A(self, a):
    if self.isdiscrete: 
      _noncontwarning('F') 
    else: 
      self.F = np.eye(len(a)) + a * self.dt 


  @property 
  def B(self):
    if self.isdiscrete: 
      _noncontwarning('G')
      return None 
    return self.G / self.dt 
  
  @B.setter
  def B(self, b):
    if self.isdiscrete: 
      _noncontwarning('G')
    else: 
      self.G = b * self.dt 


  @property 
  def C(self):
    if self.isdiscrete: 
      _noncontwarning('H')
      return None 
    return self.H 
  
  @C.setter
  def C(self, c):
    if self.isdiscrete: 
      _noncontwarning('H')
    else: 
      self.H = c


  @property 
  def Q(self):
    if self.isdiscrete: 
      _noncontwarning('Qk')
      return None 
    return self.Qk / self.dt
  
  @Q.setter
  def Q(self, q):
    if self.isdiscrete: 
      _noncontwarning('Qk')
    else: 
      self.Qk = q * self.dt 


  @property 
  def R(self):
    if self.isdiscrete: 
      _noncontwarning('Rk')
      return None 
    return self.Rk * self.dt 
  
  @R.setter
  def R(self, r):
    if self.isdiscrete: 
      _noncontwarning('Rk')
    else: 
      self.Rk = r / self.dt 


  # def predict(self, u = None):
  def predict(self, u: Optional[np.ndarray] = None
                , Q: Optional[np.ndarray] = None, Qk: Optional[np.ndarray] = None):
  

    if self.Kinf is None:

      if Q is not None: 
        self.Qk = np.atleast_2d(Q) * self.dt
      elif Qk is not None: 
        self.Qk = np.atleast_2d(Qk)
      elif self.Qk is None: 
        raise ValueError(r'Q or Qk must be provided in every call to predict() (optional only in steadystate mode)')

      self.P = self.F @ self.P @ self.F.T + self.Qk 
      # self.P = self.F @ self.P @ self.F.T + self.Q
         
    # this F can be either linear or nonlinear function of x. 
    # print(f'{x=}')
    self.X = self.F @ self.X 
    # print(f'{x=}')

    if u is not None:
      if self.G is None:
        # c4d.cprint(f"""Warning: u={u} is introduced as control input but the input matrix 
        #                   is zero! (G for discrete system or B for continuous)""", 'r')

        warnings.warn(f"""\nWarning: u={u} is introduced as control input but the input matrix is zero! (G for discrete system or B for continuous).""" 
                      , c4d.c4warn)
              
      else: 
        
        if len(u.ravel()) != self.G.shape[1]:
          raise ValueError(f"""The number of elements in u must equal the number of columns of the input matrix (B or G), {len(u.ravel())} != {self.G.shape[1]}""")
        self.X += self.G @ u.ravel() 

    
 
  def update(self, z: np.ndarray
                , R: Optional[np.ndarray] = None, Rk: Optional[np.ndarray] = None):

    if len(z.ravel()) != self.H.shape[0]:
      raise ValueError(f"""The number of elements in z must equal 
                          the number of roww=s of the measurement matrix (C or H), 
                              {len(z.ravel())} != {self.H.shape[0]}""")
    
    if self.Kinf is None:
      if R is not None: 
        self.Rk = np.atleast_2d(R) / self.dt
      elif Rk is not None: 
        self.Rk = np.atleast_2d(Rk)
      elif self.Rk is None: 
        raise ValueError(r'R or Rk must be provided in every call to update() (optional only in steadystate mode)')

      K = self.P @ self.H.T @ np.linalg.inv(self.H @ self.P @ self.H.T + self.Rk)
      self.P = self.P - K @ self.H @ self.P
    else: 
      K = self.Kinf



    # this H can be expressed as either linear or nonlinear function of x.  
    # print(f'\n correct \n')
    # print(f'{x=} {K=} {z=} {hx=}')
    self.X += K @ (z.ravel() - self.H @ self.X)
    
    




  # def store(self, t = -1):
  def store(self, t: int = -1):

    super().store(t) # store state 
    # store covariance: 
    for i, p in enumerate(np.diag(self.P)): 
      pstr = f'P{i}{i}'
      setattr(self, pstr, p) # set 
      self.storeparams(pstr, t) # store 
    



  @staticmethod
  # def velocitymodel(dt, process_noise, measure_noise):  
  def velocitymodel(dt: float, process_noise: float, measure_noise: float):

    '''
      Defines a linear Kalman filter model for tracking position and velocity.

      Parameters
      ----------
      dt : float
          Time step for the system model.
      process_noise : float
          Standard deviation of the process noise.
      measure_noise : float
          Standard deviation of the measurement noise.

      Returns
      -------
      kf : kalman
          A Kalman filter object initialized with the linear system model.

          

      X = [x, y, w, h, vx, vy]
      #    0  1  2  3  4   5  

      x'  = vx
      y'  = vy
      w'  = 0
      h'  = 0
      vx' = 0
      vy' = 0

      H = [1 0 0 0 0 0
          0 1 0 0 0 0
          0 0 1 0 0 0
          0 0 0 1 0 0]
    '''
    from scipy.linalg import expm 

    A = np.zeros((6, 6))
    A[0, 4] = A[1, 5] = 1
    F = expm(A * dt)
    H = np.zeros((4, 6))
    H[0, 0] = H[1, 1] = H[2, 2] = H[3, 3] = 1

    Qk = np.eye(6) * process_noise**2
    Rk = np.eye(4) * measure_noise**2

    Q = np.eye(6) * process_noise**2
    R = np.eye(4) * measure_noise**2

    # kf = kalman({'x': 0, 'y': 0, 'w': 0, 'h': 0, 'vx': 0, 'vy': 0}
    #                   , steadystate = True, A = A, C = H, Q = Q, R = R, dt = dt)
    kf = kalman({'x': 0, 'y': 0, 'w': 0, 'h': 0, 'vx': 0, 'vy': 0}
                          , steadystate = True, F = F, H = H, Qk = Qk, Rk = Rk)
    return kf 







if __name__ == "__main__":
  import contextlib
  import doctest

  # Redirect both stdout and stderr to a file within this block
  with open('output.txt', 'w') as f:
    with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
      doctest.testmod()
 



