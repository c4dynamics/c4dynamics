import sys

import numpy as np

from c4dynamics.eqm.derivs import _derivs6, _derivs6q
from c4dynamics.rotmat import dcm321, quat2dcm

# x configuration, ardupilot motor order: front-right, rear-left, front-left, rear-right.
# +1: counterclockwise seen from above, -1: clockwise.
_ROTOR_DIR_X = np.array([1.0, 1.0, -1.0, -1.0])


def _up(frame):
    # direction of 'up' along the body z axis: +1 for FLU (ENU), -1 for FRD (NED).
    if frame == "NED":
        return -1.0
    if frame == "ENU":
        return 1.0
    raise ValueError(f"frame must be 'NED' or 'ENU', got {frame!r}")


def _bi(X):
    # body from inertial DCM of a 12-state (euler) or a 13-state (quaternion) vector.
    if len(X) == 12:
        return dcm321(X[6], X[7], X[8])
    if len(X) == 13:
        return quat2dcm(X[6:10])
    raise ValueError(f"X must have 12 (euler) or 13 (quaternion) entries, got {len(X)}")


def _rotor_geometry(quad, up):
    # rotor positions (body x, y) and spin directions. without explicit rotor_pos,
    # an x configuration with moment arm l, in the body frame of the given frame.
    rotor_pos = getattr(quad, "rotor_pos", None)
    if rotor_pos is None:
        l = quad.l
        y_right = -up * l
        rotor_pos = np.array([[ l,  y_right],    # front-right
                              [-l, -y_right],    # rear-left
                              [ l, -y_right],    # front-left
                              [-l,  y_right]])   # rear-right
    rotor_dir = getattr(quad, "rotor_dir", None)
    if rotor_dir is None:
        rotor_dir = _ROTOR_DIR_X
    return np.asarray(rotor_pos, float)[:, :2], np.asarray(rotor_dir, float)


def quadforces(X, quad, rotor_speeds, frame="NED"):
    """
    Body-frame force and moment acting on a quadcopter.

    The force is the rotor thrust plus the linear aerodynamic drag, without
    gravity. The moment is the rotor thrust and reaction torques, the
    rotational drag and the rotor gyroscopic coupling.
    :func:`quadeqm <c4dynamics.eqm.quadcopter.quadeqm>` adds gravity and
    integrates both through the rigid-body equations of motion.


    Parameters
    ----------
    X : array_like
        State vector. 12 entries for an euler-angles body
        (:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`):
        ``[x, y, z, vx, vy, vz, phi, theta, psi, p, q, r]``,
        or 13 entries for a quaternion body
        (:class:`quatbody <c4dynamics.states.lib.quatbody.quatbody>`):
        ``[x, y, z, vx, vy, vz, qw, qx, qy, qz, p, q, r]``.
    quad : object
        The vehicle parameters as attributes:
        ``kT`` thrust coefficient [N/(rad/s)^2],
        ``kQ`` torque coefficient [N.m/(rad/s)^2],
        ``Ax, Ay, Az`` linear drag along the body axes [N/(m/s)],
        ``Ar`` rotational drag [N.m/(rad/s)],
        ``IR`` rotor inertia [kg.m^2] (optional, default 0),
        ``wind`` wind velocity in the inertial frame [m/s] (optional,
        default still air; the drag acts on the air-relative velocity),
        and the rotor geometry: either ``rotor_pos`` (4 x 2, body x, y of
        each rotor [m], in the body frame of `frame`) with ``rotor_dir``
        (4, +1 counterclockwise seen from above, -1 clockwise, default
        ``[1, 1, -1, -1]``), or ``l`` [m] for an x configuration in the motor
        order front-right, rear-left, front-left, rear-right.
    rotor_speeds : array_like
        The four rotor speeds [rad/s].
    frame : {'NED', 'ENU'}, optional
        Inertial frame convention. ``'NED'`` with a forward-right-down body
        frame, ``'ENU'`` with a forward-left-up body frame. Defaults ``'NED'``.


    Returns
    -------
    F_b : numpy.ndarray
        Body-frame force, thrust plus drag [N].
    M_b : numpy.ndarray
        Body-frame moment [N.m].


    Note
    ----
    ``F_b / m`` is the specific force an accelerometer at the center of
    mass measures.


    Examples
    --------

    .. code::

        >>> import c4dynamics as c4d
        >>> import numpy as np
        >>> quad = c4d.struct(kT=3e-6, kQ=1e-7, l=0.2, Ax=0.3, Ay=0.3, Az=0.25, Ar=0.2)
        >>> X = np.zeros(12)
        >>> F_b, M_b = c4d.eqm.quadforces(X, quad, [600, 600, 600, 600])
        >>> F_b   # doctest: +NUMPY_FORMAT
        [0  0  -4.32]
        >>> M_b   # doctest: +NUMPY_FORMAT
        [0  0  0]

    """
    X = np.asarray(X, float).ravel()
    up = _up(frame)
    return _forces(X, quad, rotor_speeds, up, _bi(X))


def _forces(X, quad, rotor_speeds, up, BI):
    # quadforces() for a validated state vector, 'up' sign and body-from-inertial DCM.
    omega = np.asarray(rotor_speeds, float)
    p, q, r = X[-3:]

    pos, d = _rotor_geometry(quad, up)
    F = quad.kT * omega**2

    # thrust along body 'up' and linear drag on the air-relative body velocity
    wind = getattr(quad, "wind", None)
    v_air = X[3:6] if wind is None else X[3:6] - np.asarray(wind, float)
    u, v, wb = BI @ v_air
    F_b = np.array([-quad.Ax * u, -quad.Ay * v, up * F.sum() - quad.Az * wb])

    # thrust moments r x (0, 0, up * F), and the rotor reaction torques: a
    # counterclockwise rotor turns the body clockwise seen from above.
    # rotational drag, and the rotor gyroscopic coupling -w x h, where the
    # rotors' angular momentum h = IR * sum(d * omega) points along body 'up'.
    h = up * getattr(quad, "IR", 0.0) * (d @ omega)
    M_b = np.array([up * (pos[:, 1] @ F) - quad.Ar * p - q * h,
                    -up * (pos[:, 0] @ F) - quad.Ar * q + p * h,
                    -up * quad.kQ * (d @ omega**2) - quad.Ar * r])

    return F_b, M_b


def quadeqm(t, X, quad, rotor_speeds, frame="NED"):
    """
    Quadcopter equations of motion.

    Computes the force and the moment of
    :func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>`, adds gravity,
    and returns the state derivatives of
    :func:`eqm6 <c4dynamics.eqm.derivs.eqm6>` for a 12-state (euler angles)
    vector or of :func:`eqm6q <c4dynamics.eqm.derivs.eqm6q>` for a 13-state
    (quaternion) vector. The signature fits
    :func:`scipy.integrate.solve_ivp`:

    .. code::

        sol = solve_ivp(c4d.eqm.quadeqm, [t, t + dt], quad.X, args = (quad, rotor_speeds, 'ENU'))
        quad.X = sol.y[:, -1]


    Parameters
    ----------
    t : float
        Time [s]. Unused (the model is time invariant), kept for
        :func:`scipy.integrate.solve_ivp`.
    X : array_like
        State vector, 12 entries (euler angles) or 13 (quaternion). See
        :func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>`.
    quad : object
        The vehicle parameters as attributes: ``m`` mass [kg], ``g``
        gravity [m/s^2], ``Ixx, Iyy, Izz`` principal moments of inertia
        [kg.m^2], and the parameters of
        :func:`quadforces <c4dynamics.eqm.quadcopter.quadforces>`.
    rotor_speeds : array_like
        The four rotor speeds [rad/s], held constant over the call.
    frame : {'NED', 'ENU'}, optional
        Inertial frame convention: ``'NED'`` with a forward-right-down body
        frame (gravity along +z), ``'ENU'`` with a forward-left-up body frame
        (gravity along -z). Defaults ``'NED'``.


    Returns
    -------
    dX : numpy.ndarray
        State derivatives, the same length as `X`.


    Examples
    --------

    At hover, the thrust carries the weight and the vehicle stays put:

    .. code::

        >>> import c4dynamics as c4d
        >>> import numpy as np
        >>> quad = c4d.struct(m=0.468, g=9.81, Ixx=4.856e-3, Iyy=4.856e-3, Izz=8.801e-3,
        ...                   kT=2.98e-6, kQ=1.14e-7, l=0.225, Ax=0.3, Ay=0.3, Az=0.25, Ar=0.2)
        >>> w_hover = np.sqrt(quad.m * quad.g / 4 / quad.kT)
        >>> dX = c4d.eqm.quadeqm(0, np.zeros(12), quad, [w_hover] * 4, 'ENU')
        >>> np.allclose(dX, 0)
        True

    The same vehicle with a quaternion attitude:

    .. code::

        >>> X = np.zeros(13)
        >>> X[6] = 1   # identity quaternion
        >>> np.allclose(c4d.eqm.quadeqm(0, X, quad, [w_hover] * 4, 'ENU'), 0)
        True

    """
    X = np.asarray(X, float).ravel()
    up = _up(frame)
    BI = _bi(X)
    F_b, M_b = _forces(X, quad, rotor_speeds, up, BI)

    # body force to the inertial frame, plus gravity (along -up)
    F_i = BI.T @ F_b
    F_i[2] -= up * quad.m * quad.g
    I = (quad.Ixx, quad.Iyy, quad.Izz)

    if len(X) == 12:
        return _derivs6(X, quad.m, I, F_i, M_b)
    return _derivs6q(X, quad.m, I, F_i, M_b)


if __name__ == "__main__":

    from c4dynamics import rundoctests
    rundoctests(sys.modules[__name__])
