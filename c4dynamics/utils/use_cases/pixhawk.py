"""
Pixhawk flight-controller board -- the sensor kit of the ArduPilot simulation.

Supporting module of the ArduPilot-simulation use case
(``docs/source/programs/ardupilot_sim/ardupilot_fig8.ipynb``). On a real
vehicle the Pixhawk carries the sensors and runs the ArduCopter firmware:
the IMU chips sit on the board and the firmware reads them directly, not
over MAVLink, and the EKF that turns the raw measurements into a navigation
solution runs on the board too. :class:`Pixhawk` is the single place where
the simulated vehicle's state turns into what the firmware
(:class:`ardupilot.ArduCopter <c4dynamics.utils.use_cases.ardupilot.ArduCopter>`)
reads every fast-loop tick.

=======================  ===================================================
``read_imu``             gyroscope and accelerometer sample
``read_nav``             navigation solution (EKF stand-in)
``read``                 both, in the order ``ArduCopter.update`` takes them
=======================  ===================================================

Frames are ArduPilot's: NED earth, FRD body. The board is mounted at the
vehicle's center of mass, aligned with the body axes, so the readings carry
no lever-arm or misalignment terms.

Like the rest of ``use_cases`` this is example scaffolding, not public API.
"""

import numpy as np

from c4dynamics.rotmat import euler2quat


class Pixhawk:
    """
    Flight-controller board carrying the sensors.

    Parameters
    ----------
    gyro_std : float, optional
        Gyroscope white noise, 1 sigma [rad/s]. Defaults ``0.003``.
    gyro_bias : float, optional
        Gyroscope initial bias, 1 sigma per axis [rad/s]. Defaults ``0.01``.
    gyro_rw : float, optional
        Gyroscope bias random walk [rad/s/sqrt(s)]. Defaults ``0.0002``.
    accel_std : float, optional
        Accelerometer white noise, 1 sigma [m/s^2]. Defaults ``0.05``.
    accel_bias : float, optional
        Accelerometer initial bias, 1 sigma per axis [m/s^2]. Defaults ``0.15``.
    accel_rw : float, optional
        Accelerometer bias random walk [m/s^2/sqrt(s)]. Defaults ``0.005``.
    att_std : float, optional
        Navigation-solution attitude noise, 1 sigma [rad]. Defaults ``0``.
    pos_std : float, optional
        Navigation-solution position noise, 1 sigma [m]. Defaults ``0``.
    vel_std : float, optional
        Navigation-solution velocity noise, 1 sigma [m/s]. Defaults ``0``.
    dt : float, optional
        IMU sample period [s], one :meth:`read_imu` call per sample.
        Defaults ``1 / 400`` (``SCHED_LOOP_RATE``).


    The vehicle the board is mounted on is a c4dynamics rigid body, a
    ``rigidbody`` or a ``quatbody``, in NED / FRD. The board reads its true:

    - ``vehicle.X[0:6]``: NED position and velocity.
    - ``vehicle.quat``: body->NED attitude quaternion ``[qw, qx, qy, qz]``
      (a ``rigidbody``: from its 3-2-1 Euler angles ``vehicle.angles``).
    - ``vehicle.ang_rates``: FRD body rates ``[p, q, r]``.
    - ``vehicle.specific_force``: the specific force at the center of mass,
      body FRD [m/s^2], i.e. the non-gravitational force over the mass.

    The IMU error model is white noise on top of a bias. The bias of each
    axis is drawn once, when the board is created, and then walks:
    ``b[k+1] = b[k] + rw * sqrt(dt) * n``. ArduPilot calibrates most of the
    initial bias away (gyro offsets at boot, ``INS_ACCOFFS``); set
    ``gyro_bias`` / ``accel_bias`` to the residual to model a calibrated board.

    The noise is drawn from ``numpy.random``, so ``numpy.random.seed`` makes
    a run reproducible.
    """

    def __init__(self, gyro_std=0.003, gyro_bias=0.01, gyro_rw=0.0002,
                 accel_std=0.05, accel_bias=0.15, accel_rw=0.005,
                 att_std=0.0, pos_std=0.0, vel_std=0.0, dt=1.0 / 400):
        self.gyro_std = gyro_std
        self.gyro_rw = gyro_rw
        self.accel_std = accel_std
        self.accel_rw = accel_rw
        self.att_std = att_std
        self.pos_std = pos_std
        self.vel_std = vel_std
        self.dt = dt
        # the biases the board powers up with
        self.gyro_b = gyro_bias * np.random.randn(3)
        self.accel_b = accel_bias * np.random.randn(3)

    # ======================================================================
    #  IMU
    # ======================================================================

    def read_imu(self, vehicle):
        """
        One IMU sample: gyroscope and accelerometer.

        The gyroscope measures the body rates, the accelerometer the specific
        force, each with a bias and white noise:
        ``z_gyro = w + b_g + n_g``, ``z_acc = f + b_a + n_a``.
        The biases then take one random-walk step of ``dt``.

        Returns
        -------
        imu : dict
            ``gyro`` [rad/s] and ``accel`` [m/s^2], body FRD -- the input of
            ``ArduCopter.update``.
        """
        imu = {'gyro' : np.asarray(vehicle.ang_rates) + self.gyro_b + self.gyro_std * np.random.randn(3),
               'accel': vehicle.specific_force + self.accel_b + self.accel_std * np.random.randn(3)}
        self.gyro_b = self.gyro_b + self.gyro_rw * np.sqrt(self.dt) * np.random.randn(3)
        self.accel_b = self.accel_b + self.accel_rw * np.sqrt(self.dt) * np.random.randn(3)
        return imu

    # ======================================================================
    #  NAVIGATION SOLUTION
    # ======================================================================

    def read_nav(self, vehicle):
        """
        The navigation solution: attitude, position and velocity.

        On a real vehicle EKF3 fuses the IMU with GPS, compass and barometer
        into this solution. EKF3 is not ported yet: the solution is the true
        state with optional white noise.

        The attitude is a quaternion, as EKF3 keeps it. Its noise is a small
        body-frame rotation ``dtheta`` (1 sigma ``att_std`` per axis):
        ``q_nav = q * [1, dtheta / 2]``, renormalized.

        Returns
        -------
        nav : dict
            ``quat`` body->NED ``[qw, qx, qy, qz]``, ``pos_ned`` [m],
            ``vel_ned`` [m/s] -- the input of ``ArduCopter.update``.
        """
        X = vehicle.X
        return {'quat'   : self._noisy_quat(self._quat(vehicle)),
                'pos_ned': X[0:3] + self.pos_std * np.random.randn(3),
                'vel_ned': X[3:6] + self.vel_std * np.random.randn(3)}

    @staticmethod
    def _quat(vehicle):
        # a quatbody carries its quaternion; a rigidbody only its Euler angles
        if hasattr(vehicle, 'quat'):
            return np.asarray(vehicle.quat, dtype=float)
        return np.asarray(euler2quat(*vehicle.angles), dtype=float)

    def _noisy_quat(self, q):
        if self.att_std == 0:
            return q
        dx, dy, dz = 0.5 * self.att_std * np.random.randn(3)
        w, x, y, z = q
        dq = np.array([w - x*dx - y*dy - z*dz,      # q * [1, dx, dy, dz]
                       x + w*dx + y*dz - z*dy,
                       y - x*dz + w*dy + z*dx,
                       z + x*dy - y*dx + w*dz])
        return dq / np.linalg.norm(dq)

    # ======================================================================
    #  BOTH
    # ======================================================================

    def read(self, vehicle):
        """
        All the sensors, in the order ``ArduCopter.update(t, imu, nav)`` takes them.

        Returns
        -------
        imu, nav : dict, dict
            See :meth:`read_imu` and :meth:`read_nav`.

        Example
        -------
        ``pwm = copter.update(t, *board.read(plant))``
        """
        return self.read_imu(vehicle), self.read_nav(vehicle)
