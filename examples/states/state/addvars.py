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




c4d.cprint('addvars', 'c')
s = c4d.state(x = 0, y = 0)
print(s)
# [ x  y ]
s.addvars(vx = 0, vy = 0)
print(s)
# [ x  y  vx  vy ]


s = c4d.state(x = 1, y = 1)
s.store()
s.store()
s.store()
s.addvars(vx = 0, vy = 0)
print(s.data('x')[1])
# [1. 1. 1.]
print(s.data('vx')[1])
# [0. 0. 0.]




