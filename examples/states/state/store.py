import os, sys
sys.path.append('')
import numpy as np 
import c4dynamics as c4d 
from matplotlib import pyplot as plt 
plt.style.use('dark_background')  
plt.switch_backend('TkAgg')




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

c4d.cprint('get data for a particular variable', 'c') 
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

s.plot('z', filename = 'D:\\Dropbox\\c4dynamics\\docs\\source\\_examples\\z.png')










    