import os 
import numpy as np
import c4dynamics as c4d 
from numpy.typing import NDArray
from typing import Any
import warnings 

class state:
  ''' 
  Custom state object. 

  A state object represents a state vector and other attributes 
  that form an entity of a physical (dynamic) system.    
  
  A custom state object means any set of state variables is possible, 
  while pre-defined states from the :mod:`state library<c4dynamics.states.lib>` 
  are ready to use out of the box. 

  Keyword Arguments 
  =================

  **kwargs : float or int  
      Keyword arguments representing the variables and their initial conditions.
      Each key is a variable name and each value is its initial condition.
      For example: :code:`s = c4d.state(x = 0, theta = 3.14)`


  See Also
  ========
  .states

  
  Examples
  ======== 

  
  ``Pendulum``

  .. code::
  
    >>> s = c4d.state(theta = 10 * c4d.d2r, omega = 0)
    [ θ  ω ]

  ``Strapdown navigation system`` 
  
  .. code::
  
    >>> s = c4d.state(x = 0, y = 0, z = 0, vx = 0, vy = 0, vz = 0, q0 = 0, q1 = 0, q2 = 0, q3 = 0, bax = 0, bay = 0, baz = 0)
    [ x  y  z  vx  vy  vz  q0  q1  q2  q3  bax  bay  baz ]
  
  ``Objects tracker`` 

  .. code::
  
    >>> s = c4d.state(x = 960, y = 540, w = 20, h = 10)
    [ x  y  w  h ]
    
  ``Aircraft``

  .. code::
  
    >>> s = c4d.state(x = 0, y = 0, z = 0, vx = 0, vy = 0, vz = 0, phi = 0, theta = 0, psi = 0, p = 0, q = 0, r = 0)
    [ x  y  z  vx  vy  vz  φ  θ  Ψ  p  q  r ]
  
  ``Self-driving car``

  .. code::
  
    >>> s = c4d.state(x = 0, y = 0, v = 0, theta = 0, omega = 0)
    [ x  y  v  θ  ω ]

  ``Robot arm``

  .. code::
  
    >>> s = c4d.state(theta1 = 0, theta2 = 0, omega1 = 0, omega2 = 0)
    [ θ1  θ2  ω1  ω2 ]

    
  '''


  # Α α # Β β # Γ γ # Δ δ # Ε ε # Ζ ζ # Η η # Θ θ # Ι ι 
  # Κ κ # Λ λ # Μ μ # Ν ν # Ξ ξ # Ο ο # Π π # Ρ ρ # Σ σ/ς
  # Τ τ # Υ υ # Φ φ # Χ χ # Ψ ψ # Ω ω
  _greek_unicode = (
    ('alpha', '\u03B1'), ('beta', '\u03B2'), ('gamma', '\u03B3'), ('delta', '\u03B4'),
      ('epsilon', '\u03B5'), ('zeta', '\u03B6'), ('eta', '\u03B7'), ('theta', '\u03B8'),
        ('iota', '\u03B9'), ('kappa', '\u03BA'), ('lambda', '\u03BB'), ('mu', '\u03BC'),
          ('nu', '\u03BD'), ('xi', '\u03BE'), ('omicron', '\u03BF'), ('pi', '\u03C0'),
            ('rho', '\u03C1'), ('sigma', '\u03C3'), ('final_sigma', '\u03C2'), ('tau', '\u03C4'),
              ('upsilon', '\u03C5'), ('phi', '\u03C6'), ('chi', '\u03C7'), ('psi', '\u03C8'),
    ('omega', '\u03C9'), ('Alpha', '\u0391'), ('Beta', '\u0392'), ('Gamma', '\u0393'),
      ('Delta', '\u0394'), ('Epsilon', '\u0395'), ('Zeta', '\u0396'), ('Eta', '\u0397'),
        ('Theta', '\u0398'), ('Iota', '\u0399'), ('Kappa', '\u039A'), ('Lambda', '\u039B'),
          ('Mu', '\u039C'), ('Nu', '\u039D'), ('Xi', '\u039E'), ('Omicron', '\u039F'),
            ('Pi', '\u03A0'), ('Rho', '\u03A1'), ('Sigma', '\u03A3'), ('Tau', '\u03A4'),
              ('Upsilon', '\u03A5'), ('Phi', '\u03A6'), ('Chi', '\u03A7'), ('Psi', '\u03A8'), ('Omega', '\u03A9'))
    # 


  def __init__(self, **kwargs):    
    # TODO allow providing type for the setter.X output.      

    # the problem with this is it cannot be used with seeker and other c4d objects
    # that takes datapoint objects.
    # beacuse sometimes it misses attributes such as y, z that are necessary for poistion etc
    
    # alternatives:

    # 1. all the attributes always exist but they are muted and most importantly not reflected
    #   in the state vector when doing dp.X

    # 2. they will not be used in this fucntions. 

    # 3. the user must provide his implementations for poisiton velcity etc.. like used in the P() function that there i 
    #   encountered the problem.

    # 4. 




    self._data = []    # for permanent class variables (t, x, y .. )
    self._prmdata = {} # for user additional variables 

    self._didx = {'t': 0}

    for i, (k, v) in enumerate(kwargs.items()):
      setattr(self, k, v)
      setattr(self, k + '0', v)
      self._didx[k] = 1 + i


  def __str__(self):
    

    self_str = '[ '
    for i, s in enumerate(self._didx.keys()):
      if s == 't': continue
      s = dict(self._greek_unicode).get(s, s) 
      if i < len(self._didx.keys()) - 1:
        self_str += s + '  '
      else:
        self_str += s + ' ]'

    return self_str
  



  #
  # state operations
  ## 


  @property
  def X(self) -> NDArray[Any]:
    '''
    Gets and sets the state vector variables.

        
    Parameters
    ----------
    x : array_like 
        Values vector to set the variables of the state. 
        
    Returns
    -------
    out : numpy.array
        Values vector of the state.

    

    Examples
    --------

    Getter:

    .. code:: 
    
      >>> s = c4d.state(x1 = 0, x2 = -1)
      >>> s.X
      [0  -1]


    Setter:

    .. code:: 
    
      >>> s = c4d.state(x1 = 0, x2 = -1)
      >>> s.X += [0, 1] # equivalent to: s.X = s.X + [0, 1]
      >>> s.X
      [0  0]


    :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` getter - setter: 

    .. code:: 
    
      >>> dp = c4d.datapoint()
      >>> dp.X
      [0  0  0  0  0  0]
      >>> #       x     y    z  vx vy vz 
      >>> dp.X = [1000, 100, 0, 0, 0, -100] 
      >>> dp.X
      [1000  100  0  0  0  -100]
    

    '''


    xout = [] 

    for k in self._didx.keys():
      if k == 't': continue
      # the alteast_1d() + the flatten() is necessary to 
      # cope with non-homogenuous array 
      xout.append(np.atleast_1d(eval('self.' + k)))

    # return np.array(xout).flatten().astype(np.float64) # XXX why float64? maybe it's just some default unlsess anything else required. 
    return np.array(xout).ravel().astype(np.float64) # XXX why float64? maybe it's just some default unlsess anything else required. 

  @X.setter
  def X(self, x):
    # x = np.atleast_1d(x).flatten()
    # i think to replace flatten() with ravel() is 
    # safe also here because x is iterated over its elements which are
    # mutable. but lets XXX it to keep tracking. 
    x = np.atleast_1d(x).ravel()

    xlen = len(x)
    Xlen = len(self.X)

    if xlen < Xlen:
      # NOTE maybe it's too dangerous to allow partial vector here and
      # the test must verify the exact length 
      # another reason to not do partial assignment is that the operation:
      # s.X = 3 may be interpreted as fixing a state with constant values like s.X = s.X * 0 + 3
      # the problem is i think dp makes use of it. 
      # c4d.cprint(f'Warning: partial vector assignment, len(x) = {xlen}, len(X) = {Xlen}', 'r')
      raise ValueError(f'Partial vector assignment, len(x) = {xlen}, len(X) = {Xlen}', 'r')

    elif xlen > Xlen:
      raise ValueError(f'The length of the input state is bigger than X, len(x) = {xlen}, len(X) = {Xlen}')

    for i, k in enumerate(self._didx.keys()):
      if k == 't': continue
      if i > xlen: break # NOTE this test is probably useless. no. because it actually allows partial subs of X.  
      # eval('self.' + k + ' = ' + str(x[i - 1]))
      setattr(self, k, x[i - 1])


  @property
  def X0(self):
    '''
    Returns the initial conditions of the state vector. 
      
    The initial conditions are determined at the stage of constructing 
    the state object.
    Modifying the initial conditions is possible by direct assignment 
    of the state variable with a '0' suffix. For a state variable 
    :math:`s.x`, its initial condition is modifyied by: 
    :code:`s.x0 = x0`, where :code:`x0` is an arbitrary parameter.  
   
    
    Returns
    -------
    out : numpy.array 
        An array representing the initial values of the state variables. 
    

    Examples
    --------

    .. code:: 
    
      >>> s = c4d.state(x1 = 0, x2 = -1)
      >>> s.X += [0, 1] 
      >>> s.X0
      [0  -1]

        
    .. code:: 
    
      >>> s = c4d.state(x1 = 1, x2 = 1)
      >>> s.X0
      [1  1]
      >>> s.x10 = s.x20 = 0
      >>> s.X0
      [0  0]

      
    '''
    xout = [] 

    for k in self._didx.keys():
      if k == 't': continue
      xout.append(eval('self.' + k + '0'))

    return np.array(xout) 
  

  def addvars(self, **kwargs):
    ''' 
    Add state variables.  
    
    Adding variables to the state outside the :class:`state <c4dynamics.states.state.state>` 
    constructor is possible by using :meth:`addvars() <c4dynamics.states.state.state.addvars>`. 

        
    Parameters
    ----------

    **kwargs : float or int  
        Keyword arguments representing the variables and their initial conditions.
        Each key is a variable name and each value is its initial condition.
      
        
    Note
    ----
    If :meth:`store() <c4dynamics.states.state.state.store>` is called before 
    adding the new variables, then the time histories of the new states 
    are filled with zeros to maintain the same size as the other state variables. 



    Examples
    --------

    .. code:: 
    
      >>> s = c4d.state(x = 0, y = 0)
      >>> s
      [ x  y ]
      >>> s.addvars(vx = 0, vy = 0)
      >>> s
      [ x  y  vx  vy ]

    calling :meth:`store() <c4dynamics.states.state.state.store>` before 
    adding the new variables:

    .. code:: 
    
      >>> s = c4d.state(x = 1, y = 1)
      >>> s.store()
      >>> s.store()
      >>> s.store()
      >>> s.addvars(vx = 0, vy = 0)
      >>> s.data('x')[1]
      [1  1  1]
      >>> s.data('vx')[1]
      [0  0  0]

    '''
    b0 = len(self._didx)
    
    for i, (k, v) in enumerate(kwargs.items()):
      setattr(self, k, v)
      setattr(self, k + '0', v)
      self._didx[k] = b0 + i

    if self._data:
      # add zero columns at the size of the new vars to avoid wrong broadcasting. 
      dataarr = np.array(self._data)
      dataarr = np.hstack((dataarr, np.zeros((dataarr.shape[0], b0))))
      self._data = dataarr.tolist()



  #
  # data management operations 
  ## 

 
  def store(self, t = -1):
    ''' 
    Stores the current state.

    The current state is defined by the vector of variables 
    as given by :attr:`state.X <c4dynamics.states.state.state.X>`.
    :meth:`store() <c4dynamics.states.state.state.store>` is used to store the 
    instantaneous state variables. 


    Parameters 
    ----------
    t : float or int, optional 
        Time stamp for the stored state. 
    
    Note
    ----
    1. Time `t` is an optional parameter with a default value of :math:`t = -1`.
    The time is always appended at the head of the array to store. However, 
    if `t` is not given, default :math:`t = -1` is stored instead.

    2. The method :meth:`store() <c4dynamics.states.state.state.store>` goes together with 
    the methods :meth:`data() <c4dynamics.states.state.state.data>` 
    and :meth:`timestate() <c4dynamics.states.state.state.timestate>` as input and outputs. 

    3. :meth:`store() <c4dynamics.states.state.state.store>` only stores  
    state variables (those construct :attr:`state.X <c4dynamics.states.state.state.X>`). 
    For other parameters, use :meth:`storeparams() <c4dynamics.states.state.state.storeparams>`. 

    
    Examples
    --------

    .. code:: 

      >>> s = c4d.state(x = 1, y = 0, z = 0)
      >>> s.store()

    Store with time stamp: 

      >>> s = c4d.state(x = 1, y = 0, z = 0)
      >>> s.store(t = 0.5)
    
    Store in a for-loop:

      >>> s = c4d.state(x = 1, y = 0, z = 0)
      >>> for t in np.linspace(0, 1, 3):
      ...   s.X = np.random.rand(3)
      ...   s.store(t)


    Usage of :meth:`store() <c4dynamics.states.state.state.store>` 
    inside a program with a :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` 
    from the :mod:`states library <c4dynamics.states.lib>`:

    
    .. code::           
     
      >>> t = 0
      >>> dt = 1e-3
      >>> h0 = 100 
      >>> dp = c4d.datapoint(z = h0)
      >>> while dp.z >= 0: 
      ...   dp.inteqm([0, 0, -c4d.g_ms2], dt)
      ...   t += dt
      ...   dp.store(t)
      >>> for z in dp.data('z'):
      ...   print(z)
      99.9999950
      99.9999803
      99.9999558
      ...
      0.00033469
      -0.0439570


    ''' 
    

    self._data.append([t] + self.X.tolist())
    

  def storeparams(self, params, t = -1):
    ''' 
    Stores parameters. 

    Parameters are data attributes which are not part of the state vector.
    :meth:`storeparams() <c4dynamics.states.state.state.storeparams>` is 
    used to store the instantaneous parameters. 

    Parameters 
    ----------
    params : str or list of str
        Name or names of the parameters to store. 
    t : float or int, optional 
        Time stamp for the stored state. 
    
    Note
    ----
    1. Time `t` is an optional parameter with a default value of :math:`t = -1`.
    The time is always appended at the head of the array to store. However, 
    if `t` is not given, default :math:`t = -1` is stored instead.

    2. The method :meth:`storeparams() <c4dynamics.states.state.state.storeparams>` 
    goes together with the method :meth:`data() <c4dynamics.states.state.state.data>` 
    as input and output. 
    

    Examples
    --------
    
    .. code:: 

      >>> s = c4d.state(x = 100, vx = 10)
      >>> s.mass = 25 
      >>> s.storeparams('mass')
      >>> s.data('mass')[1]
      [25]

      
    Store with time stamp: 

    .. code:: 

      >>> s.storeparams('mass', t = 0.1)
      >>> s.data('mass')
      ([0.1], [25])    

      
    Store multiple parameters: 
    
    .. code:: 

      >>> s = c4d.state(x = 100, vx = 10)
      >>> s.x_std = 5 
      >>> s.vx_std = 10 
      >>> s.storeparams(['x_std', 'vx_std'])
      >>> s.data('x_std')[1]
      [5]
      >>> s.data('vx_std')[1]
      [10]



    Objects classification: 

    .. code:: 

      >>> s = c4d.state(x = 25, y = 25, w = 20, h = 10)
      >>> for i in range(3): 
      ...   s.X += 1 
      ...   s.w, s.h = np.random.randint(0, 50, 2)
      ...   if s.w > 40 or s.h > 20: 
      ...     s.class_id = 'truck' 
      ...   else:  
      ...     s.class_id = 'car'
      ...   s.store() # stores the state 
      ...   s.storeparams('class_id') # store the class_id parameter 
      >>> print('   x    y    w    h    class')
      >>> print(np.hstack((s.data()[:, 1:].astype(int), np.atleast_2d(s.data('class_id')[1]).T)))
      x   y   w   h   class
      26  26  34  21  truck
      27  27  2   4   car
      28  28  35  17  car


    The `morphospectra` implements a custom method `getdim` to update 
    the dimension parameter `dim` with respect to the position coordinates:
    
    .. code::

      >>> import types 
      >>> # 
      >>> def getdim(s):
      ...   if s.X[2] != 0:
      ...     # z 
      ...     s.dim = 3
      ...   elif s.X[1] != 0:
      ...     # y 
      ...     s.dim = 2
      ...   elif s.X[0] != 0:
      ...     # x
      ...     s.dim = 1
      ...   else: 
      ...     # none 
      ...     s.dim = 0
      >>> #
      >>> morphospectra = c4d.state(x = 0, y = 0, z = 0)
      >>> morphospectra.dim = 0 
      >>> morphospectra.getdim = types.MethodType(getdim, morphospectra)
      >>> # 
      >>> for r in range(10):
      ...   morphospectra.X = np.random.choice([0, 1], 3)
      ...   morphospectra.getdim()
      ...   morphospectra.store()
      ...   morphospectra.storeparams('dim')
      >>> # 
      >>> print('x y z  | dim')
      >>> print('------------')
      >>> for x, dim in zip(morphospectra.data().astype(int)[:, 1 : 4].tolist(), morphospectra.data('dim')[1].tolist()):
      ...   print(*(x + [' | '] + [dim]))
      x y z  | dim
      ------------
      0 1 0  |  2
      1 1 0  |  2
      1 0 0  |  1
      0 1 1  |  3
      1 0 0  |  1
      1 1 1  |  3
      1 1 0  |  2
      1 1 0  |  2
      1 0 1  |  3
      1 0 1  |  3

    '''
    # TODO show example of multiple vars  
    # maybe the example of the kalman variables store 
    #   from the detect track exmaple. 
    # TODO add test if the params is not 0 or 1 dim throw error or warning. why?
    # TODO document about the two if's down here: nonscalar param and empty param. 
    from functools import reduce
        
    lparams = params if isinstance(params, list) else [params]
    for p in lparams:
      if p not in self._prmdata:
        self._prmdata[p] = []

      vval = np.atleast_1d(reduce(getattr, p.split('.'), self)).flatten()
      if len(vval) == 0: # empty, convert to none to keep homogenuous array 
        vval = np.atleast_1d(np.nan)
      elif len(vval) > 1:
        # c4d.cprint(f'{p} is not a scalar. only first item is stored', 'r')
        warnings.warn(f'{p} is not a scalar. Only first item is stored', c4d.c4warn)
        vval = vval[:1]
      self._prmdata[p].append([t] + vval.tolist())

  
  def data(self, var = None, scale = 1):
    ''' 
    Returns arrays of stored time and data.
    
    :meth:`data() <c4dynamics.states.state.state.data>` returns a tuple containing two numpy arrays:
    the first consists of timestamps, and the second 
    contains the values of a `var` corresponding to those timestamps.

    `var` may be each one of the state variables or the parameters. 
   
    If `var` is not introduced, :meth:`data() <c4dynamics.states.state.state.data>` 
    returns a single array of the entire state histories. 
    
    If data were not stored, :meth:`data() <c4dynamics.states.state.state.data>` 
    returns an empty array. 
    

    Parameters
    ----------
    var : str 
        The name of the variable or parameter of the required histories. 

    scale : float or int, optional
        A scaling factor to apply to the variable values, by default 1.

    Returns
    -------
    out : array or tuple of numpy arrays 
        if `var` is introduced, `out` is a tuple of a timestamps array
        and an array of `var` values corresponding to those timestamps.
        If `var` is not introduced, then :math:`n \\times m+1` numpy array is returned, 
        where `n` is the number of stored samples, and `m+1` is the 
        number of state variables and times. 

            

    Examples
    --------
  
    Get all stored data: 

    .. code:: 

      >>> s = c4d.state(x = 1, y = 0, z = 0)
      >>> for t in np.linspace(0, 1, 3):
      ...   s.X = np.random.rand(3)
      ...   s.store(t)
      >>> s.data())
      [[0   0.37  0.76  0.20]
      [0.5  0.93  0.28  0.59]
      [1    0.79  0.39  0.33]]


    Data of a variable: 

    .. code:: 

      >>> time, x_data = s.data('x')
      >>> time
      [0  0.5  1]
      >>> x_data
      [0.93  0.48  0.10]
      >>> s.data('y')[1]
      [0.76  0.28  0.39]


    Get data with scaling: 

    .. code::

      >>> s = c4d.state(phi = 0)
      >>> for p in np.linspace(0, c4d.pi):
      ...   s.phi = p
      ...   s.store()
      >>> s.data('phi', c4d.r2d)[1]
      [0  3.7  7.3  11  14.7  18.3  22  25.7  ..  180]


    Data of a parameter

    .. code:: 

      >>> s = c4d.state(x = 100, vx = 10)
      >>> s.mass = 25 
      >>> s.storeparams('mass', t = 0.1)
      >>> s.data('mass')
      ([0.1], [25)])


    
    '''
    if var is None: 
      # return all 
      # XXX not sure this is applicable to the new change where arrays\ matrices 
      #   are also stored.
      #   in fact the matrices are not stored in _data but in _prmdata  
      return np.array(self._data)
     
    idx = self._didx.get(var, -1)
    if idx >= 0:
      if not self._data:
        # empty array  
        c4d.cprint('Warning: no history of state samples.', 'r')
        return np.array([])
      
      if idx == 0: 
        return np.array(self._data)[:, 0]

      return (np.array(self._data)[:, 0], np.array(self._data)[:, idx] * scale)

    # else \ user defined variables 
    if var not in self._prmdata:
      c4d.cprint('Warning: no history samples of ' + var + '.', 'r')
      return np.array([])

    # if the var is text, dont multiply by scale
    if np.issubdtype(np.array(self._prmdata[var])[:, 1].dtype, np.number):
      return (np.array(self._prmdata[var])[:, 0], np.array(self._prmdata[var])[:, 1] * scale)
    else: 
      return (np.array(self._prmdata[var])[:, 0], np.array(self._prmdata[var])[:, 1])
    

  def timestate(self, t):
    '''
    Returns the state as stored at time `t`. 

    The method searches the closest time  
    to time `t` in the sampled histories and 
    returns the state that stored at the time.  

    If data were not stored returns None. 

    Parameters
    ----------
    t : float or int   
        The time at the required sample. 
            
    Returns
    -------
    out : numpy.array 
        An array of the state vector 
        :attr:`state.X <c4dynamics.states.state.state.X>` 
        at time `t`. 

        
    Examples
    --------

    .. code:: 

      >>> s = c4d.state(x = 0, y = 0, z = 0)
      >>> for t in np.linspace(0, 1, 3):
      ...   s.X += 1
      ...   s.store(t)
      >>> s.timestate(0.5))
      [0.28, 0.95, 0.82]

      
    .. code:: 

      >>> s = c4d.state(x = 1, y = 0, z = 0)
      >>> s.timestate(0.5)
      Warning: no history of state samples.
      None 



    '''

    # TODO what about throwing a warning when dt is too long? \\ what is dt and so what if its long? 
    times = self.data('t')
    if len(times) == 0: 
      out = None
    else:
      idx = min(range(len(times)), key = lambda i: abs(times[i] - t))
      out = self._data[idx][1:]

    return out 
    

  def plot(self, var, scale = 1, ax = None, filename = None, darkmode = True, linecolor = 'm'):
    ''' 
    Draws plots of variable evolution over time.

    This method plots the evolution of a state variable over time. 
    The resulting plot can be saved to a directory if specified.

    Parameters
    ----------
    var : str
        The name of the variable or parameter to be plotted.

    scale : float or int, optional
        A scaling factor to apply to the variable values. Defaults to `1`.

    ax : matplotlib.axes.Axes, optional
        An existing Matplotlib axis to plot on. 
        If None, a new figure and axis will be created, by default None.

    filename : str, optional
        Full file name to save the plot image. 
        If None, the plot will not be saved, by default None.

    darkmode : bool, optional
        Directory path to save the plot image. 
        If None, the plot will not be saved, by default None.

    linecolor : str, optional 
        Color name for the line, by default 'm' (magenta). 

    Examples
    --------

    Plot an arbitrary state variable and save: 

    .. code:: 
    
      >>> s = c4d.state(x = 0, y = 0)
      >>> s.store()
      >>> for _ in range(100):
      ...   s.x = np.random.randint(0, 100, 1)
      ...   s.store()
      >>> s.plot('x', filename = 'x.png') 
      >>> plt.show()

    .. figure:: /_examples/state/plot_x.png

    
    Plot in interactive mode:

    .. code:: 
    
      >>> plt.switch_backend('TkAgg')
      >>> s.plot('x') 
      >>> plt.show(block = True)


    Dark mode off:  

      >>> s = c4d.state(x = 0)
      >>> s.xstd = 0.2 
      >>> for t in np.linspace(-2 * c4d.pi, 2 * c4d.pi, 1000):
      ...   s.x = c4d.sin(t) + np.random.randn() * s.xstd 
      ...   s.store(t)
      >>> s.plot('x', darkmode = False) 
      >>> plt.show()

    .. figure:: /_examples/state/plot_darkmode.png


      
    Scale plot:  

    .. code:: 

      >>> s = c4d.state(phi = 0)
      >>> for y in c4d.tan(np.linspace(-c4d.pi, c4d.pi, 500)):
      ...   s.phi = c4d.atan(y)
      ...   s.store()
      >>> s.plot('phi', scale = c4d.r2d, fontsize = 'small', facecolor = None) 
      >>> plt.gca().set_ylabel('deg')
      >>> plt.show()

    .. figure:: /_examples/state/plot_scale.png


    Given axis: 

    .. code:: 

      >>> plt.subplots(1, 1)
      >>> plt.plot(np.linspace(-c4d.pi, c4d.pi, 500) * c4d.r2d, 'c')
      >>> s.plot('phi', scale = c4d.r2d, ax = plt.gca()) 
      >>> ax.set_ylabel('deg')
      >>> plt.legend(['θ', 'φ'])
      >>> plt.show()

    .. figure:: /_examples/state/plot_axis.png


    Top view + side view - options of :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` 
    and :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>` objects:
    
    .. code::

      >>> dt = 0.01
      >>> helium_balloon = c4d.datapoint(vx = 10 * c4d.k2ms)
      >>> helium_balloon.mass = 0.1 
      >>> for t in np.arange(0, 10, dt):
      ...   helium_balloon.inteqm(forces = [0, 0, .05], dt = dt)
      ...   helium_balloon.store(t)
      >>> helium_balloon.plot('side')
      >>> plt.gca().invert_yaxis()
      >>> plt.show()

    .. figure:: /_examples/state/plot_dp_inteqm3.png



    '''

    from matplotlib import pyplot as plt 
    # 
    # points to consider 
    # -------------------
    # 
    # figsize
    # -------
    # 
    # i think the challenge here is to get view + save images with 
    # 1920 x 1080 pixels (Full HD) 
    # 72 DPI (the standard for web images). no way. 72dpi is poor res. at least 300. 
    # --> alternative: 960x540 600dpi.       # 
    # 
    # get the screen dpi to get the desired resolution. 
    #
    # 
    # 
    # backends
    # --------
    # 
    # non-interactive backends: Agg, SVG, PDF: 
    #     When saving plots to files.
    #     include plt.show()
    # interactive backends: 
    #     TkAgg, Qt5Agg, etc.
    #     dont include plt.show()
    # 
    # Check Backend: matplotlib.get_backend().
    # avoid hardcoding backend settings.
    # Avoid using features that are specific to certain backends.
    # Users should be able to override backend settings.
    # 
    # Test your plotting functions across different backends. 
    #
    # finally i think the best soultion regardint backends is not 
    # to do anythink and let the user select the backend from outside. 
    ##  

    if darkmode: 
      plt.style.use('dark_background')  
    else:
      plt.style.use('default')
 

    # plt.switch_backend('TkAgg')
    # plt.switch_backend('TkAgg')

    # try:
    #   from IPython import get_ipython
    #   if get_ipython() is None:
    #       return False
    #   else:
    #       return True
    # except ImportError:
    #   return False
    
    if ax is None: 
      # factorsize = 4
      # aspectratio = 1080 / 1920 
      # _, ax = plt.subplots(1, 1, dpi = 200
      #               , figsize = (factorsize, factorsize * aspectratio) 
      #                       , gridspec_kw = {'left': 0.15, 'right': .9
      #                                           , 'top': .9, 'bottom': .2})
      _, ax = c4d._figdef()
    else: 
      if linecolor == 'm':
        linecolor = 'c'
      
    if not len(np.flatnonzero(self.data('t') != -1)): # values for t weren't stored
      x = range(len(self.data('t'))) # t is just indices 
      xlabel = 'Samples'
    else:
      x = self.data('t')
      xlabel = 'Time'
    y = np.array(self._data)[:, self._didx[var]] * scale if self._data else np.empty(1) # used selection 
      
    if dict(self._greek_unicode).get(var, '') != '': 
      title = '$\\' + var + '$' 
    else: 
      title = var 

    ax.plot(x, y, linecolor, linewidth = 1.5)
    c4d.plotdefaults(ax, title, xlabel, '', 8)
    


    if filename: 
      # plt.tight_layout(pad = 0)
      plt.savefig(filename, bbox_inches = 'tight', pad_inches = .2, dpi = 600)
      

    # plt.show(block = True)




  #
  # math operations 
  ## 


  @property 
  def norm(self):
    '''
    Returns the Euclidean norm of the state vector. 
      
        
    Returns
    -------
    out : float  
        The computed norm of the state vector. The return type specifically is a numpy.float64. 
    

    Examples
    --------

    .. code:: 
    
      >>> s = c4d.state(x1 = 1, x2 = -1)
      >>> s.norm
      1.414

    '''
    return np.linalg.norm(self.X)
  
  
  @property 
  def normalize(self):
    '''
    Returns a unit vector representation of the state vector. 
    
        
    Returns
    -------
    out : numpy.array   
        A normalized vector of the same direction and shape as `self.X`, where the norm of the vector is `1`. 
    

    Examples
    --------

    .. code:: 
    
      >>> s = c4d.state(x = 1, y = 2, z = 3)
      >>> s.normalize
      [0.27  0.53  0.80]

    '''

    return self.X / np.linalg.norm(self.X)

  
  # cartesian operations


  @property
  def position(self):
    ''' 
    Returns a vector of position coordinates. 

    If the state doesn't include any position coordinate (x, y, z), 
    an empty array is returned.  
    
    Note
    ----
    In the context of :attr:`position <c4dynamics.states.state.state.position>`, 
    only x, y, z, are considered position coordinates.  

    
    Returns
    -------
    out : numpy.array   
        A vector containing the values of the position coordinates, 
        with a size corresponding to the number of these coordinates.


    Examples
    --------

    .. code:: 
    
      >>> s = c4d.state(theta = 3.14, x = 1, y = 2)
      >>> s.position
      [1  2]
    
      
    .. code:: 
    
      >>> s = c4d.state(theta = 3.14, x = 1, y = 2, z = 3)
      >>> s.position
      [1  2  3]
    
    
    .. code:: 
    
      >>> s = c4d.state(theta = 3.14, z = -100)
      >>> s.position
      [-100]
      

    .. code:: 
    
      >>> s = c4d.state(theta = 3.14)
      >>> s.position
      Warning: position is valid when at least one cartesian coordinate variable (x, y, z) exists
      []

    '''
   
    Pcoords = []
    for var in ['x', 'y', 'z']:
      coord = getattr(self, var, None)
      if coord is not None: 
        Pcoords.append(coord) 

    if not Pcoords:
      c4d.cprint('Warning: position is valid when at least one cartesian'
                  ' coordinate variable (x, y, z) exists.', 'm')
    
    return np.array(Pcoords)
  

  @property
  def velocity(self):
    '''     
    Returns a vector of velocity coordinates. 
    
    If the state doesn't include any velocity coordinate (vx, vy, vz), 
    an empty array is returned.  

    Note
    ----
    In the context of :attr:`velocity <c4dynamics.states.state.state.velocity>`, 
    only vx, vy, vz, are considered velocity coordinates.  

    Returns
    -------
    out : numpy.array   
        A vector containing the values of the velocity coordinates, with a size corresponding to the number of these coordinates.


    Examples
    --------

    .. code:: 
    
      >>> s = c4d.state(x = 100, y = 0, vx = -10, vy = 5)
      >>> s.velocity
      [-10  5]

      
    .. code:: 
    
      >>> s = c4d.state(x = 100, vz = -100)
      >>> s.velocity
      [-100]


    .. code:: 
    
      >>> s = c4d.state(z = 100)
      >>> s.velocity
      Warning: velocity is valid when at least one velocity coordinate variable (vx, vy, vz) exists.    
      []


    '''

    Vcoords = []
    for var in ['vx', 'vy', 'vz']:
      coord = getattr(self, var, None)
      if coord is not None: 
        Vcoords.append(coord) 

    if not Vcoords:
      c4d.cprint('Warning: velocity is valid when at least one velocity '
                  'coordinate variable (vx, vy, vz) exists.', 'm')
    
    return np.array(Vcoords)


  def P(self, state2 = None):
    ''' 
    Euclidean distance. 

    Calculates the Euclidean distance between the self state object and 
    a second object `state2`. If `state2` is not provided, then the self 
    Euclidean distance is calculated. 

    If the state doesn't include any position coordinate (x, y, z), 
    a `ValueError` is raised.  

    When a second state object is provided: 

    .. math:: 

      P = \\sum_{k=x,y,z} (self.k - state2.k)^2


    Otherwise: 

    .. math:: 

      P = \\sum_{k=x,y,z} self.k^2
    
      
    Raises 
    ------
    ValueError
        If the state doesn't include any position coordinate (x, y, z).  


    Note
    ----
    In the context of :meth:`P() <c4dynamics.states.state.state.P>`, 
    x, y, z, are considered position coordinates.      
      

    
    Parameters
    ----------
    state2 : :class:`state <c4dynamics.states.state.state>`
        A second state object for which the relative distance is calculated. 
    

    Returns
    -------
    out : float 
        Euclidean norm of the distance vector. The return type specifically is a numpy.float64.


    Examples
    --------

    .. code:: 

      >>> import c4dynamics as c4d 

    .. code::
    
      >>> s = c4d.state(theta = 3.14, x = 1, y = 1)
      >>> s.P()
      1.414 

    .. code:: 

      >>> s  = c4d.state(theta = 3.14, x = 1, y = 1)
      >>> s2 = c4d.state(x = 1)
      >>> s.P(s2)
      0

    .. code:: 

      >>> s  = c4d.state(theta = 3.14, x = 1, y = 1)
      >>> s2 = c4d.state(z = 1)
      >>> s.P(s2)
      Exception has occurred: ValueError  
      At least one position coordinate, x, y, or z, must be common to both instances.

      
    .. code:: 

      >>> import numpy as np 
      >>> from matplotlib import pyplot as plt  

    .. code:: 

      >>> camera = c4d.state(x = 0, y = 0)
      >>> car    = c4d.datapoint(x = -100, vx = 40, vy = -7)
      >>> dist   = []
      >>> for t in np.linspace(0, 10, 1000):
      ...   car.inteqm(np.zeros(3), time[1] - time[0])
      ...   dist.append(camera.P(car))
      >>> plt.plot(time, dist, 'm', linewidth = 2)
      >>> plt.show()

    .. figure:: /_examples/states/state_P.png



    '''
    arg1 = False 
    if state2 is None: 
      state2 = c4d.datapoint() 
      arg1 = True 
      

    comcoords = [var for var in ['x', 'y', 'z'] if hasattr(self, var) and hasattr(state2, var)]
    if not any(comcoords):
      if arg1: 
        raise ValueError('P() is valid when at least one position ' 
                            'coordinate variable (x, y, z) exists')
      else: 
        raise ValueError('At least one position coordinate, '
                           'x, y, or z, must be common to both instances.')

    dist = 0 
    for var in comcoords: 
      dist += (getattr(self, var) - getattr(state2, var))**2

    return np.sqrt(dist)


  def V(self):
    ''' 
    Velocity Magnitude. 

    Calculates the magnitude of the object velocity :

    .. math::

      V = \\sum_{k=v_x,v_y,v_z} self.k^2

    If the state doesn't include any velocity coordinate (vx, vy, vz), 
    a `ValueError` is raised.  
      
            

    Returns
    -------
    out : float
        Euclidean norm of the velocity vector. The return type specifically is a numpy.float64.


    Raises 
    ------
    ValueError
        If the state does not include any velocity coordinate (vx, vy, vz).

    Note
    ----
    In the context of :meth:`V() <c4dynamics.states.state.state.V>`, 
    vx, vy, vz, are considered velocity coordinates.      
      

    Examples
    --------

    .. code::

      >>> s = c4d.state(vx = 7, vy = 24)
      >>> s.V()
      25.0

    .. code:: 

      >>> s = c4d.state(x = 100, y = 0, vx = -10, vy = 7)
      >>> s.V()
      12.2

    .. code::

      >>> s = c4d.state(x = 100, y = 0)
      >>> s.V()
      Warning: velocity is valid when at least one velocity coordinate variable (vx, vy, vz) exists.     
      []


    '''
    
    velocity = self.velocity

    if len(velocity): 
      velocity = np.linalg.norm(velocity)

    return velocity
  

  def cartesian(self):
    # TODO document! 
    if any([var for var in ['x', 'y', 'z'] if hasattr(self, var)]):
      return True
    else: 
      return False      

