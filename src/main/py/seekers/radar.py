import numpy as np

import c4dynamics as c4d 

# np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)                 

class dzradar:
  """ 
    an electromagnetic radar 
    meausres target vertical position.
    vk: noise variance  
  """
  
  # 
  # state vector
  #   r position (in one dimension range)
  #   v velocity 
  #   b ballistic coefficient 
  ##
  r = 0 # measured range 
  # vx = 0 # velocity 
  
  
  ts = 0 # 50e-3                        # sample time 
  q33 = 0
  data = np.array([[0, 0, 0, 0]])   # time, z target, v target, beta target 
  
  # luenberger gains 
  L = 0
  
  # 
  # seeker errors 
  ##
  bias = 0 # deg
  sf = 1 # scale factor error -10%
  noise = np.sqrt(500 * c4d.params.ft2m) # 1 sigma 
  # misalignment = 0.01 # deg

  def __init__(obj, x0, filtype, ts):
      '''
       initial estimate: 
       100025 ft    25ft error
       6150 ft/s    150ft/s error
       800 lb/ft^2  300lb/ft^2 
      '''
      obj.ts = ts
      if filtype == c4d.filters.filtertype.ex_kalman:
        obj.ifilter = c4d.filters.e_kalman(x0
                                           , [obj.noise
                                              , 141.42 * c4d.params.ft2m
                                              , 300 * c4d.params.lbft2kgm]
                                           , obj.ts)
      elif filtype == c4d.filters.filtertype.luenberger:
        # linear model
        beta0 = x0[2]
        A = np.array([[0, 1, 0], [0, -np.sqrt(2 * 0.0034 * c4d.params.g / beta0)
                                  , -c4d.params.g / beta0], [0, 0, 0]])
        b = np.array([[0], [0], [0]])
        c = np.array([1, 0, 0])
        obj.ifilter = c4d.filters.luenberger(A, b, c)
      elif filtype == c4d.filters.filtertype.lowpass:
        obj.ifilter = c4d.filters.lowpass(.2, obj.ts, x0)
      else:
        print('filter type error')
      
      obj.data[0, :] =  np.insert(x0, 0, 0)  
      
      
  def measure(obj, x):
    # 
    # apply errors
    ##
    obj.r = x * obj.sf + obj.bias + obj.noise * np.random.randn(1) 
  
      
  def filter(obj, t):
    
    # check that t is at time of operation 
    
    
    if (1000 * t) % (1000 * obj.ts) > 1e-6 or t <= 0:
      return
    
    
    # print(t)
    rho = .0034 * np.exp(-obj.ifilter.x[0, 0] / 22000 / c4d.params.ft2m)
    f21 = -rho * c4d.params.g * obj.ifilter.x[1, 0]**2 / 44000 / obj.ifilter.x[2, 0] 
    f22 =  rho * c4d.params.g * obj.ifilter.x[1, 0] / obj.ifilter.x[2, 0]
    f23 = -rho * c4d.params.g * obj.ifilter.x[1, 0]**2 / 2 / obj.ifilter.x[2, 0]**2 
    
    Phi = np.array([[1, obj.ifilter.tau, 0], 
                    [f21 * obj.ifilter.tau, 1 + f22 * obj.ifilter.tau, f23 * obj.ifilter.tau], 
                    [0, 0, 1]])
    
    Q   = np.array([[0, 0, 0], 
                    [0, obj.q33 * f23**2 * obj.ifilter.tau**3 / 3, obj.q33 * f23 * obj.ifilter.tau**2 / 2], 
                    [0, obj.q33 * f23 * obj.ifilter.tau**2 / 2, obj.q33 * obj.ifilter.tau]])

    f = lambda w: c4d.seekers.dzradar.system_model(w)

    #
    # prepare luenberger matrices
    ##

    ''' predict '''
    obj.ifilter.predict(f, Phi, Q)
    ''' correct '''    
    x = obj.ifilter.update(f, obj.r)  
 
    obj.r = x[0]
    #
    # store results 
    ##
 
    # obj.data = np.concatenate((obj.data, np.expand_dims(np.insert(x, 0, t), axis = 0)), axis = 0)  
    obj.data = np.vstack((obj.data, np.insert(x, 0, t))).copy()
    
    return obj.r

    

  @staticmethod
  def system_model(x):
    dx = np.zeros((len(x), 1))
    dx[0, 0] = x[1, 0]
    dx[1, 0] = .0034 * np.exp(-x[0, 0].astype('float') / 22000 / c4d.params.ft2m) * c4d.params.g * x[1, 0]**2 / 2 / x[2, 0] - c4d.params.g
    dx[2, 0] = 0
    return dx

 
class radar:
  # direction radar 
  
  noisestd = 0
  bias = 0
  sf = 1
  
  def __init__(obj, **kwargs):
    obj.__dict__.update(kwargs)
  
  def measure(obj, x):
    return x * obj.sf + obj.bias + obj.noisestd * np.random.randn()
  
  