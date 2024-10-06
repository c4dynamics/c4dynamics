import os, sys
sys.path.append('')
import numpy as np 
import c4dynamics as c4d 


s = c4d.state(x = 0, y = 0, z = 0)
for t in np.linspace(0, 1, 3):
  s.X += 1
  s.store(t)

c4d.cprint('get state at a particular time', 'c') 
print(s.timestate(0.5))
# [0.2878431269074173, 0.9522673608993524, 0.8275101397814865]

c4d.cprint('get state when no histories', 'c') 
s = c4d.state(x = 1, y = 0, z = 0)
print(s.timestate(0.5))
# Warning: no history of state samples.
# None 

