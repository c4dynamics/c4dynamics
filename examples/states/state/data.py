# type: ignore

import os, sys
sys.path.append('')
import numpy as np 
import c4dynamics as c4d 


c4d.cprint('get all stored data', 'c') 
np.random.seed(100)
s = c4d.state(x = 1, y = 0, z = 0)
for t in np.linspace(0, 1, 3):
  s.X = np.random.rand(3)
  s.store(t)
print(s.data())
# [[0.         0.54340494 0.27836939 0.42451759]
#  [0.5        0.84477613 0.00471886 0.12156912]
#  [1.         0.67074908 0.82585276 0.13670659]]


c4d.cprint('get data for a particular variable', 'c') 
time, x_data = s.data('x')
print(time)
# [0.  0.5 1. ]
print(x_data)
# [0.54340494 0.27836939 0.42451759]
y_data = s.data('y')[1]
print(y_data)
# 0.84477613 0.00471886 0.12156912


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






    