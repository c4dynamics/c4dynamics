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



def kalman_is_state(): 
  from c4dynamics.filters import kalman 
  z = np.zeros((2, 2))
  kf = kalman(X = {'x1': 0, 'x2': 0}, dt = 0.1, P0 = z, A = z, C = z, Q = z, R = z)
  print(kf)


class Trkstate(Enum):
  OPENED      = 0
  PREDICTED   = 1 
  CORRECTED   = 2 
  CLOSED      = 3 



dt, tf = 0.01, 50  
tspan = np.arange(dt, tf, dt)  
dtsensor = 0.02 # .01# 

Hf = 1000 
z0 = Hf + 10 
gamma0 = 0

A = np.array([[0, 5], [0, -0.5]])
b = np.array([0, 0.1])
c = np.array([1, 0])



w1 = .5 # ft. - 1std; np.sqrt(.5) # w1 = 0.3, 1std; Q11 = 0.1, variance.  
w2 = .1 * c4d.d2r # 0 # .1 * c4d.d2r # deg. - 1std; np.sqrt(.3 * c4d.d2r) # w2 = 1, 1std; Q22 = 1 variance. 
nu  = .5 # 0# std: nu = .1, variance: R = .01


''' Tests if the system (A, c) is observable. '''
n = A.shape[0]
obsv = c
for i in range(1, n):
    obsv = np.vstack((obsv, c @ np.linalg.matrix_power(A, i)))
# Compute the rank of the observability matrix
rank = np.linalg.matrix_rank(obsv)
c4d.cprint(f'The system is observable (rank = n = {n}).' if rank == n else 'The system is not observable (rank = {rank), n = {n}).', 'y')



''' true target ''' 
tgt = c4d.state(z = z0, gamma = gamma0)
tgt.store(0)


def autopilot(y, t, u = 0, Q = np.zeros(2)):
  return A @ y + b * u + Q


def ideal():
  ''' ideal '''

  altmtr = c4d.sensors.radar(isideal = True)
  Q = np.zeros((2, 2))

  for t in tspan:

    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    if Z is not None:   
      tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - Z, np.sqrt(Q) @ np.random.randn(2, 1)))[-1]

    tgt.store(t)
    
  return tgt, altmtr, 'ideal' 
  

def noisy():
  ''' noisy no kalman ''' 

  Q = np.diag([w1**2, w2**2])

  altmtr = c4d.sensors.radar(rng_noise_std = nu, dt = dtsensor)

  for t in tspan:

    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    if Z is not None: 
      tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - Z, np.sqrt(Q) @ np.random.randn(2, 1)))[-1]

    tgt.store(t)
  
  return tgt, altmtr, 'noisy'
  

def filtered():
  ''' filtered ''' 


  ''' sensor init '''
  altmtr = c4d.sensors.radar(rng_noise_std = nu, dt = dtsensor) 
  

  ''' observer '''
  z_err = 5 
  gma_err = 0.05 * c4d.d2r

  Q = np.diag([w1**2, w2**2])
  # htgt = c4d.state(z = tgt.z + z_err, gamma = tgt.gamma + gma_err) 
  
  kf = c4d.filters.kalman(X = {'z': tgt.z + z_err, 'gamma': tgt.gamma + gma_err}
                               , P0 = [2 * z_err, 2 * gma_err] 
                                  , Rk = nu**2 / dtsensor, Qk = Q * dt, dt = dt #    
                                      , F = np.eye(2) + A * dt, G = b * dt, H = c, steadystate = False) # True) # 
  # htgt.state = Trkstate.OPENED

  for t in tspan:

    # tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - htgt.z, np.sqrt(Q) @ np.random.randn(2, 1)))[-1]
    tgt.X = odeint(autopilot, tgt.X, [t, t + dt], args = (Hf - kf.z, np.sqrt(Q) @ np.random.randn(2, 1)))[-1]

    # htgt.X = htgt.kf.predict(htgt.X, u = Hf - htgt.z)
    kf.predict(u = Hf - kf.z)
    # htgt.state = Trkstate.PREDICTED

    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    if Z is not None: 
      # htgt.X = htgt.kf.update(htgt.X, Z)
      kf.update(Z)
      # htgt.state = Trkstate.CORRECTED

    tgt.store(t)
    kf.store(t)
    # htgt.p11, htgt.p22 = np.diag(htgt.kf.P) 
    # htgt.storeparams(['state', 'p11', 'p22'], t)


  return tgt, altmtr, 'filtered', kf 



if __name__ == '__main__': 

  
  kalman_is_state()
  # tgt, altmtr, flabel = ideal()
  # tgt, altmtr, flabel = noisy()
  # tgt, altmtr, flabel, kf = filtered()

  sys.exit()




if True: 
  from matplotlib.ticker import ScalarFormatter
  plotcov = False 
  textsize = 10
  covlabel = ''
  pad_left = 0.1
  pad_others = 0.2

  # pdb.set_trace()
  fig, ax = plt.subplots(1, 2, dpi = 200, figsize = (6, 3) #  # figsize = (8, 2) # 
                # , gridspec_kw = {'hspace': 0.5, 'wspace': 0.3})#)
                  , gridspec_kw = {'left': .15, 'right': .95
                                    , 'top': .9 , 'bottom': .1
                                      , 'hspace': 0.5, 'wspace': 0.3}) 
  



  ''' altitiude ''' 

  ax[0].plot(*tgt.data('z'), 'c', linewidth = 2, label = 'true', zorder = 2) 
  ax[0].plot(*altmtr.data('range'), '.m', markersize = 1, label = 'altmeter', zorder = 1)

  # ax[0].plot(*htgt.data('z'), 'y', linewidth = 1, label = 'estimation')
  if 'kf' in locals():

    x = kf.data('z')[1]
    t_sig, x_sig = kf.data('P00') 
    # iscorrect = np.where(np.vectorize(lambda x: x.value)(htgt.data('state')[1]) == Trkstate.CORRECTED.value)[0]

    ax[0].plot(t_sig, x, linewidth = 1, color = 'y', label = 'kf')

    if plotcov: 
      # ±std 
      ax[0].plot(t_sig, x + np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
      ax[0].plot(t_sig, x - np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w') # np.array(v.color) / 255)
      # correct
      # ax[0].plot(t_sig[iscorrect], x[iscorrect], linewidth = 0, color = color
      #                       , marker = 'o', markersize = 2, markerfacecolor = 'none', label = 'correct') 

      covlabel = 'cov'

    ax[0].set_ylim((995, 1012))




  c4d.plotdefaults(ax[0], 'Altitude', 't', 'ft', textsize)
  ax[0].legend(fontsize = 'xx-small', facecolor = None, framealpha = .5)  #, edgecolor = None Set font size and legend box properties

  ax[0].yaxis.set_major_formatter(ScalarFormatter())
  ax[0].yaxis.get_major_formatter().set_useOffset(False)
  ax[0].yaxis.get_major_formatter().set_scientific(False)




  ''' path angle ''' 

  ax[1].plot(*tgt.data('gamma', c4d.r2d), 'c', linewidth = 1.5, label = 'true') # label = r'$\gamma$') #'\\gamma') # 
  # ax[1].plot(*htgt.data('gamma', c4d.r2d), 'y', linewidth = 1, label = 'estimation') # r'$\\hat{\\varphi}$'

  if 'kf' in locals():

    x = kf.data('gamma')[1]
    t_sig, x_sig = kf.data('P11') 
    # iscorrect = np.where(np.vectorize(lambda x: x.value)(htgt.data('state')[1]) == Trkstate.CORRECTED.value)[0]

    if plotcov: 
      ax[1].plot(t_sig, x * c4d.r2d, linewidth = 1, color = 'y', label = 'kf')
      # ±std 
      ax[1].plot(t_sig, (x + np.sqrt(x_sig.squeeze())) * c4d.r2d, linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
      ax[1].plot(t_sig, (x - np.sqrt(x_sig.squeeze())) * c4d.r2d, linewidth = 1, color = 'w') # np.array(v.color) / 255)
      # state
      # ax[1].plot(t_sig[iscorrect], x[iscorrect] * c4d.r2d, linewidth = 0, color = 'w'
      #                     , marker = '.', markersize = 2, markerfacecolor = 'none', label = 'correct') 

  c4d.plotdefaults(ax[1], 'Path Angle', 't', 'deg', textsize)
  # ax[1].legend(fontsize = 'small', facecolor = None)



  for ext in ['.png', '.svg']:
    plt.savefig(os.path.join(os.getcwd(), 'docs/source/_static/figures/filters_' 
                          + os.path.basename(__file__)[:-3] + '_' + flabel + covlabel + ext)
                  , dpi = 1200
                    # , bbox_inches = 'tight', pad_inches = 0.2)
                    , bbox_inches = np.array([pad_left, pad_others, 1 - pad_others, 1 - pad_others])
                      , pad_inches = 0)


  plt.show(block = True)


else:

  fig, ax = plt.subplots(1, 2, figsize = (10, 3))

  ax[0].plot(*tgt.data('z'), label = 'true') 
  ax[0].plot(*altmtr.data('range'), label = 'altmeter')
  if 'kf' in locals():
    x = kf.data('z')[1]
    t_sig, x_sig = kf.data('P00') 
    ax[0].plot(t_sig, x, label = 'est')
    # ±std 
    ax[0].plot(t_sig, x + np.sqrt(x_sig.squeeze()), label = 'std') 
    ax[0].plot(t_sig, x - np.sqrt(x_sig.squeeze())) 

    ax[0].set_ylim((995, 1012))
  c4d.plotdefaults(ax[0], 'Altitude', 't', 'ft', ilines = [0, 1, 2, 3, 3])
  

  ax[1].plot(*tgt.data('gamma', c4d.r2d), label = 'true') 
  if 'kf' in locals():
    x = kf.data('gamma')[1]
    t_sig, x_sig = kf.data('P11') 
    # iscorrect = np.where(np.vectorize(lambda x: x.value)(htgt.data('state')[1]) == Trkstate.CORRECTED.value)[0]
    ax[1].plot(t_sig, x * c4d.r2d, label = 'est')
    # ±std
    ax[1].plot(t_sig, (x + np.sqrt(x_sig.squeeze())) * c4d.r2d, label = 'std') 
    ax[1].plot(t_sig, (x - np.sqrt(x_sig.squeeze())) * c4d.r2d) 
    # state
    # ax[1].plot(t_sig[iscorrect], x[iscorrect] * c4d.r2d, linewidth = 0, color = 'w'
    #                     , marker = '.', markersize = 2, markerfacecolor = 'none', label = 'correct') 
  c4d.plotdefaults(ax[1], 'Path Angle', 't', 'deg', ilines = [0, 2, 3, 3])


  c4d.figdefaults(fig)#, os.path.join(os.getcwd(), 'docs/source/_static/figures/filters_' 
                       #   + os.path.basename(__file__)[:-3] + '_' + flabel + '.png'))



  plt.show(block = True)


