import numpy as np

# directly import a submodule (eqm3) from the c4dynamics.eqm package:
import c4dynamics as c4d 
from c4dynamics.eqm import int3  
# from c4dynamics.src.main.py.eqm import eqm3
from c4dynamics.states.state import state 

def create(X):
  if len(X) > 6:
    rb = c4d.rigidbody()
    rb.X = X
    return rb

  dp = c4d.datapoint()
  dp.X = X 
  return dp
  

class datapoint(state):
  '''  
  A data-point object.
  

  The :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` is the most basic element 
  in translational dynamics; it's a point in space with the following state vector:
  
  .. math:: 

    X = [x, y, z, v_x, v_y, v_z]^T 

  - Position coordinates, velocity coordinates. 


  As such, each one of the state variables is a parameter whose value determines 
  its initial conditions: 
  
  **Arguments**

  x : float or int, optional
      The x-position of the datapoint. Default value :math:`x = 0`. 
  y : float or int, optional
      The y-position of the datapoint. Default value :math:`y = 0`. 
  z : float or int, optional
      The z-position of the datapoint. Default value :math:`z = 0`. 
  vx : float or int, optional
      Component of velocity along the x-axis. Default value :math:`v_x = 0`. 
  vy : float or int, optional
      Component of velocity along the y-axis. Default value :math:`v_y = 0`. 
  vz : float or int, optional
      Component of velocity along the z-axis. Default value :math:`v_z = 0`. 

      

  The input arguments determine the initial values of the instance. 
  The vector of initial conditions can be retrieved by calling 
  :attr:`datapoint.X0 <c4dynamics.states.state.state.X0>`:

  
  .. code::

    >>> dp = c4d.datapoint(x = 1000, vx = -100)
    >>> dp.X0
    [1000  0  0  -100  0  0]


  When the initial values are not known at the stage of constructing 
  the state object, it's possible to pass zeros and override them later 
  by direct assignment of the state variable with a `0` suffix. 
  See more at :attr:`X0 <c4dynamics.states.state.state.X0>`. 

  
  Parameters
  ==========

  mass : float  
      The mass of the datapoint   


  See Also
  ========
  .lib
  .state 
  .eqm 


  Example
  =======
  
  The following example simulates the 
  motion of a body in a free fall. 

  The example employs the :mod:`eqm <c4dynamics.eqm>` 
  module to solve the equations of motion of a point-mass 
  in the three dimensional space, and integrate them 
  using the fourth-order Runge-Kutta method.


  .. code:: 

    >>> dp = c4d.datapoint(z = 100)
    >>> dt = 1e-2
    >>> t = np.arange(0, 10, dt) 
    >>> for ti in t:
    ...   if dp.z < 0: break
    ...   dp.inteqm([0, 0, -c4d.g_ms2], dt) 
    ...   dp.store(ti)
    >>> dp.plot('z')
    >>> plt.show()

  .. figure:: /_static/figures/datapoint/intro_freefall.png


  '''

  
  # Attributes
  # ==========

  # As mentioned earlier, reading and writing of the state vairables is allowed by using the 
  # :attr:`X <datapoint.X>` property. The entire attributes which support 
  # the reading and the updating of a datapoint instance are given in the following list:  


  # .. automethod:: c4dynamics.datapoint
  #     the datapoint object is the most basic element in the translational dynamics domain.
  #     --
  #     TBD:
  # - there should be one abstrcact class \ inerface of a 'bodyw type which defines eqm(), store() etc.
  #     and datapoint and rigidbody impement it. the body also includes the drawing functions  
  # - all these nice things storage, plot etc. have to be move out of here. 
  # - add an option in the constructor to select the variables required for storage. 
  # - make a dictionary containing the variable name and the variable index in the data storage to save and to extract for plotting. 
  # - add total position, velocity, acceleration variables (path angles optional) and update them for each update in the cartesian components. 
    
    
  #   # 
  #   # position
  #   ##
  #    maybe it's a better choise to work with vectors?? 
  #       maybe there's an option to define an array which will just designate its enteries. 
  #       namely a docker that just references its variables 
  #       -> this is actually a function! 
        
        
  #       In Python, all variable names are references to values.
  # https://stackoverflow.com/questions/986006/how-do-i-pass-a-variable-by-reference


  #   https://docs.python.org/3/library/stdtypes.html
    
    
  #   Lists may be constructed in several ways:
  #     Using a pair of square brackets to denote the empty list: []
  #     Using square brackets, separating items with commas: [a], [a, b, c]
  #     Using a list comprehension: [x for x in iterable]
  #     Using the type constructor: list() or list(iterable)
      
  #   Tuples may be constructed in a number of ways:
  #       Using a pair of parentheses to denote the empty tuple: ()
  #       Using a trailing comma for a singleton tuple: a, or (a,)
  #       Separating items with commas: a, b, c or (a, b, c)
  #       Using the tuple() built-in: tuple() or tuple(iterable)
        
  #   The arguments to the range constructor must be integers
    
  # __slots__ = ['x', 'y', 'z', 'vx', 'vy', 'vz', 'mass' # , 'ax', 'ay', 'az'
  #                 , 'x0', 'y0', 'z0', 'vx0', 'vy0', 'vz0'
  #                   , '_data', '_vardata', '_didx', '__dict__'] 




  

  _mass = 1


  def __init__(self, x = 0, y = 0, z = 0, vx = 0, vy = 0, vz = 0):
     
    dpargs = {}
    dpargs.setdefault('x', x) 
    dpargs.setdefault('y', y) 
    dpargs.setdefault('z', z) 
    dpargs.setdefault('vx', vx) 
    dpargs.setdefault('vy', vy) 
    dpargs.setdefault('vz', vz) 
    
    super().__init__(**dpargs)


  @property 
  def mass(self): 
    '''
    Gets and sets the object's mass. 
    
    Default value :math:`mass = 1`. 


    Parameters 
    ---------- 
    mass : float or int
        Mass of the object. 
    
    Returns
    -------
    out : float or int 
        A scalar representing the object's mass. 
    
        
    Example 
    -------

    1. `datapoint` 

    Two Helium balloons of 1kg and 10kg float with total force of L = 0.5N 
    and expreience a side wind of 10k.

    .. code:: 

      >>> t1, t2, dt = 0, 10, 0.01
      >>> F = [0, 0, .5]
      >>> #
      >>> hballoon1 = c4d.datapoint(vx = 10 * c4d.k2ms)
      >>> hballoon1.mass = 1 
      >>> #
      >>> hballoon10 = c4d.datapoint(vx = 10 * c4d.k2ms)
      >>> hballoon10.mass = 10 
      >>> #
      >>> for t in np.arange(t1, t2, dt):
      ...   hballoon1.X = int3(hballoon1, F, dt)
      ...   hballoon1.store(t)
      ...   hballoon10.X = int3(hballoon10, F, dt)
      ...   hballoon10.store(t)
      >>> hballoon1.plot('side')
      >>> hballoon10.plot('side', ax = plt.gca(), linecolor = 'c')
      >>> plt.show() 

    .. figure:: /_static/figures/datapoint/mass_balloon.png

    2. `rigidbody`
    The previous example for a `datapoint` object is directly applicable 
    to the `rigidbody` object, as both classes share the same underlying principles 
    concerning translational dynamics. Simply replace :code:`c4d.datapoint(vx = 10 * c4d.k2ms)` 
    with :code:`c4d.rigidbody(vx = 10 * c4d.k2ms)`.







    '''
    return self._mass  

  @mass.setter 
  def mass(self, mass): 
    self._mass = mass 


  #
  # runge kutta integration
  ##
  def inteqm(self, forces, dt):
    ''' 
    Advances the state vector :attr:`datapoint.X <c4dynamics.states.state.state.X>`, 
    with respect to the input
    forces on a single step of time, `dt`.

    Integrates equations of three degrees translational motion using the Runge-Kutta method. 

    This method numerically integrates the equations of motion for a dynamic system
    using the fourth-order Runge-Kutta method as given by 
    :func:`int3 <c4dynamics.eqm.integrate.int3>`. 

    The derivatives of the equations are of three 
    dimensional translational motion and 
    produced with     
    :func:`eqm3 <c4dynamics.eqm.derivs.eqm3>` 
    
    
    Parameters
    ----------
    forces : numpy.array or list
        An external forces vector acting on the body, `forces = [Fx, Fy, Fz]`  
    dt : float or int 
        Interval time step for integration.


    Returns
    -------
    out : numpy.float64
        An acceleration array at the final time step.

    Warning 
    ------- 
    This method is not recommanded when the vector 
    of forces depends on the state variables.
    Since the vector of forces is provided once at the 
    entrance to the integration, it remains constant 
    for the entire steps. 
    Therefore, when the forces depend on the state variables 
    the results of this method are not accurate and may lead to instability.

    
 

    
    Examples
    --------

    Simulation of the motion of a body in a free fall. 

    Employing the :mod:`eqm <c4dynamics.eqm>` 
    module to solve the equations of motion of a point-mass 
    in the three dimensional space.
    Integrating the equations of motion  
    using the fourth-order Runge-Kutta method.


    .. code:: 

      >>> dp = c4d.datapoint(z = 100)
      >>> dt = 1e-2
      >>> t = np.arange(0, 10, dt) 
      >>> for ti in t:
      ...   if dp.z < 0: break
      ...   dp.inteqm([0, 0, -c4d.g_ms2], dt) 
      ...   dp.store(ti)
      >>> dp.plot('z')
      >>> plt.show()

    .. figure:: /_static/figures/datapoint/intro_freefall.png
    


    '''
    self.X, acc = int3(self, forces, dt, derivs_out = True)
    return acc
     
  
  #
  # ploting functions
  ##

  def plot(self, var, scale = 1, ax = None, filename = None, darkmode = True, linecolor = 'm'):
    ''' 
    Draws plots of trajectories or variable evolution over time. 

    `var` can be each one of the state variables, or `top`, `side`, for trajectories. 


    Parameters
    ----------

    var : str
        The variable to be plotted. 
        Possible variables for trajectories: `top`, `side`.
        For time evolution, any one of the state variables is possible: 
        `x`, `y`, `z`, `vx`, `vy`, `vz` - for a datapoint object, and
        also `phi`, `theta`, `psi`, `p`, `q`, `r` - for a rigidbody object. 

    scale : float or int, optional
        A scaling factor to apply to the variable values. Defaults to `1`.

    ax : matplotlib.axes.Axes, optional
        An existing Matplotlib axis to plot on. 
        If None, a new figure and axis will be created. By default None.

    filename : str, optional
        Full file name to save the plot image. 
        If None, the plot will not be saved, by default None.

    darkmode : bool, optional
        Directory path to save the plot image. 
        If None, the plot will not be saved, by default None.

    linecolor : str, optional 
        Color name for the line, by default 'm' (magenta).         

    Notes
    -----
    - The method overrides the :meth:`plot <c4dynamics.states.state.state.plot>` of 
      the parent :class:`state <c4dynamics.states.state.state>` object and is 
      applicable to :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>` 
      and its subclass :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`.  

    - Uses matplotlib for plotting.

    - Trajectory views (`top` and `side`) show the crossrange vs. 
      downrange or downrange vs. altitude.
    
    



    Examples
    --------

    1) `datapoint`: 

    .. code:: 

      >>> pt = c4d.datapoint()
      >>> for t in np.arange(0, 10, .01):
      ...   pt.x = 10 + np.random.randn()
      ...   pt.store(t)
      >>> pt.plot('x')

    .. figure:: /_static/figures/datapoint/plot.png

    2) `rigidbody`:

    A physical pendulum is represented by a rigidoby object.
    `scipy's odeint` integrates the equations of motion to simulate 
    the angle of rotation of the pendulum over time.    

    .. code:: 

      >>> dt =.01 
      >>> pndlm  = c4d.rigidbody(theta = 80 * c4d.d2r)
      >>> pndlm.I = [0, .5, 0]
      >>> # dynamics  
      >>> def physical_pendulum(yin, t, Iyy):
      ...   yout = np.zeros(12)
      ...   yout[7]  =  yin[10]
      ...   yout[10] = -c4d.g_ms2 * c4d.sin(yin[7]) / Iyy - .5 * yin[10]
      ...   return yout
      >>> # main loop 
      >>> for ti in np.arange(0, 4, dt): 
      ...   pndlm.X = scipy.integrate.odeint(pendulum, pndlm.X, [ti, ti + dt], (pndlm.I[1],))[1]
      ...   pndlm.store(ti)
      >>> pndlm.plot('theta', scale = c4d.r2d)

    .. figure:: /_static/figures/rigidbody/plot_pendulum.png     


    '''
    from matplotlib import pyplot as plt

    if darkmode: 
      plt.style.use('dark_background')  
    else:
      plt.style.use('default')
    # plt.switch_backend('TkAgg')

    # plt.rcParams['image.interpolation'] = 'nearest'
    # # plt.rcParams['figure.figsize'] = (6.0, 4.0) # set default size of plots
    # plt.rcParams['font.family'] = 'Times New Roman'   # 'Britannic Bold' # 'Modern Love'#  'Corbel Bold'# 
    # plt.rcParams['font.size'] = 8
    
    # plt.ion()
    # plt.show()

    # grid
    # increase margins for labels. 
    # folder for storage
    # dont close
    # integrate two objects for integration and plotting.
    


    if var.lower() == 'top':
      # x axis: y data
      # y axis: x data 
      x = self.data('y')[1]
      y = self.data('x')[1]
      xlabel = 'Crossrange'
      ylabel = 'Downrange'
      title = 'Top View'
    elif var.lower() == 'side':
      # x axis: x data
      # y axis: z data 
      x = self.data('x')[1]
      y = self.data('z')[1]
      xlabel = 'Downrange'
      ylabel = 'Altitude'
      title = 'Side View'
      # ax.invert_yaxis()
    else: 
      
      if self._didx[var] >= 7: # 7 and above are angular variables 
        scale = 180 / np.pi     


      if not len(np.flatnonzero(self.data('t') != -1)): # values for t weren't stored
        x = range(len(self.data('t'))) # t is just indices 
        xlabel = 'Sample'
      else:
        x = self.data('t')
        xlabel = 'Time'
      y = np.array(self._data)[:, self._didx[var]] * scale if self._data else np.empty(1) # used selection 
      

      if 1 <= self._didx[var] <= 6:
        # x, y, z, vx, vy, vz
        title = var.title()
        ylabel = var.title()
      elif 7 <= self._didx[var] <= 9: 
        # phi, theta, psi
        title = '$\\' + var + '$'
        ylabel = title + ' (deg)'
      elif 10 <= self._didx[var] <= 12: 
        # p, q, r 
        title = var.title()
        ylabel = var + ' (deg/sec)'




    if ax is None: 
      # _, ax = plt.subplots()
      # _, ax = plt.subplots(1, 1, dpi = 200, figsize = (3, 2.3) 
      #           , gridspec_kw = {'left': .17, 'right': .9
      #                           , 'top': .85, 'bottom': .2
      #                             , 'hspace': 0.5, 'wspace': 0.3}) 

      # find the legnth of the number to adjust the left axis:
      # ndigits = len(str(int(np.max(y))))


      factorsize = 4
      aspectratio = 1080 / 1920 
      _, ax = plt.subplots(1, 1, dpi = 200
                    , figsize = (factorsize, factorsize * aspectratio) 
                            , gridspec_kw = {'left': 0.15, 'right': .9
                                                , 'top': .9, 'bottom': .2})
    else: 
      if linecolor == 'm':
        linecolor = 'c'


    ax.plot(x, y, linecolor, linewidth = 1.5)
    c4d.plotdefaults(ax, title, xlabel, ylabel, 8)

    # ax.set_title(title)
    # # plt.xlim(0, 1000)
    # # plt.ylim(0, 1000)
    # ax.set_xlabel(xlabel)
    # ax.set_ylabel(ylabel)
    # ax.grid(alpha = 0.5)
    # # plt.axis('off')
    # # plt.savefig(self.fol + '/' + var) 
    # # fig.tight_layout()
    

    if filename: 
      # plt.tight_layout(pad = 0)
      plt.savefig(filename, bbox_inches = 'tight', pad_inches = .2, dpi = 600)
  

    
  
    
  # @property
  # def X(self):
  #   '''
  #   Array of the state variables.
    
  #   X gets or sets the position and velocity variables of a datapoint 
  #   and rigidbody objects.   
    
  #   The variables of a datapoint object (position and
  #   velocity):

  #   .. math:: 

  #     X = [x, y, z, vx, vy, vz]  

  #   The variables of a rigidbody object (extended by 
  #   the angular position and angular 
  #   velocity):

  #   .. math:: 

  #     X = [x, y, z, v_x, v_y, v_z, {\\varphi}, {\\theta}, {\\psi}, p, q, r]
    

  #   Parameters (X.setter)
  #   ---------------------
  #    x : numpy.array or list
  #       Values vector to set the first N consecutive indices of the state. 
    
        
  #   Returns (X.getter)
  #   ------------------
  #   out : numpy.array 
  #       :math:`[x, y, z, v_x, v_y, v_z]` for a datapoint object.

  #       :math:`[x, y, z, v_x, v_y, v_z, {\\varphi}, {\\theta}, {\\psi}, p, q, r]` for a rigidbody object. 
    

      
  #   Examples
  #   --------

  #   Datapoint state

  #   .. code:: 
    
  #     >>> dp = c4d.datapoint()
  #     >>> print(dp.X)
  #     [0 0 0 0 0 0]
  #     >>> # Update the state:
  #     >>> #       x     y    z  vx vy vz 
  #     >>> dp.X = [1000, 100, 0, 0, 0, -100] 
  #     >>> print(dp.X)
  #     [1000  100    0    0    0 -100]
    
  #   Rigidbody state

  #   .. code:: 

  #     >>> # Get the current state of a rigidbody: 
  #     >>> rb = c4d.rigidbody(theta = 5 * c4d.d2r)
  #     >>> print(rb.X)
  #     [0.  0.  0.  0.  0.  0.   0.   0.08726646   0.   0.   0.   0.]
  #     >>> # Update only the translational variables of the rigidbody:
  #     >>> rb.X = [1000, 100, 0, 0, 0, -100] 
  #     >>> print('  '.join([f'{x}' for x in rb.X]))
  #     1000.0  100.0  0.0  0.0  0.0  -100.0  0.0  0.08726646259971647  0.0  0.0  0.0  0.0
      
  #   Partial state 

  #   Using the setter is possible only to N first consecutive indices. 
  #   To update other indices, concatenate them by using the X getter.
  #   The following example sets only the angular variables of a rigidbody: 
    
  #   .. code:: 
    
  #     >>> Xangular = np.array([5, -10, 0, 1, -1, 0]) * c4d.d2r 
  #     >>> rb.X = np.concatenate((rb.X[:6], Xangular))
  #     >>> print(rb.X[:6])
  #     [1000.  100.    0.    0.    0. -100.]
  #     >>> print('  '.join([f'{x * c4d.r2d}' for x in rb.X[6:]]))
  #     5.0  -10.0  0.0  1.0  -1.0  0.0

  #   '''

  #   xout = [] 

  #   for k in self._didx.keys():
  #     if k == 't': continue
  #     # the alteast_1d() + the flatten() is necessary to 
  #     # cope with nonhomogenuous array 
  #     xout.append(np.atleast_1d(eval('self.' + k)))

  #   return np.array(xout).flatten().astype(np.float64)


  # @property
  # def X0(self):
  #   '''
  #   Returns a vector of the initial conditions. 
    
  #   Initial variables of a datapoint object:

  #   .. math:: 

  #     X_0 = [x_0, y_0, z_0, {v_x}_0, {v_y}_0, {v_z}_0]  

  #   Initial variables of a rigidbody object:

  #   .. math:: 

  #     X_0 = [x_0, y_0, z_0, {v_x}_0, {v_y}_0, {v_z}_0, {\\varphi}_0, {\\theta}_0, {\\psi}_0, p_0, q_0, r_0]
      
        
  #   Returns
  #   -------
  #   out : numpy.array 
  #       :math:`[x_0, y_0, z_0, {v_x}_0, {v_y}_0, {v_z}_0]` for a datapoint object. 
  #       :math:`[x_0, y_0, z_0, {v_x}_0, {v_y}_0, {v_z}_0, {\\varphi}_0, {\\theta}_0, {\\psi}_0, p_0, q_0, r_0]` for a rigidbody object. 
    

        
  #   Examples
  #   --------

  #   Datapoint initial conditions 

  #   .. code:: 
    
  #     >>> dp = c4d.datapoint(x = 1000, vx = -200)
  #     >>> print(dp.X0)
  #     [1000    0    0 -200    0    0]

  #   Change dp.X and check again: 

  #   .. code::

  #     >>> dp.X = [500, 500, 0, 0, 0, 0]
  #     >>> print(dp.X)
  #     [500 500   0   0   0   0]
  #     >>> print(dp.X0)
  #     [1000    0    0 -200    0    0]


  #   Rigidbody initial conditions: 

  #   .. code::

  #     rb = c4d.rigidbody(theta = 5 * c4d.d2r)
  #     print(rb.X0 * c4d.r2d)
  #     #x    y    z    vx   vy   vz   phi theta psi  p    q    r
  #     [0.   0.   0.   0.   0.   0.   0.   5.   0.   0.   0.   0.]
      
  #   '''
  #   xout = [] 

  #   for k in self._didx.keys():
  #     if k == 't': continue
  #     xout.append(eval('self.' + k + '0'))

  #   return np.array(xout) 
  
  # def __str__(self):
  #   return f'{self.X}'
  
  # @property
  # def pos(self):
  #   ''' 
  #   Returns a translational position vector. 
     
  #   .. math:: 

  #     pos = [x, y, z]      
        

  #   Returns
  #   -------
  #   out : numpy.array 
  #       :math:`[x, y, z]` 
  
        
  #   Examples
  #   --------

  #   .. code:: 
    
  #     >>> dp = c4d.datapoint(x = 1000, y = -20, vx = -200)
  #     >>> print(dp.pos)
  #     [1000    -20    0]

  #   '''
  #   return np.array([self.x, self.y, self.z])


  # @property
  # def vel(self):
  #   ''' 
  #   Velocity vector. 
     
  #   .. math:: 

  #     vel = [v_x, v_y, v_z]      
        

  #   Returns
  #   -------
  #   out : numpy.array 
  #       :math:`[v_x, v_y, v_z]` 
  
        
  #   Examples
  #   --------

  #   .. code:: 
    
  #     >>> dp = c4d.datapoint(x = 1000, y = -20, vx = -200)
  #     >>> print(dp.vel)
  #     [-200    0    0]

  #   '''
  #   return np.array([self.vx, self.vy, self.vz])
  

  # @X.setter
  # def X(self, x):
  #   ''' Docstring under X.getter '''
  #   # XXX there must be here a protection from bad size / length of x. 
  #   for i, k in enumerate(self._didx.keys()):
  #     if k == 't': continue
  #     if i > len(x): break 
  #     # eval('self.' + k + ' = ' + str(x[i - 1]))
  #     setattr(self, k, x[i - 1])

 

  #
  # methods
  ##


  #
  # storage operations 
  ##
  # def store(self, t = -1):
  #   ''' 
  #   Stores the current state of the datapoint.

  #   The current state is defined by the vector of variables 
  #   as given by the :attr:`X <datapoint.X>`:

  #   Datapoint: :math:`[t, x, y, z, vx, vy, vz]`. 

  #   Rigidbody: :math:`[t, x, y, z, vx, vy, vz, \\varphi, \\theta, \\psi, p, q, r]`. 


  #   Parameters 
  #   ----------
  #   t : float or int, optional 
  #       Values vector to set the first N consecutive indices of the state. 
    
  #   Note
  #   ----
  #   1. Time t is an optional parameter with a default value of t = -1.
  #   The time is always appended at the head of the array to store. However, 
  #   if t is not given, default t = -1 is stored instead.

  #   2. The method :meth:`store <datapoint.store>` goes together with 
  #   the methods :meth:`data <datapoint.data>` 
  #   and :meth:`timestate <datapoint.timestate>` as input and outputs. 


  #   Examples
  #   --------

  #   Store the given state without time stamps:

  #   .. code:: 
      
  #     >>> dp = c4d.datapoint()
  #     >>> for i in range(3):
  #     ...    dp.X = np.random.randint(1, 100, 6)
  #     ...    dp.store()
  #     >>> for x in dp.data():
  #     ...    print(x)
  #     [-1 30 67 69 67 31 37]
  #     [-1 87 62 36  2 44 97]
  #     [-1 30 30  6 75  7 11]

  #   A default of t = -1 was appended to the stored vector.
  #   In this case, it is a good practice to exclude the vector header (time column):

  #   .. code::

  #     >>> for x in dp.data():

  #     ...    print(x[1:])
  #     [30 67 69 67 31 37]
  #     [87 62 36  2 44 97]
  #     [30 30  6 75  7 11]

  #   Store with time stamps: 
    
  #   .. code::           
     
  #     >>> t = 0
  #     >>> dt = 1e-3
  #     >>> h0 = 100 
  #     >>> dp = c4d.datapoint(z = h0)
  #     >>> while dp.z >= 0: 
  #     ...     dp.inteqm([0, 0, -c4d.g_ms2], dt)
  #     ...    t += dt
  #     ...    dp.store(t)
  #     >>> for z in dp.data('z'):
  #     ...    print(z)
  #     99.999995096675
  #     99.99998038669999
  #     99.99995587007498
  #     ...
  #     0.00033469879436880123
  #     -0.043957035930635484


  #   ''' 
    
  #   self._data.append([t] + self.X.tolist())
    

  # def storeparams(self, var, t = -1):
  #   ''' 
  #   Stores additional user-defined variables. 

  #   User-defined variables are those that do not appear 
  #   with new constructed instance of a :class:`datapoint` or 
  #   a :class:`rigidbody` object. 


  #   Parameters 
  #   ----------
  #   var : str
  #       Name of the user-defined variable to store. 
  #   t : float or int, optional 
  #       Values vector to set the first N consecutive indices of the state. 
    
  #   Note
  #   ----
  #   1. Time t is an optional parameter with a default value of t = -1.
  #   The time is always appended at the head of the array to store. However, 
  #   if t is not given, default t = -1 is stored instead.

  #   2. The method :meth:`storeparams <datapoint.storeparams>` goes together with 
  #   the method :meth:`data <datapoint.data>` 
  #   as input and output. 
    

  #   Examples
  #   --------

  #   The morphospectra extends the datapoint class to include also a dimension
  #   state. 
  #   The X.setter overrides the datapoint.X.setter to update the dimension with 
  #   respect to the input coordinates. 

  #   .. code:: 
      
  #     >>> class morphospectra(c4d.datapoint):
  #     ...   def __init__(self): 
  #     ...     super().__init__()  
  #     ...     self.dim = 0
  #     ...   @c4d.datapoint.X.setter
  #     ...   def X(self, x):
  #     ...     # override X.setter mechanism
  #     ...     for i, k in enumerate(self._didx.keys()):
  #     ...       if k == 't': continue
  #     ...       if i > len(x): break 
  #     ...       setattr(self, k, x[i - 1]) 
  #     ...       # update current dimension 
  #     ...       if x[2] != 0:
  #     ...         # z 
  #     ...         self.dim = 3
  #     ...         return None 
  #     ...       if x[1] != 0:
  #     ...         # y 
  #     ...         self.dim = 2
  #     ...         return None
  #     ...       if x[0] != 0:
  #     ...         self.dim = 1
  #     ... 
  #     >>> spec = morphospectra()
  #     >>> for r in range(10):
  #     ...   spec.X = np.random.choice([0, 1], 3)
  #     ...   spec.store()
  #     ...   spec.storeparams('dim')
  #     ... 
  #     >>> x_hist = spec.data()
  #     >>> print('x y z  | dim')
  #     >>> print('------------')
  #     >>> for x, dim in zip(spec.data()[:, 1 : 4].tolist(), spec.data('dim')[:, 1:].tolist()):
  #     ...   print(*(x + [' | '] + dim))
  #     x y z  | dim
  #     ------------
  #     0 1 0  |  2
  #     1 1 0  |  2
  #     1 0 0  |  1
  #     0 1 1  |  3
  #     1 0 0  |  1
  #     1 1 1  |  3
  #     1 1 0  |  2
  #     1 1 0  |  2
  #     1 0 1  |  3
  #     1 0 1  |  3

  #   '''
  #   from functools import reduce
        
  #   # TODO show example of multiple vars  
  #   # maybe the example of the kalman variables store 
  #   #   from the detect track exmaple. 
  #   lvar = var if isinstance(var, list) else [var]
  #   for v in lvar:
  #     if v not in self._vardata:
  #       self._vardata[v] = []
  #     self._vardata[v].append([t] + np.atleast_1d(reduce(getattr, v.split('.'), self)).flatten().tolist())

  
  # def data(self, var = None):
  #   ''' 
  #   Returns an array of state histories.

  #   Returns the time histories of the variable `var`
  #   at the samples that sotred with :meth:`store <datapoint.store>` or 
  #   :meth:`storeparams <datapoint.storeparams>`. 
  #   Possible values of `var` for built-in state variables:

  #   't', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'phi', 'theta', 'psi', 'p', 'q', 'r'. 

  #   For user defined variables, any value of `var` is optional, if `var` matches the 
  #   variable name and it has histories of stored samples. 

  #   If `var` is not introduced, returns the histories of the entire state. 
  #   If histories were'nt stored, returns an empty array. 


  #   Parameters
  #   ----------
  #   var : str 
  #       The name of the variable of the required histories. 
    
        
  #   Returns
  #   -------
  #   out : numpy.array 
  #       An array of the sample histories. 
  #       if `var` is introduced, out is one-dimensioanl numpy array.
  #       If `var` is not introduced, then nxm two dimensional numpy array is returned, 
  #       where n is the number of stored samples, and m is 1 + 6 (time + state variables) 
  #       for a datapoint object, and 1 + 12 (time + state variables) for a rigidbody object. 

            
  #   Note
  #   ----
  #   The time stamps are also stored on calling to the store functions 
  #   (:meth:`store <datapoint.store>`, :meth:`storeparams <datapoint.storeparams>`).
  #   To get an array of the time histories, :meth:`data <datapoint.data>`
  #   should be called with as: `data('t')`. If :meth:`data <datapoint.data>`
  #   is called without explicit `var`, the location of the time histories is the first column.

  #   Examples
  #   --------

  #   `data` of a specific variable: 
    
  #   .. code::           
     
  #     >>> t = 0
  #     >>> dt = 1e-3
  #     >>> h0 = 100 
  #     >>> dp = c4d.datapoint(z = h0)
  #     >>> while dp.z >= 0: 
  #     ...    dp.inteqm([0, 0, -c4d.g_ms2], dt)
  #     ...    t += dt
  #     ...    dp.store(t)
  #     >>> for z in dp.data('z'):
  #     ...    print(z)
  #     99.999995096675
  #     99.99998038669999
  #     99.99995587007498
  #     ...
  #     0.00033469879436880123
  #     -0.043957035930635484


  #   `data` of an entire state:  

  #   .. code:: 
      
  #     >>> dp = c4d.datapoint()
  #     >>> for i in range(3):
  #     ...    dp.X = np.random.randint(1, 100, 6)
  #     ...    dp.store()
  #     >>> for x in dp.data():
  #     ...    print(x)
  #     [-1 30 67 69 67 31 37]
  #     [-1 87 62 36  2 44 97]
  #     [-1 30 30  6 75  7 11]

  #   A default of t = -1 was appended to the stored vector.
  #   In this case, it is a good practice to exclude the vector header (time column):

  #   .. code::

  #     >>> for x in dp.data():

  #     ...    print(x[1:])
  #     [30 67 69 67 31 37]
  #     [87 62 36  2 44 97]
  #     [30 30  6 75  7 11]


  #   `data` of a user defined variable: 
    
  #   The morphospectra extends the datapoint class to include also a dimension
  #   state. 
  #   The X.setter overrides the datapoint.X.setter to update the dimension with 
  #   respect to the input coordinates. 

  #   .. code:: 
      
  #     >>> class morphospectra(c4d.datapoint):
  #     ...   def __init__(self): 
  #     ...     super().__init__()  
  #     ...     self.dim = 0
  #     ...   @c4d.datapoint.X.setter
  #     ...   def X(self, x):
  #     ...     # override X.setter mechanism
  #     ...     for i, k in enumerate(self._didx.keys()):
  #     ...       if k == 't': continue
  #     ...       if i > len(x): break 
  #     ...       setattr(self, k, x[i - 1]) 
  #     ...       # update current dimension 
  #     ...       if x[2] != 0:
  #     ...         # z 
  #     ...         self.dim = 3
  #     ...         return None 
  #     ...       if x[1] != 0:
  #     ...         # y 
  #     ...         self.dim = 2
  #     ...         return None
  #     ...       if x[0] != 0:
  #     ...         self.dim = 1
  #     ... 
  #     >>> spec = morphospectra()
  #     >>> for r in range(10):
  #     ...   spec.X = np.random.choice([0, 1], 3)
  #     ...   spec.store()
  #     ...   spec.storeparams('dim')
  #     ... 
  #     ... # get the data of the user-defined 'dim' variable: 
  #     ... dim_history = spec.data('dim')[:, 1:]
  #     ...
  #     >>> print('x y z  | dim')
  #     >>> print('------------')
  #     >>> for x, dim in zip(spec.data()[:, 1 : 4].tolist(), spec.data('dim')[:, 1:].tolist()):
  #     ...   print(*(x + [' | '] + dim))
  #     x y z  | dim
  #     ------------
  #     0 1 0  |  2
  #     1 1 0  |  2
  #     1 0 0  |  1
  #     0 1 1  |  3
  #     1 0 0  |  1
  #     1 1 1  |  3
  #     1 1 0  |  2
  #     1 1 0  |  2
  #     1 0 1  |  3
  #     1 0 1  |  3

  #   '''
  #   # one of the pregiven variables t, x, y ..
    
  #   if var is None: 
  #     # return all 
  #     # XXX not sure this is applicable to the new change where arrays\ matrices 
  #     #   are also stored.
  #     #   in fact the matrices are not stored in _data but in _vardata  
  #     return np.array(self._data)
     
  #   idx = self._didx.get(var, -1)
  #   if idx >= 0:
  #     if not self._data:
  #       # empty array  
  #       return np.array([])

  #     return (np.array(self._data)[:, 0], np.array(self._data)[:, idx])

  #   # else \ user defined variables 
  #   if var not in self._vardata:
  #     c4d.cprint('Warning: no history samples of ' + var, 'r')
  #     return np.array([])

  #   return (np.array(self._vardata[var])[:, 0], np.array(self._vardata[var])[:, 1:])
    

  # def timestate(self, t):
  #   '''
  #   Returns the state as stored at time t. 

  #   The function searches the closest time  
  #   to the time t in the sampled histories and 
  #   returns the state that stored at the time.  

  #   Parameters
  #   ----------
  #   t : float or int  
  #       The time of the required sample. 
            
  #   Returns
  #   -------
  #   out : numpy.array 
  #       An array of the sample at time t. 
  #       One-dimensioanl numpy array of 6 state variables 
  #       for a datapoint object or 
  #       12 variables for a rigidbody object. 


  #   Examples
  #   --------

  #   .. code:: 

  #     >>> dp = c4d.datapoint()
  #     >>> time = np.linspace(-2, 3, 1000)
  #     >>> for t in time: 
  #     ...   dp.X = np.random.randint(1, 100, 6)
  #     ...   dp.store(t)
  #     >>> print(dp.timestate(0))
  #     [6, 9, 53, 13, 49, 99]

  #   '''
  #   # TODO what about throwing a warning when dt is too long? 
  #   times = self.data('t')
  #   if times.size == 0: 
  #     out = None
  #   else:
  #     idx = min(range(len(times)), key = lambda i: abs(times[i] - t))
  #     out = self._data[idx][1:]

  #   return out 
    

  # 
  # to norms:
  # ##
  # @property 
  # def P(self):
  #   ''' 
  #   Returns the Euclidean norm of the position coordinates in three dimensions. 
    
  #   This method computes the Euclidean norm (magnitude) of a 3D vector represented
  #   by the instance variables self.x, self.y, and self.z:

  #   .. math::
  #     P = \\sqrt{x^2 + y^2 + z^2}
            

  #   Returns
  #   -------
  #   out : numpy.float64
  #       Euclidean norm of the 3D position vector.


  #   Examples
  #   --------
  #   .. code::

  #     >>> dp = c4d.datapoint(x = 7, y = 24)
  #     >>> print(dp.P)
  #     25.0
  #     >>> dp.X = np.zeros(6)
  #     >>> print(dp.P)
  #     0.0

  #   '''
  #   return np.sqrt(self.x**2 + self.y**2 + self.z**2)
  
  # @property 
  # def V(self):
  #   ''' 
  #   Returns the Euclidean norm of the velocity 
  #   coordinates in three dimensions. 

  #   This method computes the Euclidean norm (magnitude) 
  #   of a 3D vector represented
  #   by the instance variables self.vx, self.vy, and self.vz:

  #   .. math::
  #     V = \\sqrt{v_x^2 + v_y^2 + v_z^2}

            

  #   Returns
  #   -------
  #   out : numpy.float64
  #       Euclidean norm of the 3D velocity vector.


  #   Examples
  #   --------
  #   .. code::

  #     >>> dp = c4d.datapoint(vx = 7, vy = 24)
  #     >>> print(dp.V)
  #     25.0
  #     >>> dp.X = np.zeros(6)
  #     >>> print(dp.V)
  #     0.0

  #   '''
  #   return np.sqrt(self.vx**2 + self.vy**2 + self.vz**2)
  
  
  #
  # two objects operation
  ##
  # def dist(self, dp2):
  #   ''' 
  #   Calculates the Euclidean distance between the self body and 
  #   a second datapoint 'dp2'.

  #   .. math:: 

  #     dist = \\sqrt{(self.x - dp2.x)^2 + (self.y - dp2.y)^2 + (self.z - dp2.z)^2}
    

  #   This method computes the Euclidean distance between the current 3D point
  #   represented by the instance variables self.x, self.y, and self.z, and another
  #   3D point represented by the provided DataPoint object, dp2.

    
  #   Parameters
  #   ----------
  #   dp2 : :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`
  #       A second datapoint object for which the distance should be calculated.  

  #   Returns
  #   -------
  #   out : numpy.float64
  #       Euclidean norm of the 3D range vector.


  #   Examples
  #   --------
  #   .. code::
    
  #     >>> camera = c4d.datapoint()
  #     >>> car = c4d.datapoint(x = -100, vx = 40, vy = -7)
  #     >>> dist = []
  #     >>> time = np.linspace(0, 10, 1000)
  #     >>> for t in time:
  #     ...   car.inteqm(np.zeros(3), time[1] - time[0])
  #     ...   dist.append(camera.dist(car))
  #     >>> plt.plot(time, dist, 'm', linewidth = 2)

  #   .. figure:: /_static/figures/distance.png



  #   '''
  #   return np.sqrt((self.x - dp2.x)**2 + (self.y - dp2.y)**2 + (self.z - dp2.z)**2)
  
  