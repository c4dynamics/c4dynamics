# type: ignore

from matplotlib import pyplot as plt 
import sys, os, socket 
sys.path.append('.')
import c4dynamics as c4d
import numpy as np 

import open3d as o3d
from IPython.display import Image


example_imgs = os.path.join(os.getcwd(), 'examples', '_out', 'animations')
savefol = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'animate')


def bunny():

  c4d.cprint('bunny', 'y')
  bunny_path = c4d.datasets.d3_model('bunny')
  outfol = os.path.join(example_imgs, 'ex_bunny')
  gifname = 'bunny.gif'
  gifpath = os.path.join(savefol, gifname)


  bunny = c4d.rigidbody()
  dt = .01
  T = 5
  for t in np.arange(0, T, dt): 
    bunny.psi += dt * 360 * c4d.d2r / T
    bunny.store(t)
  bunny.animate(bunny_path, savedir = outfol, cbackground = [0, 0, 0])

  c4d.gif(outfol, gifname, duration = 1)
  os.replace(os.path.join(outfol, gifname), gifpath)
  Image(filename = gifpath) 


def bunnymesh(): 
  ## painted bunny 
  c4d.cprint(' painted bunny', 'y')


  # mpath = os.path.join(modelpath, 'bunny_mesh.ply')
  bunnymesh_path = c4d.datasets.d3_model('bunny_mesh')
  outfol = os.path.join(example_imgs, 'ex_color_bunny')
  gifname = 'bunny_red.gif'
  gifpath = os.path.join(savefol, gifname)


  bunny = c4d.rigidbody()

  dt = .01
  T = 5
  for t in np.arange(0, T, dt): 
    bunny.psi += dt * 360 * c4d.d2r / T
    bunny.store(t)

  bunny.animate(bunnymesh_path, savedir = outfol, cbackground = [0, 0, 0], modelcolor = [1, 0, .5])

  c4d.gif(outfol, gifname, duration = 1)
  os.replace(os.path.join(outfol, gifname), gifpath)
  Image(filename = gifpath) 


def ply(): 
  c4d.cprint('ply file', 'y')
  ##  example: ply's 
  ### custom trajectory


  # mpath = os.path.join(modelpath, 'f16')
  f16_path = c4d.datasets.d3_model('f16')
  outfol = os.path.join(example_imgs, 'f16')
  gifname = 'f16.gif'
  gifpath = os.path.join(savefol, gifname)


  f16 = c4d.rigidbody()

  str(f16)

  dt = .01

  for t in np.arange(0, 9, dt): 
    # in 3 seconds make 180 deg: 
    if t < 3: 
        f16.psi += dt * 180 * c4d.d2r / 3
    elif t < 6: 
        f16.theta += dt * 180 * c4d.d2r / 3
    else:
        f16.phi -= dt * 180 * c4d.d2r / 3 
    f16.store(t)

  # plt.figure(figsize = (15, 5))
  fig, axs = plt.subplots(1, 3, figsize = (15, 5))
  axs[0].plot(*f16.data('psi', scale = c4d.r2d), 'm', linewidth = 2)
  axs[1].plot(*f16.data('theta', scale = c4d.r2d), 'm', linewidth = 2)
  axs[2].plot(*f16.data('phi', scale = c4d.r2d), 'm', linewidth = 2)
  c4d.plotdefaults(axs[0], '$\\psi$', 'Time', 'deg', fontsize = 18)
  c4d.plotdefaults(axs[1], '$\\theta$', 'Time', 'deg', fontsize = 18)
  c4d.plotdefaults(axs[2], '$\\varphi$', 'Time', 'deg', fontsize = 18)

  plt.tight_layout()
  plt.savefig(os.path.join(savefol, 'f16_eulers.png'), dpi = 600, bbox_inches = 'tight', pad_inches = 0)

  f16.animate(f16_path, savedir = outfol)

  c4d.gif(outfol, gifname, duration = 1)
  os.replace(os.path.join(outfol, gifname), gifpath)
  Image(filename = gifpath) 


def IC(): 
  ## example: IC


  # it's obvious that the object doesnt follow the order of rotation: 
  # rotation about z (psi), then about y (theta) then about x (phi)
  # this because its inital postion doesnt follow the screen foc. 
  # to allign the frames which defined as (missile) x centerline z downward y completes to righthand, 
  # let's view it with open3d: 

  # mpath = 'C:\\simulations\\dont_sync\\C4dynamics-main\\models\\F-16\\stl'
  # mpath = os.path.join(modelpath, 'f16')

  # mpath = os.path.join(modelpath, 'f16')

  f16_path = c4d.datasets.d3_model('f16')

  outfol = os.path.join(example_imgs, 'f16_IC')
  gifname = 'f16_IC.gif'
  gifpath = os.path.join(savefol, gifname)


  model = []
  for f in sorted(os.listdir(f16_path)):
    mfilepath = os.path.join(f16_path, f)
    model.append(o3d.io.read_triangle_mesh(mfilepath))
  o3d.visualization.draw_geometries(model)

  # then it has theta(screen) = 180, phi (screen) = 90
  x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r] 

  f16.animate(f16_path, savedir = outfol, angle0 = x0)

  c4d.gif(outfol, gifname, duration = 1)
  os.replace(os.path.join(outfol, gifname), gifpath)
  Image(filename = gifpath) 


def custompaint(): 
  c4d.cprint('custom paint', 'y')
  ## example: custom paint


  # mpath = os.path.join(modelpath, 'f16')
  f16_path = c4d.datasets.d3_model('f16')
  outfol = os.path.join(example_imgs, 'f16_color')
  gifname = 'f16_color.gif'
  gifpath = os.path.join(savefol, gifname)


  # the attitude is good but the the model is colorless. 
  # let's give it some color:
  # we sort the colors by the jet's parts alphabetically as it assigns the values according to the order of an alphabetical reading of the files in the folder: 
  # fiinally convert it to a list. 
  # note that the function takes a list of colors the dictionary here was introduced for convinience presentaation of the each part's color. 
  f16colors = list({'Aileron_A_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
                  , 'Aileron_B_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
                  , 'Body_F16':          [0.8, 0.8, 0.8]
                  , 'Cockpit_F16':       [0.1, 0.1, 0.1]
                  , 'LE_Slat_A_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
                  , 'LE_Slat_B_F16':     [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
                      , 'Rudder_F16':        [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
                          , 'Stabilator_A_F16':  [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
                              , 'Stabilator_B_F16':  [0.3 * 0.8, 0.3 * 0.8, 0.3 * 1]
              }.values())

  # then it has theta(screen) = 180, phi (screen) = 90
  x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r] 


  f16.animate(f16_path, savedir = outfol, angle0 = x0, modelcolor = f16colors)

  c4d.gif(outfol, gifname, duration = 1)
  os.replace(os.path.join(outfol, gifname), gifpath)
  Image(filename = gifpath) 


def monochromeF16(): 
  ## monochrome f16
  c4d.cprint('monochrome f16', 'y')

  # it can also be painted with a single color on all its parts and a single color for the background: 


  # mpath = os.path.join(modelpath, 'f16')
  f16_path = c4d.datasets.d3_model('f16')
  outfol = os.path.join(example_imgs, 'f16_monochrome')
  gifname = 'f16_monochrome.gif'
  gifpath = os.path.join(savefol, gifname)


  f16 = c4d.rigidbody()
  dt = .01
  for t in np.arange(0, 9, dt): 
    # in 3 seconds make 180 deg: 
    if t < 3: 
        f16.psi += dt * 180 * c4d.d2r / 3
    elif t < 6: 
        f16.theta += dt * 180 * c4d.d2r / 3
    else:
        f16.phi -= dt * 180 * c4d.d2r / 3 
    f16.store(t)

  # then it has theta(screen) = 180, phi (screen) = 90

  x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r] 

  f16.animate(f16_path, savedir = outfol, angle0 = x0, modelcolor = [0, 0, 0], cbackground = [230 / 255, 230 / 255, 255 / 255])

  c4d.gif(outfol, gifname, duration = 1)
  os.replace(os.path.join(outfol, gifname), gifpath)
  Image(filename = gifpath) 


def f16color2(): 
  ## f-16 color 2
  c4d.cprint(' f16 color 2', 'y')


  # mpath = os.path.join(modelpath, 'f16')
  f16_path = c4d.datasets.d3_model('f16')
  outfol = os.path.join(example_imgs, 'f16_color2')
  gifname = 'f16_color2.gif'
  gifpath = os.path.join(savefol, gifname)


  # it can also be painted with a single color on all its parts: 


  f16 = c4d.rigidbody()
  dt = .01
  for t in np.arange(0, 9, dt): 
    # in 3 seconds make 180 deg: 
    if t < 3: 
        f16.psi += dt * 180 * c4d.d2r / 3
    elif t < 6: 
        f16.theta += dt * 180 * c4d.d2r / 3
    else:
        f16.phi -= dt * 180 * c4d.d2r / 3 
    f16.store(t)

  # then it has theta(screen) = 180, phi (screen) = 90
  x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r] 

  f16colors = np.vstack(([255, 215, 0], [255, 215, 0]
                          , [184, 134, 11], [0, 32, 38]
                              , [218, 165, 32], [218, 165, 32], [54, 69, 79]
                                  , [205, 149, 12], [205, 149, 12])) / 255

  f16.animate(f16_path, angle0 = x0, savedir = outfol, modelcolor = f16colors)

  c4d.gif(outfol, gifname, duration = 1)

  os.replace(os.path.join(outfol, gifname), gifpath)
  Image(filename = gifpath) 


if __name__ == '__main__': 

  bunny()
  bunnymesh()
  ply()
  IC()
  custompaint()
  monochromeF16()
  f16color2() 



