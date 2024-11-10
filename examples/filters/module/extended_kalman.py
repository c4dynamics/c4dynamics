# type: ignore

import numpy as np 
from scipy.integrate import odeint 

from matplotlib import pyplot as plt 
plt.style.use('dark_background')  
# plt.switch_backend('TkAgg')

import os, sys
sys.path.append('')

import c4dynamics as c4d 


savedir = os.path.join(c4d.c4dir(os.getcwd()), 'docs', 'source', '_examples', 'filters') 


dt, tf =  0.01, 30 # .05, 30 #
tspan = np.arange(0, tf + dt, dt)  
dtsensor = .05 # 0.1 # 





rho0 = .0034 
k = 22000 
nu = np.sqrt(500) 
zerr, vzerr, betaerr = 25, -150, 300 

def drawekf(ekf = None, trueobj = None, measures = None, title = '', filename = None, std = False): 

  from matplotlib.ticker import ScalarFormatter
  textsize = 10
  

  fig, ax = plt.subplots(1, 3, dpi = 200, figsize = (9, 3) # figsize = (8, 2) # 
                , gridspec_kw = {'left': .15, 'right': .95
                                  , 'top': .80, 'bottom': .15
                                    , 'hspace': 0.5, 'wspace': 0.4}) 

  fig.suptitle('                ' + title, fontsize = 14, fontname = 'Times New Roman')
  plt.subplots_adjust(top = 0.95)  # Adjust for suptitle space


  ''' altitude '''

  if trueobj: 
    ax[0].plot(*trueobj.data('z'), 'm', linewidth = 1.2, label = 'true') 
  
  if measures: 
    ax[0].plot(*measures.data('range'), '.c', markersize = 1, label = 'altmeter')

  if ekf:
    ax[0].plot(*ekf.data('z'), linewidth = 1, color = 'y', label = 'ekf')

  if std: 
    x = ekf.data('z')[1]
    t_sig, x_sig = ekf.data('P00')
    # ±std 
    ax[0].plot(t_sig, x + np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
    ax[0].plot(t_sig, x - np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w') # np.array(v.color) / 255)
    # correct
    # ax[0].plot(t_sig[iscorrect], x[iscorrect], linewidth = 0, color = color
    #                       , marker = 'o', markersize = 2, markerfacecolor = 'none', label = 'correct') 

    # ax[0].set_ylim((995, 1012))



  c4d.plotdefaults(ax[0], 'Altitude', 'Time [s]', 'ft', textsize)
  ax[0].legend(fontsize = 'xx-small', facecolor = None, framealpha = .5)  #, edgecolor = None Set font size and legend box properties
  # xx-small, x-small, small, medium, large, x-large, xx-large, larger, smaller, None

  # ax[0].yaxis.set_major_formatter(ScalarFormatter())
  # ax[0].yaxis.get_major_formatter().set_useOffset(False)
  # ax[0].yaxis.get_major_formatter().set_scientific(False)



  ''' velocity '''

  if trueobj: 
    ax[1].plot(*trueobj.data('vz'), 'm', linewidth = 1.2, label = 'true') 

  if ekf:
    ax[1].plot(*ekf.data('vz'), linewidth = 1, color = 'y', label = 'ekf')

  if std: 
    x = ekf.data('vz')[1]
    t_sig, x_sig = ekf.data('P11') 
    # ±std 
    ax[1].plot(t_sig, (x + np.sqrt(x_sig.squeeze())), linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
    ax[1].plot(t_sig, (x - np.sqrt(x_sig.squeeze())), linewidth = 1, color = 'w') # np.array(v.color) / 255)
    # state
    # ax[1].plot(t_sig[iscorrect], x[iscorrect] * c4d.r2d, linewidth = 0, color = 'w'
    #                     , marker = '.', markersize = 2, markerfacecolor = 'none', label = 'correct') 


  c4d.plotdefaults(ax[1], 'Velocity', 'Time [s]', 'ft/s', textsize)
  # ax[1].legend(fontsize = 'small', facecolor = None)




  ''' ballistic coefficient '''

  if trueobj: 
    ax[2].plot(*trueobj.data('beta'), 'm', linewidth = 1.2, label = 'true') # label = r'$\gamma$') #'\\gamma') # 

  if ekf:
    ax[2].plot(*ekf.data('beta'), linewidth = 1, color = 'y', label = 'ekf')

  if std: 
    x = ekf.data('beta')[1]
    t_sig, x_sig = ekf.data('P22')
    # ±std 
    ax[2].plot(t_sig, (x + np.sqrt(x_sig.squeeze())), linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
    ax[2].plot(t_sig, (x - np.sqrt(x_sig.squeeze())), linewidth = 1, color = 'w') # np.array(v.color) / 255)
    # state
    # ax[1].plot(t_sig[iscorrect], x[iscorrect] * c4d.r2d, linewidth = 0, color = 'w'
    #                     , marker = '.', markersize = 2, markerfacecolor = 'none', label = 'correct') 


  c4d.plotdefaults(ax[2], 'Beta', 'Time [s]', 'lb/ft^2', textsize)

  # from matplotlib.transforms import Bbox
  # width_fig, height_fig = fig.get_size_inches()

  # # bbox = Bbox([[pad_left, pad_others], [1 - pad_others, 1 - pad_others]])
  # pad_left = .0001
  # bbox = Bbox.from_extents(# [left, bottom, right, top]
  #           pad_left * width_fig
  #             , pad_others * height_fig
  #               , (1 - pad_others) * width_fig
  #               , (1 - pad_others) * height_fig)  

  if filename: 
    plt.savefig(c4d.j(savedir, filename + '.png')
                    , pad_inches = .2, dpi = 600)








def ballistics(y, t):

  # altitude 
  # velocity 
  # ballistic coefficient 
 

  return [y[1], rho0 * np.exp(-y[0] / k) * y[1]**2 * c4d.g_fts2 / 2 / y[2] - c4d.g_fts2, 0]


def ideal():
  ''' ideal '''
  tgt = c4d.state(z = 100000, vz = -6000, beta = 500)
  altmtr = c4d.sensors.radar(isideal = True, dt = dtsensor)

  for t in tspan:
    tgt.store(t)
    
    tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
    altmtr.measure(tgt, t = t, store = True)
    
  return tgt, altmtr
  

def noisy():
  ''' noisy no kalman ''' 
  tgt = c4d.state(z = 100000, vz = -6000, beta = 500)
  altmtr = c4d.sensors.radar(rng_noise_std = nu, dt = dtsensor)

  for t in tspan:
    tgt.store(t)

    tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
    altmtr.measure(tgt, t = t, store = True)

  return tgt, altmtr
  

def filtered():
  ''' filtered ''' 
  tgt = c4d.state(z = 100000, vz = -6000, beta = 500)


  p0 = np.diag([nu**2, vzerr**2, betaerr**2]) # when a list is given the std are provided. when matrix the variances. 
  R = nu**2 / dt


  ''' sensor init '''
  altmtr = c4d.sensors.radar(rng_noise_std = nu, dt = dtsensor) 
  Q = np.diag([0, 0, betaerr**2 / tf * dt])  

  np.random.seed(1337)

  H = [1, 0, 0]
  ekf = c4d.filters.ekf(X = {'z': tgt.z + zerr, 'vz': tgt.vz + vzerr
                                  , 'beta': tgt.beta + betaerr}
                          , P0 = p0, H = H, Q = Q, R = R) 

  for t in tspan:

    ''' store the state '''
    tgt.store(t)
    ekf.store(t)

    tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]


    ''' 
    the necessary linear parameters for the predict stage: the 
    state transition matrix Phi (or its first order approximation F - the discreteized system matrix) 
    '''
    rhoexp  =   rho0 * np.exp(-ekf.z / k) * c4d.g_fts2 * ekf.vz / ekf.beta
    fx      =   [ekf.vz, rhoexp * ekf.vz / 2 - c4d.g_fts2, 0]
    f2i     =   rhoexp * np.array([-ekf.vz / 2 / k, 1, -ekf.vz / 2 / ekf.beta])
    F       =   np.array([[0, 1, 0], f2i, [0, 0, 0]]) * dt + np.eye(3)
    ekf.predict(F = F, fx = fx, dt = dt)


    ''' the necessary linear parameters for the predict stage: the measure matrix H '''
    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    
    if Z is not None:  
      ekf.update(Z)




  return tgt, altmtr, ekf 


   
if __name__ == '__main__': 
  
  tgt1, altmtr = ideal()
  # drawekf(trueobj = tgt1, measures = altmtr, title = 'Ideal', filename = 'bal_ideal')

  tgt2, altmtr = noisy()
  # drawekf(trueobj = tgt2, measures = altmtr, title = 'Noisy')
  
  
  tgt, altmtr, ekf = filtered()
  drawekf(trueobj = tgt2, measures = altmtr, ekf =  ekf, title = 'Filtered', filename = 'bal_filtered')


  plt.show(block = True)







