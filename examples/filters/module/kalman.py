# type: ignore

import numpy as np 
from scipy.integrate import odeint 

from matplotlib import pyplot as plt 
plt.style.use('dark_background')  
plt.switch_backend('TkAgg')

import os, sys
sys.path.append('')

import c4dynamics as c4d 

from scipy.linalg import solve_discrete_are
from enum import Enum  


savedir = os.path.join(c4d.c4dir(os.getcwd()), 'docs', 'source', '_examples', 'filters') 

def kalman_is_state(): 
  from c4dynamics.filters import kalman 
  z = np.zeros((2, 2))
  kf = kalman(X = {'x1': 0, 'x2': 0}, P0 = z, F = z, H = z, Q = z, R = z)
  print(kf)



dt, tf = 0.01, 50  
tspan = np.arange(0, tf + dt, dt)  
dtsensor = dt# * 2 # 0.02 # .01# 

Hf = 1000 
z0 = Hf + 10 
gamma0 = 0

A = np.array([[0, 5], [0, -0.5]])
B = np.array([0, 0.1])
C = np.array([1, 0])



w1 = .5 # ft. - 1std; np.sqrt(.5) # w1 = 0.3, 1std; Q11 = 0.1, variance.  
w2 = .1 * c4d.d2r # 0 # .1 * c4d.d2r # deg. - 1std; np.sqrt(.3 * c4d.d2r) # w2 = 1, 1std; Q22 = 1 variance. 
nu  = 1 # 0 # .1 # .5 # 0 # std: nu = .1, variance: R = .01


''' Tests if the system (A, C) is observable. '''
n = A.shape[0]
obsv = C
for i in range(1, n):
  obsv = np.vstack((obsv, C @ np.linalg.matrix_power(A, i)))
# Compute the rank of the observability matrix
rank = np.linalg.matrix_rank(obsv)
c4d.cprint(f'The system is observable (rank = n = {n}).' if rank == n else 'The system is not observable (rank = {rank), n = {n}).', 'y')





def drawkf(kf = None, trueobj = None, measures = None, title = '', filename = None, std = False): 
  
  from matplotlib.ticker import ScalarFormatter
  textsize = 10

  # pdb.set_trace()
  fig, ax = plt.subplots(1, 2, dpi = 200, figsize = (6, 3) #  # figsize = (8, 2) # 
                # , gridspec_kw = {'hspace': 0.5, 'wspace': 0.3})#)
                  , gridspec_kw = {'left': .15, 'right': .95
                                    , 'top': .85 , 'bottom': .15
                                      , 'hspace': 0.5, 'wspace': 0.3}) 
  fig.suptitle('        ' + title, fontsize = 14, fontname = 'Times New Roman')
  plt.subplots_adjust(top = 0.95)  # Adjust for suptitle space





  if trueobj: 
    ax[0].plot(*trueobj.data('z'), 'm', linewidth = 1.2, label = 'true', zorder = 2) 

  if measures: 
    ax[0].plot(*measures.data('range'), '.c', markersize = 1, label = 'altmeter', zorder = 1)

  # ax[0].plot(*htgt.data('z'), 'y', linewidth = 1, label = 'estimation')

  if kf: 
    ax[0].plot(*kf.data('z'), linewidth = 1, color = 'y', label = 'kf')


  if std: 
    x = kf.data('z')[1]
    t_sig, x_sig = kf.data('P00') 
    # ±std 
    ax[0].plot(t_sig, x + np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
    ax[0].plot(t_sig, x - np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w') # np.array(v.color) / 255)
    # correct
    # ax[0].plot(t_sig[iscorrect], x[iscorrect], linewidth = 0, color = color
    #                       , marker = 'o', markersize = 2, markerfacecolor = 'none', label = 'correct') 

  # ax[0].set_ylim((995, 1012))
 


  c4d.plotdefaults(ax[0], 'Altitude', 'Time (s)', '(ft)', textsize)
  ax[0].legend(fontsize = 'xx-small', facecolor = None, framealpha = .5)  #, edgecolor = None Set font size and legend box properties

  # ax[0].yaxis.set_major_formatter(ScalarFormatter())
  # ax[0].yaxis.get_major_formatter().set_useOffset(False)
  # ax[0].yaxis.get_major_formatter().set_scientific(False)




  ''' path angle ''' 

  if trueobj: 
    ax[1].plot(*trueobj.data('gamma', c4d.r2d), 'm', linewidth = 1.2, label = 'true') # label = r'$\gamma$') #'\\gamma') # 
    # ax[1].plot(*htgt.data('gamma', c4d.r2d), 'y', linewidth = 1, label = 'estimation') # r'$\\hat{\\varphi}$'

  if kf: 
    # ax[0].plot(t_sig, x, linewidth = 1, color = 'y', label = 'kf')
    ax[1].plot(*kf.data('gamma', c4d.r2d), linewidth = 1, color = 'y', label = 'kf')

  if std: 
    x = kf.data('gamma')[1]
    t_sig, x_sig = kf.data('P11') 
    # ±std 
    ax[1].plot(t_sig, (x + np.sqrt(x_sig.squeeze())) * c4d.r2d, linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
    ax[1].plot(t_sig, (x - np.sqrt(x_sig.squeeze())) * c4d.r2d, linewidth = 1, color = 'w') # np.array(v.color) / 255)
    # state
    # ax[1].plot(t_sig[iscorrect], x[iscorrect] * c4d.r2d, linewidth = 0, color = 'w'
    #                     , marker = '.', markersize = 2, markerfacecolor = 'none', label = 'correct') 

  c4d.plotdefaults(ax[1], 'Path Angle', 'Time (s)', '(deg)', textsize)
  # ax[1].legend(fontsize = 'small', facecolor = None)



  if filename: 
    # fig.tight_layout()

    # pad_left = 0.1
    # pad_others = 0.2
    fig.savefig(c4d.j(savedir, filename + '.png')
                  # , bbox_inches = np.array([pad_left, pad_others, 1 - pad_others, 1 - pad_others])
                    , pad_inches = 0.2, dpi = 600)



  plt.show(block = True)

from scipy.integrate import solve_ivp


def autopilot(y, t, u = 0, q = np.zeros((2, 2))): # w = np.zeros(2)):
  # return A @ y + B * u + w
  return A @ y + B * u + q @ np.random.randn(2)

def autopilot_ivp(t, y, u = 0, q = np.zeros((2, 2))): # w = np.zeros(2)):
  # return A @ y + B * u + w
  return A @ y + B * u + q @ np.random.randn(2)


def ideal():
  ''' ideal '''
  process_noise = np.zeros((2, 2))
  ''' true target ''' 
  tgt = c4d.state(z = z0, gamma = gamma0)
  # tgt.store(0) 


  altmtr = c4d.sensors.radar(isideal = True, dt = dtsensor)

  for t in tspan:
    tgt.store(t)

    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    if Z is not None:   
      tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - Z, process_noise @ np.random.randn(2)))[-1]

    
  return tgt, altmtr
  

def noisy():
  ''' noisy no kalman ''' 
  process_noise = np.diag([w1, w2])

  tgt = c4d.state(z = z0, gamma = gamma0)


  altmtr = c4d.sensors.radar(rng_noise_std = nu, dt = dtsensor)

  for t in tspan:
    tgt.store(t)

    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    if Z is not None: 
      tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - Z, process_noise @ np.random.randn(2)))[-1]

  
  return tgt, altmtr
  

def filtered():
  ''' filtered ''' 
  tgt = c4d.state(z = z0, gamma = gamma0)


  ''' sensor init '''
  altmtr = c4d.sensors.radar(rng_noise_std = nu, dt = dtsensor) 
  

  ''' observer '''
  z_err = 5 
  gma_err = 1 * c4d.d2r # 0.05 * c4d.d2r
  process_noise = np.diag([w1, w2]) # np.zeros((2, 2)) # 
  
  F = np.eye(2) + A * dt
  
  
  Qk = F @ (process_noise**2) @ F.T * dt 
  Qk = process_noise**2 
  Qk = process_noise**2 * dt**2 
  Qk = process_noise**2 * dt 
  Qk = np.array([[0.250000002538478, 7.59005070968549e-8], [7.59005070968549e-8, 3.03096871166273e-6]])
  
  Rk = nu**2 / dt
  Rk = nu**2

  # print(f'{Rk = }')
  print(f'{Qk/Rk = }')

  kf = c4d.filters.kalman(X = {'z': tgt.z + z_err, 'gamma': tgt.gamma + gma_err}
                               , P0 = [2 * z_err, 2 * gma_err] 
                                  , R = Rk, Q = Qk 
                                      , F = np.eye(2) + A * dt, G = B * dt, H = C) # True) # 

  for t in tspan:

    tgt.store(t)
    kf.store(t)



    # tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - htgt.z, np.sqrt(Q) @ np.random.randn(2, 1)))[-1]
    # tgt.X =    odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - kf.z, process_noise))[-1]# @ np.random.randn(2)))[-1]
    tgt.X = solve_ivp(autopilot_ivp, [t, t + dt], tgt.X, args = (Hf - kf.z, process_noise), method = 'BDF').y[:, -1]

    # htgt.X = htgt.kf.predict(htgt.X, u = Hf - htgt.z)
    kf.predict(u = Hf - kf.z)
      # htgt.X = htgt.kf.update(htgt.X, Z)

    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    if Z is not None: 
      kf.update(Z)

    # htgt.p11, htgt.p22 = np.diag(htgt.kf.P) 
    # htgt.storeparams(['state', 'p11', 'p22'], t)


  return tgt, altmtr, kf 



if __name__ == '__main__': 

  
  kalman_is_state()


  # tgt1, altmtr = ideal()
  # drawkf(trueobj = tgt1, measures = altmtr, title = 'Ideal', filename = 'ap_ideal')


  # tgt2, altmtr = noisy()
  # drawkf(trueobj = tgt2, measures = altmtr, title = 'Noisy', filename = 'ap_noisy')


  tgt3, altmtr, kf = filtered()
  drawkf(kf = kf, trueobj = tgt3, measures = altmtr, title = 'Filtered', std = True)
  # drawkf(kf = tgt3, trueobj = tgt2, measures = altmtr, title = 'compare')
  # drawkf(kf = kf, trueobj = tgt3, measures = altmtr, title = 'Filtered', filename = 'ap_filtered')

  # c4d.tic()
  # print(f'nees {c4d.filters.kalman.nees(kf, tgt3)}')
  # c4d.toc()


