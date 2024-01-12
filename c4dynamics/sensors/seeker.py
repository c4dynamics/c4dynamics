import numpy as np
import c4dynamics as c4d 

class seeker(c4d.rigidbody):

  
  _scale_factor = 1.0
  ''' float; The scale factor error of the seeker angels. 
  It is a normally distributed random variable with
  standard deviation scale_factor_std.
  When isideal seeker is configured scale_factor = 1. 
  '''

  scale_factor_std = 0.05  
  ''' float; A standard deviation of the scale factor error ''' 


  _bias = 0.0
  ''' float; The bias error of the seeker angels. 
  It is a normally distributed random variable with
  standard deviation bias_std
  When isideal seeker is configured bias = 0. 
  '''

  bias_std = 0.1 * c4d.d2r 
  ''' float; A standard deviation of the bias error. Defaults 0.1deg '''  
  
  noise_std = 0.4 * c4d.d2r 
  ''' float; A standard deviation of the seeker angular noise. Default value for nonideal 
  seeker: noise_std = 0.4 deg '''

  # dt = 50e-3
  # ''' float; The time-constant of the operational rate of the seeker '''
  
  # 

  def __init__(self, origin = None, isideal = False, **kwargs):
    # A flag indicating whether to run the errors model 

    # Initializes the Seeker object.

    # Args:
    #     isideal (bool): A flag indicating whether to run the errors model.

    # TODO
    # 1 limit field of view. 
    # 2 add range errors.
    # 3 add time-const operation  

    self.__dict__.update(kwargs)
    super().__init__()

    self.measure_data = []

    self.az = 0
    self.el = 0
    self.range = 0

    if origin is not None: 
      self.X = origin.X 


    if isideal:
      self.noise_std = 0
    else: 
      self._errors_model()
    


  @property
  def bias(self):
    ''' 
    Gets or sets seeker's bias.


    `bias` gets or sets the bias parameter of the seeker. 
    
    Normally, the bias is a random variable generated at the stage of constructing the 
    seeker instance:
    
    .. math::

      bias = bias.std \\cdot randn

    The `bias.std` has a default value of `0.1deg` and it can 
    be set by the **kwargs at the stage of constructing the seeker instance:
    
    .. code::

      skr = c4d.sensors.seeker(bias_std = 0.5 * c4d.d2r) # d2r = degrees to radians

    Calling `bias` returns the generated variable.    
    Calling `bias` with a parameter overrides 
    the random generated variable with the user input. 

    
    Parameters (Setter)
    -------------------

    bias : float 
        The required bias for the seeker. 

        
    Returns (Getter)
    ----------------
    
    bias : float 
        The current bias of the seeker. 

    Example
    -------

    .. code::

      >>> from c4dynamics.sensors import seeker
      >>> radars_type_A = []
      >>> radars_type_B = []
      >>> B_std = 0.5 * c4d.d2r
      >>> for i in range(1000):
      ...   radars_type_A.append(seeker().bias * c4d.r2d)
      ...   radars_type_B.append(seeker(bias_std = B_std).bias * c4d.r2d)
      >>> plt.hist(radars_type_B, color = 'cyan', bins = 30, edgecolor = 'black', label = 'Type B') #, alpha=0.1, label='Histogram 2')
      >>> plt.hist(radars_type_A, color = 'magenta', bins = 30, edgecolor = 'black', label = 'Type A')  

    .. figure:: /_static/figures/seeker_bias.png

       
    '''
    return self._bias


  @bias.setter
  def bias(self, bias):
    '''
    bias setter.
    '''
    self.bias = bias 


  @property
  def scale_factor(self):
    ''' 
    Gets or sets seeker's scale_factor.

    `scale_factor` gets or sets the scale facotr 
    parameter of the seeker. 
    
    Normally, the scale_factor is a random variable generated at the stage of 
    constructing the seeker instance:
    
    .. math::
    
      scalefactor = scalefactor.std \\cdot randn

    The `scalefactor.std` has a default value of 0.05 and it can 
    be set by the **kwargs at the stage of constructing the seeker instance:

    .. code::

      skr = c4d.sensors.seeker(scale_factor_std = 0)

    Calling `scale_factor` 
    returns the generated variable.    
    Calling `scale_factor` with a parameter overrides 
    the random generated variable with the user input. 

    
    Parameters (Setter)
    -------------------

    scale_factor : float 
        The required scalefactor for the seeker. 


    Returns (Getter)
    ----------------

    scale_factor : float 
      The current scalefactor of the seeker. 


    Example
    -------

    .. code::

      >>> from c4dynamics.sensors import seeker
      >>> dt = .01
      >>> time = np.arange(0, 30, dt)
      >>> tgt = c4d.datapoint(x = 1000, y = 0, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
      >>> seeker_sf = 1.2
      >>> skr = seeker(bias_std = 0, noise_std = 0)
      >>> skr.scale_factor = seeker_sf
      >>> for t in time:
      ...   tgt.inteqm(np.zeros(3), dt)
      ...   skr.measure(tgt, store = True, t = t)  
      ...   tgt.store(t)
      >>> plt.plot(tgt.get_data('t'), c4d.atan(tgt.get_data('y') / tgt.get_data('x')) * c4d.r2d, 'm', label = 'target')
      >>> plt.plot(tgt.get_data('t'), skr.get_data('az')[:, 1] *  c4d.r2d, 'c', label = 'seeker')

    .. figure:: /_static/figures/seeker_sf.png

                
    '''
    return self._scale_factor


  @scale_factor.setter
  def scale_factor(self, scale_factor):
    ''' scale_factor setter '''
    self._scale_factor = scale_factor 



  def measure(self, tgt, store = False, t = -1):
    '''
    Measures range, azimuth, and elevation between the seeker and a target.
    If `store = True`, stores the measured azimuth and elevation along with a timestamp.
    If timestamp is provided, joins it to the stored measures, otherwise, joins `t = -1`.


    Parameters
    ----------
    tgt : datapoint
        A datapoint object detected by the radar.
    store : boolen, optional
        A flag indicating whether to store the measured values. Defaults `False`.
    t : float, optional
        Timestamp. Defaults -1 if not provided.

    Returns
    -------
    out : tuple
        Range, azimuth, and elevation
    
        
    Example
    -------

    .. code:: 

      >>> from c4dynamics.sensors import seeker
      >>> dt = .01
      >>> time = np.arange(0, 30, dt)
      >>> tgt = c4d.datapoint(x = 1000, y = 0, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
      >>> skr = seeker()
      >>> for t in time:
      ...     tgt.inteqm(np.zeros(3), dt)
      ...     skr.measure(tgt, store = True, t = t)  
      ...     tgt.store(t)
      >>> plt.plot(tgt.get_data('t'), skr.get_data('az')[:, 1] *  c4d.r2d, 'c', label = 'seeker')
      >>> plt.plot(tgt.get_data('t'), c4d.atan(tgt.get_data('y') / tgt.get_data('x')) * c4d.r2d, 'm', label = 'target')

    .. figure:: /_static/figures/seeker_measure.png
    

    '''

    # self: The rigid body object on which the seeker is installed
    # tgt: A datapoint object detected by the radar 
    
    # target-radar position in inertial coordinates 
    self.range = self.dist(tgt)
    
    # target-radar position in radar-body coordinates
    x = tgt.X[:3] - self.X[:3] 
    x_body = self.BI @ x 

    # extract angles:
    az_true = c4d.atan2(x_body[1], x_body[0])
    el_true = c4d.atan2(x_body[2], c4d.sqrt(x_body[0]**2 + x_body[1]**2))


    self.az = az_true * self._scale_factor + self._bias + self.noise_std * np.random.randn()  
    self.el = el_true * self._scale_factor + self._bias + self.noise_std * np.random.randn() 

    if store: 
        self.storevar(['az', 'el', 'range'], t = t)

    return self.az, self.el, self.range

    


  def _errors_model(self):
    ''' 
    measured_angle = true_angle * scale_factor + bias + noise

    Applies the errors model to azimuth and elevation angles.
    Updates the scale factor, bias, and calculates noise.
    '''
    self._scale_factor = 1 + self.scale_factor_std * np.random.randn()
    self._bias = self.bias_std * np.random.randn()
    
    
