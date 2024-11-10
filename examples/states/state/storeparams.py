# type: ignore

import os, sys
sys.path.append('')
import numpy as np 
import c4dynamics as c4d 
from matplotlib import pyplot as plt 
plt.style.use('dark_background')  
plt.switch_backend('TkAgg')



# every example should be self contained. 
runerrors = False
saveimages = False   
viewimages = False 

    


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



c4d.cprint('multiple params', 'c') 
s = c4d.state(x = 100, vx = 10)
s.x_std = 5 
s.vx_std = 10 
s.store()
s.storeparams(['x_std', 'vx_std'])
print(s.data('x_std')[1])
# [5]
print(s.data('vx_std')[1])
# [10]



c4d.cprint('objects detection', 'c') 
s = c4d.state(x = 25, y = 25, w = 20, h = 10)

np.random.seed(44)
for i in range(3): 

  s.X += 1 
  s.w, s.h = np.random.randint(0, 50, 2)

  if s.w > 40 or s.h > 20: 
    s.class_id = 'truck' 
  else:  
    s.class_id = 'car'

  s.store()
  s.storeparams('class_id')

print('   x    y    w    h    class')
print(np.hstack((s.data()[:, 1:].astype(int), np.atleast_2d(s.data('class_id')[1]).T)))
#   x    y    w    h    class
# [['26' '26' '20' '35' 'truck']
#  ['27' '27' '49' '45' 'truck']
#  ['28' '28' '3' '32' 'truck']]


c4d.cprint('add method', 'c') 


import types 

def getdim(s):
  if s.X[2] != 0:
    # z 
    s.dim = 3
  elif s.X[1] != 0:
    # y 
    s.dim = 2
  elif s.X[0] != 0:
    # x
    s.dim = 1
  else: 
    # none 
    s.dim = 0

morphospectra = c4d.state(x = 0, y = 0, z = 0)
morphospectra.dim = 0 
# setattr(morphospectra, 'getdim', getdim)
morphospectra.getdim = types.MethodType(getdim, morphospectra)

for r in range(10):
  morphospectra.X = np.random.choice([0, 1], 3)
  morphospectra.getdim()
  morphospectra.store()
  morphospectra.storeparams('dim')

print('x y z  | dim')
print('------------')
for x, dim in zip(morphospectra.data().astype(int)[:, 1 : 4].tolist(), morphospectra.data('dim')[1].tolist()):
  print(*(x + [' | '] + [dim]))
# x y z  | dim
# ------------
# 0 1 1  |  3
# 0 0 0  |  0
# 1 1 1  |  3
# 0 1 0  |  2
# 1 0 1  |  3
# 0 0 1  |  3
# 0 1 0  |  2
# 0 1 0  |  2
# 0 1 1  |  3
# 0 0 0  |  0










