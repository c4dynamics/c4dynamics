import numpy as np
import c4dynamics as c4d 


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

  
  
 
    
  where: 
  - \\tau is the time constant of the filter.

  '''

  
  def __init__(self, alpha = None, dt = None, tau = None, y0 = 0):     

    if dt is not None and tau is not None: 
      self.alpha = dt / tau 

    elif alpha is not None:
      self.alpha = alpha

    else: 
      raise ValueError('At least one set has to be provided: ' 
                         '\nFor a continuous system: tau and dt. where: y'' = -y/tau + x/tau '
                         '\nFor a dicscrete system: alpha. where y[k] = (1 - alpha)*y[k-1] + alpha*x[k] '
                          )

    self.y = y0 
    

  
  def sample(self, x):

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



