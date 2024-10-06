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


c4d.cprint('X - getter', 'c')
s = c4d.state(x1 = 0, x2 = -1)
print(s.X)


c4d.cprint('X - setter', 'c')
s = c4d.state(x1 = 0, x2 = -1)
s.X += [0, 1]
print(s.X)

