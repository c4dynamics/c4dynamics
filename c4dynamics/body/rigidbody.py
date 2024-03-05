import numpy as np
# from scipy.integrate import solve_ivp 

import c4dynamics as c4d
# from c4dynamics.src.main.py.eqm.eqm6 import eqm6
from c4dynamics.eqm import eqm6
from c4dynamics.rotmat import dcm321

class rigidbody(c4d.datapoint):  # 
  
  # 
  # euler angles 
  #   rad 
  ##
  phi   = 0
  ''' float; Euler angle representing rotation around the x-axis (rad). '''
  theta = 0
  ''' float; Euler angle representing rotation around the y-axis (rad). '''
  psi   = 0
  ''' float; Euler angle representing rotation around the z-axis (rad). '''
  
  # 
  # angular rates 
  #   rad / sec 
  ##
  p     = 0
  ''' float; Angular rate around the x-axis (roll). (rad/sec). '''
  q     = 0
  ''' float; Angular rate around the y-axis (pitch). (rad/sec). '''
  r     = 0
  ''' float; Angular rate around the z-axis (yaw). (rad/sec). '''
  
  # 
  # abgular accelerations
  #   rad / sec^2
  ## 
  p_dot = 0
  ''' float; Angular acceleration around the x-axis (rad/sec^2). '''
  q_dot = 0
  ''' float; Angular acceleration around the y-axis (rad/sec^2). '''
  r_dot = 0
  ''' float; Angular acceleration around the z-axis (rad/sec^2). '''


  
  # 
  # inertia properties 
  ## 
  ixx = 0   
  ''' float; Moment of inertia about the x-axis. '''
  iyy = 0  
  ''' float; Moment of inertia about the y-axis. '''
  izz = 0   
  ''' float; Moment of inertia about the z-axis. '''
  xcm = 0   
  ''' float; Distance from nose to center of mass. '''
  



  # 
  # bounded methods 
  ##
  def __init__(self, **kwargs):
    #
    # reset mutable attributes:
    # 
    # variables for storage
    ##
    super().__init__(**kwargs)  # Dummy values
    self.__dict__.update(kwargs)
    # self._data = [] # np.zeros((1, 19))
    self._didx.update({'phi': 7, 'theta': 8, 'psi': 9
                        , 'p': 10, 'q': 11, 'r': 12})  

    # i think this one should be 
    # self.x0 = self.x
    # self.y0 = self.y
    # self.z0 = self.z
    # self.vx0 = self.vx
    # self.vy0 = self.vy
    # self.vz0 = self.vz

    self.phi0   = self.phi
    self.theta0 = self.theta
    self.psi0   = self.psi
    self.p0   = self.p
    self.q0   = self.q
    self.r0   = self.r
    

   

  @property
  def angles(self):
    ''' 
    Returns an Euler angles array. 
     
    .. math:: 
        X = [\\varphi, \\theta, \\psi]


    Returns
    -------
    out : numpy.array 
        :math:`[\\varphi, \\theta, \\psi]` 
  
        
    Examples
    --------

    .. code:: 
    
      >>> rb = c4d.rigidbody(phi = 135 * c4d.d2r)
      >>> print(rb.angles * c4d.r2d)
      [135.   0.   0.]
    
    '''

    return np.array([self.phi, self.theta, self.psi])


  @property
  def ang_rates(self):
    ''' 
    Returns an angular rates array. 
     
    .. math:: 

      X = [p, q, r]


    Returns
    -------
    out : numpy.array 
        :math:`[p, q, r]` 
  
        
    Examples
    --------

    .. code:: 

      >>> q0 = 30 * c4d.d2r
      >>> rb = c4d.rigidbody(q = q0)
      >>> print(rb.ang_rates * c4d.r2d)
      [ 0. 30.  0.]

    '''
    return np.array([self.p, self.q, self.r])


  @property 
  def IB(self): 
    ''' 
    Returns an Inertial from Body Direction Cosine Matrix (DCM). 

    Based on the current Euler angles, generates a DCM in a 3-2-1 order.
    i.e. first rotation about the z axis (yaw), then a rotation about the 
    y axis (pitch), and finally a rotation about the x axis (roll).
 
    For the background material regarding the rotational matrix operations, 
    see :mod:`rotmat <c4dynamics.rotmat>`. 

    Returns
    -------

    out : numpy.ndarray
        A 3x3 DCM matrix uses to rotate a vector from a body frame 
        to an inertial frame of coordinates.


    Example
    -------

    .. code::

      >>> v_body = [np.sqrt(3), 0, 1]
      >>> rb = c4d.rigidbody(theta = 30 * c4d.d2r)
      >>> v_inertial = rb.IB @ v_body
      >>> print(v_inertial.round(decimals = 2))
      [2. 0. 0.]


    '''
    # inertial from body dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return np.transpose(dcm321(self))
  

  @property
  def BI(self): 
    ''' 

    Returns a Body from Inertial Direction Cosine Matrix (DCM). 

    Based on the current Euler angles, generates a DCM in a 3-2-1 order.
    i.e. first rotation about the z axis (yaw), then a rotation about the 
    y axis (pitch), and finally a rotation about the x axis (roll).
 
    For the background material regarding the rotational matrix operations, 
    see :mod:`rotmat <c4dynamics.rotmat>`. 

    Returns
    -------

    out : numpy.ndarray
        A 3x3 DCM matrix uses to rotate a vector from an inertial frame 
        to a body frame of coordinates.


    Example
    -------

    .. code::

      >>> v_inertial = [1, 0, 0]
      >>> rb = c4d.rigidbody(psi = 45 * c4d.d2r)
      >>> v_body = rb.BI @ v_inertial 
      >>> print(v_body.round(decimals = 3))
      [ 0.707 -0.707  0.   ]


    '''
    # body from inertial dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return dcm321(self)


  def inteqm(self, forces, moments, dt):
    '''
    Advances the state vector, `rigidbody.X`, with respect to the input
    forces and moments on a single step of time, `dt`.

    Integrates equations of six degrees motion using the Runge-Kutta method. 

    This method numerically integrates the equations of motion for a dynamic system
    using the fourth-order Runge-Kutta method as given by 
    :func:`int6 <int6>`. 

    The derivatives of the equations are of six dimensional motion as 
    given by 
    :py:func:`eqm6 <c4dynamics.eqm.eqm6>` 
    
    
    Parameters
    ----------
    forces : numpy.array or list
        An external forces vector acting on the body, `forces = [Fx, Fy, Fz]`  
    moments : numpy.array or list
        An external moments vector acting on the body, `moments = [Mx, My, Mz]`
    dt : float
        Interval time step for integration.


    Returns
    -------
    out : numpy.float64
        An acceleration array at the final time step.


    Note
    ----
    The integration steps follow the Runge-Kutta method:

    1. Compute k1 = f(ti, yi)

    2. Compute k2 = f(ti + dt / 2, yi + dt * k1 / 2)

    3. Compute k3 = f(ti + dt / 2, yi + dt * k2 / 2)

    4. Compute k4 = f(ti + dt, yi + dt * k3)

    5. Update yi = yi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    

    
    Examples
    --------


    .. code::

      >>> dt = .5e-3 
      >>> t = np.arange(0, 10, dt) # np.linspace(0, 10, 1000)
      >>> theta0 =  80 * c4d.d2r       # deg 
      >>> q0     =  0 * c4d.d2r        # deg to sec
      >>> Iyy    =  .4                  # kg * m^2 
      >>> length =  1                  # meter 
      >>> mass   =  0.5                # kg 
      >>> rb = c4d.rigidbody(theta = theta0, q = q0, iyy = Iyy, mass = mass)
      >>> for ti in t: 
      ...    tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
      ...    rb.X = c4d.eqm.int6(rb, np.zeros(3), [0, tau_g, 0], dt)
      ...    rb.store(ti)
      >>> rb.draw('theta')

    .. figure:: /_static/figures/eqm6_theta.png
        
    
    '''
    self.X, acc = c4d.eqm.int6(self, forces, moments, dt, derivs_out = True)
    return acc 




  def animate(self, modelpath, angle0 = [0, 0, 0] 
                , modelcolor = None, dt = 1e-3 
                  , savedir = None, cbackground = [1, 1, 1]):
    '''

    Animates the rigid body's motion using a 3D model 
    according to the 3-2-1 Euler angles histories.

    Important Note
    --------------
    Using the `animate` function requires installation of `Open3D` which is not a prerequisite of `C4dynamics`.
    For the different ways to install `Open3D` please refer to its `official website <https://www.open3d.org/>`_. 
    A direct installation with pip: 

    .. code:: 

      pip install open3d


    Parameters
    ----------

    modelpath : str
      A path to a single file model or a path to a folder containing multiple 
      model files.
      If the provided path is of a folder, only model files should exist in it. 
      Typically supported files for mesh models are .obj, .stl, .ply.
      Supported point cloud file is .pcd.
      If your point cloud file has .ply extension, convert it to a .pcd first. 
      You may do that by using `Open3D`: 

      .. code::

          >>> import open3d as o3d
          >>> pcd = o3d.io.read_point_cloud('model.ply')
          >>> o3d.io.write_point_cloud('model.pcd', pcd)
      
      For more info see `Open3D documentation <https://www.open3d.org/docs/release/tutorial/geometry/file_io.html>`_

    angle0 : array_like, optional 
      Initial Euler angles :math:`[\\varphi, \\theta, \\psi]`, in radians, representing
      the model attitude with respect to the screen frame. 
      The screen frame is defined as follows: 

      ::

        x: right
        y: up
        z: outside 

      Default attitude [0, 0, 0].

    modelcolor : array_like, optional 
      Colors array [R, G, B] of values between 0 and 1. 
      The shape of `modelcolor` is `mx3`, where m is either 1 or as 
      the number of the model files.
      If `m > 1`, then the order of the colors in the array 
      should match the alphabetical order of the files in `modelpath`.

    dt : float, optional
      Time step between two frames for the animation. 
      Default is 1msec. 

    savedir : str, optional
      If provided, saves each frame as an image in the specified directory. 
      Default is None.
     

    Note
    ----
    - The `animate` function Uses `Open3D` library for 3D visualization.
    - Currently, only 321 Euler order of rotation is supported. Therefore if the stored angular state is produced by using other set of Euler angles, they have to be converted to a 321 set first. 


    Examples
    --------
    
    Animate Stanford bunny
    ^^^^^^^^^^^^^^^^^^^^^^
    
    1. The Stanford bunny is a computer graphics 3D test model 
    developed by Greg Turk and Marc Levoy in 1994 at Stanford University. 
    The model consists of 69,451 triangles, with the data determined by 
    3D scanning a ceramic figurine of a rabbit. The model can be downloaded from 
    `The Stanford 3D Scanning Repository <https://graphics.stanford.edu/data/3Dscanrep/#bunny>`_

    .. code:: 

      >>> bunny = c4d.rigidbody()
      >>> # generate an arbitrary attitude motion
      >>> dt = 0.01
      >>> T = 5
      >>> for t in np.arange(0, T, dt): 
      ...     bunny.psi += dt * 360 * c4d.d2r / T
      ...     bunny.store(t)
      >>> # generate paths for the model and output folder and run the animation function
      >>> modelpath = 'examples\\resources\\bunny.pcd'
      >>> bunny.animate(modelpath, cbackground = [0, 0, 0])
    
    .. figure:: /_static/images/bunny.gif

      
    2. You can change the model's color by setting the `modelcolor` parameter.
    Here is an example of a mesh version of Stanford bunny with a custom color:  

    .. code::

      >>> modelpath = 'examples\\resources\\BunnyMesh.ply'
      >>> bunny.animate(modelpath, cbackground = [0, 0, 0], modelcolor = [1, 0, .5])

    .. figure:: /_static/images/bunny_red.gif

    
    Motion of a dynamic system
    ^^^^^^^^^^^^^^^^^^^^^^^^^^

    3. An F16 has the following Euler angles: 

    .. code:: 

      >>> f16 = c4d.rigidbody()
      >>> dt = 0.01
      >>> for t in np.arange(0, 9, dt): 
      ...     if t < 3: 
      ...       f16.psi += dt * 180 * c4d.d2r / 3
      ...     elif t < 6: 
      ...       f16.theta += dt * 180 * c4d.d2r / 3
      ...     else:
      ...       f16.phi -= dt * 180 * c4d.d2r / 3 
      >>>     f16.store(t)

    .. figure:: /_static/images/f16_eulers.png
    
    The jet model is consisted of multiple files, therefore the `f16` rigidbody object
    that was simulated with the above motion is provided with a path to the consisting folder.  

    .. code::

      >>> modelpath = 'examples\\resources\\f16'
      >>> f16.animate(modelpath)

    .. figure:: /_static/images/f16.gif

    
    4. It's obvious that the animated model doesn't follow the required rotation as simulated above. 
    This because the model initial postion isn't aligned with the screen frame. 
    To align the aircraft body frame which defined as:
    
    :: 

      x: centerline 
      z: perpendicular to x, downward 
      y: completes the right-hand coordinate system

    With the screen frame which defined as: 

    :: 
    
      x: rightward 
      y: upward 
      z: outside the screen  

    We should examine a frame of the model before any rotation.
    It can be achieved by using `Open3D`: 
    
    .. code::

      >>> import open3d as o3d
      >>> modelpath = 'examples\\resources\\f16'
      >>> model = []
      >>> for f in sorted(os.listdir(modelpath)):
      ...   mfilepath = os.path.join(modelpath, f)
      ...   model.append(o3d.io.read_triangle_mesh(mfilepath))
      >>> o3d.visualization.draw_geometries(model)

    .. figure:: /_static/images/f16_static.png

    
    It turns out that for 3-2-1 order of rotation (see :mod:`rotmat <c4dynamics.rotmat>`)
    the body frame with respect to the screen frame is given by:

    - Rotation of `180deg` about `y` (up the screen)

    - Rotation of `90deg` about `x` (right the screen)

    Let's re-run with the correct initial conditions: 

    .. code::

      >>> x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r] 
      >>> f16.animate(modelpath, angle0 = x0)

    .. figure:: /_static/images/f16_IC.gif


    5. The attitude is correct but the the model is colorless. 
    Let's give it some color; 
    We sort the colors by the jet's parts alphabetically as it 
    assigns the values according to the order of an alphabetical 
    reading of the files in the folder. 
    Finally convert it to a list. 

    .. code::

      >>> f16colors = list({'Aileron_A_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
      ...                 , 'Aileron_B_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
      ...                 , 'Body_F16':          [0.8, 0.8, 0.8]
      ...                 , 'Cockpit_F16':       [0.1, 0.1, 0.1]
      ...                 , 'LE_Slat_A_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
      ...                 , 'LE_Slat_B_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
      ...                     , 'Rudder_F16':        [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
      ...                       , 'Stabilator_A_F16':  [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
      ...                          , 'Stabilator_B_F16':  [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
      ...                 }.values())
      >>> f16.animate(modelpath, angle0 = x0, modelcolor = f16colors)

    .. figure:: /_static/images/f16_color.gif

    
    6. It can also be painted with a single color for all its parts and a single color for the background: 

    .. code::

      >>> f16.animate(modelpath, savedir = outfol, angle0 = x0, modelcolor = [0, 0, 0], cbackground = np.array([230, 230, 255]) / 255)

    .. figure:: /_static/images/f16_monochrome.gif

      
    7. Finally, let's use the `savedir` option with c4dynamics' gif util to generate a gif file out of the model animation

    .. code::

      >>> f16colors = np.vstack(([255, 215, 0], [255, 215, 0]
                                  , [184, 134, 11], [0, 32, 38]
                                      , [218, 165, 32], [218, 165, 32], [54, 69, 79]
                                          , [205, 149, 12], [205, 149, 12])) / 255
      >>> outfol ='examples\\out\\f16'
      >>> f16.animate(modelpath, angle0 = x0, savedir = outfol, modelcolor = f16colors)
      >>> # the storage folder 'outfol' is the source of images for the gif function
      >>> # the 'duration' parameter sets the required length of the animation  
      >>> gifname = 'f16_animation.gif'
      >>> c4d.gif(outfol, gifname, duration = 1)
    
    Viewing the gif on a Jupyter notebook is possible by using the `Image` funtion of the `IPython` module: 

    .. code::

      >>> from IPython.display import Image
      >>> import os 
      >>> gifpath = os.path.join(outfol, gifname)
      >>> Image(filename = gifpath) 

    .. figure:: /_static/images/f16_color2.gif

    '''
    import os 
    import open3d as o3d
    import time 
    import tkinter as tk
    # currenty supports only 321 euler order attitude histories. 

    # 
    # load the model 
    #   get all the files
    #   check type
    #   read model
    #   add color 
    ##

    model = []

    if os.path.isfile(modelpath):
      modelpath, files = os.path.split(modelpath)
      files = [files]
    else: 
      files = os.listdir(modelpath)
      files = [file for file in files if os.path.isfile(os.path.join(modelpath, file))]

    modelcolor = np.atleast_2d(modelcolor)

    if modelcolor.shape[1] != 1 and modelcolor.shape[0] == 1: # if one row array, duplicate 
      modelcolor = np.atleast_2d(np.repeat(modelcolor, len(files), axis = 0)) 

    # c4d.cprint(modelcolor, 'm')
    # c4d.cprint(type(modelcolor), 'r')  
    # c4d.cprint(modelcolor.shape, 'c')

    for i, f in enumerate(sorted(files)):

      mfilepath = os.path.join(modelpath, f)
      ismesh = True if any(f[-3:] == s for s in ['stl', 'obj', 'ply']) else False 
      imodel = o3d.io.read_triangle_mesh(mfilepath) if ismesh else o3d.io.read_point_cloud(mfilepath) 
      if modelcolor.shape[1] != 1:
        imodel.paint_uniform_color(modelcolor[i])
        if ismesh: 
          imodel.compute_vertex_normals()
      
      model.append(imodel)

      
    # if any(modelpath[-3:] == s for s in ['stl', 'obj', 'ply']):
    #   imodel = o3d.io.read_triangle_mesh(modelpath) 
    # else: 
    #   imodel = o3d.io.read_point_cloud(modelpath)

    # if np.atleast_2d(modelcolor).shape[1] == 1: 
    #   model.append(imodel)
    # else: 
    #   model.append(imodel.paint_uniform_color(modelcolor).compute_vertex_normals())

      
      
    # for i, f in enumerate(sorted(os.listdir(modelpath))):

    #   mfilepath = os.path.join(modelpath, f)

    #   if any(f[-3:] == s for s in ['stl', 'obj', 'ply']):
    #     imodel = o3d.io.read_triangle_mesh(mfilepath)
    #   else: 
    #     imodel = o3d.io.read_point_cloud(mfilepath)
        
    #   if np.atleast_2d(modelcolor).shape[1] == 1: 
    #     model.append(imodel)
    #   elif np.atleast_2d(modelcolor).shape[0] == 1: 
    #     model.append(imodel.paint_uniform_color(modelcolor).compute_vertex_normals())
    #   else: 
    #     model.append(imodel.paint_uniform_color(modelcolor[i]).compute_vertex_normals())

            
    #
    # set the window form 
    ##
    
    # # # find largest coordinate in the model
    # max_coord = 0
    # for i in range(len(model)): 
    #   # Extract coordinates
    #   max_coord = max(max_coord, int(np.max(np.abs(np.asarray(m.points))))) 




    # Create a dummy tkinter window
    root = tk.Tk()
    # Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # Close the dummy window
    root.destroy()

    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name = '' 
                        , width = int(screen_width / 2)
                            , height = int(screen_height / 2)
                                , left = int(screen_width / 2)
                                    , top = int(screen_height / 4))
    opt = vis.get_render_option()
    opt.background_color = cbackground  # RGB values for black

    #
    # prepare output folder
    ##
    if savedir and not os.path.exists(savedir):
      os.makedirs(savedir)


    #
    # load the angular data 
    ##

    psidata   = self.get_data('psi')
    thetadata = self.get_data('theta')
    phidata   = self.get_data('phi')

    for m in model: 
      vis.add_geometry(m)

    # here xscreen = xplane, yscreen = -zplane, and zscreen = yplane  
    # then dcm321(phi, theta, psi) => dcm231(phi, -theta, -psi)
    # but now the conversion of intrinsic frame to extrinsic frame is translated as:
    # -> dcm132(phi, -theta, -psi)

    # rotate the object to its initial attitude 
    Robj = c4d.rotmat.rotx(angle0[0]) @ c4d.rotmat.roty(angle0[1]) @ c4d.rotmat.rotz(angle0[2])


    for i in range(len(phidata)): 
        
        # match the inertial axes to the screen axes 
        self = c4d.rigidbody(phi = -phidata[i] # about x screen 
                                , theta = psidata[i] # about y screen 
                                    , psi = -thetadata[i]) # about z screen 
        
        # 321 intrinsic => 132 extrinsic 
        Rin = c4d.rotmat.roty(self.theta) @ c4d.rotmat.rotz(self.psi) @ c4d.rotmat.rotx(self.phi)
        DR = Rin @ Robj.T
        Robj = Rin 

        for m in model: 
          m.rotate(DR, center = (0, 0, 0)) 
          vis.update_geometry(m)
        
        vis.poll_events()
        vis.update_renderer()

        time.sleep(dt)

        if savedir: 
          vis.capture_screen_image(os.path.join(savedir, 'animated' + str(i) + '.png'))

    vis.destroy_window()


