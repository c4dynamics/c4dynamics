import numpy as np
# import c4dynamics as c4d 
from c4dynamics.utils.const import *  
from c4dynamics.utils.math import *  


def rotx(phi):
    ''' 
    Generate a 3x3 Direction Cosine Matrix for 
    a positive rotation about the x-axis by an angle :math:`\\phi` in radians.

    A right-hand rotation matrix about `x` is given by: 

    .. math:: 
        
        R = \\begin{bmatrix}
            1 & 0 & 0 \\\\ 
                0 & cos(\\varphi) & sin(\\varphi) \\\\ 
                    0 & -sin(\\varphi) & cos(\\varphi) 
            \\end{bmatrix} 

        

    Parameters
    ----------
    phi : float or int
        The angle of rotation in radians.

    Returns
    -------
    out : numpy.array
        A 3x3 rotation matrix representing the rotation about the x-axis.

    
    Examples
    --------
    
    >>> rotx(0)
    [[1  0  0]
    [0  1  0]
    [0  0  1]]

    
    >>> R = rotx(c4d.pi / 2)
    >>> R
    [[1  0  0]
    [0  0  1]
    [0  -1  0]]

           
    >>> v1 = [0, 0, 1]
    >>> phi = 90 * c4d.d2r
    >>> v2 = rotx(phi) @ v1
    >>> v2
    [0  1  0]

    
    >>> phi = 45 * c4d.d2r
    >>> v2 = rotx(phi) @ v1
    >>> v2
    [0  0.707  0.707]

    '''
    return np.array([[1, 0, 0], [0, cos(phi), sin(phi)], [0, -sin(phi), cos(phi)]])


def roty(theta):
    ''' 
    Generate a 3x3 Direction Cosine Matrix for 
    a positive rotation about the y-axis by an angle :math:`\\theta` in radians.



    A right-hand rotation matrix about `y` is given by: 

    .. math:: 
        
        R = \\begin{bmatrix}
            cos(\\theta) & 0& -sin(\\theta) \\\\
                0 & 1 & 0 \\\\ 
                    sin(\\theta) & 0 & cos(\\theta)
            \\end{bmatrix}  

    
    Parameters
    ----------
    theta : float or int
        The angle of rotation in radians.

    Returns
    -------
    out : numpy.array
        A 3x3 rotation matrix representing the rotation about the y-axis.

    Examples
    --------
    
    >>> roty(0)
    [[1  0  0]
    [0  1  0]
    [0  0  1]]
           
        
    >>> R = roty(c4d.pi / 2)
    >>> R
    [[ 0  0  -1]
    [ 0  1  0]
    [ 1  0  0]]

    
    >>> v1 = [0, 0, 1]
    >>> phi = 90 * c4d.d2r
    >>> v2 = roty(phi) @ v1
    >>> v2
    [-1  0  0]

    
    >>> phi = 45 * c4d.d2r
    >>> v2 = roty(phi) @ v1
    >>> v2
    [-0.707  0  0.707]

    '''
    return np.array([[cos(theta), 0, -sin(theta)], [0, 1, 0], [sin(theta), 0, cos(theta)]])


def rotz(psi):
    ''' 
    Generate a 3x3 Direction Cosine Matrix for 
    a positive rotation about the z-axis by an angle :math:`\\psi` in radians.

    A right-hand rotation matrix about `y` is given by: 


    .. math:: 
        
        R = \\begin{bmatrix}
            cos(\\psi) & sin(\\psi) & 0 \\\\
                -sin(\\psi) & cos(\\psi) & 0 \\\\ 
                    0 & 0 & 1
            \\end{bmatrix}  



    Parameters
    ----------
    psi : float or int
        The angle of rotation in radians.

    Returns
    -------
    out : numpy.array
        A 3x3 rotation matrix representing the rotation about the z-axis.

    Examples
    --------
    
    >>> rotz(0)
    [[1  0  0]
    [0  1  0]
    [0  0  1]]


    >>> R = rotz(c4d.pi / 2)
    >>> R
    [[0  1  0]
    [-1  0  0]
    [0  0  1]]

    
    >>> v1 = [0.707, 0.707, 0]
    >>> phi = 90 * c4d.d2r
    >>> v2 = rotz(phi) @ v1
    >>> v2
    [0.707  -0.707  0]

    >>> phi = 45 * c4d.d2r
    >>> v2 = rotz(phi) @ v1
    >>> v2
    [1  0  0]
    
    '''
    return np.array([[cos(psi), sin(psi), 0], [-sin(psi), cos(psi), 0], [0, 0, 1]])


def dcm321(phi = 0, theta = 0, psi = 0):
    '''
    Generate a 3x3 Direction Cosine Matrix (DCM) for a sequence of 
    positive rotations around the axes in the following order: 
    :math:`z`, then :math:`y`, then :math:`x`.

    The final form of the matrix is given by: 

    .. math:: 
        
        R = \\begin{bmatrix}
              c\\theta \\cdot c\\psi 
            & c\\theta \\cdot s\\psi 
            & -s\\theta \\\\
                  s\\varphi \\cdot s\\theta \\cdot c\\psi - c\\varphi \\cdot s\\psi 
                & s\\varphi \\cdot s\\theta \\cdot s\\psi + c\\varphi \\cdot c\\psi 
                & s\\varphi \\cdot c\\theta \\\\ 
                      c\\varphi \\cdot s\\theta \\cdot c\\psi + s\\varphi \\cdot s\\psi 
                    & c\\varphi \\cdot s\\theta \\cdot s\\psi - s\\varphi \\cdot c\\psi 
                    & c\\varphi \\cdot c\\theta
            \\end{bmatrix}  

    where 

    - :math:`c\\varphi \\equiv cos(\\varphi)`
    - :math:`s\\varphi \\equiv sin(\\varphi)`
    - :math:`c\\theta \\equiv cos(\\theta)`
    - :math:`s\\theta \\equiv sin(\\theta)`
    - :math:`c\\psi \\equiv cos(\\psi)`
    - :math:`s\\psi \\equiv sin(\\psi)`    



    Parameters
    ----------
    phi : float or int 
        The angle in radian of rotation about `x`, default :math:`\\phi = 0`. 
    theta : float or int 
        The angle in radian of rotation about `y`, default :math:`\\theta = 0`. 
    psi : float or int 
        The angle in radian of rotation about `z`, default :math:`\\psi = 0`. 

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
    
    >>> vb = rb.BR @ v
    >>> vb
    [129.9  0  75]

    '''
    # FIXME very bad example 
    return rotx(phi) @ roty(theta) @ rotz(psi)


def dcm321euler(dcm):
    '''    
    Extract Euler angles (roll, pitch, yaw) from a Direction Cosine Matrix (DCM) of 3-2-1 order.

    The form of a 3-2-1 rotation matrix:   

    .. math:: 

        R = \\begin{bmatrix}
            c\\theta \\cdot c\\psi 
            & c\\theta \\cdot s\\psi 
            & -s\\theta \\\\
                s\\varphi \\cdot s\\theta \\cdot c\\psi - c\\varphi \\cdot s\\psi 
                & s\\varphi \\cdot s\\theta \\cdot s\\psi - c\\varphi \\cdot c\\psi 
                & s\\varphi \\cdot c\\theta \\\\ 
                    s\\varphi \\cdot s\\theta \\cdot s\\psi + s\\varphi \\cdot s\\psi 
                    & s\\varphi \\cdot s\\theta \\cdot s\\psi - s\\varphi \\cdot c\\psi 
                    & c\\varphi \\cdot c\\theta
            \\end{bmatrix}  

    where 

    - :math:`c\\varphi \\equiv cos(\\varphi)`
    - :math:`s\\varphi \\equiv sin(\\varphi)`
    - :math:`c\\theta \\equiv cos(\\theta)`
    - :math:`s\\theta \\equiv sin(\\theta)`
    - :math:`c\\psi \\equiv cos(\\psi)`
    - :math:`s\\psi \\equiv sin(\\psi)`
        

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
    - Asymmetric Set: 2nd angle is ±90 degrees. For example, the 3-2-1 angle of an aircraft with 90 degrees pitch. 

    Examples
    --------

    >>> dcm321euler(np.eye(3))
    (0, 0, 0)    
        
    A rotation matrix that represents the attitude of an aircraft with respect to 
    an inertial earth frame is given by:

    >>> BI = np.array([[ 0.866,     0, -0.5      ]
                        , [ 0,      1,  0        ]
                        , [ 0.5,    0,  0.866    ]])
    >>> dcm321euler(BI)
    (0, 30, 0)

    '''
    
    psi   =  atan2(dcm[0, 1], dcm[0, 0]) * r2d
    theta = -asin(dcm[0, 2]) * r2d
    phi   =  atan2(dcm[1, 2], dcm[2, 2]) * r2d

    return phi, theta, psi 
