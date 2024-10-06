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


c4d.cprint('velocity', 'c')
s = c4d.state(x = 100, y = 0, vx = -10, vy = 5)
print(s.velocity)
# [-10  5]

s = c4d.state(z = 100, vz = -100)
print(s.velocity)
# [-100]

s = c4d.state(z = 100)
print(s.velocity)
# Warning: velocity is valid when at least one cartesian coordinate variable (vx, vy, vz) exists.    
# []

