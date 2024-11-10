# type: ignore

import sys, os 
sys.path.append('.')
import c4dynamics as c4d
from c4dynamics.utils.tictoc import * 

import numpy as np 
from matplotlib import pyplot as plt 

datasetdir = os.path.join(os.getcwd(), 'datasets')  
savedir = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'seeker') 

factorsize = 4
aspectratio = 1080 / 1920 



def constructor(): 

  c4d.cprint('Constructor', 'y')
  ## constructor 

  # pt = c4d.datapoint()
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
  skr = c4d.sensors.seeker(origin = pedestal, isideal = True)
  # methods = [attr for attr in dir(c4d.sensors.seeker) if callable(getattr(c4d.sensors.seeker, attr))]
  # Print the list of methods
  # print(methods)
  print(skr.measure(c4d.datapoint(), store = False))
  # (array([3.14159265]), array([-1.55334303]))
  print(skr.bias)
  # 0.0


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
  ax.text(-35, -150, 'seeker', color = 'blue', fontsize = 8, verticalalignment = 'bottom')
  ax.text(75, 500, 'target', color = 'magenta', fontsize = 8)
  plt.savefig(c4d.j(savedir, 'target.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  return tgt 


def ideal(tgt): 

  c4d.cprint('ideal seeker', 'y')
  ''' ideal seeker '''
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  # seeker position and attitude
  skr_ideal = c4d.sensors.seeker(origin = pedestal, isideal = True)
  # measure the target position
  for x in tgt.data():
    skr_ideal.measure(c4d.create(x[1:]), t = x[0], store = True)


  fig, axs = plt.subplots(2, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('ideal')

  dx =  tgt.data('x')[1] - skr_ideal.x
  dy =  tgt.data('y')[1] - skr_ideal.y
  dz =  tgt.data('z')[1] - skr_ideal.z

  # iscorrect = np.where(np.vectorize(lambda x: x.value)(v.data('state')[1]) == Trkstate.CORRECTED.value)[0]
  # Xb = np.vectorize(lambda tgtX: skr_ideal.BR @ [tgtX[1] - skr_ideal.x, tgtX[2] - skr_ideal.y, tgtX[3] - skr_ideal.z])(tgt.data())
  Xb = np.array([skr_ideal.BR @ [X[1] - skr_ideal.x, X[2] - skr_ideal.y, X[3] - skr_ideal.z] for X in tgt.data()])


  axs[0].plot(tgt.data('t'), c4d.atan2d(Xb[:, 1], Xb[:, 0]), 'm', linewidth = 2, label = 'target')
  axs[0].plot(*skr_ideal.data('az', scale = c4d.r2d), 'c', linewidth = 1, label = 'seeker')
  c4d.plotdefaults(axs[0], '', '', 'Azimuth (deg)', 8)
  axs[0].legend(fontsize = 4, facecolor = None, loc = 'upper left')

  axs[1].plot(tgt.data('t'), c4d.atan2d(Xb[:, 2], c4d.sqrt(Xb[:, 0]**2 + Xb[:, 1]**2)), 'm', linewidth = 2)
  axs[1].plot(*skr_ideal.data('el', scale = c4d.r2d), 'c', linewidth = 1)
  c4d.plotdefaults(axs[1], '', 'Time (s)', 'Elevation (deg)', 8)

  plt.savefig(c4d.j(savedir, 'ideal.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  return skr_ideal 


def nonideal(tgt, skr_ideal): 
  c4d.cprint('non-ideal seeker', 'y')
  ''' non-ideal seeker'''

  # print(np.random.randn)
  np.random.seed(42)
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
  skr = c4d.sensors.seeker(origin = pedestal)
  # measure the target position
  # measured_angles = []


  for x in tgt.data():
    # measured_angles.append(skr.measure(c4d.create(x[1:]))[:2])
    skr.measure(c4d.create(x[1:]), t = x[0], store = True)



  print(f'{ skr.bias * c4d.r2d }')
  #  -0.01
  print(f'{ skr.scale_factor}')
  # 1.02
  print(f'{ skr.noise_std * c4d.r2d }')
  # .4

  fig, axs = plt.subplots(2, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('non-ideal+measure')

  axs[0].plot(*skr_ideal.data('az', scale = c4d.r2d), 'm', linewidth = 1, label = 'ideal', zorder = 12)
  axs[0].plot(*skr.data('az', scale = c4d.r2d), 'c', linewidth = 1, label = 'non-ideal', zorder = 11)
  c4d.plotdefaults(axs[0], '', '', 'Azimuth (deg)', 8)
  axs[0].legend(fontsize = 4, facecolor = None)

  axs[1].plot(*skr_ideal.data('el', scale = c4d.r2d), 'm', linewidth = 1, zorder = 12)
  axs[1].plot(*skr.data('el', scale = c4d.r2d), 'c', linewidth = 1, zorder = 11)
  c4d.plotdefaults(axs[1], '', 'Time (s)', 'Elevation (deg)', 8)

  plt.savefig(c4d.j(savedir, 'nonideal.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def yawing(tgt, skr_ideal): 

  c4d.cprint('yawing seeker', 'y')
  ''' yawing seeker '''
      
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
  skr = c4d.sensors.seeker(origin = pedestal)




  print(f'{ skr.bias * c4d.r2d :.2f}')
  # -.01
  print(f'{ skr.scale_factor :.2f}')
  # .96
  print(f'{ skr.noise_std * c4d.r2d :.2f}')
  # .4 


  for x in tgt.data():
    skr.psi += .02 * c4d.d2r 
    skr.measure(c4d.create(x[1:]), t = x[0], store = True)
    skr.store(x[0])

  skr.plot('psi', filename = c4d.j(savedir, 'psi.png'))

  fig, axs = plt.subplots(2, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('yawing')

  axs[0].plot(*skr_ideal.data('az', c4d.r2d), 'm', linewidth = 1, label = 'ideal static seeker', zorder = 12)
  axs[0].plot(*skr.data('az', c4d.r2d), 'c', linewidth = 1, label = 'non-ideal yawing seeker', zorder = 11)
  c4d.plotdefaults(axs[0], '', '', 'Azimuth (deg)', 8)
  axs[0].legend(fontsize = 4, facecolor = None)


  axs[1].plot(*skr_ideal.data('el', scale = c4d.r2d), 'm', linewidth = 1, zorder = 12)
  axs[1].plot(*skr.data('el', scale = c4d.r2d), 'c', linewidth = 1, zorder = 11)
  c4d.plotdefaults(axs[1], '', 'Time (s)', 'Elevation (deg)', 8)

  plt.savefig(c4d.j(savedir, 'yawing.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def dt(): 

  c4d.cprint('dt', 'y')
  ''' dt '''

  np.random.seed(770)

  tgt1 = c4d.datapoint(x = 100, y = 100)
  skr = c4d.sensors.seeker(dt = 0.01)
  for t in np.arange(0, .025, .005):
    print(f'{t}: {skr.measure(tgt1, t = t)}')
  # 0.0: (0.7325279510815786, 0.007487690440959094)
  # 0.005: (None, None)
  # 0.01: (0.7316160225965218, 0.0006844339202759578)
  # 0.015: (None, None)
  # 0.02: (0.7185263968437489, 0.006279255919993379)


def bias1(tgt): 

  c4d.cprint('bias1', 'y')
  ## bias 
  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  skr = c4d.sensors.seeker(origin = pedestal, scale_factor_std = 0, noise_std = 0)
  skr.bias = .5 * c4d.d2r 

  for i, x in enumerate(tgt.data()):
                        # 0 1 2 3 4  5  6  7   8     9   
    dx1 =  x[1] - skr.x # t x y z vx vy vz phi theta psi p q r 
    dy1 =  x[2] - skr.y
    dz1 =  x[3] - skr.z
    xb = skr.BR @ [dx1, dy1, dz1]
    az1 = np.arctan2(xb[1], xb[0])
    el1 = np.arctan2(xb[2], np.sqrt(xb[0]**2 + xb[1]**2))

    az2, el2 = skr.measure(c4d.create(x[1:]), t = x[0], store = True)

    if np.abs(el1 - el2) < .01 * c4d.d2r or np.abs(az1 - az2) < .01 * c4d.d2r:
      print(f'{i} t = {x[0]} :    del {np.abs(el1 - el2) * c4d.r2d}   daz {np.abs(az1 - az2) * c4d.r2d}')

  print(f'{ skr.bias * c4d.r2d :.2f}')
  # .5
  print(f'{ skr.scale_factor :.2f}')
  # 1
  print(f'{ skr.noise_std * c4d.r2d :.2f}')
  # .00 

  fig, axs = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('bias1')

  axs.plot(*skr_ideal.data('el', scale = c4d.r2d), 'm', linewidth = 1, zorder = 12, label = 'target')
  axs.plot(*skr.data('el', scale = c4d.r2d), 'c', linewidth = 1, zorder = 11, label = 'seeker')
  c4d.plotdefaults(axs, '', 'Time (s)', 'Elevation (deg)', 8)
  axs.legend(fontsize = 4, facecolor = None)

  plt.savefig(c4d.j(savedir, 'bias1.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def bias2(): 

  c4d.cprint('bias2', 'y')

  seekers_type_A = []
  seekers_type_B = []
  B_std = 0.5 * c4d.d2r

  for i in range(1000):
    seekers_type_A.append(c4d.sensors.seeker().bias * c4d.r2d)
    seekers_type_B.append(c4d.sensors.seeker(bias_std = B_std).bias * c4d.r2d)

  # Plot the histogram
  fig, ax = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio) , gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('bias 2')

  ax.hist(seekers_type_A, 30, facecolor = 'magenta', edgecolor = 'black', label = 'Type A', zorder = 12, alpha = 1)
  ax.hist(seekers_type_B, 30, facecolor = 'cyan'   , edgecolor = 'black', label = 'Type B', zorder = 11, alpha = 1) 
  c4d.plotdefaults(ax, 'Seeker Type vs Bias std', 'Values', 'Frequency', 8)
  ax.legend(fontsize = 4, facecolor = None)

  plt.savefig(c4d.j(savedir, 'bias2.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def SF(tgt): 
  c4d.cprint('SF', 'y')
  ## scale factor 

  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)
  skr = c4d.sensors.seeker(origin = pedestal, bias_std = 0, noise_std = 0)
  skr.scale_factor = 1.2

  print(f'{ skr.bias * c4d.r2d :.2f}')
  # .00
  print(f'{ skr.scale_factor :.2f}')
  #  1.2
  print(f'{ skr.noise_std :.2f}')
  # .01 

  for x in tgt.data():
    skr.measure(c4d.create(x[1:]), t = x[0], store = True)  
    

  fig, axs = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('sf')

  axs.plot(*skr_ideal.data('az', scale = c4d.r2d), 'm', linewidth = 1, zorder = 12, label = 'target')
  axs.plot(*skr.data('az', scale = c4d.r2d), 'c', linewidth = 1, zorder = 11, label = 'seeker')
  c4d.plotdefaults(axs, '', 'Time (s)', 'Azimuth (deg)', 8)
  axs.legend(fontsize = 4, facecolor = None)

  plt.savefig(c4d.j(savedir, 'sf.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


def measure(tgt): 
  c4d.cprint('measure', 'y')


  np.random.seed(321)
  dt = .01
  tgt = c4d.datapoint(x = 1000, vx = -80 * c4d.kmh2ms, vy = 10 * c4d.kmh2ms)

  pedestal = c4d.rigidbody(z = 30, theta = -1 * c4d.d2r)

  skr = c4d.sensors.seeker(origin = pedestal, dt = 0.05)
  # skr.bias = -0.02 * c4d.d2r
  # skr.scale_factor = .95

  skr_ideal = c4d.sensors.seeker(origin = pedestal, isideal = True)



  print(f'{ skr.bias * c4d.r2d }')
  # 0.16
  print(f'{ skr.scale_factor }')
  # 1
  print(f'{ skr.noise_std * c4d.r2d}')
  # 0.4

  for t in np.arange(0, 60, dt):
    tgt.inteqm(np.zeros(3), dt)
    skr_ideal.measure(tgt, t = t, store = True)  
    skr.measure(tgt, t = t, store = True)  
    tgt.store(t)


  fig, ax = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'hspace': 0.5, 'top': .9, 'bottom': .2})
  fig.canvas.manager.set_window_title('measure')

  l1 = ax.plot(*skr_ideal.data('az', scale = c4d.r2d), '.m', markersize = 1, label = 'target')
  l2 = ax.plot(*skr.data('az', scale = c4d.r2d), '.c', markersize = 1, label = 'seeker')
  c4d.plotdefaults(ax, '', '', 'Azimuth (deg)', 8)
  ax.legend(fontsize = 4, facecolor = None)
  plt.savefig(c4d.j(savedir, 'measure.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  for l in l1 + l2: 
    l.set_markersize(4)
  ax.set_xlim(10, 11)
  ax.set_ylim(-.5, 3.5)
  ax.legend(fontsize = 4, facecolor = None)
  plt.savefig(c4d.j(savedir, 'measure_zoom.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)




if __name__ == '__main__': 

  # constructor()
  tgt = target() 
  skr_ideal = ideal(tgt)
  # nonideal(tgt, skr_ideal)
  # yawing(tgt, skr_ideal)
  # dt()
  # bias1(tgt)
  # bias2()
  # SF(tgt)
  measure(tgt) 

  # plt.show()







