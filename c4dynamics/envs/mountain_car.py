import numpy as np
import sys 
sys.path.append('.')
import c4dynamics as c4d 
# import warnings 
# from typing import Optional


class mountain_car(c4d.state):
  '''
  A mountain car environment for a reinforcement learning problem. 


  Parameters
  ==========

  mass : float
      ...
  gravity : float
      ...
  action : float
      ...
  dt : float 
      ... 
  velocity_lim : tuple 
      ... 
  \\ position lim cannot be set becuase it determines the shape of the problem in the cos() 

  See Also 
  ========
  ... 




  **Dynamics**
  

  The state variables of a mountain car are: 

  .. math::

    X = [x, v]^T 

  Where: 
  - :math:`x` is the position of the car along the x-axis.
  - :math:`v` is the velocity of the car along the x-axis. 

  The car is goverened by the following equations of motion which represent the dynamics 
  of climbing a steep hill in the presence of gravity and resistance forces:

  .. math:: 
    \\dot{x} = v 

    \\dot{v} = g \\cdot cos(3 \\cdot x) + a_c / m - k \\cdot v / m
   
  Where:
  - :math:`x` is the position coordinate in :math:`x` direction. Default units :math:`[m]`
  - :math:`v` is the velocity coordinate in :math:`x` direction. Default units :math:`[m/s]`
  - :math:`g` is the gravity force. Defaults :math:`9.8 [N]`
  - :math:`m` is the car mass. Defaults :math:`1500 [kg]`
  - :math:`a_c` is the action (force) command. Defaults :math:`-20[N]` (left), :math:`0` (do nothing), or :math:`20[N]` (right)
  - :math:`k` is the resistance coefficient. Defaults :math:`0.5 [1/s]` 


  The position and velocity are subject to the boundaries:

  .. math:: 

    x \\in speed_lim

    v \\in [vmin, vmax]

  Where: 
  - :math:`xmin` is the minimum position coordinate in :math:`x` direction. Defaults :math:`-120 [m]`
  - :math:`xmax` is the maximum position coordinate in :math:`x` direction. Defaults :math:`50 [m]`
  - :math:`vmin` is the minimum velocity coordinate in :math:`x` direction. Default units :math:`-30 [m/s]`
  - :math:`vmax` is the maximum velocity coordinate in :math:`x` direction. Default units :math:`30 [m/s]`
  
  Outside a boundary the vairable is clipped (extraploated with last value). 


  **Reward** 
  
  
  \\ Goal: When the car reaches :math:`xmax`, the environment provides 


  **Discretization**
  ...


  Example
  =======
  ...


  '''


  def __init__(self, mode = 'gymnasium', n_bins = 12): 
    """ 
      Args
      ---- 
        mass: mass of the car (default 0.2) 
        friction: friction in Newton (default 0.3)
        dt: time step in seconds (default 0.1)
    """
    
    self.mode = mode 
    self.n_bins = n_bins

    if self.mode == 'gymnasium':
      self.steep_factor = 1

      self.dt = 1
      self.gravity = 0.0025 

      self.mass = 1
      self.cos_factor = 1
      
      self.friction = 0
      self.position_lim = (-1.2, 0.5) 
      
      self.speed_lim = (-0.07, 0.07) 
      self.action_list = (-0.001, 0, 0.001)
      
      self.normalized = True
      
    elif self.mode == 'sarsa':
      self.steep_factor = 1
    
      self.dt = 0.1
      self.gravity = 9.8 
      
      self.mass = 0.1
      self.cos_factor = 1
      
      self.friction = 0.1 
      self.position_lim = (-1.2, 0.5) 
      
      self.speed_lim = (-.5, .5)  
      self.action_list = (-1, 0, 1) #(-1 * k * 0.31, 0, 1 * k * 0.31) # .25, .3 - FAIL, .75, .5, .333, .32 - SHARP PASS, .31 - gradual (but still not seems momentum-based)
      
      self.normalized = True
    
    elif self.mode == 'orig_sarsa':
      self.steep_factor = 1
      
      self.dt = 0.1
      self.gravity = 9.8 
      
      self.mass = 0.2
      self.cos_factor = 1
      
      self.friction = 0.3
      self.position_lim = (-1.2, 0.5) 
      
      self.speed_lim = (-1.5, 1.5) # (-3, 3) 
      self.action_list = (-1, 0, 1) # it seems like +-0.2 but its not because he mistakenly multiplies the gravity andthe friction by the mass. i'm not sure about that anymore.  
      
      self.normalized = False
    
    elif self.mode == 'physical': # physical scene

      self.dt = 0.1
      self.gravity = 9.8 

      self.mass = 1500 # kg
      self.cos_factor = 100
      self.steep_factor = 100

      self.friction = 0
      self.position_lim = (-120, 50) # m

      self.speed_lim = (-30, 30)  # m/s
      self.action_list = (-10, 0, 10)

      self.normalized = True
    
    
    super().__init__(position = 0, velocity = 0) 

    xmax = self.position_lim[1] 
    vmax = self.speed_lim[1] 
    self.e_max = self.mass * self.gravity * (np.sin((xmax - (0.5 * np.pi)) + 0.5) + 1.0) + 0.5 * vmax**2

    self.state_lim = (-1, 1)
    self.state_interval = np.linspace(self.state_lim[0],    self.state_lim[1],    num = self.n_bins - 1, endpoint = False)
    self.pos_interval   = np.linspace(self.position_lim[0], self.position_lim[1], num = self.n_bins - 1, endpoint = False)
    self.vel_interval   = np.linspace(self.speed_lim[0],    self.speed_lim[1],    num = self.n_bins - 1, endpoint = False)


  def step(self, action):
    """
      Performs one step in the environment following the action.
      
      Args 
      ----
        action: an integer representing one of three actions [0, 1, 2]
                where 0=move_left, 1=do_not_move, 2=move_right
      
      Returns
        (postion_t1, velocity_t1): state 
        reward: always negative but when the goal is reached
        done: True when the goal is reached
    
    """
    

    # Semi-implicit Euler integraton
    acc = self.action_list[action] / self.mass                                      \
              - self.gravity * self.steep_factor * np.cos(3 * self.position / self.cos_factor)          \
                  - self.friction * self.velocity / self.mass

    self.velocity += acc * self.dt
    self.velocity = np.clip(self.velocity, self.speed_lim[0], self.speed_lim[1])

    self.position += self.velocity * self.dt
    self.position = np.clip(self.position, self.position_lim[0], self.position_lim[1])

    if self.position <= self.position_lim[0] and self.velocity < 0:
      self.velocity = 0

    self.store()
    reward, done = (-0.01, False) if self.position < self.position_lim[1] else (1, True)
  
    return reward, done


  def energy_normalized(self, state = None):

    if state is None: 
      state = self.X

    e_state = self.mass * self.gravity * (np.sin((state[0] - (0.5 * np.pi)) + 0.5) + 1.0) + 0.5 * state[1]**2
    return 2 * e_state / self.e_max    
  

  def energy(self, state = None):

    if state is None: 
      state = self.X

    # potential energy (height modeled by sine curve)
    potential = self.mass * self.gravity * (np.sin((x - (0.5 * np.pi)) + 0.5) + 1.0)
    # kinetic energy
    kinetic = 0.5 * self.mass * v**2

    e_state = self.mass * self.gravity * (np.sin((state[0] - (0.5 * np.pi)) + 0.5) + 1.0) + 0.5 * state[1]**2
    return 2 * e_state / self.e_max    
    

  def reset(self, exploring_starts = True): 
    """ 
      Resets the car to an initial position [-1.2, 0.5]
      
      Args
      ---- 
        exploring_starts: if True a random position is taken
        initial_position: the initial position of the car (requires exploring_starts=False)
      
      Returns
      ------- 
        Initial position of the car and the velocity
    
    """

    # seed_seq = np.random.SeedSequence(seed)
    # np_seed = seed_seq.entropy
    # rng = RandomNumberGenerator(np.random.PCG64(seed_seq))
    # seed = np.random.randint(0, 2**24)
    # np.random.seed(seed)
    super().reset() 
    
    if exploring_starts: # gym: always generates. but on small interval (-0.6,-0.4 uniformly) 
      
      # initial_position = np.random.uniform(-1.2, 0.5)
      # initial_position = np.random.uniform(initial_position - 0.1, initial_position + 0.1)
      pos0 = self.position_lim[0] + 0.3888 * (self.position_lim[1] - self.position_lim[0])
      dpos = 0.0555 * (self.position_lim[1] - self.position_lim[0]) 
      initial_position = np.random.uniform(pos0 - dpos, pos0 + dpos)
    
    else:
        initial_position = -0.5 

    initial_position = np.clip(initial_position, self.position_lim[0], self.position_lim[1])
    self.position = initial_position
    self.velocity = 0
    
    self.store()
      

  def discretize(self): 

    if self.normalized:
      # normalized the state to (-1, 1) and discretize for N bins. 
      pos = np.digitize(np.interp(self.position, self.position_lim, self.state_lim), self.state_interval)
      vel = np.digitize(np.interp(self.velocity, self.speed_lim, self.state_lim), self.state_interval)
 
    else: 
      # normalized the state to (-1, 1) and discretize for N bins. 
      pos = np.digitize(self.position, self.pos_interval)
      vel = np.digitize(self.velocity, self.vel_interval)
    
    return vel, pos


  def render(self, file_path = './simulation_render.gif', mode = 'gif'):
    # def render(self, file_path = './mountain_car.mp4', mode = 'mp4'):
    """ 
      When the method is called it saves an animation
      of what happened until that point in the episode.
      Ideally it should be called at the end of the episode,
      and every k episodes.
      
      ATTENTION: requires avconv and/or imagemagick installed.
      
      Args
      ----
        file_path: the name and path of the video file
        mode: the file can be saved as 'gif' or 'mp4'
    
    """

    # Plot init
    fig = plt.figure()
    ax = fig.add_subplot(111, autoscale_on = False, xlim = (-1.2, 0.5), ylim = (-1.1, 1.1))
    ax.grid(False)  # disable the grid
    x_sin = np.linspace(start = -1.2, stop = 0.5, num = 100)
    y_sin = np.sin(3 * x_sin)

    # plt.plot(x, y)
    ax.plot(x_sin, y_sin)  # plot the sine wave
    # line, _ = ax.plot(x, y, 'o-', lw=2)
    dot, = ax.plot([], [], 'ro')
    time_text = ax.text(0.05, 0.9, '', transform = ax.transAxes)
    _position_list = self.data('position')[1]
    _dt = self.dt

    def _init():
      dot.set_data([], [])
      time_text.set_text('')
      return dot, time_text

    def _animate(i):
      x = _position_list[i]
      y = np.sin(3 * x)
      dot.set_data([x], [y])
      time_text.set_text("Time: " + str(np.round(i * _dt, 1)) + "s" + '\n' + "Frame: " + str(i))
      return dot, time_text


    # Argument	             | Meaning
    # --------               | -------
    # fig	                   | The figure object where the animation will be drawn.
    # _animate	             | The function that updates the animation frame by frame.
    # np.arange(1,           | The sequence of frame numbers (i) that _animate(i) will receive. 
    #   len(self.data('t'))) |	  Starts from 1 to len(self.data('t')) - 1.
    # blit = True	           | Optimizes rendering by only redrawing changed parts of the frame.
    # init_func = _init	     | Calls _init() once at the beginning to set up the animation.
    # repeat = False	       | The animation runs only once and does not loop.
    ani = animation.FuncAnimation(fig, _animate, np.arange(1, len(self.data('t'))), blit = True, init_func = _init, repeat = False)

    if file_path: 
      if mode == 'gif':
        ani.save(file_path, writer = 'imagemagick', fps = int(1 / self.dt))
      elif mode == 'mp4':
        ani.save(file_path, fps = int(1/self.dt), writer='avconv', codec='libx264')
    
    plt.show()
    # Clear the figure
    fig.clear()
    plt.close(fig)


  def render_axis(self, fig, ax):
    
    ax.grid(False)  # disable the grid
    dot, = ax.plot([], [], 'ro')
    time_text = ax.text(0.05, 0.9, '', transform = ax.transAxes)
    _position_list = self.data('position')[1]
    _dt = self.dt

    def _init():
      dot.set_data([], [])
      time_text.set_text('')
      return dot, time_text

    def _animate(i):
      x = _position_list[i]
      y = np.sin(3 * x)
      dot.set_data([x], [y])
      time_text.set_text("Time: " + str(np.round(i * _dt, 1)) + "s" + '\n' + "Frame: " + str(i))
      return dot, time_text

    ani = animation.FuncAnimation(fig, _animate
                                   , np.arange(1, len(self.data('t')))
                                   , blit = True, init_func = _init
                                   , repeat = False)
    
    return ani, dot


  def animate(self, file_path = './simulation_animate.gif', debug = False):

    from animation_tools import animateit 
    from IPython.display import Image

    # debug = False
    # # Get data
    # t_array = self.data('t')
    # x_array = self.data('position')[1]
    # dt = self.dt

    # inputs = [(i, x_array[i], dt) for i in range(len(t_array))]

    # if debug:
    #   frames = [render_frame(inp) for inp in inputs]
    # else: 
    #   # Parallel rendering
    #   with Pool() as pool:
    #     # frames = pool.map(render_frame, inputs)
    #     results = pool.map(square, range(10))

    # frames = animateit(self) 

    # Get data
    t_array = self.data('t')
    x_array = self.data('position')[1]
    dt = self.dt

    inputs = [(i, x_array[i], dt) for i in range(len(t_array))]

    if debug:
      frames = [render_frame(inp) for inp in inputs]
    else: 
      # Parallel rendering
      with Pool() as pool:
        frames = pool.map(render_frame, inputs)
        # frames = pool.map(square, range(10))

    # gifname = 'car_rl.gif'
    imageio.mimsave(file_path, frames, duration = 0.1, loop = 0)
    # c4d.gif(outfol, gifname, duration = 1)
    Image(file_path)  # doctest: +IGNORE_OUTPUT


  def _plot(self, ax, alpha = 0.4):
    
    # Plot init
    # fig = plt.figure()
    # ax = fig.add_subplot(111, autoscale_on = False, xlim = (-1.2, 0.5), ylim = (-1.1, 1.1))
    ax.grid(False)  # disable the grid
    # ax.set_facecolor((0, 1, 0, alpha))

    x = np.linspace(start = self.position_lim[0], stop = self.position_lim[1], num = 100)
    z = np.sin(3 * x / self.cos_factor)
    ax.plot(x, z, color = '#003366')  # plot the sine wave
    ax.fill_between(x, ax.get_ylim()[0], z, color = '#9370DB', alpha = alpha)

    # plt.plot(x, y)
    # line, _ = ax.plot(x, y, 'o-', lw=2)
    positions_x = self.data('position')[1]
    positions_z = np.sin(3 * self.data('position')[1] / self.cos_factor)

    ax.plot(positions_x, positions_z, 'b.', alpha = 0.3)
    indmaxx = np.argmax(positions_x)
    ax.plot(positions_x[indmaxx], positions_z[indmaxx], 'bo')

    # plt.show()
    # plt.savefig(file_path)
    




