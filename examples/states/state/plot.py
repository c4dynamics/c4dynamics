# type: ignore

import os, sys
sys.path.append('')
import numpy as np 
import c4dynamics as c4d 
from matplotlib import pyplot as plt 
# plt.style.use('dark_background')  
# plt.switch_backend('TkAgg')



# every example should be self contained. 
runerrors  = False
saveimages = True   
viewimages = True 


print(os.getcwd()) 
savedir = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'state') 



def simpleplot():
  c4d.cprint('simple plot', 'c') 
  s = c4d.state(x = 0)
  s.store()
  for _ in range(100):
    s.x = np.random.randint(0, 100, 1)
    s.store()

  plt.switch_backend('TkAgg')
  s.plot('x', filename = os.path.join(savedir, 'plot_x.png')) 


def scaling(): 
  c4d.cprint('with scale', 'c')

  s = c4d.state(phi = 0, y = 0)
  for y in c4d.tan(np.linspace(-c4d.pi, c4d.pi, 500)):
    s.y   = y
    s.phi = c4d.atan(y)
    s.store()
  s.plot('y') 
  s.plot('phi', scale = c4d.r2d) 
  plt.gca().set_ylabel('deg')
  # plt.tight_layout(pad = 0)
  plt.savefig(os.path.join(savedir, 'plot_scale.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)
  return s 


def anotheraxis(s): 

  c4d.cprint('other axis', 'c')
  theta = np.linspace(-c4d.pi, c4d.pi, 500)

  plt.subplots(1, 1, dpi = 200, figsize = (4, 4 * 1080 / 1920), gridspec_kw = {'left': 0.15, 'right': .9, 'top': .9, 'bottom': .2})

  plt.plot(theta * c4d.r2d, 'm')
  ax = plt.gca()
  s.plot('phi', scale = c4d.r2d, ax = ax, filename = os.path.join(savedir, 'plot_axis.png'), color = 'c') 
  ax.set_ylabel('deg')
  plt.legend(['θ', 'φ'], fontsize = 'x-small', facecolor = None, edgecolor = None)
  plt.title('θ vs φ', fontsize = 10)
  # plt.tight_layout(pad = 0)

  plt.savefig(os.path.join(savedir, 'plot_axis.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def sideview(): 
  c4d.cprint('side view', 'c')

  dt = 0.01
  floating_balloon = c4d.datapoint(vx = 10 * c4d.k2ms)
  floating_balloon.mass = 0.1 

  for t in np.arange(0, 10, dt):
    floating_balloon.inteqm(forces = [0, 0, .05], dt = dt)
    floating_balloon.store(t)


  # plt.tight_layout(pad = 0)
  floating_balloon.plot('side')
  plt.gca().invert_yaxis()
  plt.savefig(os.path.join(savedir, 'plot_dp_inteqm3.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def darkmode(): 
  c4d.cprint('darkmode', 'c')

  s = c4d.state(x = 0)
  s.xstd = 0.2 

  for t in np.linspace(-2 * c4d.pi, 2 * c4d.pi, 1000):
    s.x = c4d.sin(t) + np.random.randn() * s.xstd 
    s.store(t)

  plt.switch_backend('TkAgg')
  s.plot('x', darkmode = False, filename = os.path.join(savedir, 'plot_darkmode.png')) 


if __name__ == '__main__': 
  simpleplot()
  s = scaling()
  anotheraxis(s) 
  sideview() 
  darkmode() 

  plt.show(block = True)





