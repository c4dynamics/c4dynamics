import numpy as np 

def eqm3(dp, F): 
    '''
    Translational motion derivatives.

    These equations represent a set of first-order ordinary 
    differential equations (ODEs) that describe the motion 
    of a datapoint in three-dimensional space under the influence 
    of external forces. 
    
    Parameters
    ----------
    dp : datapoint
        C4dynamics' datapoint object for which the 
        equations of motion are calculated on. 
    F : array_like
        Force vector :math:`[F_x, F_y, F_z]`
   
    Returns
    -------
    out : numpy array 
        :math:`[dx, dy, dz, dv_x, dv_y, dv_z]`
        6 derivatives of the equations of motion, 3 position derivatives, 
        and 3 velocity derivatives.  

    Examples
    --------

    >>> dp = c4d.datapoint(mass = 10)   # mass 10kg
    >>> F  = [0, 0, c4d.g_ms2]          # g_ms2 = 9.8m/s^2
    >>> c4d.eqm.eqm3(dp, F)
    array([0., 0., 0., 0., 0., -0.980665])

    Euler integration on the equations of motion of 
    mass in a free fall:

    >>> h0 = 100
    >>> dp = c4d.datapoint(z = h0)
    >>> dt = 1e-2
    >>> while True:
    ...    if dp.z < 0: break
    ...    dx = c4d.eqm.eqm3(dp, [0, 0, -c4d.g_ms2])
    ...    dp.X = dp.X + dx * dt 
    ...    dp.store()
    >>> dp.draw('z')

    .. figure:: /_static/figures/eqm3_z.png

    '''
    
    dx = dp.vx
    dy = dp.vy
    dz = dp.vz

    dvx = F[0] / dp.mass
    dvy = F[1] / dp.mass
    dvz = F[2] / dp.mass

    return np.array([dx, dy, dz, dvx, dvy, dvz])







