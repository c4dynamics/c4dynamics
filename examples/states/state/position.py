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




c4d.cprint('position', 'c')
s = c4d.state(theta = 3.14, x = 1, y = 2)
print(s.position)
# [1, 2]

s = c4d.state(theta = 3.14, x = 1, y = 2, z = 3)
print(s.position)
# [1  2  3]

s = c4d.state(theta = 3.14, z = -100)
print(s.position)
# [-100]

s = c4d.state(theta = 3.14)
print(s.position)
# Warning: position is valid when at least one cartesian coordinate variable (x, y, z) exists.


