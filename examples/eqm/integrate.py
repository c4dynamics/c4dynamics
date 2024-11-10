# type: ignore

import os, sys 
sys.path.append('.')
import c4dynamics as c4d

import numpy as np 
from matplotlib import pyplot as plt 

c4path = c4d.c4dir(os.getcwd())
savedir = os.path.join(c4path, 'docs', 'source', '_examples', 'eqm') 




c4d.cprint('int3 - free fall', 'y')

h0 = 10000
pt = c4d.datapoint(z = h0)

while pt.z > 0:
    pt.store()
    pt.X = c4d.eqm.int3(pt, [0, 0, -c4d.g_ms2], dt = 1)

pt.plot('z', filename = c4d.j(savedir, 'int3.png'))

plt.show()



c4d.cprint('int6 - fixed stick', 'y')

dt = .5e-3 

t = np.arange(0, 10, dt) 

theta0 =  80 * c4d.d2r       # deg 
q0     =  0 * c4d.d2r        # deg to sec
Iyy    =  .4                  # kg * m^2 
length =  1                  # meter 
mass   =  0.5                # kg 

# integration 
rb = c4d.rigidbody(theta = theta0, q = q0)
rb.I = [0, Iyy, 0] 
rb.mass = mass 

for ti in t: 

    rb.store(ti)

    tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
    rb.X = c4d.eqm.int6(rb, np.zeros(3), [0, tau_g, 0], dt)
     

rb.plot('theta', filename = c4d.j(savedir, 'int6.png'))
plt.show()





# comparison with scipy solution 

from scipy.integrate import odeint

def pend(y, t):
    theta, omega = y
    dydt = [omega, -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(theta) / Iyy]
    return dydt

sol = odeint(pend, [theta0, q0], t)


plt.plot(*rb.data('theta', c4d.r2d), 'm', linewidth = 2, label = 'c4dynamics.int6')
plt.plot(t, sol[:, 0] * c4d.r2d, 'c', linewidth = 1.5, label = 'scipy.odeint')
c4d.plotdefaults(plt.gca(), 'Equations of Motion Integration ($\\theta$)', 'Time', 'degrees', fontsize = 12)
plt.legend()

plt.savefig(c4d.j(savedir, 'int6_vs_scipy.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

plt.show(block = True)














