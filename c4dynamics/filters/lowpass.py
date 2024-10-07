import numpy as np
import c4dynamics as c4d 
from typing import Optional


class lowpass(c4d.state):
  ''' 
    First-order lowpass filter

    
    Parameters
    ==========
    TODO complete 

    
    See Also
    ========
    .filters
    .kalman  
    .ekf 
    .seeker 
    .eqm 


    Example
    =======
    TODO complete

    
    A first-order lowpass filter is defined by:

    .. math:: 
    
      \\dot{y}(t) = -{1 \\over \\tau} \\cdot y(t) + {1 \\over \\tau} \\cdot x(t) 

    in the continuous-time domain, and by:

    .. math:: 
    
      y_k = \\alpha \\cdot x_k + (1 - \\alpha) \\cdot y_{k-1}

    in the discrete-time domain. 

    The differential equation of the continuous-time filter 
    can be Euler-integrated with time constant :math:`dt` as:

    .. math::

      y = y + dt \\cdot (-{1 \\over \\tau} \\cdot y + {1 \\over \\tau} \\cdot x)


    We can denote:

    .. math::

      \\alpha = {dt \\over \\tau}

    
    
  
      
    Where: 
    
    - \\tau is the time constant of the filter.

  '''

  
  # def __init__(self, alpha = None, dt = None, tau = None, y0 = 0):     
  def __init__(self, alpha: Optional[float] = None, dt: Optional[float] = None, tau: Optional[float] = None, y0: float = 0) -> None:
    '''
      Initializes the filter with either continuous or discrete system parameters.

      Parameters
      ----------
      alpha : float, optional
          Smoothing factor for a discrete system. Defaults to None.
      dt : float, optional
          Time step for a continuous system. Defaults to None.
      tau : float, optional
          Time constant for a continuous system. Defaults to None.
      y0 : float, optional
          Initial value for the state. Defaults to 0.

      Raises
      ------
      ValueError
          If neither `alpha` nor both `dt` and `tau` are provided.

      Notes
      -----
      - For a continuous system, `tau` and `dt` are required, and `alpha` is computed as `dt / tau`.
      - For a discrete system, `alpha` is required, and it directly specifies the smoothing factor.
      - If no valid combination of parameters is provided, a `ValueError` is raised.

      Example
      -------
      # Continuous system example
      >>> filter = SomeFilterClass(dt=0.1, tau=5)
      
      # Discrete system example
      >>> filter = SomeFilterClass(alpha=0.1)
    '''

    if dt is not None and tau is not None: 
      self.alpha = dt / tau 

    elif alpha is not None:
      self.alpha = alpha

    else: 
      raise ValueError('At least one set has to be provided: ' 
                         '\nFor a continuous system: tau and dt. Where: y'' = -y/tau + x/tau '
                         '\nFor a dicscrete system: alpha. where y[k] = (1 - alpha)*y[k-1] + alpha*x[k] '
                          )

    self.y = y0 
    

  
  # def sample(self, x):
  def sample(self, x: float) -> float:
    '''
      Applies the low-pass filter to the input value and returns the filtered output.

      Parameters
      ----------
      x : float
          Input value to be filtered.

      Returns
      -------
      float
          The filtered output value.

      Notes
      -----
      - **Continuous System**: Uses the equation `y'(t) = -y(t) / tau + x(t) / tau`.
      - **Discrete System**: Uses the equation `y[k] = (1 - alpha) * y[k-1] + alpha * x[k]`.
      - The filter's state `self.y` is updated in place based on the filter type.

      Example
      -------
      >>> lpf = SomeFilterClass(alpha=0.1)
      >>> output = lpf.sample(10)
      >>> print(output)
      1.0  # Example output, the actual value depends on the filter's state and parameters.
    '''

    # ''' 
    # sample 

    #       ---------
    # x --->|  LPF  |---> y
    #       ---------

    # continuous:     y'(t) = -y(t) / tau + x(t) / tau
    # discrete:       y[k]  = (1 - alpha) * y[k-1] + alpha * x[k] 

    # '''    

    self.y = (1 - self.alpha) * self.y + self.alpha * x 
    
    return self.y 



