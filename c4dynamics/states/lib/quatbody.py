import sys
import warnings

import numpy as np
from matplotlib import pyplot as plt

# sys.path.append(".")
import c4dynamics as c4d
from c4dynamics.states.lib.datapoint import datapoint


class quatbody(datapoint):
    """
    A rigid-body object with a quaternion attitude


    The :class:`quatbody` is the quaternion replicate of the
    :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`.
    It extends the
    :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`
    class to form an elementary rigidbody object in space, i.e.
    an object with length and attitude,
    where the attitude is represented by a unit quaternion
    rather than by Euler angles.

    The dynamics model is the same model of the
    :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`.
    However, the Euler angles kinematics are singular at
    :math:`\\theta = \\pm 90°` (gimbal lock), while the quaternion
    kinematics are not. This makes the `quatbody` suitable
    for agile vehicles, such as drones, that may
    reach any attitude (e.g. flips).

    Its state vector consists of the following variables:

    .. math::

      X = [x, y, z, v_x, v_y, v_z, q_w, q_x, q_y, q_z, p, q, r]^T

    - Position coordinates, velocity coordinates.
    - Attitude quaternion (scalar first), angular rates.

    The quaternion :math:`[q_w, q_x, q_y, q_z]` represents
    the same attitude as the 3-2-1 Euler angles
    :math:`[\\varphi, \\theta, \\psi]` of the
    :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
    (see :func:`euler2quat <c4dynamics.rotmat.rotmat.euler2quat>`).
    The Euler angles :attr:`phi`, :attr:`theta`, :attr:`psi`
    are available as properties that are derived from the quaternion.



    **Arguments**

    x : float or int, optional
        The x-position of the datapoint. Default value :math:`x = 0`.
    y : float or int, optional
        The y-position of the datapoint. Default value :math:`y = 0`.
    z : float or int, optional
        The z-position of the datapoint. Default value :math:`z = 0`.
    vx : float or int, optional
        Component of velocity along the x-axis. Default value :math:`v_x = 0`.
    vy : float or int, optional
        Component of velocity along the y-axis. Default value :math:`v_y = 0`.
    vz : float or int, optional
        Component of velocity along the z-axis. Default value :math:`v_z = 0`.
    phi : float or int, optional
        Initial Euler angle representing rotation around the x-axis (rad). Default value
        :math:`\\varphi = 0`.
    theta : float or int, optional
        Initial Euler angle representing rotation around the y-axis (rad). Default value
        :math:`\\theta = 0`.
    psi : float or int, optional
        Initial Euler angle representing rotation around the z-axis (rad). Default value
        :math:`\\psi = 0`.
    p : float or int, optional
        Angular rate around the x-axis (roll). (rad/sec). Default value :math:`p = 0`.
    q : float or int, optional
        Angular rate around the y-axis (pitch). (rad/sec). Default value :math:`q = 0`.
    r : float or int, optional
        Angular rate around the z-axis (yaw). (rad/sec). Default value :math:`r = 0`.
    quat : array_like, optional
        Initial attitude quaternion :math:`[q_w, q_x, q_y, q_z]`.
        If provided, it overrides `phi`, `theta`, and `psi`. The
        quaternion is normalized. Default value: `None`.


    The initial attitude is provided either by Euler angles,
    as in the :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`,
    or directly by a quaternion.
    The vector of initial conditions can be retrieved by calling
    :attr:`quatbody.X0 <c4dynamics.states.state.state.X0>`:

    .. code::

      >>> from c4dynamics import quatbody

    .. code::

      >>> qb = quatbody(z = 10, psi = 90 * c4d.d2r, r = 0.5)
      >>> qb.X0 # doctest: +NUMPY_FORMAT
      [0  0  10  0  0  0  0.707  0  0  0.707  0  0  0.5]


    Note
    ----
    The quaternion components are named :math:`q_w, q_x, q_y, q_z`
    (`qw`, `qx`, `qy`, `qz`) rather than :math:`q_0, ..., q_3`,
    since the `0` suffix of a state variable is reserved for its
    initial value (e.g. `q0` is the initial pitch rate,
    see :attr:`state.X0 <c4dynamics.states.state.state.X0>`).


    Parameters
    ==========

    mass : float
        The mass of the datapoint
    I : [float, float, float]
        An array of moments of inertia

    See Also
    ========
    .lib
    .rigidbody
    .rotmat
    .state
    .eqm


    Example
    =======

    A quadcopter performs a back flip: it starts at a level attitude
    with a pitch rate of one revolution per second, and
    rotates freely (no external forces nor moments) for one second.

    The Euler angles kinematics of a
    :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
    cross the singularity at :math:`\\theta = 90°`.
    The quaternion kinematics of the `quatbody` remain regular
    along the entire maneuver.


    import required packages:

    .. code::

      >>> import c4dynamics as c4d
      >>> from matplotlib import pyplot as plt
      >>> import numpy as np


    Settings and initial conditions:

    .. code::

      >>> dt = 0.001
      >>> drone = c4d.quatbody(z = 10, q = 2 * np.pi)
      >>> drone.I = [0.0082, 0.0082, 0.0149]
      >>> drone.mass = 1.2


    Main loop:

    .. code::

      >>> for t in np.arange(0, 1, dt):
      ...   drone.store(t)
      ...   drone.inteqm(np.zeros(3), np.zeros(3), dt)  # doctest: +IGNORE_OUTPUT


    After a full revolution the quaternion returns to
    the level attitude (up to the sign):

    .. code::

      >>> drone.store(1)
      >>> np.abs(drone.quat)  # doctest: +NUMPY_FORMAT
      [1  0  0  0]


    The pitch component of the quaternion,
    :math:`q_y = sin(q \\cdot t / 2)`, goes smoothly through the
    entire revolution:

    .. code::

      >>> _, ax = plt.subplots(2, 1)
      >>> drone.plot('qw', ax = ax[0])
      >>> ax[0].set(xlabel = '')  # doctest: +IGNORE_OUTPUT
      >>> drone.plot('qy', ax = ax[1])

    .. figure:: /_examples/quatbody/intro_backflip.png

    The :meth:`animate` method allows the user to play the attitude
    histories given a 3D model (requires installation of `open3D`),
    exactly as with the
    :meth:`rigidbody.animate <c4dynamics.states.lib.rigidbody.rigidbody.animate>`.

    """

    qw: float
    qx: float
    qy: float
    qz: float
    p: float
    q: float
    r: float

    _ixx = 0
    _iyy = 0
    _izz = 0

    _angles_names = ("phi", "theta", "psi")

    def __init__(
        self,
        x=0,
        y=0,
        z=0,
        vx=0,
        vy=0,
        vz=0,
        phi=0,
        theta=0,
        psi=0,
        p=0,
        q=0,
        r=0,
        quat=None,
    ):

        if quat is None:
            quat = c4d.rotmat.euler2quat(phi, theta, psi)
        quat = self._unitquat(quat)

        qbargs = {}

        qbargs.setdefault("x", x)
        qbargs.setdefault("y", y)
        qbargs.setdefault("z", z)
        qbargs.setdefault("vx", vx)
        qbargs.setdefault("vy", vy)
        qbargs.setdefault("vz", vz)

        qbargs.setdefault("qw", quat[0])
        qbargs.setdefault("qx", quat[1])
        qbargs.setdefault("qy", quat[2])
        qbargs.setdefault("qz", quat[3])
        qbargs.setdefault("p", p)
        qbargs.setdefault("q", q)
        qbargs.setdefault("r", r)

        c4d.state.__init__(self, **qbargs)

    @staticmethod
    def _unitquat(quat):
        quat = np.asarray(quat, dtype=np.float64).ravel()
        if quat.size != 4:
            raise ValueError("quat must be an array of four elements [qw, qx, qy, qz].")
        qnorm = np.linalg.norm(quat)
        if qnorm == 0:
            raise ValueError("quat must be a non-zero quaternion.")
        return quat / qnorm

    @property
    def I(self):
        """
        Gets and sets the array of moments of inertia.

        .. math::

          I = [I_{xx}, I_{yy}, I_{zz}]


        Default: :math:`I = [0, 0, 0]`


        Parameters
        ----------
        I : numpy.array or list
            An array of three moments of inertia about each
            one of the axes :math:`([I_{xx}, I_{yy}, I_{zz}])`.


        Returns
        -------
        out : numpy.array
            An array of the three moments of inertia :math:`[I_{xx}, I_{yy}, I_{zz}]`.


        Example
        -------

        The moments of inertia determine how much torque is
        required for a desired angular acceleration about a rotational axis.

        In this example, two drones with the same yaw torque
        and different moments of inertia about the z axis
        are compared.
        The drone with the larger moment of inertia accelerates slower:

        .. math::

          \\dot{r} = {M_z \\over I_{zz}}


        Import required packages:

        .. code::

          >>> import c4dynamics as c4d
          >>> from matplotlib import pyplot as plt
          >>> import numpy as np


        Settings and initial condtions:

        .. code::

          >>> dt = 0.01
          >>> torque = [0, 0, 0.01]
          >>> light = c4d.quatbody()
          >>> light.I = [0.0082, 0.0082, 0.0149]
          >>> heavy = c4d.quatbody()
          >>> heavy.I = [0.0164, 0.0164, 0.0298]


        Main loop

        .. code::

          >>> for ti in np.arange(0, 2, dt):
          ...   light.inteqm(np.zeros(3), torque, dt)  # doctest: +IGNORE_OUTPUT
          ...   light.store(ti)
          ...   heavy.inteqm(np.zeros(3), torque, dt)  # doctest: +IGNORE_OUTPUT
          ...   heavy.store(ti)


        Plot results:

        .. code::

          >>> light.plot('psi')
          >>> heavy.plot('psi', ax = plt.gca(), color = 'c')

        .. figure:: /_examples/quatbody/Izz_yaw.png


        """
        return np.array([self._ixx, self._iyy, self._izz])

    @I.setter
    def I(self, I):
        self._ixx = I[0]
        self._iyy = I[1]
        self._izz = I[2]

    @property
    def quat(self):
        """
        Gets and sets the attitude quaternion.

        .. math::

          quat = [q_w, q_x, q_y, q_z]

        The quaternion is scalar first (Hamilton convention).
        A set quaternion is normalized to a unit quaternion.


        Parameters
        ----------
        quat : numpy.array or list
            A quaternion :math:`[q_w, q_x, q_y, q_z]`.


        Returns
        -------
        out : numpy.array
            The attitude quaternion :math:`[q_w, q_x, q_y, q_z]`.


        Examples
        --------

        .. code::

          >>> qb = c4d.quatbody(phi = 90 * c4d.d2r)
          >>> qb.quat  # doctest: +NUMPY_FORMAT
          [0.707  0.707  0  0]

        .. code::

          >>> qb.quat = [1, 0, 0, 1]
          >>> qb.quat  # doctest: +NUMPY_FORMAT
          [0.707  0  0  0.707]
          >>> qb.angles * c4d.r2d  # doctest: +NUMPY_FORMAT
          [0  0  90]

        """
        return np.array([self.qw, self.qx, self.qy, self.qz])

    @quat.setter
    def quat(self, quat):
        self.qw, self.qx, self.qy, self.qz = self._unitquat(quat)

    @property
    def angles(self):
        """
        Returns an array of Euler angles.


        .. math::

          angles = [\\varphi, \\theta, \\psi]


        The 3-2-1 Euler angles are derived from the attitude quaternion
        (see :func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>`).


        Returns
        -------
        out : numpy.array
            An array of three Euler angles, about each one of the axes
            :math:`([\\varphi, \\theta, \\psi])`


        Examples
        --------

        .. code::

          >>> qb = c4d.quatbody(phi = 135 * c4d.d2r)
          >>> qb.angles * c4d.r2d # doctest: +NUMPY_FORMAT
          [135  0  0]

        """

        return c4d.rotmat.quat2euler(self.quat)

    @property
    def phi(self):
        """
        Gets and sets the Euler roll angle, :math:`\\varphi` (rad).

        The angle is derived from the attitude quaternion.
        Setting the angle updates the quaternion while
        the other two Euler angles are kept.

        Examples
        --------

        .. code::

          >>> qb = c4d.quatbody(theta = 10 * c4d.d2r)
          >>> qb.phi = 20 * c4d.d2r
          >>> qb.angles * c4d.r2d  # doctest: +NUMPY_FORMAT
          [20  10  0]

        """
        return self.angles[0]

    @phi.setter
    def phi(self, phi):
        _, theta, psi = self.angles
        self.quat = c4d.rotmat.euler2quat(phi, theta, psi)

    @property
    def theta(self):
        """
        Gets and sets the Euler pitch angle, :math:`\\theta` (rad).

        The angle is derived from the attitude quaternion.
        Setting the angle updates the quaternion while
        the other two Euler angles are kept.

        Examples
        --------

        .. code::

          >>> qb = c4d.quatbody()
          >>> qb.theta = 30 * c4d.d2r
          >>> qb.theta * c4d.r2d  # doctest: +NUMPY_FORMAT
          30

        """
        return self.angles[1]

    @theta.setter
    def theta(self, theta):
        phi, _, psi = self.angles
        self.quat = c4d.rotmat.euler2quat(phi, theta, psi)

    @property
    def psi(self):
        """
        Gets and sets the Euler yaw angle, :math:`\\psi` (rad).

        The angle is derived from the attitude quaternion.
        Setting the angle updates the quaternion while
        the other two Euler angles are kept.

        Examples
        --------

        .. code::

          >>> qb = c4d.quatbody()
          >>> qb.psi = 45 * c4d.d2r
          >>> qb.quat  # doctest: +NUMPY_FORMAT
          [0.924  0  0  0.383]

        """
        return self.angles[2]

    @psi.setter
    def psi(self, psi):
        phi, theta, _ = self.angles
        self.quat = c4d.rotmat.euler2quat(phi, theta, psi)

    @property
    def ang_rates(self):
        """
        Returns an array of angular rates.

        .. math::

          angular rates = [p, q, r]



        Returns
        -------
        out : numpy.array
            An array of three angular rates of the body axes
            :math:`([p, q, r])`


        Examples
        --------

        .. code::

          >>> q0 = 30
          >>> qb = c4d.quatbody(q = q0)
          >>> qb.ang_rates # doctest: +NUMPY_FORMAT
          [0  30  0]

        """
        return np.array([self.p, self.q, self.r])

    @property
    def BR(self):
        """
    Returns a Body-from-Reference Direction Cosine Matrix (DCM).


    Based on the current attitude quaternion :math:`[q_w, q_x, q_y, q_z]`,
    `BR` returns the DCM that is calculated by the
    :func:`quat2dcm <c4dynamics.rotmat.rotmat.quat2dcm>` function
    and is given by:

    .. math::

      R = \\begin{bmatrix}
            1 - 2(q_y^2 + q_z^2)
          & 2(q_x q_y + q_w q_z)
          & 2(q_x q_z - q_w q_y) \\\\
                2(q_x q_y - q_w q_z)
              & 1 - 2(q_x^2 + q_z^2)
              & 2(q_y q_z + q_w q_x) \\\\
                    2(q_x q_z + q_w q_y)
                  & 2(q_y q_z - q_w q_x)
                  & 1 - 2(q_x^2 + q_y^2)
          \\end{bmatrix}

    The matrix is identical to the DCM in a 3-2-1 order
    (:func:`dcm321 <c4dynamics.rotmat.rotmat.dcm321>`) of the same attitude.

    For the background material regarding the rotational matrix operations,
    see :mod:`rotmat <c4dynamics.rotmat>`.

    Returns
    -------

    out : numpy.ndarray
        A 3x3 DCM matrix uses to rotate a vector
        to the body frame
        from a reference frame of coordinates.


    Example
    -------

    .. code::

      >>> v_inertial = [1, 0, 0]
      >>> qb = c4d.quatbody(psi = 45 * c4d.d2r)
      >>> v_body = qb.BR @ v_inertial
      >>> v_body  # doctest: +NUMPY_FORMAT
      [0.707  -0.707  0.0]

    """

        return c4d.rotmat.quat2dcm(self.quat)

    @property
    def RB(self):
        """
    Returns a Reference-from-Body Direction Cosine Matrix (DCM).


    Based on the current attitude quaternion, `RB` returns the
    transpose matrix of :attr:`BR <c4dynamics.states.lib.quatbody.quatbody.BR>`,
    where :attr:`BR <c4dynamics.states.lib.quatbody.quatbody.BR>`
    is the Body from Reference DCM:

    .. math::

      R = \\begin{bmatrix}
            1 - 2(q_y^2 + q_z^2)
          & 2(q_x q_y - q_w q_z)
          & 2(q_x q_z + q_w q_y) \\\\
                2(q_x q_y + q_w q_z)
              & 1 - 2(q_x^2 + q_z^2)
              & 2(q_y q_z - q_w q_x) \\\\
                    2(q_x q_z - q_w q_y)
                  & 2(q_y q_z + q_w q_x)
                  & 1 - 2(q_x^2 + q_y^2)
          \\end{bmatrix}


    For the background material regarding the rotational matrix operations,
    see :mod:`rotmat <c4dynamics.rotmat>`.


    Returns
    -------

    out : numpy.ndarray
        A 3x3 DCM matrix uses to rotate a vector from a body frame
        to a reference frame of coordinates.


    Example
    -------

    .. code::

      >>> v_body = [np.sqrt(3), 0, 1]
      >>> qb = c4d.quatbody(theta = 30 * c4d.d2r)
      >>> v_inertial = qb.RB @ v_body
      >>> v_inertial   # doctest: +NUMPY_FORMAT
      [2.0  0.0  0.0]

    """
        return np.transpose(self.BR)

    def inteqm(self, forces, moments, dt):  # type: ignore
        """
        Advances the state vector, :attr:`quatbody.X <c4dynamics.states.state.state.X>`,
        with respect to the input
        forces and moments on a single step of time, `dt`.

        Integrates equations of six degrees motion using the Runge-Kutta method.

        This method numerically integrates the equations of motion for a dynamic system
        using the fourth-order Runge-Kutta method as given by
        :func:`eqm.int6q <c4dynamics.eqm.integrate.int6q>`.

        The derivatives of the equations are of six dimensional motion
        with quaternion attitude kinematics as given by
        :py:func:`eqm.eqm6q <c4dynamics.eqm.derivs.eqm6q>`.
        The quaternion is normalized at the end of each step.


        Parameters
        ----------
        forces : numpy.array or list
            An external forces vector acting on the body, `forces = [Fx, Fy, Fz]`
        moments : numpy.array or list
            An external moments vector acting on the body, `moments = [Mx, My, Mz]`
        dt : float or int
            Interval time step for integration.


        Returns
        -------
        out : numpy.float64
            An acceleration array at the final time step,
            :math:`[dv_x, dv_y, dv_z, dp, dq, dr]`.


        Warning
        -------
        This method is not recommanded when the vectors
        of forces or moments depend on the state variables.
        Since the vectors of forces and moments are provided once at the
        entrance to the integration, they remain constant
        for the entire steps.
        Therefore, when the forces or moments depend on the state variables
        the results of this method are not accurate and may lead to instability.


        Examples
        --------
        A drone applies a roll torque to perform a half roll
        and then stops the rotation by an opposite torque,
        ending up inverted (:math:`q_x \\approx 1`, i.e. :math:`\\varphi \\approx 180°`).

        Import required packages:

        .. code::

          >>> import c4dynamics as c4d
          >>> from matplotlib import pyplot as plt
          >>> import numpy as np


        Settings and initial conditions:

        .. code::

          >>> dt = 0.001
          >>> drone = c4d.quatbody()
          >>> drone.I = [0.0082, 0.0082, 0.0149]


        Main loop:

        .. code::

          >>> for ti in np.arange(0, 1, dt):
          ...   torque = [0.1, 0, 0] if ti < 0.5 else [-0.1, 0, 0]
          ...   drone.inteqm(np.zeros(3), torque, dt)  # doctest: +IGNORE_OUTPUT
          ...   drone.store(ti)


        Plot results:

        .. code::

          >>> _, ax = plt.subplots(2, 1, gridspec_kw = {'hspace': 0.5})
          >>> drone.plot('p', ax = ax[0])
          >>> ax[0].set(xlabel = '')  # doctest: +IGNORE_OUTPUT
          >>> drone.plot('qx', ax = ax[1])

        .. figure:: /_examples/quatbody/inteqm_halfroll.png


        """
        self.X, acc = c4d.eqm.int6q(self, forces, moments, dt, derivs_out=True)
        return acc

    def data(self, var=None, scale=1.0):
        """
        Returns arrays of stored time and data.

        Extends :meth:`state.data() <c4dynamics.states.state.state.data>`
        with the Euler angles `phi`, `theta`, `psi`, which are
        derived from the stored quaternion histories
        (see :func:`quat2euler <c4dynamics.rotmat.rotmat.quat2euler>`).
        For every other variable, the behavior is identical to
        :meth:`state.data() <c4dynamics.states.state.state.data>`.


        Parameters
        ----------
        var : str, optional
            The name of the variable or parameter of the required histories.
            In addition to the state variables and the parameters,
            `phi`, `theta`, `psi` are supported.
        scale : float or int, optional
            A scaling factor to apply to the variable values. Defaults to `1`.


        Returns
        -------
        out : tuple of numpy.array or numpy.array
            A tuple of the time and the variable histories,
            or the entire state histories if `var` is not provided.


        Examples
        --------

        .. code::

          >>> qb = c4d.quatbody()
          >>> for t in [0, 1, 2]:
          ...   qb.psi = t * 10 * c4d.d2r
          ...   qb.store(t)
          >>> qb.data('psi', c4d.r2d)  # doctest: +NUMPY_FORMAT
          (array([0, 1, 2]), array([0, 10, 20]))

        """
        if var in self._angles_names:
            if not self._data:
                warnings.warn("""No history of state samples.""", c4d.c4warn)
                return np.array([])

            data = np.array(self._data)
            iqw = self._didx["qw"]
            angles = c4d.rotmat.quat2euler(data[:, iqw : iqw + 4])

            return data[:, 0], angles[:, self._angles_names.index(var)] * scale

        return super().data(var, scale)

    def plot(self, var, scale=1, ax=None, filename=None, darkmode=True, **kwargs):
        """
        Draws plots of trajectories or variable evolution over time.

        `var` can be each one of the state variables, the Euler angles
        `phi`, `theta`, `psi`, or `top`, `side`, for trajectories.


        Parameters
        ----------

        var : str
            The variable to be plotted.
            Possible variables for trajectories: `top`, `side`.
            For time evolution, any one of the state variables is possible:
            `x`, `y`, `z`, `vx`, `vy`, `vz`, `qw`, `qx`, `qy`, `qz`, `p`, `q`, `r`,
            and the Euler angles `phi`, `theta`, `psi`
            (derived from the quaternion histories).

        scale : float or int, optional
            A scaling factor to apply to the variable values. Defaults to `1`.

        ax : matplotlib.axes.Axes, optional
            An existing Matplotlib axis to plot on.
            If None, a new figure and axis will be created. By default None.

        filename : str, optional
            Full file name to save the plot image.
            If None, the plot will not be saved, by default None.

        darkmode : bool, optional
            Plot in a dark background style. By default True.

        **kwargs : dict, optional
            Additional key-value arguments passed to `matplotlib.pyplot.plot`.
            These can include any keyword arguments accepted by `plot`,
            such as `color`, `linestyle`, `marker`, etc.


        Notes
        -----
        - The method overrides the
          :meth:`datapoint.plot <c4dynamics.states.lib.datapoint.datapoint.plot>`.
        - As in the :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`,
          Euler angles and angular rates are plotted in degrees
          and degrees per second, respectively.
        - The quaternion components are plotted unitless.


        Examples
        --------

        .. code::

          >>> import c4dynamics as c4d
          >>> import numpy as np

        .. code::

          >>> dt = 0.01
          >>> drone = c4d.quatbody(r = 90 * c4d.d2r)
          >>> drone.I = [0.0082, 0.0082, 0.0149]
          >>> for ti in np.arange(0, 1, dt):
          ...   drone.inteqm(np.zeros(3), np.zeros(3), dt)  # doctest: +IGNORE_OUTPUT
          ...   drone.store(ti)
          >>> drone.plot('psi')

        .. figure:: /_examples/quatbody/plot_yaw.png

        """

        if var.lower() in ("top", "side") or 1 <= self._didx.get(var, 0) <= 6:
            return super().plot(var, scale, ax, filename, darkmode, **kwargs)

        if var not in self._didx and var not in self._angles_names:
            warnings.warn(f"""{var} is not a state variable.""", c4d.c4warn)
            return None
        if not self._data:
            warnings.warn(f"""No stored data for {var}.""", c4d.c4warn)
            return None

        if darkmode:
            plt.style.use("dark_background")
        else:
            plt.style.use("default")

        if var in self._angles_names:
            # phi, theta, psi
            y = self.data(var, c4d.r2d)[1]
            title = "$\\" + var + "$"
            ylabel = title + " (deg)"
        elif var in ("qw", "qx", "qy", "qz"):
            y = np.array(self._data)[:, self._didx[var]] * scale
            title = "$q_" + var[1] + "$"
            ylabel = title
        else:
            # p, q, r
            y = np.array(self._data)[:, self._didx[var]] * c4d.r2d
            title = var.title()
            ylabel = var + " (deg/sec)"

        if not len(np.flatnonzero(self.data("t") != -1)):  # values for t weren't stored
            x = range(len(self.data("t")))  # t is just indices
            xlabel = "Sample"
        else:
            x = self.data("t")
            xlabel = "Time"

        # Set default values in kwargs only if the user hasn't provided them
        kwargs.setdefault("color", "m")
        kwargs.setdefault("linewidth", 1.2)

        if ax is None:
            factorsize = 4
            aspectratio = 1080 / 1920
            _, ax = plt.subplots(
                1,
                1,
                dpi=200,
                figsize=(factorsize, factorsize * aspectratio),
                gridspec_kw={"left": 0.15, "right": 0.85, "top": 0.9, "bottom": 0.2},
            )

        ax.plot(x, y, **kwargs)
        c4d.plotdefaults(ax, title, xlabel, ylabel, 8)

        if filename:
            plt.savefig(filename, bbox_inches="tight", pad_inches=0.2, dpi=600)

    def animate(
        self,
        modelpath,
        angle0=[0, 0, 0],
        modelcolor=None,
        dt=1e-3,
        savedir=None,
        cbackground=[1, 1, 1],
    ):

        c4d.rotmat.animate(self, modelpath, angle0, modelcolor, dt, savedir, cbackground)


quatbody.animate.__doc__ = c4d.rotmat.animate.__doc__


if __name__ == "__main__":

    from c4dynamics import rundoctests

    try:
        import open3d as o3d  # noqa: F401

        rundoctests(sys.modules[__name__])
    except ImportError:
        rundoctests(sys.modules[__name__], ["__main__.quatbody.animate"])
