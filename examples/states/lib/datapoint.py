import sys, os
sys.path.append('')
import c4dynamics as c4d

import numpy as np 
from matplotlib import pyplot as plt 


savedir = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'datapoint') 



def intro(): 

  c4d.cprint('introduction + inteqm() - free fall', 'g') 


  dp = c4d.datapoint(z = 100)
  dt = 1e-2
  t = np.arange(0, 10, dt) 

  for ti in t:
    if dp.z < 0: break
    dp.inteqm([0, 0, -c4d.g_ms2], dt) 
    dp.store(ti)


  dp.plot('z', filename = os.path.join(savedir, 'intro_freefall.png'))


def initials(): 
  c4d.cprint('initial conditions', 'g') 

  dp = c4d.datapoint(x = 1000, vx = -100)
  print(dp.X0)
  # [1000    0    0 -100    0    0]


def mass(): 
  c4d.cprint('mass', 'g') 

  from c4dynamics.eqm import int3 
  '''

  2 Helium balloons of 1kg and 10kg float with total force of L = 0.5N 
  and expreience a side wind of 10k.

  g = 10m/s^2 
  m = 1kg
  F = ma = 10 kg*m/s^2 

  a = 0.5m/s^2 
  m = 1kg 
  F = .5 * .1 = .05 kg*m/s^2 


  theres some problem here with the method to calc eqm 
  with gravity. 
  we know that mass doesnt influence the gravity force 
  and the acceleration is g for any object:
  z = vz0 * t + 0.5 * g * t^2

  now, if we assume some force opposing gravity. say, 5N, then the
  total force is given by:

  F = Flift - Fgravity = 5 - m*g 

  then, when we want to get the acceleration for integration: 
  a = Flift/m - g 

  actually theres no problem.

  '''
  # 
  t1, t2, dt = 0, 10, 0.01
  F = [0, 0, .5]

  hballoon1 = c4d.datapoint(vx = 10 * c4d.k2ms)
  hballoon1.mass = 1 

  hballoon10 = c4d.datapoint(vx = 10 * c4d.k2ms)
  hballoon10.mass = 10 

  for t in np.arange(t1, t2, dt):
    hballoon1.X = int3(hballoon1, F, dt)
    hballoon1.store(t)
    hballoon10.X = int3(hballoon10, F, dt)
    hballoon10.store(t)



  hballoon1.plot('Side')
  hballoon10.plot('Side', ax = plt.gca(), linecolor = 'c', filename = os.path.join(savedir, 'mass_balloon.png'))



def plot(): 
  c4d.cprint('plot', 'g') 

  pt = c4d.datapoint()

  for t in np.arange(0, 10, .01):
    pt.x = 10 + np.random.randn()
    pt.store(t)

  pt.plot('x', filename = os.path.join(savedir, 'plot.png'))



if __name__ == '__main__': 

  intro()
  initials()
  mass()
  plot() 


  plt.show()








