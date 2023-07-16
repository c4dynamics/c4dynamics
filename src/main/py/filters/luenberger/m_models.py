import numpy as np
from m_params import params
# np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)                 

""" 
"""
        
def nonlinear(x, t):
    dx = np.zeros(len(x))
    dx[0] = x[1]
    dx[1] = .0034 * np.exp(-x[0] / 22000) * x[1]**2 / 2 / x[2] - params.g
    dx[2] = 0
    return dx

def nonlinear_simp(x, t):
    dx = np.zeros(len(x))
    dx[0] = x[1]
    dx[1] = .0034 * x[1]**2 / 2 / x[2] - params.g
    dx[2] = 0
    return dx

def linear(x, t, b0): # linearized wrt the simplified nonlinear system. namely where the density is constant over all the altitudes. 
    dx = np.zeros(len(x))
    dx[0] = x[1]
    dx[1] = -np.sqrt(2 * 0.0034 * params.g / b0) * x[1] - params.g / b0 * x[2]
    dx[2] = 0
    return dx
