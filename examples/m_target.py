# import math 
import numpy as np
from builtins import object

import os, sys
os.getcwd()
sys.path.append(os.path.join(os.getcwd(), '..'))

import C4dynamics as c4d


class c_target(object):
    """ 
        data point 
        vertically falling target
        ballistic coeficient 
    """
    z = 0
    vz = 0
    az = 0
    beta = 0
    data = np.array([[0, 0, 0, 0]]) # r, v, a, beta 
    
    def __init__(obj, x0, beta):
        obj.z, obj.vz, obj.az = x0
        obj.beta = beta
        obj.data = np.array([[obj.z, obj.vz, obj.az, obj.beta]]) #


    @staticmethod
    def deriv(y, t, tgt): 
        """ 
        run the target equations of motion. 
        """
        if y.ndim == 1:
            zT = y[0]
            vzT = y[1]
        else:
            zT = y[:, 0]
            vzT = y[:, 1]
            
        dzT = vzT
        dvzT = .0034 * np.exp(-zT.astype('float') / 22000 / c4d.params.ft2m) * c4d.params.g * vzT**2 / 2 / tgt.beta - c4d.params.g
            
        return dzT, dvzT

 
