import os, sys
sys.path.append('')
import numpy as np 
import c4dynamics as c4d 


c4d.cprint('get all stored data', 'c') 
s = c4d.state(x = 1, y = 0, z = 0)
for t in np.linspace(0, 1, 3):
  s.X = np.random.rand(3)
  s.store(t)
print(s.data())
# [[0.     0.37  0.76  0.20]
#  [0.5    0.93  0.28  0.59]
#  [1.     0.79  0.39  0.33]]


c4d.cprint('get data for a particular variable', 'c') 
time, x_data = s.data('x')
print(time)
# [0.  0.5 1. ]
print(x_data)
# [.37 .93 .79]
z_data = s.data('z')[1]
print(z_data)
# .20 .59 .33


c4d.cprint(' data with scalar ', 'c') 
s = c4d.state(phi = 0)
for p in np.linspace(0, c4d.pi):
  s.phi = p
  s.store()
print(s.data('phi', c4d.r2d)[1])
# [  0.           3.67346939   7.34693878  11.02040816  14.69387755
#   18.36734694  22.04081633  25.71428571


c4d.cprint('storeparams', 'c') 
s = c4d.state(x = 100, vx = 10)
s.mass = 25 
s.store()
s.storeparams('mass')
print(s.data('mass')[1])
# [25]



c4d.cprint('store with time stamp', 'c') 
s = c4d.state(x = 100, vx = 10)
s.mass = 25 
s.store()
s.storeparams('mass', t = 0.1)
print(s.data('mass'))
# ([0.1], [25)])






    