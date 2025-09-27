# type: ignore

from matplotlib import pyplot as plt 
# import sys, os, socket 
# sys.path.append('.')
import c4dynamics as c4d
import numpy as np 
from scipy.integrate import solve_ivp


# a simple pendulum with a point mass on a rigid massless rod of length = 1[m], 
# swiniging under gravity 9.8m/s^2 with angle theta(0) = 0 and q(0) = 0, integrated with solve_ivp 
# with a time step of 0.01s for 5s
 
dt = 0.01 
pend  = c4d.state(theta = 50 * c4d.d2r, q = 0)

for ti in np.arange(0, 5, dt): 
  pend.store(ti)
  pend.X = solve_ivp(lambda t, y: [y[1], -9.8 * c4d.sin(y[0])], [ti, ti + dt], pend.X).y[:, -1]

pend.plot('theta', scale = c4d.r2d, darkmode = False)
plt.savefig(r'examples\_out\pendulum.png', bbox_inches = 'tight', pad_inches = .2, dpi = 600)
plt.savefig(r'paper\pendulum.png', bbox_inches = 'tight', pad_inches = .2, dpi = 600)
plt.show()








