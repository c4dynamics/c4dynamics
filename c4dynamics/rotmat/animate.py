import os 
import time 
import numpy as np 
import tkinter as tk
import c4dynamics as c4d 

def animate(rb, modelpath, angle0 = [0, 0, 0] 
              , modelcolor = None, dt = 1e-3 
                , savedir = None, cbackground = [1, 1, 1]):
  
  '''
  Animate a rigidbody. 

  Animates the rigid body's motion using a 3D model 
  according to the 3-2-1 Euler angles histories.

  **Important Note**
  
  Using the `animate` function requires installation of `Open3D` which is not a prerequisite of `C4dynamics`.
  For the different ways to install `Open3D` please refer to its `official website <https://www.open3d.org/>`_. 
  A direct installation with pip: 

  :: 

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
      You may do that by using `Open3D`, see note below. 
  
  angle0 : array_like, optional 
      Initial Euler angles :math:`[\\varphi, \\theta, \\psi]`, in radians, representing
      the model attitude with respect to the screen frame, see note below. 
  
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
  - Currently, only 321 Euler order of rotation is supported. 
    Therefore if the stored angular state is produced by 
    using other set of Euler angles, they have to be converted to a 321 set first. 
  - If the provided path is of a folder, only model files should exist in it. 
    Typically supported files for mesh models are .obj, .stl, .ply.
    Supported point cloud file is .pcd.
    If your point cloud file has .ply extension, convert it to a .pcd first. 
    You may do that by using `Open3D`: 
    
    .. code::

      >>> import open3d as o3d
      >>> pcd = o3d.io.read_point_cloud('model.ply')
      >>> o3d.io.write_point_cloud('model.pcd', pcd)
    
    For more info see `Open3D documentation <https://www.open3d.org/docs/release/tutorial/geometry/file_io.html>`_
  - Initial Euler angles :math:`[\\varphi, \\theta, \\psi]`, in radians, representing
    the model attitude with respect to the screen frame, see note below. 
    The screen frame is defined as follows: 

    ::

      x: right
      y: up
      z: outside 

    Default attitude [0, 0, 0].

  Examples
  --------
  
  **Animate Stanford bunny**
  
  
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
    ...   bunny.psi += dt * 360 * c4d.d2r / T
    ...   bunny.store(t)
    >>> bunny.animate('bunny.pcd', cbackground = [0, 0, 0])
  
  .. figure:: /_static/gifs/bunny.gif

    
  2. You can change the model's color by setting the `modelcolor` parameter.
  Here is an example of a mesh version of Stanford bunny with a custom color:  

  .. code::

    >>> bunny.animate('bunny_mesh.ply', cbackground = [0, 0, 0], modelcolor = [1, 0, .5])

  .. figure:: /_static/gifs/bunny_red.gif

  
  **Motion of a dynamic system**
  

  3. An F16 has the following Euler angles: 

  .. code:: 

    >>> f16 = c4d.rigidbody()
    >>> dt = 0.01
    >>> for t in np.arange(0, 9, dt): 
    ...   if t < 3: 
    ...     f16.psi += dt * 180 * c4d.d2r / 3
    ...   elif t < 6: 
    ...     f16.theta += dt * 180 * c4d.d2r / 3
    ...   else:
    ...     f16.phi -= dt * 180 * c4d.d2r / 3 
    >>>   f16.store(t)

  .. figure:: /_static/images/f16_eulers.png
  
  The jet model is consisted of multiple files, therefore the `f16` rigidbody object
  that was simulated with the above motion is provided with a path to the consisting folder.  

  .. code::

    >>> f16.animate('f16')

  .. figure:: /_static/gifs/f16.gif

  
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
    >>> model = []
    >>> for f in sorted(os.listdir('f16')):
    ...   mfilepath = os.path.join('f16', f)
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
    >>> f16.animate('f16', angle0 = x0)

  .. figure:: /_static/gifs/f16_IC.gif


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
    >>> f16.animate('f16', angle0 = x0, modelcolor = f16colors)

  .. figure:: /_static/gifs/f16_color.gif

  
  6. It can also be painted with a single color for all its parts and a single color for the background: 

  .. code::

    >>> f16.animate('f16', savedir = outfol, angle0 = x0, modelcolor = [0, 0, 0], cbackground = np.array([230, 230, 255]) / 255)

  .. figure:: /_static/gifs/f16_monochrome.gif

    
  7. Finally, let's use the `savedir` option with c4dynamics' gif util to generate a gif file out of the model animation

  .. code::

    >>> f16colors = np.vstack(([255, 215, 0], [255, 215, 0]
                                , [184, 134, 11], [0, 32, 38]
                                    , [218, 165, 32], [218, 165, 32], [54, 69, 79]
                                        , [205, 149, 12], [205, 149, 12])) / 255
    >>> outfol ='out\\f16'
    >>> f16.animate('f16', angle0 = x0, savedir = outfol, modelcolor = f16colors)
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

  .. figure:: /_static/gifs/f16_color2.gif

  '''
  try:
    import open3d as o3d
  except ImportError:
    raise ImportError(
          "The 'open3d' package is required for this function to work. "
          "Please install it by running 'pip install open3d'."
      )
        

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
    ismesh = True if any(f[-3:].lower() == s for s in ['stl', 'obj', 'ply']) else False 
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

  psidata   = rb.data('psi')[1]
  thetadata = rb.data('theta')[1]
  phidata   = rb.data('phi')[1]

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
      rbi = c4d.rigidbody(phi = -phidata[i] # about x screen 
                              , theta = psidata[i] # about y screen 
                                  , psi = -thetadata[i]) # about z screen 
      
      # 321 intrinsic => 132 extrinsic 
      Rin = c4d.rotmat.roty(rbi.theta) @ c4d.rotmat.rotz(rbi.psi) @ c4d.rotmat.rotx(rbi.phi)
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


