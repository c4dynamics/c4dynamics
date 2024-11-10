# type: ignore

# from scipy.integrate import odeint 
# from scipy.linalg import solve_discrete_are
import numpy as np 
import cv2 
from matplotlib import pyplot as plt 


# not for demonstration: 
import os, sys
from enum import Enum  
import zlib 




plt.style.use('dark_background')  
plt.switch_backend('TkAgg')


def c4dir(dir, addpath = ''):
  # dirname and basename are supplamentary:
  # c:\dropbox\c4dynamics\text.txt
  # dirname: c:\dropbox\c4dynamics
  # basename: text.txt 

  inc4d = os.path.basename(dir) == 'c4dynamics'
  hasc4d = any(f == 'c4dynamics' for f in os.listdir(dir) 
                if os.path.isdir(os.path.join(dir, f)))

  if inc4d and hasc4d: 
    addpath += ''
    return addpath
  
  addpath += '..\\'
  return c4dir(os.path.dirname(dir), addpath)

c4path = c4dir(os.getcwd())

sys.path.append(c4path)


import c4dynamics as c4d 
# from c4dynamics.utils.tictoc import tic, toc 

# from c4dynamics.filters import kalman 

savedir = os.path.join(c4path, 'docs', 'source', '_examples', 'ekf') 



def nees(ekf, train):
  # normalized estimated error squared 

  Ptimes = ekf.data('P00')[0]
  err = []
  for t in ekf.data('t'):

    xkf = ekf.timestate(t)
    xtrain = train.timestate(t)

    idx = min(range(len(Ptimes)), key = lambda i: abs(Ptimes[i] - t))
    P = ekf.data('P00')[1][idx]


    xerr = xtrain - xkf
    err.append(xerr**2 / P)  
  return np.mean(err)


def draw_kf(ekf, title, trueobj = None, filename = None, measures = True, std = False): 
  # ekf.plot('x', filename = c4d.j(savedir, 'x_est.png'))
  # plt.gca().plot(*ekf.data('detect'), 'co', markersize = 1, label = 'detection')

  # fig, ax = c4d._figdef()
  # ax.plot(*ekf.data('P00'), 'c')
  # c4d.plotdefaults(ax, 'P', 'Time', '')
  # plt.savefig(c4d.j(savedir, 'x_err.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)
  # # plt.show(block = True)


  ekf.plot('x')
  plt.gca().plot(*ekf.data('detect'), 'co', markersize = 1, label = 'detection')
  plt.gca().legend(**c4d._legdef())


  
  if trueobj: 
    ax = trueobj.plot('x', color = 'w')
    ax.get_lines()[0].set_linewidth(.5)
    ax.get_lines()[0].set_label('train')
  else: 
    _, ax = c4d._figdef()
    

  t, x = ekf.data('x')
  ax.plot(t, x, 'm', label = 'est', linewidth = 1)

  if measures: 
    ax.plot(*ekf.data('detect'), 'co', markersize = 1, label = 'detection')

  if std: 
    sig1 = np.sqrt(ekf.data('P00')[1])
    ax.plot(t, x - sig1, 'w', label = '1 std', linewidth = 1)
    ax.plot(t, x + sig1, 'w', linewidth = 1)

  c4d.plotdefaults(ax, title, 'Time', '')
  plt.legend(**c4d._legdef())
  if filename: 
    plt.savefig(c4d.j(savedir, filename + '.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  _, ax = c4d._figdef()
  ax.plot(*ekf.data('K'), 'm', linewidth = .8)
  c4d.plotdefaults(plt.gca(), 'Kalman gain', 't', '')

  plt.show(block = True)




def varying_Q(cont = False): 

  train = c4d.state(x = 0)
  

  v = 300
  sensor_noise = 20

  ekf = c4d.filters.ekf({'x': 0}, P0 = 500**2, F = 1, G = v, H = 1, Q = 0, R = sensor_noise**2)
  ekf.detect = 0 
  ekf.K = 0
 

  for t in range(1, 25 + 1): #  seconds. 

    process_noise = .1 * t # (1 + t)#(1 + 50 * t * np.random.randn() / v)


    train.store(t)
    train.X += v * (1 + process_noise * np.random.randn())



    ekf.store(t)
    ekf.storeparams('detect', t)

    ekf.predict(u = 1, Q = process_noise**2)
    ekf.detect = train.X + np.random.randn() * sensor_noise   # v * t #
    ekf.K = ekf.update(ekf.detect)
    ekf.storeparams('K', t)


  # ekf.store(t)
  # ekf.storeparams('detect', t)
  # train.store(t)
  # train.storeparams('measure', t)

  train.plot('x')
  # plt.gca().plot(*ekf.data('x'), linewidth = 1)

  c4d._figdef()
  # plt.plot(*train.data('measure'), linewidth = 1)
  # c4d.plotdefaults(plt.gca(), 'time', 'train', '')

  return ekf



def varying_R(): 

  train = c4d.state(x = 0)
  

  v = 150
  # sensor_noise = 20

  ekf = c4d.filters.ekf({'x': 0}, P0 = 0.5**2, F = 1, G = v, H = 1, Q = 0.05)
  # ekf = c4d.filters.ekf({'x': 1000}, P0 = 1000**2, F = 1, G = v, H = 1, Q = 0.05)


 

  for t in range(1, 25 + 1): #  seconds. 



    train.store(t)
    train.X += v 
    if train.X != v * t: raise ValueError('train.X != v * t')



    ekf.store(t)

    sensor_noise = 200 + 8 * t 
    ekf.predict(u = 1)
    ekf.detect = v * t + np.random.randn() * sensor_noise   # v * t #
    ekf.K = ekf.update(ekf.detect, R = sensor_noise**2) # 1) #
    
    ekf.storeparams('detect', t)
    ekf.storeparams('K', t)


  # ekf.store(t)
  # ekf.storeparams('detect', t)
  # train.store(t)
  # train.storeparams('measure', t)

  # train.plot('x')
  # plt.gca().plot(*ekf.data('x'), linewidth = 1)

  # c4d._figdef()
  # plt.plot(*train.data('measure'), linewidth = 1)
  # c4d.plotdefaults(plt.gca(), 'time', 'train', '')

  return ekf, train


if __name__ == '__main__': 

  ekf, train = varying_R() 
  print(nees(ekf, train))
  draw_kf(ekf, 'Varying R', std = False, trueobj = train, measures = True)
  draw_kf(ekf, 'Varying R', filename = 'varying_q')

