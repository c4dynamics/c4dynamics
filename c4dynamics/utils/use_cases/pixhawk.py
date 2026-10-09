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


class Pixhawk:
    """
    Flight-controller board carrying the sensors.

    Parameters
    ----------
    gyro_std : float, optional
        Gyroscope white noise, 1 sigma [rad/s]. Defaults ``0.005``.
    accel_std : float, optional
        Accelerometer white noise, 1 sigma [m/s^2]. Defaults ``0.05``.
    att_std : float, optional
        Navigation-solution attitude noise, 1 sigma [rad]. Defaults ``0``.
    pos_std : float, optional
        Navigation-solution position noise, 1 sigma [m]. Defaults ``0``.
    vel_std : float, optional
        Navigation-solution velocity noise, 1 sigma [m/s]. Defaults ``0``.


    The vehicle the board is mounted on is a c4dynamics rigid body, a
    ``rigidbody`` or a ``quatbody``, in NED / FRD. The board reads its true:

    - ``vehicle.X[0:6]``: NED position and velocity.
    - ``vehicle.angles``: 3-2-1 Euler angles ``[phi, theta, psi]``.
    - ``vehicle.ang_rates``: FRD body rates ``[p, q, r]``.
    - ``vehicle.specific_force``: the specific force at the center of mass,
      body FRD [m/s^2], i.e. the non-gravitational force over the mass.

    The noise is drawn from ``numpy.random``, so ``numpy.random.seed`` makes
    a run reproducible.
    """

    def __init__(self, gyro_std=0.005, accel_std=0.05, att_std=0.0, pos_std=0.0, vel_std=0.0):
        self.gyro_std = gyro_std
        self.accel_std = accel_std
        self.att_std = att_std
        self.pos_std = pos_std
        self.vel_std = vel_std

    # ======================================================================
    #  IMU
    # ======================================================================

    def read_imu(self, vehicle):
        """
        One IMU sample: gyroscope and accelerometer.

        The gyroscope measures the body rates, the accelerometer the specific
        force, each with white noise:
        ``z_gyro = w + n_g``, ``z_acc = f + n_a``.

        Returns
        -------
        imu : dict
            ``gyro`` [rad/s] and ``accel`` [m/s^2], body FRD -- the input of
            ``ArduCopter.update``.
        """
        return {'gyro' : np.asarray(vehicle.ang_rates) + self.gyro_std * np.random.randn(3),
                'accel': vehicle.specific_force + self.accel_std * np.random.randn(3)}

    # ======================================================================
    #  NAVIGATION SOLUTION
    # ======================================================================

    def read_nav(self, vehicle):
        """
        The navigation solution: attitude, position and velocity.

        On a real vehicle EKF3 fuses the IMU with GPS, compass and barometer
        into this solution. EKF3 is not ported yet: the solution is the true
        state with optional white noise.

        Returns
        -------
        nav : dict
            ``euler`` (roll, pitch, yaw) [rad], ``pos_ned`` [m],
            ``vel_ned`` [m/s] -- the input of ``ArduCopter.update``.
        """
        X = vehicle.X
        return {'euler'  : np.asarray(vehicle.angles) + self.att_std * np.random.randn(3),
                'pos_ned': X[0:3] + self.pos_std * np.random.randn(3),
                'vel_ned': X[3:6] + self.vel_std * np.random.randn(3)}

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
