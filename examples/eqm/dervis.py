# type: ignore

import os, sys 
sys.path.append('.')
import c4dynamics as c4d

import numpy as np 
from matplotlib import pyplot as plt 

c4path = c4d.c4dir(os.getcwd())
savedir = os.path.join(c4path, 'docs', 'source', '_examples', 'eqm') 



c4d.cprint('eqm3 - point mass', 'y')

pt = c4d.datapoint()
pt.mass = 10 
F = [0, 0, c4d.g_ms2]

print(c4d.eqm.eqm3(pt, F))
# [0. 0. 0. 0. 0. 0.980665]


c4d.cprint('eqm3 - euler integration', 'y')

'''
Run the equations of motion of mass in a free fall:
'''

h0 = 10000
pt = c4d.datapoint(z = h0)

while pt.z > 0:
    pt.store()
    dx = c4d.eqm.eqm3(pt, [0, 0, -c4d.g_ms2])
    pt.X += dx # dt = 1

# comapre to anayltic solution 
t = np.arange(len(pt.data('t')))
z = h0 - .5 * c4d.g_ms2 * t**2 

pt.plot('z')
plt.gca().plot(t[z > 0], z[z > 0], 'c', linewidth = 1, label = 'analytic')
plt.legend(**c4d._legdef())
plt.savefig(c4d.j(savedir, 'eqm3.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

plt.show(block = True)






c4d.cprint('eqm6 - fixed stick', 'y')

dt = .5e-3 
t = np.arange(0, 10, dt) # np.linspace(0, 10, 1000)
theta0 =  80 * c4d.d2r       # deg 
q0     =  0 * c4d.d2r        # deg to sec
Iyy    =  .4                  # kg * m^2 
length =  1                  # meter 
mass   =  0.5                # kg 
# theta = theta0 - Iyy / t 
# integration 
rb = c4d.rigidbody(theta = theta0, q = q0)
rb.mass = mass
rb.I = [0, Iyy, 0] 

for ti in t: 
    rb.store(ti)
    tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
    dx = c4d.eqm.eqm6(rb, np.zeros(3), [0, tau_g, 0])
    rb.X = rb.X + dx * dt 

rb.plot('theta', filename = c4d.j(savedir, 'eqm6.png'))










