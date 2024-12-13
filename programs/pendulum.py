# type: ignore

import sys 
sys.path.append('.')
import c4dynamics as c4d
from scipy.integrate import solve_ivp 
from matplotlib import pyplot as plt 
plt.style.use('dark_background') 
import numpy as np 
import cv2 



animateon = True

# Video settings
video_filename = "pend_video.avi"
frame_size = (640, 480)  # Width and height of the video
fps = 30  # Frames per second

# Create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # Codec
video_out = cv2.VideoWriter(video_filename, fourcc, fps, frame_size)



# Calculate Matplotlib figure size based on frame size and DPI
dpi = 100  # Dots per inch




class trailing: 


  def __init__(self, L, dt):

    # Plot a trail of the m2 bob's position for the last trail_secs seconds.
    # This corresponds to max_trail time points.
    max_trail = int(1 / dt)
    self.ns = 20
    # The trail will be divided into ns segments and plotted as a fading line.
    self.s = max_trail // self.ns



    self.lines = {}
    for j in range(self.ns):
      self.lines[j], = ax.plot([], [], c = 'r', solid_capstyle='butt',lw=2)


  def plot(self, pend): 
    
    for j in range(self.ns): # ns = 20 
      
      imin = - (self.ns - j) * self.s
      imax =  imin + self.s + 1
      # The fading looks better if we square the fractional length along the trail.
      alpha = (j / self.ns)**2

      theta_prev = pend.data('theta')[1][imin : min(-1, imax)]
      x_prev =  L * np.sin(theta_prev)
      y_prev = -L * np.cos(theta_prev)

      self.lines[j].set_data(x_prev, y_prev)
      self.lines[j].set_alpha(alpha)


L = 1       # rod length (m)
tmax, dt = 30, 0.01                 
t = np.arange(0, tmax + dt, dt)     

if animateon:
  fig, ax = plt.subplots(figsize=(frame_size[0] / dpi, frame_size[1] / dpi), dpi = dpi)
  # Create a figure
  ax.set_aspect('equal')
  ax.set_xlim(-1.2 * L, 1.2 * L)
  ax.set_ylim(-1.2 * L, 0.2 * L)
  ax.axis(False)

  # Create a line and point for the pendulum
  line1, = ax.plot([], [], 'o-', lw = 2, color = 'm')

  trail = trailing(L, dt)             


def pendulum(t, y):   
  return y[1], -(c4d.g_ms2 / L) * np.sin(y[0])    # equations of motion 

pend  = c4d.state(theta = np.pi / 4, omega = 0)   # pendulum definition 
for i, ti in enumerate(t):
  pend.store(ti)                                  # store current state 
  pend.X = solve_ivp(pendulum, [0, dt], pend.X).y[:, -1]
  if animateon:
    if i % 10 != 0: continue 

    line1.set_data([0, L * np.sin(pend.theta)], [0, -L * np.cos(pend.theta)])
    trail.plot(pend)  

    plt.pause(0.05)  
    fig.canvas.draw()




    img = cv2.cvtColor(np.array(fig.canvas.renderer.buffer_rgba()), cv2.COLOR_RGBA2BGR)
    img = cv2.resize(img, frame_size)

    assert img.shape[:2] == (frame_size[1], frame_size[0]), "Frame size mismatch!"

    video_out.write(img)
    cv2.imshow('', img)
    cv2.waitKey(10)


cv2.destroyAllWindows()
video_out.release()
pend.plot('theta', filename = 'pendulum.png')
plt.show(block = False)