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



c4d.cprint('norm', 'c')
s = c4d.state(x1 = 1, x2 = -1)
print(s.norm)
print(type(s.norm))

