# from c4dynamics.params import * 
import numpy as np

def eqm6(xs, f, m, mass, ixx, iyy, izz): 
    '''
    translational motion derivatives
    euler angles derivatives
    angular motion derivatives 
    '''
    _, _, _, vx, vy, vz, phi, theta, psi, p, q, r = xs

    #
    # translational# motion derivatives
    ##

    dx = vx
    dy = vy
    dz = vz

    dvx = f[0] / mass 
    dvy = f[1] / mass
    dvz = f[2] / mass
    # 
    # euler angles derivatives
    ## 

    dphi   = (q * np.sin(phi) + r * np.cos(phi)) * np.tan(theta) + p
    dtheta =  q * np.cos(phi) - r * np.sin(phi)
    dpsi   = (q * np.sin(phi) + r * np.cos(phi)) / np.cos(theta)

    # 
    # angular motion derivatives 
    ## 
    # dp     = (lA - q * r * (izz - iyy)) / ixx
    dp = 0 if ixx == 0 else (m[0] - q * r * (izz - iyy)) / ixx
    dq = 0 if iyy == 0 else (m[1] - p * r * (ixx - izz)) / iyy
    dr = 0 if izz == 0 else (m[2] - p * q * (iyy - ixx)) / izz

    return np.array([dx, dy, dz, dvx, dvy, dvz, dphi, dtheta, dpsi, dp, dq, dr])


