import numpy as np

# import c4dynamics as c4d
from .eqm3 import eqm3

class datapoint:
  """ 
    the datapoint object is the most basic element in the translational dynamics domain.
    --
    TBD:
      - there should be one abstrcact class \ inerface of a 'bodyw type which defines eqm(), store() etc.
          and datapoint and rigidbody impement it. the body also includes the drawing functions  
      - all these nice things storage, plot etc. have to be move out of here. 
      - add an option in the constructor to select the variables required for storage. 
      - make a dictionary containing the variable name and the variable index in the data storage to save and to extract for plotting. 
      - add total position, velocity, acceleration variables (path angles optional) and update them for each update in the cartesian components. 
  """
  
  # 
  # position
  ##
  ''' maybe it's a better choise to work with vectors?? 
      maybe there's an option to define an array which will just designate its enteries. 
      namely a docker that just references its variables 
      -> this is actually a function! 
      
      
      In Python, all variable names are references to values.
https://stackoverflow.com/questions/986006/how-do-i-pass-a-variable-by-reference


  https://docs.python.org/3/library/stdtypes.html
  
  
  Lists may be constructed in several ways:
    Using a pair of square brackets to denote the empty list: []
    Using square brackets, separating items with commas: [a], [a, b, c]
    Using a list comprehension: [x for x in iterable]
    Using the type constructor: list() or list(iterable)
    
  Tuples may be constructed in a number of ways:
      Using a pair of parentheses to denote the empty tuple: ()
      Using a trailing comma for a singleton tuple: a, or (a,)
      Separating items with commas: a, b, c or (a, b, c)
      Using the tuple() built-in: tuple() or tuple(iterable)
      
  The arguments to the range constructor must be integers
  
  '''
  x = 0
  y = 0
  z = 0

  # 
  # velocity
  ##
  vx = 0
  vy = 0
  vz = 0

  #
  # acceleration
  ##
  ax = 0
  ay = 0
  az = 0
  
  # 
  # initial position 
  ##
  x0 = 0
  y0 = 0
  z0 = 0

  # 
  # mass properties 
  # kg 
  ## 
  m = 1     # mass 

  # https://www.geeksforgeeks.org/getter-and-setter-in-python/
  # https://stackoverflow.com/questions/4555932/public-or-private-attribute-in-python-what-is-the-best-way
  # https://stackoverflow.com/questions/17576009/python-class-property-use-setter-but-evade-getter
  
  
  # 
  # variables for storage
  ##
  # _data = [] # np.zeros((1, 10))
  _didx = {'t': 0, 'x': 1, 'y': 2, 'z': 3, 'vx': 4, 'vy': 5, 'vz': 6, 'ax': 7, 'ay': 8, 'az': 9}
  


  def __init__(obj, **kwargs):
    # reset mutable attributes:
    # 
    # variables for storage
    ##
    obj._data = []    # for permanent class variables (t, x, y .. )
    obj._vardata = {} # for user additional variables 

    obj.__dict__.update(kwargs)
    
    obj.x0 = obj.x
    obj.y0 = obj.y
    obj.z0 = obj.z
    
    # fol = os.getcwd() + '/fig'
    # if not os.path.exists(fol):
    #   os.mkdir(fol)

  def update(obj, x):
    obj.x   = x[0]
    obj.y   = x[1]
    obj.z   = x[2]
    obj.vx  = x[3]
    obj.vy  = x[4]
    obj.vz  = x[5]
    
  
  # def set_x(obj, x):
  #   obj.r = x
  
  # x = property(x, set_x)
  





  def store(obj, t = -1):
    obj._data.append([t, obj.x, obj.y,  obj.z
                        , obj.vx, obj.vy, obj.vz 
                          , obj.ax, obj.ay, obj.az])
    

  def storevar(obj, var, t = -1):
    '''
    use storevar to store additional variables.
    '''

    for v in [var]:

      if v not in obj._vardata:
        obj._vardata[v] = []

      obj._vardata[v].append([t, getattr(obj, v)])




  # def set_t(): print('setting or deleting stored data is impossible')
  
  # def get_t(obj):
  #   return np.array(obj._data)[:, 0] if obj._data else np.empty(1)
  # the reason i commented it is these are mutable. and mutable
  #   are not reset upon calling the constructor. 
  #   and when i tried to reset them manually by:
  #     obj.data_t = None 
  #   i got an error because the setting property is not defined. 
  
  # data_t = property(get_t, set_t, set_t)

  # def get_x(obj):
  #   return np.array(obj._data)[:, 1] if obj._data else np.empty(1)
  # # data_x = property(get_x, set_t, set_t)
  
  # def get_y(obj):
  #   return np.array(obj._data)[:, 2] if obj._data else np.empty(1)
  # # data_y = property(get_y, set_t, set_t)
  
  # def get_z(obj):
  #   return np.array(obj._data)[:, 3] if obj._data else np.empty(1)
  # # data_z = property(get_z, set_t, set_t)
  
  # def get_vx(obj):
  #   return np.array(obj._data)[:, 4] if obj._data else np.empty(1)
  # # data_vx = property(get_vx, set_t, set_t)
  
  # def get_vy(obj):
  #   return np.array(obj._data)[:, 5] if obj._data else np.empty(1)
  # # data_vy = property(get_vy, set_t, set_t)
  
  # def get_vz(obj):
  #   return np.array(obj._data)[:, 6] if obj._data else np.empty(1)
  # # data_vz = property(get_vz, set_t, set_t)
  
  # def get_ax(obj):
  #   return np.array(obj._data)[:, 7] if obj._data else np.empty(1)
  # # data_ax = property(get_ax, set_t, set_t)
  
  # def get_ay(obj):
  #   return np.array(obj._data)[:, 8] if obj._data else np.empty(1)
  # # data_ay = property(get_ay, set_t, set_t)
  
  # def get_az(obj):
  #   return np.array(obj._data)[:, 9] if obj._data else np.empty(1)
  # # data_az = property(get_az, set_t, set_t)
  

  def get_data(obj, var):
    
    # one of the pregiven variables t, x, y .. 
    idx = obj._didx.get(var, -1)
    if idx >= 0:
      return np.array(obj._data)[:, idx] if obj._data else np.empty(1)

    # else \ user defined variables 
    return np.array(obj._vardata.get(var, np.empty((1, 2))))
    

  # 
  # to vectors:
  ##
  def pos(obj):
    return np.array([obj.x, obj.y, obj.z])
  def vel(obj):
    return np.array([obj.vx, obj.vy, obj.vz])
  def acc(obj):
    return np.array([obj.ax, obj.ay, obj.az])
  

  # 
  # to norms:
  ##
  def P(obj):
    return np.sqrt(obj.x**2 + obj.y**2 + obj.z**2)
  def V(obj):
    return np.sqrt(obj.vx**2 + obj.vy**2 + obj.vz**2)
  def A(obj):
    return np.sqrt(obj.ax**2 + obj.ay**2 + obj.az**2)
  
  
  def run(obj, dt, forces):
    # 
    # integration 
    # $ runge kutta 
    #     ti = tspan(i); yi = Y(:,i);
    #     k1 = f(ti, yi);
    #     k2 = f(ti+dt/2, yi+dt*k1/2);
    #     k3 = f(ti+dt/2, yi+dt*k2/2);
    #     k4 = f(ti+dt  , yi+dt*k3);
    #     dy = 1/6*(k1+2*k2+2*k3+k4);
    #     Y(:,i+1) = yi +dy;
    ## 
    
    y = np.array([obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz])
    
    # step 1
    dydx = eqm3(y, forces, obj.m)
    yt = y + dt / 2 * dydx 
    
    # step 2 
    dyt = eqm3(yt, forces, obj.m)
    yt = y + dt / 2 * dyt 
    
    # step 3 
    dym = eqm3(yt, forces, obj.m)
    yt = y + dt * dym 
    dym += dyt 
    
    # step 4
    dyt = eqm3(yt, forces, obj.m)
    yout = y + dt / 6 * (dydx + dyt + 2 * dym)    
    
    # 
    obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz = yout 
    obj.ax, obj.ay, obj.az = dyt[-3:]
    ##
  
   
   
   
   
   
  
  # 
  # plot functions
  ##
  def draw(obj, var):
    from matplotlib import pyplot as plt
    plt.rcParams['figure.figsize'] = (6.0, 4.0) # set default size of plots
    # plt.rcParams['image.cmap'] = 'gray'
    plt.rcParams["font.size"] = 12
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams["font.family"] = "Times New Roman"   # "Britannic Bold" # "Modern Love"#  "Corbel Bold"# 
    plt.style.use('dark_background')  # 'default' # 'seaborn' # 'fivethirtyeight' # 'classic' # 'bmh'
    
    plt.ion()
    # plt.show()

    # grid
    # increase margins for labels. 
    # folder for storage
    # dont close
    # integrate two objects for integration and plotting.
    
    fig = plt.figure()
    
    if var.lower() == 'top':
      # x axis: y data
      # y axis: x data 
      x = obj.get_data('y')
      y = obj.get_data('x')
      xlabel = 'crossrange'
      ylabel = 'downrange'
      title = 'top view'
    elif var.lower() == 'side':
      # x axis: x data
      # y axis: z data 
      x = obj.get_data('x')
      y = obj.get_data('z')
      xlabel = 'downrange'
      ylabel = 'altitude'
      title = 'side view'
      plt.gca().invert_yaxis()
    else: 
      uconv = 1
      if obj._didx[var] > 9: # 10 and above are angular variables 
        uconv = 180 / np.pi     
      
      if not len(np.flatnonzero(obj.get_data('t') != -1)): # values for t weren't stored
        x = range(len(np.array(obj.get_data('t')))) # t is just indices 
        xlabel = 'index'
      else:       
        x = np.array(obj.get_data('t')) 
        xlabel = 't'
      y = np.array(obj._data)[:, obj._didx[var]] * uconv if obj._data else np.empty(1) # used selection 
      ylabel = var
      title = var
    
    
    plt.plot(x, y, 'g', linewidth = 2)

    plt.title(title)
    # plt.xlim(0, 1000)
    # plt.ylim(0, 1000)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(alpha = 0.5)
    # plt.axis('off')
    # plt.savefig(obj.fol + "/" + var) 
    fig.tight_layout()
    
    # plt.pause(1e-3)
    plt.show() # block = True # block = False
