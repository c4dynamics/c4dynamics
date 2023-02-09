import numpy as np 

def eqm3(xs, f, mass): 
    #
    # translational motion derivatives in inertial frame 
    ##
    _, _, _, vx, vy, vz = xs

    dx = vx
    dy = vy
    dz = vz

    dvx = f[0] / mass
    dvy = f[1] / mass
    dvz = f[2] / mass

    return np.array([dx, dy, dz, dvx, dvy, dvz])

