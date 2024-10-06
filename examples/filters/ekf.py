import numpy as np 
from scipy.integrate import odeint 

from matplotlib import pyplot as plt 
plt.style.use('dark_background')  
# plt.switch_backend('TkAgg')

import os, sys
sys.path.append('')

import c4dynamics as c4d 


dt, tf =  0.01, 30 # .05, 30 #
tspan = np.arange(dt, tf, dt)  
dtsensor = .05 # 0.1 # 


tgt = c4d.state(z = 100000, vz = -6000, beta = 500)
tgt.store(0)


rho0 = .0034 
k = 22000 
nu = np.sqrt(500) 
zerr, vzerr, betaerr = 25, -150, 300 


def ballistics(y, t):

  # altitude 
  # velocity 
  # ballistic coefficient 
 

  return [y[1], rho0 * np.exp(-y[0] / k) * y[1]**2 * c4d.g_fts2 / 2 / y[2] - c4d.g_fts2, 0]


def ideal():
  ''' ideal '''
  altmtr = c4d.sensors.seeker(isideal = True, dt = dtsensor)

  for t in tspan:
    
    tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
    altmtr.measure(tgt, t = t, store = True)
    tgt.store(t)
    
  return tgt, altmtr, 'ideal' 
  

def noisy():
  ''' noisy no kalman ''' 
  altmtr = c4d.sensors.seeker(rng_noise_std = nu, dt = dtsensor)

  for t in tspan:

    tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]
    altmtr.measure(tgt, t = t, store = True)
    tgt.store(t)

  return tgt, altmtr, 'noisy'
  

def filtered():
  ''' filtered ''' 
  p0 = np.diag([nu**2, vzerr**2, betaerr**2]) # when a list is given the std are provided. when matrix the variances. 
  Rk = nu**2 / dt


  ''' sensor init '''
  altmtr = c4d.sensors.seeker(rng_noise_std = nu, dt = dtsensor) 
  Qk = np.diag([0, 0, betaerr**2 / tf * dt])  

  np.random.seed(1337)

  ekf = c4d.filters.ekf(X = {'z': tgt.z + zerr, 'vz': tgt.vz + vzerr
                                      , 'beta': tgt.beta + betaerr}
                            , P0 = p0, dt = dt) 

  for t in tspan:

    tgt.X = odeint(ballistics, tgt.X, [t, t + dt])[-1]


    ''' 
    the necessary linear parameters for the predict stage: the 
    state transition matrix Phi (or its first order approximation F - the discreteized system matrix) 
    '''
    rhoexp = rho0 * np.exp(-ekf.z / k) * c4d.g_fts2 * ekf.vz / ekf.beta
    fx = [ekf.vz, rhoexp * ekf.vz / 2 - c4d.g_fts2, 0]
    f2i = rhoexp * np.array([-ekf.vz / 2 / k, 1, -ekf.vz / 2 / ekf.beta])
    F = np.array([[0, 1, 0], f2i, [0, 0, 0]]) * dt + np.eye(3)
    ekf.predict(F, Qk, fx = fx)


    ''' the necessary linear parameters for the predict stage: the measure matrix H '''
    _, _, Z = altmtr.measure(tgt, t = t, store = True)
    
    if Z is not None:  
      H = [1, 0, 0]
      ekf.update(Z, H, Rk)


    ''' store the state '''
    tgt.store(t)
    ekf.store(t)


  return tgt, altmtr, 'filtered', ekf 


   
if __name__ == '__main__': 
  
  tgt, altmtr, flabel = ideal()
  tgt, altmtr, flabel = noisy()
  tgt, altmtr, flabel, ekf = filtered()








if True: 
  from matplotlib.ticker import ScalarFormatter
  plotcov = False 
  textsize = 10
  covlabel = ''
  pad_left = 0.1
  pad_others = 0.2

  fig, ax = plt.subplots(1, 3, dpi = 200, figsize = (9, 3) # figsize = (8, 2) # 
                , gridspec_kw = {'left': .1, 'right': .95
                                  , 'top': .9 , 'bottom': .1
                                    , 'hspace': 0.5, 'wspace': 0.4}) 



  ''' altitude '''

  ax[0].plot(*tgt.data('z'), 'c', linewidth = 2, label = 'true') 
  ax[0].plot(*altmtr.data('range'), '.m', markersize = 1, label = 'altimeter')

  if 'ekf' in locals():

    x = ekf.data('z')[1]
    t_sig, x_sig = ekf.data('P00')
    # iscorrect = np.where(np.vectorize(lambda x: x.value)(htgt.data('state')[1]) == Trkstate.CORRECTED.value)[0]

    ax[0].plot(t_sig, x, linewidth = 1, color = 'y', label = 'est')

    if plotcov: 
      # ±std 
      ax[0].plot(t_sig, x + np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
      ax[0].plot(t_sig, x - np.sqrt(x_sig.squeeze()), linewidth = 1, color = 'w') # np.array(v.color) / 255)
      # correct
      # ax[0].plot(t_sig[iscorrect], x[iscorrect], linewidth = 0, color = color
      #                       , marker = 'o', markersize = 2, markerfacecolor = 'none', label = 'correct') 

      # ax[0].set_ylim((995, 1012))
      covlabel = 'cov'


  c4d.plotdefaults(ax[0], 'Altitude', 'Time [s]', 'ft', textsize)
  ax[0].legend(fontsize = 'xx-small', facecolor = None, framealpha = .5)  #, edgecolor = None Set font size and legend box properties
  # xx-small, x-small, small, medium, large, x-large, xx-large, larger, smaller, None

  ax[0].yaxis.set_major_formatter(ScalarFormatter())
  ax[0].yaxis.get_major_formatter().set_useOffset(False)
  ax[0].yaxis.get_major_formatter().set_scientific(False)



  ''' velocity '''

  ax[1].plot(*tgt.data('vz'), 'c', linewidth = 2, label = 'true') 

  if 'ekf' in locals():

    x = ekf.data('vz')[1]
    t_sig, x_sig = ekf.data('P11') 
    # iscorrect = np.where(np.vectorize(lambda x: x.value)(htgt.data('state')[1]) == Trkstate.CORRECTED.value)[0]

    ax[1].plot(t_sig, x, linewidth = 1, color = 'y', label = 'est')

    if plotcov: 
      # ±std 
      ax[1].plot(t_sig, (x + np.sqrt(x_sig.squeeze())), linewidth = 1, color = 'w', label = 'std') # np.array(v.color) / 255)
      ax[1].plot(t_sig, (x - np.sqrt(x_sig.squeeze())), linewidth = 1, color = 'w') # np.array(v.color) / 255)
      # state
      # ax[1].plot(t_sig[iscorrect], x[iscorrect] * c4d.r2d, linewidth = 0, color = 'w'
      #                     , marker = '.', markersize = 2, markerfacecolor = 'none', label = 'correct') 


  c4d.plotdefaults(ax[1], 'Velocity', 'Time [s]', 'ft/s', textsize)
  # ax[1].legend(fontsize = 'small', facecolor = None)




  ''' ballistic coefficient '''

  ax[2].plot(*tgt.data('beta'), 'c', linewidth = 1.5, label = 'true') # label = r'$\gamma$') #'\\gamma') # 

  if 'ekf' in locals():

    x = ekf.data('beta')[1]
    t_sig, x_sig = ekf.data('P22')
    # iscorrect = np.where(np.vectorize(lambda x: x.value)(htgt.data('state')[1]) == Trkstate.CORRECTED.value)[0]

    ax[2].plot(t_sig, x, linewidth = 1, color = 'y', label = 'ekf')

    if plotcov: 
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


  for ext in ['.png', '.svg']:
    plt.savefig(os.path.join(os.getcwd(), 'docs', 'source', '_static', 'figures'
                          , 'filters_' + os.path.basename(__file__)[:-3] + '_' + flabel + ext)
                , dpi = 1200
                    , bbox_inches = 'tight', pad_inches = .3)
                    # , bbox_inches = bbox)





  plt.show(block = True)


