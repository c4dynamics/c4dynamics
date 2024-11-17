# type: ignore

import sys
sys.path.append('')
import c4dynamics as c4d 
import numpy as np 


s = c4d.state(x = 1, y = 0, z = 0)
print(s)
print(s.X)
R = c4d.rotmat.dcm321(psi = c4d.pi / 2)


c4d.cprint('scalar multiplication', 'g') 
print(s.X * 2)
# [2  0  0]


c4d.cprint('matrix multiplication', 'g') 
print(s.X @ R)
# [0  1  0]


c4d.cprint('magnitude \ norm ', 'g') 
print(np.linalg.norm(s.X))
# 1 


c4d.cprint('Addition', 'g') 
print(s.X + [-1, 0, 0])
# [0  0  0]


c4d.cprint('dot product', 'g') 
print(s.X @ s.X)
# 1


c4d.cprint('normaliztion', 'g') 
print(s.X / np.linalg.norm(s.X))
# [1  0  0]





c4d.cprint('store', 'c') 
s = c4d.state(x = 1, y = 0, z = 0)
s.store()
# -- 

c4d.cprint('store with time stamp', 'c') 
s = c4d.state(x = 1, y = 0, z = 0)
s.store(t = 0.5)
# -- 

c4d.cprint('get all stored data', 'c') 
s = c4d.state(x = 1, y = 0, z = 0)
for t in np.linspace(0, 1, 3):
  s.X = np.random.rand(3)
  s.store(t)
print(s.data())
# [[0.     0.37  0.76  0.20]
#  [0.5    0.93  0.28  0.59]
#  [1.     0.79  0.39  0.33]]


c4d.cprint('get the time series of the stored data', 'c') 
print(s.data('t'))
# [0.  0.5 1. ]

c4d.cprint('get the time series and the variable histories', 'c') 
time, x_data = s.data('x')
print(x_data)
# [0.92952596 0.48015511 0.10267647]
# 

c4d.cprint('get data for any particular variable', 'c') 
time, x_data = s.data('x')
print(time)
# [0.  0.5 1. ]
print(x_data)
# [0.92952596 0.48015511 0.10267647]
z_data = s.data('z')[1]
print(z_data)
# 


c4d.cprint('get state at a particular time', 'c') 
X05 = s.timestate(0.5)
print(X05)


c4d.cprint('plot the histories of a variable', 'c')
s = c4d.state(z = 0.20)
s.store(0)
s.z = 0.59 
s.store(0.5)
s.z = 0.33 
s.store(1)




c4d.cprint('new var: ', 'c')
s = c4d.state(y = 0, z = 0)
print(s)
s.new_var = 0
print(s)






if False: 






  c4d.cprint('rotation of a 2D vector in 90deg', 'g') 
  s = c4d.state(x = 1, y = 0)
  R = c4d.rotmat.rotz(c4d.pi / 2)[:2, :2]
  s.X @= R 
  print(s.X)


  c4d.cprint('rotation of a 3D vector in space', 'g') 
  s = c4d.state(x = 1, y = 1, z = 1)
  a = c4d.pi / 3
  R = c4d.rotmat.dcm321(phi = a, theta = a, psi = a)
  s.X @= R
  print(s.X)



  c4d.cprint('plot greek letter', 'c') 
  s = c4d.state(eta = 0)
  for t in np.linspace(0, 1, 100):
    s.X = np.random.rand()
    s.store(t)
  s.plot('eta')


  # utils 




