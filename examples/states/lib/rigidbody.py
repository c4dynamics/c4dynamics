# type: ignore

from matplotlib import pyplot as plt 
import sys, os, socket 
sys.path.append('.')
import c4dynamics as c4d
import numpy as np 
from scipy.integrate import odeint



savedir = c4d.j(os.getcwd(), 'docs', 'source', '_examples', 'rigidbody') 
example_imgs = c4d.j(os.getcwd(), 'examples', '_out', 'rigidbody', 'gif_images')

modelpath = c4d.datasets.d3_model('f16')

g = c4d.g_ms2 
b = .5



def pendulum(yin, t, Iyy):

  theta, q = yin[7], yin[10]
  yout = np.zeros(12)

  yout[7]  =  q
  yout[10] = -g * c4d.sin(theta) / Iyy - b * q

  return yout


def physical_pendulum(yin, t, Iyy):

  yout = np.zeros(12)

  yout[7]  =  yin[10]
  yout[10] = -c4d.g_ms2 * c4d.sin(yin[7]) / Iyy - .5 * yin[10]

  return yout


def intro(): 
  # x y z vx vy vz phi theta psi p q  r 
  # 0 1 2 3  4  5  6   7     8   9 10 11 

  c4d.cprint('intro', 'y')
  rb = c4d.rigidbody(z = 1000, theta = 10 * c4d.d2r, q = 0.5 * c4d.d2r)
  print(rb.X0)
  # [0  0  1000  0  0  0  0  0.174  0  0  0.0087  0]




  c4d.cprint('intro example - autopilot', 'y')


  dt, tf = 0.01, 15
  tspan = np.arange(0, tf, dt)  


  A = np.zeros((12, 12))
  A[2, 7] =    5
  A[7, 2] = -0.1
  A[7, 7] = -0.5

  f16 = c4d.rigidbody(z = 5, theta = 0)


  # def fdynamics(y, t): # , u = 0):
  #   return A @ y # + b * u 

  for t in tspan:
    f16.X = odeint(lambda y, t: A @ y, f16.X, [t, t + dt])[-1] # , args = (f16.z, )
    f16.store(t)

  plt.style.use('dark_background') 
  factorsize = 4
  aspectratio = 1080 / 1920 
  _, ax = plt.subplots(2, 1, dpi = 200
                , figsize = (factorsize, factorsize * aspectratio) 
                        , gridspec_kw = {'left': 0.15, 'right': .9
                                            , 'top': .9, 'bottom': .2, 'hspace': .8})

  # ax[0].plot(x, y, color, linewidth = 1.5)

  f16.plot('z', ax = ax[0])
  ax[0].set(xlabel = '')
  # ax1.set(xlabel = 'time', ylabel = '')
  f16.plot('theta', ax = ax[1], scale = c4d.r2d, filename = c4d.j(savedir, 'intro_f16_autopilot'))




  if socket.gethostname() != 'ZivMeri-PC':

    f16colors = np.vstack(([255, 215, 0], [255, 215, 0]
                                    , [184, 134, 11], [0, 32, 38]
                                        , [218, 165, 32], [218, 165, 32], [54, 69, 79]
                                            , [205, 149, 12], [205, 149, 12])) / 255

    f16.animate(modelpath, angle0 = [90 * c4d.d2r, 0, 180 * c4d.d2r], savedir = example_imgs, modelcolor = f16colors)
    c4d.gif(example_imgs, 'rb_intro_ap', duration = 1)

  plt.show(block = True)

def iyy(): 
  c4d.cprint('iyy', 'y')



  rb05  = c4d.rigidbody(theta = 80 * c4d.d2r)
  rb05.I = [0, .5, 0] 

  rb005 = c4d.rigidbody(theta = 80 * c4d.d2r)
  rb005.I = [0, .05, 0] 


  # integrate the equations of motion 

  dt = .01

  for ti in np.arange(0, 5, dt): 

    rb05.X = odeint(pendulum, rb05.X, [ti, ti + dt], (rb05.I[1],))[1]
    rb05.store(ti)

    rb005.X = odeint(pendulum, rb005.X, [ti, ti + dt], (rb005.I[1], ))[1]
    rb005.store(ti)


  rb05.plot('theta')
  rb005.plot('theta', ax = plt.gca(), color = 'c', filename = c4d.j(savedir, 'Iyy_pendulum'))
  plt.show(block = True)

def angles(): 
  c4d.cprint('angles', 'y')
  rb = c4d.rigidbody(phi = 135 * c4d.d2r)
  print(rb.angles * c4d.r2d)
  # [135  0  0]


def anglerates(): 
  c4d.cprint('angle rates', 'y')
  rb = c4d.rigidbody(q = 30 * c4d.d2r)
  print(rb.ang_rates * c4d.r2d)
  # [0  30  0]


def RB(): 
  c4d.cprint('RB', 'y')
  rb = c4d.rigidbody(theta = 30 * c4d.d2r)
  v_body = [np.sqrt(3), 0, 1]
  print(rb.RB @ v_body)
  # [2  0  0]


def BR(): 
  c4d.cprint('BR', 'y')
  rb = c4d.rigidbody(psi = 45 * c4d.d2r)
  v_inertial = [1, 0, 0]
  print(rb.BR @ v_inertial) 
  # [0.707  -0.707  0]


def inteqm(): 
  c4d.cprint('inteqm - spacecraft stabilization', 'y')

  dt = 0.001
  torque = [.1, 0, 0]  # Constant torque applied around the x-axis (roll)

  # Initialize rigidbody object with initial angle
  rb = c4d.rigidbody()
  rb.I = [0.5, 0, 0]  # Moments of inertia

  # Time integration loop
  for ti in np.arange(0, 5, dt):
    rb.inteqm(np.zeros(3), torque, dt)  # Integrate equations of motion
    if rb.p >= 10 * c4d.d2r:
      torque = [0, 0, 0]
    rb.store(ti)  # Store state for later analysis

  rb.plot('p', filename = c4d.j(savedir, 'inteqm_rollstable'))


def plot(): 

  c4d.cprint('plot', 'y')
  # physical pendulum 

  dt =.01 

  pndlm  = c4d.rigidbody(theta = 80 * c4d.d2r)
  pndlm.I = [0, .5, 0] 

  # integrate the equations of motion 

  # x y z vx vy vz phi theta psi p q  r 
  # 0 1 2 3  4  5  6   7     8   9 10 11 



  for ti in np.arange(0, 4, dt): 

    pndlm.X = odeint(pendulum, pndlm.X, [ti, ti + dt], (pndlm.I[1],))[1]
    pndlm.store(ti)



  pndlm.plot('theta', scale = c4d.r2d, filename = c4d.j(savedir, 'plot_pendulum.png'))


if __name__ == '__main__': 

  # intro() 
  iyy() 
  # angles() 
  # anglerates() 
  # RB() 
  # BR() 
  # inteqm() 
  # plot() 







