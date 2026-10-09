import sys
from typing import Union

import numpy as np

from c4dynamics import datapoint, quatbody, rigidbody

# sys.path.append(".")
from c4dynamics.utils.math import cos, sin, tan


def eqm3(dp: "datapoint", F: Union[np.ndarray, list]) -> np.ndarray:
    """
    Translational motion derivatives.

    These equations represent a set of first-order ordinary
    differential equations (ODEs) that describe the motion
    of a datapoint in three-dimensional space under the influence
    of external forces.

    Parameters
    ----------
    dp : :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`
        C4dynamics' datapoint object for which the equations of motion are calculated.

    F : array_like
        Force vector :math:`[F_x, F_y, F_z]`

    Returns
    -------
    out : numpy.array
        :math:`[dx, dy, dz, dv_x, dv_y, dv_z]`
        6 derivatives of the equations of motion, 3 position derivatives,
        and 3 velocity derivatives.

    Examples
    --------

    Import required packages:

    .. code::

      >>> import c4dynamics as c4d
      >>> from matplotlib import pyplot as plt
      >>> import numpy as np


    .. code::

      >>> dp = c4d.datapoint()
      >>> dp.mass = 10                    # mass 10kg     # doctest: +IGNORE_OUTPUT
      >>> F  = [0, 0, c4d.g_ms2]          # g_ms2 = 9.8m/s^2
      >>> c4d.eqm.eqm3(dp, F)             # doctest: +NUMPY_FORMAT
      array([0  0  0  0  0  0.980665])


    Euler integration on the equations of motion of
    mass in a free fall:


    .. code::

      >>> h0 = 10000
      >>> pt = c4d.datapoint(z = 10000)
      >>> while pt.z > 0:
      ...   pt.store()
      ...   dx = c4d.eqm.eqm3(pt, [0, 0, -c4d.g_ms2])
      ...   pt.X += dx  # (dt = 1)
      >>> pt.plot('z')
      >>> # comapre to anayltic solution
      >>> t = np.arange(len(pt.data('t')))
      >>> z = h0 - .5 * c4d.g_ms2 * t**2
      >>> plt.gca().plot(t[z > 0], z[z > 0], 'c', linewidth = 1) # doctest: +IGNORE_OUTPUT

    .. figure:: /_examples/eqm/eqm3.png

    """

    dx = dp.vx
    dy = dp.vy
    dz = dp.vz

    dvx = F[0] / dp.mass
    dvy = F[1] / dp.mass
    dvz = F[2] / dp.mass

    return np.array([dx, dy, dz, dvx, dvy, dvz])


def eqm6(rb: "rigidbody", F: Union[np.ndarray, list], M: Union[np.ndarray, list]) -> np.ndarray:
    """
    Translational and angular motion derivatives.

    A set of first-order ordinary
    differential equations (ODEs) that describe the motion
    of a rigid body in three-dimensional space under the influence
    of external forces and moments.

    Parameters
    ----------
    rb : :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
        C4dynamics' rigidbody object for which the
        equations of motion are calculated on.
    F : array_like
        Force vector :math:`[F_x, F_y, F_z]`
    M : array_like
        Moments vector :math:`[M_x, M_y, M_z]`

    Returns
    -------
    out : numpy.array
        :math:`[dx, dy, dz, dv_x, dv_y, dv_z, d\\varphi, d\\theta, d\\psi, dp, dq, dr]`

        12 total derivatives; 6 of translational motion, 6 of rotational motion.

    Examples
    --------
    Euler integration on the equations of motion of
    a stick fixed at one edge:

    (mass: 0.5 kg, moment of inertia about y: 0.4 kg*m^2,
    Length: 1m, initial Euler pitch angle: 80° (converted to radians))


    Import required packages:

    .. code::

      >>> import c4dynamics as c4d
      >>> import numpy as np

    Settings and initial conditions

    .. code::

      >>> dt = 0.5e-3
      >>> t = np.arange(0, 10, dt)
      >>> length =  1  # metter
      >>> rb = c4d.rigidbody(theta = 80 * c4d.d2r)
      >>> rb.mass = 0.5 # kg
      >>> rb.I = [0, 0.4, 0]


    Main loop:

    .. code::

      >>> for ti in t:
      ...    rb.store(ti)
      ...    tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
      ...    dx = c4d.eqm.eqm6(rb, np.zeros(3), [0, tau_g, 0])
      ...    rb.X += dx * dt
      >>> rb.plot('theta')

    .. figure:: /_examples/eqm/eqm3.png

    """

    return _derivs6(rb.X, rb.mass, rb.I, F, M)


def _derivs6(X, mass, I, F, M) -> np.ndarray:
    # euler angles six dof derivatives as a function of an explicit state vector.
    # x, y, z, vx, vy, vz, phi, theta, psi, p, q, r
    _, _, _, vx, vy, vz, phi, theta, _, p, q, r = X
    ixx, iyy, izz = I

    #
    # translational motion derivatives
    ##
    dx = vx
    dy = vy
    dz = vz

    dvx = F[0] / mass
    dvy = F[1] / mass
    dvz = F[2] / mass

    #
    # euler angles derivatives
    ##
    dphi = (q * sin(phi) + r * cos(phi)) * tan(theta) + p
    dtheta = q * cos(phi) - r * sin(phi)
    dpsi = (q * sin(phi) + r * cos(phi)) / cos(theta)

    #
    # angular motion derivatives
    ##
    dp = 0 if ixx == 0 else (M[0] - q * r * (izz - iyy)) / ixx
    dq = 0 if iyy == 0 else (M[1] - p * r * (ixx - izz)) / iyy
    dr = 0 if izz == 0 else (M[2] - p * q * (iyy - ixx)) / izz

    #       0   1   2   3    4    5    6     7       8     9   10  11
    return np.array([dx, dy, dz, dvx, dvy, dvz, dphi, dtheta, dpsi, dp, dq, dr])


def eqm6q(qb: "quatbody", F: Union[np.ndarray, list], M: Union[np.ndarray, list]) -> np.ndarray:
    """
    Translational and angular motion derivatives, quaternion attitude.

    The same six degrees of freedom model as
    :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>`,
    where the attitude kinematics are given by the
    quaternion :math:`q = [q_w, q_x, q_y, q_z]`
    rather than by Euler angles:

    .. math::

      \\dot{q} = {1 \\over 2} \\cdot q \\otimes [0, p, q, r]

    i.e.:

    .. math::

      \\dot{q}_w = -{1 \\over 2} (q_x p + q_y q + q_z r)

      \\dot{q}_x = {1 \\over 2} (q_w p + q_y r - q_z q)

      \\dot{q}_y = {1 \\over 2} (q_w q - q_x r + q_z p)

      \\dot{q}_z = {1 \\over 2} (q_w r + q_x q - q_y p)

    Unlike the Euler angles derivatives, the quaternion
    derivatives are free of singularities (e.g. at :math:`\\theta = \\pm 90°`).

    Parameters
    ----------
    qb : :class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`
        C4dynamics' quatbody object for which the
        equations of motion are calculated on.
    F : array_like
        Force vector :math:`[F_x, F_y, F_z]`
    M : array_like
        Moments vector :math:`[M_x, M_y, M_z]`

    Returns
    -------
    out : numpy.array
        :math:`[dx, dy, dz, dv_x, dv_y, dv_z, dq_w, dq_x, dq_y, dq_z, dp, dq, dr]`

        13 total derivatives; 6 of translational motion, 7 of rotational motion.

    Examples
    --------
    Euler integration on the equations of motion of
    a stick fixed at one edge:

    (mass: 0.5 kg, moment of inertia about y: 0.4 kg*m^2,
    Length: 1m, initial pitch angle: 80° (converted to radians))


    Import required packages:

    .. code::

      >>> import c4dynamics as c4d
      >>> import numpy as np

    Settings and initial conditions

    .. code::

      >>> dt = 0.5e-3
      >>> t = np.arange(0, 10, dt)
      >>> length =  1  # metter
      >>> qb = c4d.quatbody(theta = 80 * c4d.d2r)
      >>> qb.mass = 0.5 # kg
      >>> qb.I = [0, 0.4, 0]


    Main loop:

    .. code::

      >>> for ti in t:
      ...    qb.store(ti)
      ...    tau_g = -qb.mass * c4d.g_ms2 * length / 2 * c4d.cos(qb.theta)
      ...    dx = c4d.eqm.eqm6q(qb, np.zeros(3), [0, tau_g, 0])
      ...    qb.X += dx * dt
      >>> qb.plot('theta')

    .. figure:: /_examples/eqm/eqm6q.png

    """

    return _derivs6q(qb.X, qb.mass, qb.I, F, M)


def _derivs6q(X, mass, I, F, M) -> np.ndarray:
    # quaternion six dof derivatives as a function of an explicit state vector.
    # x, y, z, vx, vy, vz, qw, qx, qy, qz, p, q, r
    _, _, _, vx, vy, vz, qw, qx, qy, qz, p, q, r = X
    ixx, iyy, izz = I

    #
    # translational motion derivatives
    ##
    dx = vx
    dy = vy
    dz = vz

    dvx = F[0] / mass
    dvy = F[1] / mass
    dvz = F[2] / mass

    #
    # quaternion derivatives
    ##
    dqw = -0.5 * (qx * p + qy * q + qz * r)
    dqx = 0.5 * (qw * p + qy * r - qz * q)
    dqy = 0.5 * (qw * q - qx * r + qz * p)
    dqz = 0.5 * (qw * r + qx * q - qy * p)

    #
    # angular motion derivatives
    ##
    dp = 0 if ixx == 0 else (M[0] - q * r * (izz - iyy)) / ixx
    dq = 0 if iyy == 0 else (M[1] - p * r * (ixx - izz)) / iyy
    dr = 0 if izz == 0 else (M[2] - p * q * (iyy - ixx)) / izz

    #       0   1   2   3    4    5    6    7    8    9   10  11  12
    return np.array([dx, dy, dz, dvx, dvy, dvz, dqw, dqx, dqy, dqz, dp, dq, dr])


if __name__ == "__main__":

    from c4dynamics import rundoctests
    rundoctests(sys.modules[__name__])
