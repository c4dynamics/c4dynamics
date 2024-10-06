# from scipy.integrate import odeint 
# from scipy.linalg import solve_discrete_are
import numpy as np 
import cv2 
from matplotlib import pyplot as plt 


# not for demonstration: 
import os, sys
from enum import Enum  
import zlib 




plt.style.use('dark_background')  
plt.switch_backend('TkAgg')


def rootdir(dir):
  print(dir)
  if dir[-2:] == ':\\': return dir  
  return rootdir(os.path.dirname(dir))

def c4dir(dir, addpath = ''):
  # dirname and basename are supplamentary:
  # c:\dropbox\c4dynamics\text.txt
  # dirname: c:\dropbox\c4dynamics
  # basename: text.txt 
  


  inc4d = os.path.basename(dir) == 'c4dynamics'
  hasc4d = any(f == 'c4dynamics' for f in os.listdir(dir) 
                if os.path.isdir(os.path.join(dir, f)))


  if inc4d and hasc4d: 
    addpath += ''
    return addpath
  
  addpath += '..\\'
  return c4dir(os.path.dirname(dir), addpath)


# rootdir(os.getcwd()) 

print(os.getcwd())
c4path = c4dir(os.getcwd())
print(c4path)
sys.path.append(c4path)


import c4dynamics as c4d 
# from c4dynamics.utils.tictoc import tic, toc 

from c4dynamics.filters import kalman 

savedir = os.path.join(c4path, 'docs', 'source', '_examples', 'kf') 





c4d.cprint()
kf = kalman({'x': 0}, P0 = 500, F = 1, G = 1, H = 1, Q = .2, R = 5)

for i in range(50):
  kf.update(i + np.random.randn())
  kf.store(i)
  kf.predict(1 + np.random.randn())

kf.plot('x')
fig, ax = c4d._figdef()
ax.plot(*kf.data('P00'), 'c')
c4d.plotdefaults(ax, 'P', 'Time', '')
plt.show(block = True)






