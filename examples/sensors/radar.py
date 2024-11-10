# type: ignore

import sys, os 
sys.path.append('.')
import c4dynamics as c4d

# import c4dynamics as c4d
from c4dynamics.utils.tictoc import * 

import numpy as np 
# import os 
from matplotlib import pyplot as plt 
# from matplotlib.transforms import Bbox
# from matplotlib.widgets import Cursor, Button
# from matplotlib import pyplot as plt 

from scipy.integrate import odeint 
plt.style.use('dark_background')  
plt.switch_backend('TkAgg')
from matplotlib.ticker import ScalarFormatter

# from PIL import Image
# import cProfile 


savedir = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'radar') 


factorsize = 4
aspectratio = 1080 / 1920 


def intro(): 

  c4d.cprint('intro', 'y')

  dt, tf = 0.01, 50  
  tspan = np.arange(dt, tf, dt)  
  dtsensor = 0.02 

  Hf = 1000 
  z0 = Hf + 10 
  gamma0 = 0

  A = np.array([[0, 5], [0, -0.5]])
  b = np.array([0, 0.1])
  c = np.array([1, 0])

  tgt = c4d.state(z = z0, gamma = gamma0)
  altmtr = c4d.sensors.radar(rng_noise_std = .5, dt = dtsensor)

  def autopilot(y, t, u = 0):
    return A @ y + b * u

  for t in tspan:
    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    if Z is not None: 
      tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - Z,))[-1]

    tgt.store(t)
    
  textsize = 10
  fig, ax = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio)
                          , gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})

  ax.plot(*tgt.data('z'), 'c', linewidth = 2, label = 'true', zorder = 2) 
  ax.plot(*altmtr.data('range'), '.m', markersize = 1, label = 'altmeter', zorder = 1)

  c4d.plotdefaults(ax, 'Altitude', 't', 'ft', textsize)
  ax.legend(fontsize = 'xx-small', facecolor = None, framealpha = .5)  #, edgecolor = None Set font size and legend box properties


def target(): 

  c4d.cprint('target', 'y')
  ## target 

  ''' generate target trajectory '''
  dt = .01 
  tgt = c4d.datapoint(x = 1000, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)
  for t in np.arange(0, 60, dt):
    tgt.inteqm(np.zeros(3), dt)
    tgt.store(t)

  tgt.plot('top')
  ax = plt.gca()
  ax.set_xlim(-50, 250)
  ax.scatter(0, 0, color = 'blue', marker = '1', s = 90, zorder = 2)
  ax.text(-35, -150, 'radar', color = 'blue', fontsize = 8, verticalalignment = 'bottom')
  ax.text(75, 500, 'target', color = 'magenta', fontsize = 8)
  plt.savefig(c4d.j(savedir, 'target.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  return tgt


def ideal(tgt): 

  c4d.cprint('ideal radar', 'y')
  ''' ideal radar '''
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  # radar position and attitude
  rdr_ideal = c4d.sensors.radar(origin = pedestal, isideal = True)
  # measure the target position
  for x in tgt.data():
    rdr_ideal.measure(c4d.create(x[1:]), t = x[0], store = True)


  fig, axs = plt.subplots(2, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('ideal')

  dx =  tgt.data('x')[1] - rdr_ideal.x
  dy =  tgt.data('y')[1] - rdr_ideal.y
  dz =  tgt.data('z')[1] - rdr_ideal.z

  # iscorrect = np.where(np.vectorize(lambda x: x.value)(v.data('state')[1]) == Trkstate.CORRECTED.value)[0]
  # Xb = np.vectorize(lambda tgtX: rdr_ideal.BR @ [tgtX[1] - rdr_ideal.x, tgtX[2] - rdr_ideal.y, tgtX[3] - rdr_ideal.z])(tgt.data())
  Xb = np.array([rdr_ideal.BR @ [X[1] - rdr_ideal.x, X[2] - rdr_ideal.y, X[3] - rdr_ideal.z] for X in tgt.data()])


  axs[0].plot(tgt.data('t'), c4d.norm(Xb, axis = 1), 'm', label = 'target', linewidth = 2)
  axs[0].plot(*rdr_ideal.data('range'), 'c', label = 'radar', linewidth = 1)

  axs[0].legend(fontsize = 4, facecolor = None, loc = 'upper left')
  c4d.plotdefaults(axs[0], '', '', 'Range (m)', 8)



  axs[1].plot(tgt.data('t'), c4d.atan2d(Xb[:, 1], Xb[:, 0]), 'm', label = 'target azimuth', linewidth = 2)
  axs[1].plot(*rdr_ideal.data('az', scale = c4d.r2d), 'c', label = 'radar azimuth', linewidth = 1)

  axs[1].plot(tgt.data('t'), c4d.atan2d(Xb[:, 2], c4d.sqrt(Xb[:, 0]**2 + Xb[:, 1]**2)), 'r', label = 'target elevation', linewidth = 2)
  axs[1].plot(*rdr_ideal.data('el', scale = c4d.r2d), 'y', label = 'radar elevation', linewidth = 1)

  axs[1].legend(fontsize = 4, facecolor = None, loc = 'upper left')
  c4d.plotdefaults(axs[1], '', 'Time (s)', 'Angles (deg)', 8)


  plt.savefig(c4d.j(savedir, 'ideal.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  return rdr_ideal


def nonideal(tgt, rdr_ideal): 



  c4d.cprint('non-ideal radar', 'y')
  ''' non-ideal radar'''

  np.random.seed(61)
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
  # print(np.random.randn)
  rdr = c4d.sensors.radar(origin = pedestal)
  # measure the target position
  # measured_angles = []

  # rdr.rng_noise_std = 3
  # rdr.bias = .4 * c4d.d2r
  # rdr.scale_factor = 1.07

  for x in tgt.data():
    # measured_angles.append(rdr.measure(c4d.create(x[1:]))[:2])
    rdr.measure(c4d.create(x[1:]), t = x[0], store = True)


  print(f'{ rdr.rng_noise_std = }')
  # 3
  print(f'{ rdr.bias * c4d.r2d =}')
  # .4
  print(f'{ rdr.scale_factor =}')
  # 1.07
  print(f'{ rdr.noise_std * c4d.r2d =}')
  # .8



  fig, axs = plt.subplots(2, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('non-ideal+measure')



  axs[0].plot(*rdr_ideal.data('range'), 'm', linewidth = 1, label = 'target', zorder = 12)
  axs[0].plot(*rdr.data('range'), 'c', linewidth = 1, label = 'radar', zorder = 11)

  axs[0].legend(fontsize = 4, facecolor = None)
  c4d.plotdefaults(axs[0], '', '', 'Range (m)', 8)


  axs[1].plot(*rdr_ideal.data('az', scale = c4d.r2d), 'm', linewidth = 1, label = 'target azimuth', zorder = 12)
  axs[1].plot(*rdr.data('az', scale = c4d.r2d), 'c', linewidth = 1, label = 'radar azimuth', zorder = 11)

  axs[1].plot(*rdr_ideal.data('el', scale = c4d.r2d), 'r', linewidth = 1, zorder = 12, label = 'target elevation')
  axs[1].plot(*rdr.data('el', scale = c4d.r2d), 'y', linewidth = 1, zorder = 11, label = 'radar elevation')

  axs[1].legend(fontsize = 4, facecolor = None)
  c4d.plotdefaults(axs[1], '', 'Time (s)', 'Angles (deg)', 8)

  plt.savefig(c4d.j(savedir, 'nonideal.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def yawing(tgt, rdr_ideal): 
    
  c4d.cprint('yawing radar', 'y')
  ''' yawing radar '''
      
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  rdr = c4d.sensors.radar(origin = pedestal)


  print(f'{ rdr.rng_noise_std :.2f}')
  # 1
  print(f'{ rdr.bias * c4d.r2d :.2f}')
  # -.5
  print(f'{ rdr.scale_factor :.2f}')
  # 1.07
  print(f'{ rdr.noise_std * c4d.r2d  :.2f}')
  # .8


  for x in tgt.data():
    rdr.psi += .02 * c4d.d2r 
    rdr.measure(c4d.create(x[1:]), t = x[0], store = True)
    rdr.store(x[0])

  rdr.plot('psi', filename = c4d.j(savedir, 'psi.png'))

  fig, axs = plt.subplots(2, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('yawing')


  axs[0].plot(*rdr_ideal.data('range'), 'm', linewidth = 1, label = 'ideal static', zorder = 12)
  axs[0].plot(*rdr.data('range'), 'c', linewidth = 1, label = 'non-ideal yawing', zorder = 11)
  c4d.plotdefaults(axs[0], '', '', 'Range (m)', 8)
  axs[0].legend(fontsize = 4, facecolor = None)



  axs[1].plot(*rdr_ideal.data('az', c4d.r2d), 'm', linewidth = 1, label = 'az: ideal static', zorder = 12)
  axs[1].plot(*rdr.data('az', c4d.r2d), 'c', linewidth = 1, label = 'az: non-ideal yawing', zorder = 11)

  axs[1].plot(*rdr_ideal.data('el', scale = c4d.r2d), 'r', label = 'el: ideal static', linewidth = 1, zorder = 12)
  axs[1].plot(*rdr.data('el', scale = c4d.r2d), 'y', label = 'el: non-ideal yawing', linewidth = 1, zorder = 11)

  axs[1].legend(fontsize = 4, facecolor = None, loc = 'upper left')
  c4d.plotdefaults(axs[1], '', 'Time (s)', 'Angles (deg)', 8)

  plt.savefig(c4d.j(savedir, 'yawing.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def timestep(tgt): 



  c4d.cprint('dt', 'y')
  ''' dt '''

  np.random.seed(770)
  tgt1 = c4d.datapoint(x = 100, y = 100)
  rdr = c4d.sensors.radar(dt = 0.01)
  for t in np.arange(0, .025, .005):
    print(f'{t}: {rdr.measure(tgt1, t = t)}')
  # 0.0: (0.7081153512624399, 0.0159259075895469, 140.14831212305964)
  # 0.005: (None, None, None)
  # 0.01: (0.723534357771057, -0.041102720436096044, 142.18464047240093)
  # 0.015: (None, None, None)
  # 0.02: (0.7213310832643385, -0.0037291551253552093, 140.46066042042435)

  c4d.cprint('bias2', 'y')


  from c4dynamics.sensors import seeker, radar 
  seekers = []
  radars = []

  for _ in range(1000):
    seekers.append(seeker().bias * c4d.r2d)
    radars.append(radar().bias * c4d.r2d)

  # Plot the histogram
  fig, ax = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio) , gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('bias 2')

  ax.hist(seekers, 30, facecolor = 'magenta', edgecolor = 'black', label = 'Seekers', zorder = 12, alpha = 1)
  ax.hist(radars, 30, facecolor = 'cyan'   , edgecolor = 'black', label = 'Radars', zorder = 11, alpha = 1) 
  c4d.plotdefaults(ax, '$σ_{Bias}$ Radar vs Seeker', 'Values', 'Frequency', 8)
  ax.legend(fontsize = 4, facecolor = None)

  plt.savefig(c4d.j(savedir, 'bias2.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def measure(tgt): 



  c4d.cprint('measure', 'y')

  dt = .01

  np.random.seed(321)
  tgt = c4d.datapoint(x = 1000, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)

  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  rdr = c4d.sensors.radar(origin = pedestal, dt = 0.05)

  # rdr.bias = -0.025 * c4d.d2r
  # rdr.scale_factor = .99

  rdr_ideal = c4d.sensors.radar(origin = pedestal, isideal = True)


  print(f'{ rdr.rng_noise_std = }')
  # 1
  print(f'{ rdr.bias * c4d.r2d  = }')
  # -.03
  print(f'{ rdr.scale_factor = }')
  # .99
  print(f'{ rdr.noise_std * c4d.r2d :.2f}')
  # .8

  for t in np.arange(0, 60, dt):
    tgt.inteqm(np.zeros(3), dt)
    rdr_ideal.measure(tgt, t = t, store = True)  
    rdr.measure(tgt, t = t, store = True)  
    tgt.store(t)


  fig, axs = plt.subplots(2, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('measure')

  l0i  = axs[0].plot(*rdr_ideal.data('range'), '.m', markersize = 1, label = 'target')
  l0ni = axs[0].plot(*rdr.data('range'), '.c', markersize = 1, label = 'radar')
  axs[0].legend(fontsize = 4, facecolor = None)
  c4d.plotdefaults(axs[0], '', '', 'Range (m)', 8)

  l1 = axs[1].plot(*rdr_ideal.data('az', scale = c4d.r2d), '.m', markersize = 1, label = 'target')
  l2 = axs[1].plot(*rdr.data('az', scale = c4d.r2d), '.c', markersize = 1, label = 'radar')
  c4d.plotdefaults(axs[1], '', '', 'Azimuth (deg)', 8)
  axs[1].legend(fontsize = 4, facecolor = None)
  plt.savefig(c4d.j(savedir, 'measure.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)



  for l in l1 + l2 + l0i + l0ni: 
    l.set_markersize(4)

  axs[0].set_xlim(10, 11)
  axs[0].set_ylim(760, 780)
  axs[0].legend(fontsize = 4, facecolor = None)

  axs[1].set_xlim(10, 11)
  axs[1].set_ylim(-.5, 3.5)
  axs[1].legend(fontsize = 4, facecolor = None)
  plt.savefig(c4d.j(savedir, 'measure_zoom.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)




  plt.show(block = True)


def bias1(tgt): 


  c4d.cprint('bias1', 'y')
  ## bias 
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  rdr = c4d.sensors.radar(origin = pedestal, scale_factor_std = 0, noise_std = 0)
  rdr.bias = .5 * c4d.d2r 

  for i, x in enumerate(tgt.data()):
                        # 0 1 2 3 4  5  6  7   8     9   
    dx1 =  x[1] - rdr.x # t x y z vx vy vz phi theta psi p q r 
    dy1 =  x[2] - rdr.y
    dz1 =  x[3] - rdr.z

    az, el, rng = rdr.measure(c4d.create(x[1:]), t = x[0], store = True)

  print(f'{ rdr.rng_noise_std :.2f}')
  # 
  print(f'{ rdr.bias * c4d.r2d :.2f}')
  # .5
  print(f'{ rdr.scale_factor :.2f}')
  # 1
  print(f'{ rdr.noise_std :.2f}')
  # .00 

  fig, axs = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('bias1')

  axs.plot(*rdr_ideal.data('el', scale = c4d.r2d), 'm', linewidth = 1, zorder = 12, label = 'target')
  axs.plot(*rdr.data('el', scale = c4d.r2d), 'c', linewidth = 1, zorder = 11, label = 'radar')
  c4d.plotdefaults(axs, '', 'Time (s)', 'Elevation (deg)', 8)
  axs.legend(fontsize = 'xx-small', facecolor = None)

  plt.savefig(c4d.j(savedir, 'bias1.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def SF(tgt): 

  c4d.cprint('SF', 'y')
  ## scale factor 
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  rdr = c4d.sensors.radar(origin = pedestal, bias_std = 0, noise_std = 0)
  rdr.scale_factor = 1.2

  print(f'{ rdr.bias * c4d.r2d :.2f}')
  # .00
  print(f'{ rdr.scale_factor :.2f}')
  #  1.2
  print(f'{ rdr.noise_std :.2f}')
  # .01 

  for x in tgt.data():
    rdr.measure(c4d.create(x[1:]), t = x[0], store = True)  
    

  fig, axs = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('sf')

  axs.plot(*rdr_ideal.data('az', scale = c4d.r2d), 'm', linewidth = 1, zorder = 12, label = 'target')
  axs.plot(*rdr.data('az', scale = c4d.r2d), 'c', linewidth = 1, zorder = 11, label = 'radar')
  c4d.plotdefaults(axs, '', 'Time (s)', 'Azimuth (deg)', 8)
  axs.legend(fontsize = 'xx-small', facecolor = None)

  plt.savefig(c4d.j(savedir, 'sf.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


if __name__ == '__main__': 

  intro()
  tgt = target()
  rdr_ideal = ideal(tgt)
  nonideal(tgt, rdr_ideal)
  yawing(tgt, rdr_ideal)
  timestep(tgt)
  measure(tgt)
  bias1(tgt)
  SF(tgt)





