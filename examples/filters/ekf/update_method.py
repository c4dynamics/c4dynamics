# type: ignore

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


savedir = os.path.join(c4path, 'docs', 'source', '_examples', 'ekf') 


def plain_correct(): 

  c4d.cprint('plain correct', 'y')

  ekf = c4d.filters.ekf({'x': 0}, P0 = .5**2, F = 1, H = 1, Q = 0.05, R = 200)
  print(ekf)
  print(ekf.X)
  print(ekf.P)
  ekf.update(z = 100)
  print(ekf.X)
  print(ekf.P) 




def varying_R(): 

  c4d.cprint('varying R', 'y')
  
  ekf = c4d.filters.ekf({'x': 0}, P0 = .5**2, F = 1, G = 150, H = 1, Q = 0.05, R = 200)

  print(ekf.X)
  print(ekf.P)
  ekf.update(z = 150, R = 0)
  print(ekf.X)
  print(ekf.P)


if __name__ == '__main__': 

  plain_correct()
  varying_R()
