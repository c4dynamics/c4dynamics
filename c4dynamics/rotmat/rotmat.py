import numpy as np
# import c4dynamics as c4d 
from c4dynamics.utils.const import *  
from c4dynamics.utils.math import *  


def rotx(a):
    ''' 
    Generate a 3x3 rotation matrix for a rotation about the x-axis by an angle 'a' in radians.

    Parameters
    ----------
    a : float or int
        The angle of rotation in radians.

    Returns
    -------
    out : numpy.array
        A 3x3 rotation matrix representing the rotation about the x-axis.

    Examples
    --------
    
    >>> rotx(0)
    array([[1., 0., 0.],
           [0., 1., 0.],
           [0., 0., 1.]])

    
    >>> R = rotx(c4d.pi / 2)
    >>> print(R.round(decimals = 3))
    [[ 1.  0.  0.]
    [ 0.  0.  1.]
    [ 0. -1.  0.]]

           
    >>> v1 = [0, 0, 1]
    >>> phi = 90 * c4d.d2r
    >>> v2 = rotx(phi) @ v1
    >>> print(v2.round(decimals = 3))
    [0.  1.  0.]

    
    >>> phi = 45 * c4d.d2r
    >>> v2 = rotx(phi) @ v1
    >>> print(v2.round(decimals = 3))
    [0.  0.707  0.707]

    '''
    return np.array([[1, 0, 0], [0, cos(a), sin(a)], [0, -sin(a), cos(a)]])


def roty(a):
    ''' 
    Generate a 3x3 rotation matrix for a rotation about the y-axis by an angle 'a' in radians.

    Parameters
    ----------
    a : float or int
        The angle of rotation in radians.

    Returns
    -------
    out : numpy.array
        A 3x3 rotation matrix representing the rotation about the y-axis.

    Examples
    --------
    
    >>> roty(0)
    array([[1., 0., 0.],
           [0., 1., 0.],
           [0., 0., 1.]])
           
        
    >>> R = roty(c4d.pi / 2)
    >>> print(R.round(decimals = 3))
    [[ 0.  0. -1.]
    [ 0.  1.  0.]
    [ 1.  0.  0.]]

    
    >>> v1 = [0, 0, 1]
    >>> phi = 90 * c4d.d2r
    >>> v2 = roty(phi) @ v1
    >>> print(v2.round(decimals = 3))
    [-1.  0.  0.]

    
    >>> phi = 45 * c4d.d2r
    >>> v2 = roty(phi) @ v1
    >>> print(v2.round(decimals = 3))
    [-0.707  0.  0.707]

    '''
    return np.array([[cos(a), 0, -sin(a)], [0, 1, 0], [sin(a), 0, cos(a)]])


def rotz(a):
    ''' 
    Generate a 3x3 rotation matrix for a rotation about the z-axis by an angle 'a' in radians.

    Parameters
    ----------
    a : float or int
        The angle of rotation in radians.

    Returns
    -------
    out : numpy.array
        A 3x3 rotation matrix representing the rotation about the z-axis.

    Examples
    --------
    
    >>> rotz(0)
    array([[ 1.,  0.,  0.],
           [ 0.,  1.,  0.],
           [ 0.,  0.,  1.]])


    >>> R = rotz(c4d.pi / 2)
    >>> print(R.round(decimals = 3))
    [[ 0.  1.  0.]
    [-1.  0.  0.]
    [ 0.  0.  1.]]

    
    >>> v1 = [0.707, 0.707, 0]
    >>> phi = 90 * c4d.d2r
    >>> v2 = rotz(phi) @ v1
    >>> print(v2.round(decimals = 3))
    [ 0.707  -0.707  0. ]

    >>> phi = 45 * c4d.d2r
    >>> v2 = rotz(phi) @ v1
    >>> print(v2.round(decimals = 3))
    [1. 0. 0.]
    
    '''
    return np.array([[cos(a), sin(a), 0], [-sin(a), cos(a), 0], [0, 0, 1]])


def dcm321(rb):
    '''
    Generate a Direction Cosine Matrix (DCM) for a sequence of 
    rotations around axes in the following order: z, y, x.

    Parameters
    ----------
    rb : rigidbody
        C4dynamics's rigidbody object for which 
        the Euler angles `(rb.phi, rb.theta, rb.psi)`
        produce the rotation matrix. 

    Returns
    -------
    out : numpy.array
        3x3 Direction Cosine Matrix representing the combined rotation.

    Examples
    --------
    
    The inertial velocity vector of an aircraft expressed in an inertial earth frame is given by:
    
    >>> v = [150, 0, 0]
    
    The attitude of the aircraft with respect to the inertial earth frame is
    given by the 3 Euler angles: 
        
    >>> rb = c4d.rigidbody(phi = 0, theta = 30 * c4d.d2r, psi = 0) 
    
    The velcoty expressed in body frame:
    
    >>> vb = rb.BI @ v
    >>> print(vb.round(decimals = 1))
    [129.9  0.  75. ]

    '''

    return rotx(rb.phi) @ roty(rb.theta) @ rotz(rb.psi)


def dcm321euler(dcm):
    '''    
    Extract Euler angles (roll, pitch, yaw) from a Direction Cosine Matrix (DCM) of 3-2-1 order.

    The form of a 3-2-1 rotation matrix:   

    .. code:: 

        | cos(theta)*cos(psi)                                cos(theta)*sin(psi)                                 -sin(theta)          |
        | sin(phi)*sin(theta)*cos(psi)-cos(phi)*sin(psi)    -sin(phi)*cos(theta)*sin(psi)-cos(phi)*cos(psi)       sin(phi)*cos(theta) |
        | cos(phi)*sin(theta)*cos(psi)+sin(phi)*sin(psi)     cos(phi)*sin(theta)*sin(psi)-sin(phi)*cos(psi)       cos(phi)*cos(theta) |

    Parameters
    ----------
    dcm : numpy.array
        3x3 Direction Cosine Matrix representing a rotation.

    Returns
    -------
    out : tuple
        A tuple containing Euler angles (yaw, pitch, roll) in degrees.

    Notes
    -----
    Each set of Euler angles has a geometric singularity where 
    two angles are not uniquely defined.
    It is always the second angle which defines this singular orientation: 

    - Symmetric Set: 2nd angle is 0 or 180 degrees. For example the 3-1-3 orbit angles with zero inclination.
    - Asymmetric Set: 2nd angle is +-90 degrees. For example, the 3-2-1 angle of an aircraft with 90 degrees pitch. 

    Examples
    --------

    >>> dcm321euler(np.eye(3))
    (0.0, 0.0, 0.0)    
        
    A rotation matrix that represents the attitude of an aircraft with respect to 
    an inertial earth frame is given by:

    >>> BI = np.array([[ 0.8660254, 0, -0.5      ]
                        , [ 0,      1,  0.       ]
                        , [ 0.5,    0,  0.8660254]])
    >>> dcm321euler(BI)
    (0.0, 30.0, 0.0)

    '''
    
    psi   =  atan2(dcm[0, 1], dcm[0, 0]) * r2d
    theta = -asin(dcm[0, 2]) * r2d
    phi   =  atan2(dcm[1, 2], dcm[2, 2]) * r2d

    return phi, theta, psi 
