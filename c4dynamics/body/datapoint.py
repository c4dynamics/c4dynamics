import numpy as np

# directly import a submodule (eqm3) from the c4dynamics.eqm package:
from c4dynamics.eqm import eqm3 
# from c4dynamics.src.main.py.eqm import eqm3


class datapoint:
  '''

  The :class:`datapoint` is the most basic element 
  in translational dynamics; it's a point in space. 

  :class:`datapoint` serves as the building block for modeling and simulating 
  the motion of objects in a three-dimensional space. 
  In the context of translational dynamics, a datapoint represents 
  a point mass in space with defined Cartesian coordinates (x, y, z) 
  and associated velocities (vx, vy, vz) and accelerations (ax, ay, az). 

  
  Functionality 
  ^^^^^^^^^^^^^

  The class incorporates functionality for storing time 
  histories of these state variables, 
  facilitating analysis and visualization of dynamic simulations.

  The class supports the integration of equations of motion 
  using the Runge-Kutta method, allowing users to model the behavior 
  of datapoints under the influence of external forces. 

  Additionally, it provides methods for storing and retrieving data, 
  enabling users to track and analyze the evolution of system variables over time.

  Furthermore, the class includes plotting functions to visualize 
  the trajectories and behaviors of datapoints. 
  Users can generate top-view and side-view plots, 
  as well as visualize the time evolution of specific variables.


  Flexibility 
  ^^^^^^^^^^^

  To enhance flexibility, the class allows users to store 
  additional variables of interest, facilitating the expansion of the basic datapoint model.
  The code encourages modularity by emphasizing the separation of concerns, 
  suggesting the move of certain functionalities to abstract classes or interfaces.

  Summary
  ^^^^^^^

  Overall, the :class:`datapoint` class serves as a versatile 
  foundation for implementing and simulating translational dynamics, 
  offering a structured approach to modeling and analyzing the motion 
  of objects in three-dimensional space.


  Parameters 
  ----------

  The construction of a datapoint object is done with a direct call 
  to the datapoint class:
  `pt = c4d.datapoint()`
  There are no explicit parameters to initialize the instance, but
  the determination of each one of the attributes is allowed through 
  the **kwargs which set the vairables in the constructor with:
  `self.__dict__.update(kwargs)`.

  Regardless of the values with which the attributes of the datapoint
  were constructed, the three variables of the position are assigned 
  to the initial position: 

  .. code:: 
    self.x0 = self.x
    self.y0 = self.y
    self.z0 = self.z


  Additional Notes
  ----------------

  - The class provides a foundation for modeling and simulating 
    translational dynamics in 3D space.
  - Users can customize initial conditions, store additional variables, 
    and visualize simulation results.
  - The integration method allows the datapoint to evolve based on external forces.
  - The plotting method supports top-view, side-view, and variable-specific plots.

    
  Example
  -------
  Simulate the flight of an aircraft starting with some given
  initial conditions and draw trajectories: 

  .. code::

    target = c4d.datapoint(x = 4000, y = 1000, z = -3000, vx = -200, vy = -150)    

    dt = 0.01 
    time = np.arange(0, 10, dt)

    for t in time: 
        target.inteqm(np.zeros(3), dt = dt)
        target.store(t)

    target.draw('top')
    fig = plt.gcf()
    fig.set_size_inches(3.0, 3.0)

    ax = plt.gca()
    ax.set_xlim(-1100, 1100)
    ax.set_ylim(0, 4500)

  .. figure:: /_static/figures/datapoint_top.png


    
  '''

# .. automethod:: c4dynamics.datapoint
#     the datapoint object is the most basic element in the translational dynamics domain.
#     --
#     TBD:
#       - there should be one abstrcact class \ inerface of a 'bodyw type which defines eqm(), store() etc.
#           and datapoint and rigidbody impement it. the body also includes the drawing functions  
#       - all these nice things storage, plot etc. have to be move out of here. 
#       - add an option in the constructor to select the variables required for storage. 
#       - make a dictionary containing the variable name and the variable index in the data storage to save and to extract for plotting. 
#       - add total position, velocity, acceleration variables (path angles optional) and update them for each update in the cartesian components. 
  
  
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
  


  #
  # position
  ##
  x = 0 
  ''' float; Cartesian coordinate representing the x-position of the datapoint. '''  
  y = 0 
  ''' float; Cartesian coordinate representing the y-position of the datapoint. '''
  z = 0 
  ''' float; Cartesian coordinate representing the z-position of the datapoint. '''

  # 
  # velocity
  ##
  vx = 0 
  ''' float; Component of velocity along the x-axis. '''
  vy = 0 
  ''' float; Component of velocity along the y-axis. '''
  vz = 0 
  ''' float; Component of velocity along the z-axis. '''

  #
  # acceleration
  ##
  ax = 0  
  ''' float; Component of acceleration along the x-axis. '''
  ay = 0  
  ''' float; Component of acceleration along the y-axis. '''
  az = 0  
  ''' float; Component of acceleration along the z-axis. '''

  # 
  # mass  
  ## 
  mass = 1.0 
  ''' float; Mass of the datapoint. '''

  # https://www.geeksforgeeks.org/getter-and-setter-in-python/
  # https://stackoverflow.com/questions/4555932/public-or-private-attribute-in-python-what-is-the-best-way
  # https://stackoverflow.com/questions/17576009/python-class-property-use-setter-but-evade-getter
  
  


  def __init__(self, **kwargs):
    # reset mutable attributes:
    # 
    # variables for storage
    ##
    

    self._data = []    # for permanent class variables (t, x, y .. )
    self._vardata = {} # for user additional variables 

    self.__dict__.update(kwargs)
    

    self.x0 = self.x
    self.y0 = self.y
    self.z0 = self.z
    
    # fol = os.getcwd() + '/fig'
    # if not os.path.exists(fol):
    #   os.mkdir(fol)

  
    # 
    # variables for storage
    ##
    # _data = [] # np.zeros((1, 10))
    # state vector variables 
    self._didx = {'t': 0, 'x': 1, 'y': 2, 'z': 3
                  , 'vx': 4, 'vy': 5, 'vz': 6}
                    # , 'ax': 7, 'ay': 8, 'az': 9}
    
    
  
  # def set_x(self, x):
  #   self.r = x
  
  # x = property(x, set_x)
  





  @property
  def X(self):
    '''
    The state vector 
    of the datapoint: [x, y, z, vx, vy, vz], 
    or the rigidbody: [x, y, z, vx, vy, vz, phi, theta, psi, p, q, r]. 
    '''
    xout = [] 

    for k in self._didx.keys():
      if k == 't': continue
      xout.append(eval('self.' + k))

    return xout 


  @property
  def pos(self):
    ''' Position vector '''
    return np.array([self.x, self.y, self.z])
  

  @property
  def vel(self):
    ''' Velocity vector '''
    return np.array([self.vx, self.vy, self.vz])
  

  @property
  def acc(self):
    ''' Acceleration vector '''
    return np.array([self.ax, self.ay, self.az])


  @X.setter
  def X(self, x):
    '''
    update the state vector
    for datapoint: [x, y, z, vx, vy, vz]^T
    for rigidbody: [x, y, z, vx, vy, vz, phi, theta, psi, p, q, r]^T
    '''

    for i, k in enumerate(self._didx.keys()):
      if k == 't': continue
      if i > len(x): break 
      # eval('self.' + k + ' = ' + str(x[i - 1]))
      setattr(self, k, x[i - 1])

 




  #
  # methods
  ##


  #
  # storage 
  ##
  def store(self, t = -1):
    ''' Stores the current state of the datapoint, including time (t). '''    
    # self._data.append([t, self.x, self.y,  self.z
    #                     , self.vx, self.vy, self.vz 
    #                       , self.ax, self.ay, self.az])
    self._data.append([t] + self.X)
    

  def storevar(self, var, t = -1):
    ''' Stores additional user-defined variables and their time histories. '''

    for v in [var]:

      if v not in self._vardata:
        self._vardata[v] = []

      self._vardata[v].append([t, getattr(self, v)])

  
  def get_data(self, var):
    ''' Retrieves time histories of state variables or user-defined variables. '''
    # one of the pregiven variables t, x, y .. 
    idx = self._didx.get(var, -1)
    if idx >= 0:
      return np.array(self._data)[:, idx] if self._data else np.empty(1)

    # else \ user defined variables 
    return np.array(self._vardata.get(var, np.empty((1, 2))))
    

  # 
  # to norms:
  ##
  def P(self):
    ''' Returns a norm of the position coordinates '''
    return np.sqrt(self.x**2 + self.y**2 + self.z**2)
  
  
  def V(self):
    ''' Returns a norm of the velocity coordinates '''    
    return np.sqrt(self.vx**2 + self.vy**2 + self.vz**2)
  
  
  def A(self):
    ''' Returns a norm of the acceleration coordinates '''
    return np.sqrt(self.ax**2 + self.ay**2 + self.az**2)
  

  #
  # two objects operation
  ##
  def dist(self, dp):
    ''' 
    Calculates the distance between the self datapoint and 
    a second datapoint 'dp'. 
    '''
    return np.sqrt((self.x - dp.x)**2 + (self.y - dp.y)**2 + (self.z - dp.z)**2)
  
  
  #
  # runge kutta integration
  ##
  def inteqm(self, forces, dt):
    ''' Integrates equations of motion using the Runge-Kutta method. '''
    # 
    # integration 
    # $ runge kutta 
    #     ti = tspan(i); 
    #     yi = Y(:,i);
    #     k1 = f(ti, yi);
    #     k2 = f(ti + dt / 2, yi + dt * k1 / 2);
    #     k3 = f(ti + dt / 2, yi + dt * k2 / 2);
    #     k4 = f(ti + dt  ,yi + dt * k3);
    #     dy = 1 / 6 * (k1 + 2 * k2 + 2 * k3 + k4);
    #     Y(:, i + 1) = yi + dy;
    ## 

    x0 = self.X
    
    # step 1
    dxdt1 = eqm3(self, forces)
    # self.update(x0 + dt / 2 * dxdt1)
    self.X = x0 + dt / 2 * dxdt1
    
    # step 2 
    dxdt2 = eqm3(self, forces)
    # self.update(x0 + dt / 2 * dxdt2)
    self.X = x0 + dt / 2 * dxdt2
    
    # step 3 
    dxdt3 = eqm3(self, forces)
    # self.update(x0 + dt * dxdt3)
    self.X = x0 + dt * dxdt3
    dxdt3 += dxdt2 
    
    # step 4
    dxdt4 = eqm3(self, forces)

    # 
    # self.update(np.concatenate((x0 + dt / 6 * (dxdt1 + dxdt4 + 2 * dxdt3), dxdt4[-3:]), axis = 0))
    self.X = x0 + dt / 6 * (dxdt1 + dxdt4 + 2 * dxdt3)
    # self.ax, self.ay, self.az = dxdt4[-3:]
    return dxdt4[-3:]
    ##
  
  
  # 
  # plot functions
  ##
  def draw(self, var, ax = None):
    ''' 
    Draws plots of trajectories or variable evolution over time. 
    'var' can be 'top' or 'side' for trajectories, or each one of the state variables. 
    '''
    from matplotlib import pyplot as plt
    plt.rcParams['figure.figsize'] = (6.0, 4.0) # set default size of plots
    # plt.rcParams['image.cmap'] = 'gray'
    plt.rcParams["font.size"] = 14
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams["font.family"] = "Times New Roman"   # "Britannic Bold" # "Modern Love"#  "Corbel Bold"# 
    plt.style.use('dark_background')  # 'default' # 'seaborn' # 'fivethirtyeight' # 'classic' # 'bmh'
    
    # plt.ion()
    # plt.show()

    # grid
    # increase margins for labels. 
    # folder for storage
    # dont close
    # integrate two objects for integration and plotting.
    
    if ax is None: 
      _, ax = plt.subplots()
    
    if var.lower() == 'top':
      # x axis: y data
      # y axis: x data 
      x = self.get_data('y')
      y = self.get_data('x')
      xlabel = 'crossrange'
      ylabel = 'downrange'
      title = 'top view'
    elif var.lower() == 'side':
      # x axis: x data
      # y axis: z data 
      x = self.get_data('x')
      y = self.get_data('z')
      xlabel = 'downrange'
      ylabel = 'altitude'
      title = 'side view'
      ax.invert_yaxis()
    else: 
      uconv = 1
      if self._didx[var] >= 7: # 7 and above are angular variables 
        uconv = 180 / np.pi     
      
      if not len(np.flatnonzero(self.get_data('t') != -1)): # values for t weren't stored
        x = range(len(np.array(self.get_data('t')))) # t is just indices 
        xlabel = 'sample'
      else:       
        x = np.array(self.get_data('t')) 
        xlabel = 't'
      y = np.array(self._data)[:, self._didx[var]] * uconv if self._data else np.empty(1) # used selection 
      ylabel = var
      title = var
    
    
    ax.plot(x, y, 'm', linewidth = 2)

    ax.set_title(title)
    # plt.xlim(0, 1000)
    # plt.ylim(0, 1000)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha = 0.5)
    # plt.axis('off')
    # plt.savefig(self.fol + "/" + var) 
    # fig.tight_layout()
    
    # plt.pause(1e-3)
    # plt.show() # block = True # block = False
