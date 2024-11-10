# type: ignore


import sys
sys.path.append('')
import c4dynamics as c4d 
import numpy as np 


dp = c4d.datapoint()
print(dp)
# [ x  y  z  vx  vy  vz ]

rb = c4d.rigidbody()
print(rb)
# [ x  y  z  vx  vy  vz  φ  θ  ψ  p  q  r ]

pp = c4d.pixelpoint()
print(pp)
# [ x  y  w  h ]


