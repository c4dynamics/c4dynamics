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

from c4dynamics.filters import kalman 

savedir = os.path.join(c4path, 'docs', 'source', '_examples', 'kf') 



def nees(kf, train):
  # normalized estimated error squared 

  Ptimes = kf.data('P00')[0]
  err = []
  for t in kf.data('t'):

    xkf = kf.timestate(t)
    xtrain = train.timestate(t)

    idx = min(range(len(Ptimes)), key = lambda i: abs(Ptimes[i] - t))
    P = kf.data('P00')[1][idx]


    xerr = xtrain - xkf
    err.append(xerr**2 / P)  
  return np.mean(err)


def draw_kf(kf, title, trueobj = None, filename = None, measures = True, std = False): 
  # kf.plot('x', filename = c4d.j(savedir, 'x_est.png'))
  # plt.gca().plot(*kf.data('detect'), 'co', markersize = 1, label = 'detection')

  # fig, ax = c4d._figdef()
  # ax.plot(*kf.data('P00'), 'c')
  # c4d.plotdefaults(ax, 'P', 'Time', '')
  # plt.savefig(c4d.j(savedir, 'x_err.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)
  # # plt.show(block = True)


  kf.plot('x')
  plt.gca().plot(*kf.data('detect'), 'co', markersize = 1, label = 'detection')
  plt.gca().legend(**c4d._legdef())


  
  if trueobj: 
    ax = trueobj.plot('x', color = 'w')
    ax.get_lines()[0].set_linewidth(.5)
    ax.get_lines()[0].set_label('train')
  else: 
    _, ax = c4d._figdef()
    

  t, x = kf.data('x')
  ax.plot(t, x, 'm', label = 'est', linewidth = 1)

  if measures: 
    ax.plot(*kf.data('detect'), 'co', markersize = 1, label = 'detection')

  if std: 
    sig1 = np.sqrt(kf.data('P00')[1])
    ax.plot(t, x - sig1, 'w', label = '1 std', linewidth = 1)
    ax.plot(t, x + sig1, 'w', linewidth = 1)

  c4d.plotdefaults(ax, title, 'Time', '')
  plt.legend(**c4d._legdef())
  if filename: 
    plt.savefig(c4d.j(savedir, filename + '.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  _, ax = c4d._figdef()
  ax.plot(*kf.data('K'), 'm', linewidth = .8)
  c4d.plotdefaults(plt.gca(), 'Kalman gain', 't', '')

  plt.show(block = True)



def steadystate(cont = False): 
  # x' = 300
  # x = 0 + 300 * t 
  # xk = xk + 300 
  # A = 0, b = 300, u = dt
  # F = I + A * dt = 1 
  # G = b * dt 
  # xk = xk + 300 * u
  # tgt = c4d.state(x = 0)
  # tgt.v = 1
  v = 150
  sensor_noise = 200 
  if cont: 
    kf = kalman({'x': 0.}, P0 = 0.5**2, A = 0, B = v, C = 1, Q = 0.05, R = sensor_noise**2, steadystate = True, dt = 1)
  else: 
    kf = kalman({'x': 0.}, P0 = 0.5**2, F = 1, G = v, H = 1, Q = 0.05, R = sensor_noise**2, steadystate = True)
    

  

  train = c4d.state(x = 0.)

  
  for t in range(1, 25 + 1): #  seconds. 

    train.store(t)
    train.X += v 



    kf.store(t)

    kf.predict(u = 1) 
    kf.detect = v * t + np.random.randn() * sensor_noise 
    kf.K = kf.update(kf.detect)
    kf.storeparams('detect', t)
    kf.storeparams('K', t)

    if train.X != v * t: raise ValueError('train.X != v * t')


  # kf.store(t)
  # kf.storeparams('detect', t)
  # train.store(t)
  # train.storeparams('measure', t)

  # train.plot('x')
  # plt.gca().plot(*kf.data('x'), linewidth = 1)

  # c4d._figdef()
  # plt.plot(*train.data('measure'), linewidth = 1)
  # c4d.plotdefaults(plt.gca(), 'time', 'train', '')

  return kf, train 


def varying_Q(cont = False): 

  train = c4d.state(x = 0.)
  

  v = 300
  sensor_noise = 20

  kf = kalman({'x': 0.}, P0 = 500**2, F = 1, G = v, H = 1, Q = 0, R = sensor_noise**2)
  kf.detect = 0 
  kf.K = 0
 

  for t in range(1, 25 + 1): #  seconds. 

    process_noise = .1 * t # (1 + t)#(1 + 50 * t * np.random.randn() / v)


    train.store(t)
    train.X += v * (1 + process_noise * np.random.randn())



    kf.store(t)
    kf.storeparams('detect', t)

    kf.predict(u = 1, Q = process_noise**2)
    kf.detect = train.X + np.random.randn() * sensor_noise   # v * t #
    kf.K = kf.update(kf.detect)
    kf.storeparams('K', t)


  # kf.store(t)
  # kf.storeparams('detect', t)
  # train.store(t)
  # train.storeparams('measure', t)

  train.plot('x')
  # plt.gca().plot(*kf.data('x'), linewidth = 1)

  c4d._figdef()
  # plt.plot(*train.data('measure'), linewidth = 1)
  # c4d.plotdefaults(plt.gca(), 'time', 'train', '')

  return kf



def varying_R(): 

  train = c4d.state(x = 0.)
  

  v = 150
  # sensor_noise = 20

  kf = kalman({'x': 0.}, P0 = 0.5**2, F = 1, G = v, H = 1, Q = 0.05)
  # kf = kalman({'x': 1000}, P0 = 1000**2, F = 1, G = v, H = 1, Q = 0.05)


 

  for t in range(1, 25 + 1): #  seconds. 



    train.store(t)
    train.X += v 
    if train.X != v * t: raise ValueError('train.X != v * t')



    kf.store(t)

    sensor_noise = 200 + 8 * t 
    kf.predict(u = 1)
    kf.detect = v * t + np.random.randn() * sensor_noise   # v * t #
    kf.K = kf.update(kf.detect, R = sensor_noise**2) # 1) #
    
    kf.storeparams('detect', t)
    kf.storeparams('K', t)


  # kf.store(t)
  # kf.storeparams('detect', t)
  # train.store(t)
  # train.storeparams('measure', t)

  # train.plot('x')
  # plt.gca().plot(*kf.data('x'), linewidth = 1)

  # c4d._figdef()
  # plt.plot(*train.data('measure'), linewidth = 1)
  # c4d.plotdefaults(plt.gca(), 'time', 'train', '')

  return kf, train


if __name__ == '__main__': 

  kf, train = steadystate() 
  print(nees(kf, train))
  draw_kf(kf, 'Steady State', std = False, trueobj = train, measures = True)
  draw_kf(kf, 'Steady State', filename = 'steadystate')

  kf, _ = steadystate(cont = True) 
  print(nees(kf, train))
  draw_kf(kf, 'cont', std = False, trueobj = train, measures = True)

  kf, train = varying_R() 
  print(nees(kf, train))
  draw_kf(kf, 'Varying R', std = False, trueobj = train, measures = True)
  draw_kf(kf, 'Varying R', filename = 'varying_r')


  # kf, train = varying_Q() 
  # print(nees(kf, train))
  # draw_kf(kf, 'Varying Q', std = False, trueobj = train, measures = True)
  # draw_kf(kf, 'Varying Q', filename = 'varying_q')

