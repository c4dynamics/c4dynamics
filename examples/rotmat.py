# type: error 

import sys 
sys.path.append('.')

import numpy as np
import c4dynamics as c4d
from c4dynamics.rotmat import rotx
from c4dynamics.rotmat import roty
from c4dynamics.rotmat import rotz
from c4dynamics.rotmat import dcm321euler
from c4dynamics.rotmat import dcm321euler, dcm321


c4d.cprint('rot x', 'y')

print(f'{rotx(0) = }')
print(f'{rotx(c4d.pi / 2) = }')

v1 = [0, 0, 1]
phi = 90 * c4d.d2r
v2 = rotx(phi) @ v1
print(f'{v2 = }')

phi = 45 * c4d.d2r
v2 = rotx(phi) @ v1
print(f'{v2 = }')


c4d.cprint('rot y', 'y')

print(f'{roty(0) = }')
print(f'{roty(c4d.pi / 2) = }')

v1 = [0, 0, 1]
phi = 90 * c4d.d2r
v2 = roty(phi) @ v1
print(f'{v2 = }')

phi = 45 * c4d.d2r
v2 = roty(phi) @ v1
print(f'{v2 = }')



c4d.cprint('rot z', 'y')

print(f'{rotz(0) = }')
print(f'{rotz(c4d.pi / 2) = }')

v1 = [0.707, 0.707, 0]
phi = 90 * c4d.d2r
v2 = rotz(phi) @ v1
print(f'{v2 = }')

phi = 45 * c4d.d2r
v2 = rotz(phi) @ v1
print(f'{v2 = }')


c4d.cprint('dcm 321', 'y')

# its inertial velocity vector is expressed in the inertial earth frame by:
v = [150, 0, 0]
# the attitude of an aircraft with respect to inerital erath frame 
# is given by: 
# the velcoty expressed in body frame is given by:
vb = dcm321(phi = 0, theta = 30 * c4d.d2r, psi = 0) @ v
print(f'{vb = }')


c4d.cprint('dcm 321 to euler', 'y')

print(dcm321euler(np.eye(3)))
print(dcm321euler(np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])))


# A rotation matrix that represents the attitude of an with respect to 
# an inertial earth frame is given by:

BI = np.array([[ 0.8660254,  0, -0.5      ]
                , [ 0,         1,  0.       ]
                , [ 0.5,       0,  0.8660254]])
print(BI)

print(dcm321euler(BI))