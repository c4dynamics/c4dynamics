import sys
import os
import numpy as np
# import matplotlib
# matplotlib.use('Agg') # dont show the plot
import matplotlib.pyplot as plt
import imageio
from scipy.integrate import odeint
from os import listdir
from os.path import isfile, join
from matplotlib.patches import Circle

class double_pendulum: 

  def __init__(obj):
    # Pendulum rod lengths (m), bob masses (kg).
    obj.L1, obj.L2 = 1, 1
    obj.m1, obj.m2 = 1, 1

    # Maximum time, time point spacings and the time grid (all in s).
    obj.tmax, obj.dt = 30, 0.01
    # t = np.arange(0, tmax+dt, dt)
    # Initial conditions: theta1, dtheta1/dt, theta2, dtheta2/dt.
    obj.y0 = np.array([3 * np.pi / 7, 0, 3 * np.pi / 4, 0])

    obj.EDRIFT = 0.05

    # Plotted bob circle radius
    obj.r = 0.05

  def calc_E(obj, y):
      """Return the total energy of the system."""

      th1, th1d, th2, th2d = y.T
      g = 9.81 

      V = -(obj.m1 + obj.m2) * obj.L1 * g * np.cos(th1) - obj.m2 * obj.L2 * g * np.cos(th2)
      T = 0.5 * obj.m1 * (obj.L1 * th1d)**2 + 0.5 * obj.m2 * ((obj.L1 * th1d)**2 + (obj.L2 * th2d)**2 
              + 2 * obj.L1 * obj.L2 * th1d * th2d * np.cos(th1 - th2))
      return T + V

  def make_plot(obj, y, savedir): # , i

    theta1, theta2 = y[:,0], y[:,2]
    # Convert to Cartesian coordinates of the two bob positions.
    x1 = obj.L1 * np.sin(theta1)
    y1 = -obj.L1 * np.cos(theta1)
    x2 = x1 + obj.L2 * np.sin(theta2)
    y2 = y1 - obj.L2 * np.cos(theta2)

    t = np.arange(0, obj.tmax + obj.dt, obj.dt)

    # Make an image every di time points, corresponding to a frame rate of fps
    # frames per second.
    # Frame rate, s-1
    fps = 10
    di = int(1 / fps / obj.dt)
    fig = plt.figure(figsize = (8.3333, 6.25), dpi=72)
    plt.ioff()
    ax = fig.add_subplot(111)
    ns = 20
    # Plot a trail of the m2 bob's position for the last trail_secs seconds.
    trail_secs = 1
    # This corresponds to max_trail time points.
    max_trail = int(trail_secs / obj.dt)

    for i in range(0, t.size, di):
      # print(i // di, '/', t.size // di)
      
      # Plot and save an image of the double pendulum configuration for time
      # point i.s
      # The pendulum rods.
      ax.plot([0, x1[i], x2[i]], [0, y1[i], y2[i]], lw = 2 
              , c = 'k')
      ax.set_facecolor('indianred')
      # Circles representing the anchor point of rod 1, and bobs 1 and 2.
      c0 = Circle((0, 0), obj.r / 2, fc = 'k', zorder = 10)
      c1 = Circle((x1[i], y1[i]), obj.r, fc = 'b', ec = 'b', zorder = 10)
      c2 = Circle((x2[i], y2[i]), obj.r, fc = 'r', ec = 'r', zorder = 10)
      ax.add_patch(c0)
      ax.add_patch(c1)
      ax.add_patch(c2)

      # The trail will be divided into ns segments and plotted as a fading line.
      s = max_trail // ns

      for j in range(ns):
          imin = i - (ns-j) * s
          if imin < 0:
              continue
          imax = imin + s + 1
          # The fading looks better if we square the fractional length along the
          # trail.
          alpha = (j / ns)**2
          ax.plot(x2[imin : imax], y2[imin : imax], c = 'r', solid_capstyle = 'butt',
                  lw = 2, alpha = alpha)

      # Centre the image on the fixed anchor point, and ensure the axes are equal
      ax.set_xlim(-obj.L1 - obj.L2 - obj.r, obj.L1 + obj.L2 + obj.r)
      ax.set_ylim(-obj.L1 - obj.L2 - obj.r, obj.L1 + obj.L2 + obj.r)
      ax.set_aspect('equal', adjustable = 'box')
      plt.axis('off')
      plt.savefig(savedir + '/_img{:04d}.png'.format(i//di), dpi = 72) # frames
      plt.cla()
    print('images saved in ' + savedir)
    plt.close(fig)
      
  def run_pendulum(obj): #if __name__ == "__main__":

    # Maximum time, time point spacings and the time grid (all in s).
    # tmax, dt = 30, 0.01
    t = np.arange(0, obj.tmax + obj.dt, obj.dt)
    # Initial conditions: theta1, dtheta1/dt, theta2, dtheta2/dt.
    # y0 = np.array([3*np.pi/7, 0,  3*np.pi/4, 0])

    # Do the numerical integration of the equations of motion
    y = odeint(double_pendulum.deriv, obj.y0, t, args = (obj, )) # args=(L1, L2, m1, m2))
    # Check that the calculation conserves total energy to within some tolerance.
    # EDRIFT = 0.05
    # Total energy from the initial conditions
    E = obj.calc_E(obj.y0)
    if np.max(np.sum(np.abs(obj.calc_E(y) - E))) > obj.EDRIFT:
        sys.exit('Maximum energy drift of {} exceeded.'.format(obj.EDRIFT))
    else:
      print('energy is fine')
    return y 


  @staticmethod

  def deriv(y, t, pend): #L1, L2, m1, m2
    """Return the first derivatives of y = theta1, z1, theta2, z2."""
    theta1, z1, theta2, z2 = y
    g = 9.81

    c, s = np.cos(theta1 - theta2), np.sin(theta1 - theta2)

    theta1dot = z1
    z1dot     = (pend.m2 * g * np.sin(theta2) * c - pend.m2 * s * (pend.L1 * z1**2 * c + pend.L2 * z2**2) 
                - (pend.m1 + pend.m2) * g * np.sin(theta1)) / pend.L1 / (pend.m1 + pend.m2 * s**2)
    theta2dot = z2
    z2dot     = ((pend.m1 + pend.m2) * (pend.L1 * z1**2 * s - g * np.sin(theta2) + g * np.sin(theta1) * c)  
                + pend.m2 * pend.L2 * z2**2 * s * c) / pend.L2 / (pend.m1 + pend.m2 * s**2)

    return theta1dot, z1dot, theta2dot, z2dot
  
  def gif(dirname):
    images = []
    dirfiles = sorted(os.listdir(dirname)) # 'frames/'
    # dirfiles = [f for f in listdir(dirname) if isfile(join(dirname, f))]
    for filename in dirfiles:
      # print(filename)
      images.append(imageio.imread(dirname + '/' + filename))
    
    imageio.mimsave('_img_movie.gif', images)
    print('_img_movie.gif is saved in ' + os.getcwd())



