import numpy as np
from .params import * 

def rotx(a):
    ''' rotation about x axis dcm by a radians '''
    return np.array([[1, 0, 0], [0, cos(a), sin(a)], [0, -sin(a), cos(a)]])

def roty(a):
    ''' rotation about y axis dcm by a radians '''
    return np.array([[cos(a), 0, -sin(a)], [0, 1, 0], [sin(a), 0, cos(a)]])

def rotz(a):
    ''' rotation about z axis dcm by a radians '''
    return np.array([[cos(a), sin(a), 0], [-sin(a), cos(a), 0], [0, 0, 1]])

def dcm321(ax, ay, az):
    ''' 
    321 dcm 
        first rotate about z axis by az radians
        then rotate about y axis by ay radians
        finally rotate about x axis by ax radians
    '''
    return rotx(ax) @ roty(ay) @ rotz(az)

def dcm321euler(dcm):
    '''
    dcm321
    see peterschaub 2.3.5 varius euler angle transformations
    
    | c(theta)*c(psi)                                 c(theta)*s(psi)                         -sin(theta) |
    | s(phi)*s(theta)*c(psi)-c(phi)*s(psi)    -s(phi)*c(theta)*s(psi)-c(phi)*c(psi)       s(phi)*c(theta) |
    | c(phi)*s(theta)*c(psi)+s(phi)*s(psi)     c(phi)*s(theta)*s(psi)-s(phi)*c(psi)       c(phi)*c(theta) |
    
    '''
    
    psi = arctan(dcm[0, 1] / dcm[0, 0]) * r2d
    theta = -arctan(dcm[0, 2]) * r2d
    phi = arctan(dcm[1, 2] / dcm[2, 2]) * r2d
    return psi, theta, phi
