"""
ArduCopter control stack -- Python port of ArduPilot Copter-4.7.1.

Supporting module of the ArduPilot-simulation use case
(``docs/source/programs/ardupilot_sim/ardupilot_fig8.ipynb``): the flight
controller side of the loop, ported line by line from the C++ so an
algorithm can be flown against ArduPilot's own position / attitude / rate
controllers and motor mixer before real flights.

Sections (each mirrors one ArduPilot library):

=======================  ===================================================
``AP_Math``              sqrt controller, kinematic shaping, quaternions
``AC_PID``               AC_PID, AC_PID_Basic, AC_PID_2D, AC_P_1D, AC_P_2D
``AP_Motors``            AP_MotorsMatrix, quad X
``AC_AttitudeControl``   AC_AttitudeControl_Multi
``AC_PosControl``        AC_PosControl
``ArduCopter``           fast loop, AHRS stand-in, GUIDED mode
=======================  ===================================================

Entry point: :class:`ArduCopter`. Frames are ArduPilot's: NED earth, FRD
body. Parameters are keyed by their ArduPilot names (see
:func:`default_params`).

Like the rest of ``use_cases`` this is example scaffolding, not public API.
"""

import numpy as np


############################################################################
#  AP_MATH
############################################################################
#
#  AP_Math port -- kinematic shaping, square-root controller, quaternion helpers.
#
#  Line-by-line Python port of the parts of ArduPilot's ``libraries/AP_Math``
#  (``control.cpp``, ``Quaternion``) that the copter position / attitude
#  controllers depend on. Function names, argument order and semantics follow
#  the C++ source of **Copter-4.7.1** so the two can be read side by side.
#
#  Differences from the C++:
#
#  - In-place ``float&`` / ``Vector2f&`` outputs become return values.
#  - ``Vector2f`` / ``Vector3f`` are ``numpy`` arrays (float64, not float32).
#  - ``INTERNAL_ERROR`` on invalid arguments becomes an early return of the
#    unchanged inputs, as the firmware does after flagging the error.
#
#  Frames: NED earth frame, FRD body frame (ArduPilot convention).
#
############################################################################


GRAVITY_MSS = 9.80665


# ============================================================
#  SCALAR HELPERS
# ============================================================


def constrain(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def wrap_PI(a):
    """Wrap an angle to [-pi, pi]."""
    return (a + np.pi) % (2.0 * np.pi) - np.pi


def safe_sqrt(x):
    return np.sqrt(x) if x > 0.0 else 0.0


def limit_length(v, max_len):
    """Vector2f/3f::limit_length. Returns (limited vector, was_limited)."""
    n = np.linalg.norm(v)
    if max_len > 0.0 and n > max_len:
        return v * (max_len / n), True
    return v, False


def calc_lowpass_alpha_dt(dt, cutoff_freq):
    """Filter/LowPassFilter.cpp: first-order IIR alpha for a given cutoff [Hz]."""
    if dt <= 0.0 or cutoff_freq <= 0.0:
        return 1.0
    rc = 1.0 / (2.0 * np.pi * cutoff_freq)
    return dt / (dt + rc)


class LowPassFilter:
    """Filter/LowPassFilter.h -- first-order low-pass filter with variable dt."""

    def __init__(self, cutoff_hz=0.0):
        self.cutoff_hz = cutoff_hz
        self.output = 0.0
        self.initialised = False

    def set_cutoff_frequency(self, cutoff_hz):
        self.cutoff_hz = cutoff_hz

    def apply(self, sample, dt):
        if not self.initialised:
            self.output = sample
            self.initialised = True
            return self.output
        self.output += (sample - self.output) * calc_lowpass_alpha_dt(dt, self.cutoff_hz)
        return self.output

    def reset(self, value):
        self.output = value
        self.initialised = True

    def get(self):
        return self.output


# ============================================================
#  SQRT CONTROLLER
# ============================================================


def sqrt_controller(error, p, second_ord_lim, dt):
    """Proportional controller with a square-root region beyond the linear zone."""
    if second_ord_lim <= 0.0:
        correction_rate = error * p
    elif p == 0.0:
        if error > 0.0:
            correction_rate = safe_sqrt(2.0 * second_ord_lim * error)
        elif error < 0.0:
            correction_rate = -safe_sqrt(2.0 * second_ord_lim * (-error))
        else:
            correction_rate = 0.0
    else:
        linear_dist = second_ord_lim / p**2
        if error > linear_dist:
            correction_rate = safe_sqrt(2.0 * second_ord_lim * (error - linear_dist / 2.0))
        elif error < -linear_dist:
            correction_rate = -safe_sqrt(2.0 * second_ord_lim * (-error - linear_dist / 2.0))
        else:
            correction_rate = error * p

    if dt > 0.0:
        # don't overshoot the target within a single step
        return constrain(correction_rate, -abs(error) / dt, abs(error) / dt)
    return correction_rate


def sqrt_controller_vec(error, p, second_ord_lim, dt):
    """Vector2f overload of :func:`sqrt_controller` (acts on the error length)."""
    error_length = np.linalg.norm(error)
    if error_length <= 0.0:
        return np.zeros_like(error)
    correction_length = sqrt_controller(error_length, p, second_ord_lim, dt)
    return error * (correction_length / error_length)


def inv_sqrt_controller(output, p, D_max):
    """Inverse of :func:`sqrt_controller`: error that produces a given output."""
    if D_max > 0.0 and p == 0.0:
        return (output * output) / (2.0 * D_max)
    if D_max <= 0.0 and p != 0.0:
        return output / p
    if D_max <= 0.0 and p == 0.0:
        return 0.0

    linear_velocity = D_max / p
    if abs(output) < linear_velocity:
        return output / p

    linear_dist = D_max / p**2
    stopping_dist = linear_dist * 0.5 + output**2 / (2.0 * D_max)
    return stopping_dist if output > 0.0 else -stopping_dist


def sqrt_controller_accel(error, rate_cmd, rate_state, p, second_ord_lim):
    """Acceleration implied by the sqrt controller as the state moves along it."""
    if not rate_cmd * rate_state > 0.0:
        return 0.0
    if second_ord_lim <= 0.0:
        return -p * rate_state
    if p <= 0.0:
        if rate_cmd == 0.0:
            return 0.0
        return -(second_ord_lim / abs(rate_cmd)) * rate_state

    linear_dist = second_ord_lim / p**2
    if abs(error) <= linear_dist:
        return -p * rate_state
    if rate_cmd == 0.0:
        return 0.0
    return -(second_ord_lim / abs(rate_cmd)) * rate_state


def stopping_distance(velocity, p, accel_max):
    return inv_sqrt_controller(velocity, p, accel_max)


# ============================================================
#  KINEMATIC PROPAGATION
# ============================================================


def update_vel_accel(vel, accel, dt, limit, vel_error):
    """Integrate velocity by accel*dt, honouring a 1D limit direction."""
    delta_vel = accel * dt
    if delta_vel * limit > 0.0 and vel_error * limit > 0.0:
        if vel * limit < 0.0:
            delta_vel = constrain(delta_vel, -abs(vel), abs(vel))
        else:
            delta_vel = 0.0
    return vel + delta_vel


def update_pos_vel_accel(pos, vel, accel, dt, limit, pos_error, vel_error):
    """Integrate position and velocity by one step (1D). Returns (pos, vel)."""
    delta_pos = vel * dt + accel * 0.5 * dt**2
    if delta_pos * limit > 0.0 and pos_error * limit > 0.0:
        delta_pos = 0.0
    pos = pos + delta_pos
    vel = update_vel_accel(vel, accel, dt, limit, vel_error)
    return pos, vel


def update_vel_accel_xy(vel, accel, dt, limit, vel_error):
    delta_vel = accel * dt
    if np.any(limit) and np.any(delta_vel):
        if delta_vel @ limit > 0.0 and vel_error @ limit > 0.0 and not vel @ limit < 0.0:
            delta_vel = np.zeros(2)
    return vel + delta_vel


def update_pos_vel_accel_xy(pos, vel, accel, dt, limit, pos_error, vel_error):
    """Integrate 2D position and velocity by one step. Returns (pos, vel)."""
    delta_pos = vel * dt + accel * 0.5 * dt**2
    if limit @ limit != 0.0:
        if delta_pos @ limit > 0.0 and pos_error @ limit > 0.0:
            delta_pos = np.zeros(2)
    pos = pos + delta_pos
    vel = update_vel_accel_xy(vel, accel, dt, limit, vel_error)
    return pos, vel


# ============================================================
#  KINEMATIC SHAPING
# ============================================================


def shape_accel(accel_desired, accel, jerk_max, dt):
    """Move accel toward accel_desired, jerk-limited. Returns new accel."""
    if jerk_max <= 0.0:
        return accel
    if dt > 0.0:
        accel_delta = constrain(accel_desired - accel, -jerk_max * dt, jerk_max * dt)
        accel = accel + accel_delta
    return accel


def shape_accel_xy(accel_desired, accel, jerk_max, dt):
    if jerk_max <= 0.0:
        return accel
    if dt > 0.0:
        accel_delta, _ = limit_length(accel_desired - accel, jerk_max * dt)
        accel = accel + accel_delta
    return accel


def shape_vel_accel(vel_desired, accel_desired, vel, accel,
                    accel_min, accel_max, jerk_max, dt, limit_total_accel):
    """1D velocity -> jerk-limited acceleration shaper. Returns new accel."""
    if not accel_min < 0.0 or accel_max <= 0.0 or jerk_max <= 0.0:
        return accel

    vel_error = vel_desired - vel
    KPa = jerk_max / accel_max if vel_error > 0.0 else jerk_max / (-accel_min)

    accel_target = sqrt_controller(vel_error, KPa, jerk_max, dt)
    accel_target = constrain(accel_target, accel_min, accel_max)
    accel_target += accel_desired
    if limit_total_accel:
        accel_target = constrain(accel_target, accel_min, accel_max)

    return shape_accel(accel_target, accel, jerk_max, dt)


def limit_accel_xy(vel, accel, accel_max):
    """Limit accel magnitude, prioritising the component across the velocity."""
    if accel_max <= 0.0:
        return accel, False
    if accel @ accel > accel_max**2:
        if not np.any(vel):
            accel, _ = limit_length(accel, accel_max)
        else:
            vel_unit = vel / np.linalg.norm(vel)
            accel_dir = vel_unit @ accel
            accel_cross = accel - vel_unit * accel_dir
            accel_cross, limited = limit_length(accel_cross, accel_max)
            if limited:
                accel_dir = 0.0
            else:
                accel_max_dir = safe_sqrt(accel_max**2 - accel_cross @ accel_cross)
                accel_dir = constrain(accel_dir, -accel_max_dir, accel_max_dir)
            accel = accel_cross + vel_unit * accel_dir
        return accel, True
    return accel, False


def limit_accel_corner_xy(vel, accel, accel_max):
    """Corner-aware accel limit used by the 2D shapers."""
    if accel_max <= 0.0:
        return accel, False
    if not np.any(vel):
        return limit_length(accel, accel_max)

    accel, _ = limit_length(accel, 2.0 * accel_max)
    vel_unit = vel / np.linalg.norm(vel)
    accel_dir_scalar = accel @ vel_unit
    accel_dir = vel_unit * accel_dir_scalar
    accel_cross = accel - accel_dir

    if accel_dir_scalar > 0.0:
        accel_cross_mag = min(np.linalg.norm(accel_cross), accel_max)
        accel_along_max = safe_sqrt(accel_max**2 - accel_cross_mag**2)
        accel_cross, _ = limit_length(accel_cross, accel_max)
        accel_dir, _ = limit_length(accel_dir, accel_along_max)
        return accel_cross + accel_dir, True

    accel_dir_scalar = max(accel_dir_scalar, -accel_max)
    accel_dir = vel_unit * accel_dir_scalar
    accel_cross_max = safe_sqrt(accel_max**2 - accel_dir_scalar**2)
    accel_cross, _ = limit_length(accel_cross, accel_cross_max)
    return accel_cross + accel_dir, True


def shape_vel_accel_xy(vel_desired, accel_desired, vel, accel,
                       accel_max, jerk_max, dt, limit_total_accel):
    if accel_max <= 0.0 or jerk_max <= 0.0:
        return accel
    KPa = jerk_max / accel_max
    accel_target = sqrt_controller_vec(vel_desired - vel, KPa, jerk_max, dt)
    accel_target, _ = limit_accel_corner_xy(vel, accel_target, accel_max)
    accel_target = accel_target + accel_desired
    if limit_total_accel:
        accel_target, _ = limit_length(accel_target, accel_max)
    return shape_accel_xy(accel_target, accel, jerk_max, dt)


def shape_pos_vel_accel(pos_desired, vel_desired, accel_desired, pos, vel, accel,
                        vel_min, vel_max, accel_min, accel_max, jerk_max, dt, limit_total):
    """1D position -> velocity -> jerk-limited acceleration shaper. Returns new accel."""
    if vel_min > 0.0 or vel_max < 0.0 or not accel_min < 0.0 or accel_max <= 0.0 or jerk_max <= 0.0:
        return accel

    pos_error = pos_desired - pos
    accel_lim = -accel_min if pos_error > 0.0 else accel_max
    k_v = jerk_max / accel_lim

    vel_corr = vel - vel_desired
    vel_corr_cmd = sqrt_controller(pos_error, k_v, accel_lim, dt)
    accel_corr_cmd = sqrt_controller_accel(pos_error, vel_corr_cmd, vel_corr, k_v, accel_lim)
    vel_corr_cmd += accel_corr_cmd / k_v

    if vel_min < 0.0:
        vel_corr_cmd = max(vel_corr_cmd, vel_min)
    if vel_max > 0.0:
        vel_corr_cmd = min(vel_corr_cmd, vel_max)

    vel_target = vel_desired + vel_corr_cmd
    if limit_total:
        if vel_min < 0.0:
            vel_target = max(vel_target, vel_min)
        if vel_max > 0.0:
            vel_target = min(vel_target, vel_max)

    accel_target = constrain((vel_target - vel) * k_v, accel_min, accel_max)
    accel_target += accel_desired
    if limit_total:
        accel_target = constrain(accel_target, accel_min, accel_max)

    return shape_accel(accel_target, accel, jerk_max, dt)


def shape_pos_vel_accel_xy(pos_desired, vel_desired, accel_desired, pos, vel, accel,
                           vel_max, accel_max, jerk_max, dt, limit_total):
    """2D position -> velocity -> jerk-limited acceleration shaper. Returns new accel."""
    if vel_max < 0.0 or accel_max <= 0.0 or jerk_max <= 0.0:
        return accel

    k_v = jerk_max / accel_max
    vel_corr_cmd = np.zeros(2)

    pos_error = pos_desired - pos
    pos_error_length = np.linalg.norm(pos_error)
    if pos_error_length > 0.0:
        vel_corr_proj = (vel - vel_desired) @ pos_error / pos_error_length
        vel_corr_cmd_length = sqrt_controller(pos_error_length, k_v, accel_max, dt)
        accel_corr_cmd_length = sqrt_controller_accel(pos_error_length, vel_corr_cmd_length,
                                                      vel_corr_proj, k_v, accel_max)
        vel_corr_cmd_length += accel_corr_cmd_length / k_v
        if vel_max > 0.0:
            vel_corr_cmd_length = constrain(vel_corr_cmd_length, -vel_max, vel_max)
        vel_corr_cmd = pos_error * (vel_corr_cmd_length / pos_error_length)

    vel_target = vel_desired + vel_corr_cmd
    if limit_total and vel_max > 0.0:
        vel_target, _ = limit_length(vel_target, vel_max)

    accel_target = (vel_target - vel) * k_v
    accel_target, _ = limit_accel_corner_xy(vel, accel_target, accel_max)
    accel_target = accel_target + accel_desired
    if limit_total:
        accel_target, _ = limit_length(accel_target, accel_max)

    return shape_accel_xy(accel_target, accel, jerk_max, dt)


def shape_angle_vel_accel(angle_desired, angle_vel_desired, angle_accel_desired,
                          angle, angle_vel, angle_accel,
                          angle_vel_min, angle_vel_max, angle_accel_max,
                          angle_jerk_max, dt, limit_total):
    angle_desired_wrapped = angle + wrap_PI(angle_desired - angle)
    return shape_pos_vel_accel(angle_desired_wrapped, angle_vel_desired, angle_accel_desired,
                               angle, angle_vel, angle_accel,
                               angle_vel_min, angle_vel_max, -angle_accel_max, angle_accel_max,
                               angle_jerk_max, dt, limit_total)


def angle_rad_to_accel_mss(angle_rad):
    return GRAVITY_MSS * np.tan(angle_rad)


def accel_mss_to_angle_rad(accel_mss):
    return np.arctan(accel_mss / GRAVITY_MSS)


# ============================================================
#  QUATERNION  (AP_Math/quaternion.cpp, [w, x, y, z])
# ============================================================


def q_mul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array([w1*w2 - x1*x2 - y1*y2 - z1*z2,
                     w1*x2 + x1*w2 + y1*z2 - z1*y2,
                     w1*y2 - x1*z2 + y1*w2 + z1*x2,
                     w1*z2 + x1*y2 - y1*x2 + z1*w2])


def q_inv(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])


def q_normalize(q):
    n = np.linalg.norm(q)
    return q / n if n > 0.0 else np.array([1.0, 0.0, 0.0, 0.0])


def q_rotate(q, v):
    """``q * v`` in AP: rotate a vector by the quaternion (body -> earth for q_body_to_ned)."""
    qv = q_mul(q_mul(q, np.array([0.0, v[0], v[1], v[2]])), q_inv(q))
    return qv[1:]


def q_from_axis_angle(v):
    """Quaternion from a rotation vector (axis * angle)."""
    theta = np.linalg.norm(v)
    if theta == 0.0:
        return np.array([1.0, 0.0, 0.0, 0.0])
    axis = v / theta
    s = np.sin(0.5 * theta)
    return np.array([np.cos(0.5 * theta), axis[0]*s, axis[1]*s, axis[2]*s])


def q_from_axis_angle2(axis, theta):
    """Quaternion from a unit axis and an angle."""
    if theta == 0.0:
        return np.array([1.0, 0.0, 0.0, 0.0])
    s = np.sin(0.5 * theta)
    return np.array([np.cos(0.5 * theta), axis[0]*s, axis[1]*s, axis[2]*s])


def q_to_axis_angle(q):
    """Rotation vector of a quaternion, angle wrapped to [-pi, pi]."""
    v = np.array([q[1], q[2], q[3]])
    l = np.linalg.norm(v)
    if l != 0.0:
        v = v / l * wrap_PI(2.0 * np.arctan2(l, q[0]))
    return v


def q_from_euler(roll, pitch, yaw):
    cr, sr = np.cos(roll * 0.5), np.sin(roll * 0.5)
    cp, sp = np.cos(pitch * 0.5), np.sin(pitch * 0.5)
    cy, sy = np.cos(yaw * 0.5), np.sin(yaw * 0.5)
    return np.array([cr*cp*cy + sr*sp*sy,
                     sr*cp*cy - cr*sp*sy,
                     cr*sp*cy + sr*cp*sy,
                     cr*cp*sy - sr*sp*cy])


def q_to_euler(q):
    w, x, y, z = q
    roll = np.arctan2(2.0 * (w*x + y*z), 1.0 - 2.0 * (x*x + y*y))
    pitch = np.arcsin(constrain(2.0 * (w*y - z*x), -1.0, 1.0))
    yaw = np.arctan2(2.0 * (w*z + x*y), 1.0 - 2.0 * (y*y + z*z))
    return np.array([roll, pitch, yaw])


############################################################################
#  AC_PID
############################################################################
#
#  AC_PID port -- the PID family used by the copter controllers.
#
#  Python port of ArduPilot's ``libraries/AC_PID`` (**Copter-4.7.1**):
#
#  =============  ==============================================================
#  ``AC_PID``       rate loops (roll/pitch/yaw) and the vertical accel loop
#  ``AC_PID_Basic`` vertical velocity loop
#  ``AC_PID_2D``    horizontal (NE) velocity loop
#  ``AC_P_1D``      vertical position loop (sqrt controller)
#  ``AC_P_2D``      horizontal position loop (sqrt controller)
#  =============  ==============================================================
#
#  Not ported (defaults leave them inactive): notch filters on target/error,
#  the slew-rate limiter (``SMAX = 0``), PD-sum limit (``PDMX = 0``).
#
############################################################################


class AC_PID:
    """Full PID with target / error / derivative filters, FF and D_FF terms.

    ``update_all`` returns P + I + D; the feedforward is read separately with
    :meth:`get_ff`, as in the firmware.
    """

    def __init__(self, p, i, d, ff, imax, filt_T_hz, filt_E_hz, filt_D_hz, dff=0.0):
        self.kp, self.ki, self.kd, self.kff, self.kdff = p, i, d, ff, dff
        self.kimax = abs(imax)
        self.filt_T_hz, self.filt_E_hz, self.filt_D_hz = filt_T_hz, filt_E_hz, filt_D_hz

        self.integrator = 0.0
        self.target = 0.0
        self.error = 0.0
        self.derivative = 0.0
        self.target_derivative = 0.0
        self.reset_filter_flag = True

        # last-step breakdown (AP_PIDInfo) for logging
        self.P = self.I = self.D = self.FF = self.DFF = 0.0

    def update_all(self, target, measurement, dt, limit=False, pd_scale=1.0, i_scale=1.0):
        if not (np.isfinite(target) and np.isfinite(measurement)):
            return 0.0

        if self.reset_filter_flag:
            self.reset_filter_flag = False
            self.target = target
            self.error = self.target - measurement
            self.derivative = 0.0
            self.target_derivative = 0.0
        else:
            target_last = self.target
            self.target += calc_lowpass_alpha_dt(dt, self.filt_T_hz) * (target - self.target)

            error_last = self.error
            error = self.target - measurement
            self.error += calc_lowpass_alpha_dt(dt, self.filt_E_hz) * (error - self.error)

            if dt > 0.0:
                derivative = (self.error - error_last) / dt
                self.derivative += calc_lowpass_alpha_dt(dt, self.filt_D_hz) * (derivative - self.derivative)
                self.target_derivative = (self.target - target_last) / dt

        self._update_i(dt, limit, i_scale)

        P_out = self.error * self.kp * pd_scale
        D_out = self.derivative * self.kd * pd_scale

        self.P, self.I, self.D = P_out, self.integrator, D_out
        self.FF = self.target * self.kff
        self.DFF = self.target_derivative * self.kdff
        return P_out + D_out + self.integrator

    def _update_i(self, dt, limit, i_scale):
        if self.ki != 0.0 and dt > 0.0:
            # with limit active, the integrator may only shrink
            if (not limit) or (self.integrator > 0.0 and self.error < 0.0) \
                    or (self.integrator < 0.0 and self.error > 0.0):
                self.integrator += self.error * self.ki * i_scale * dt
                self.integrator = constrain(self.integrator, -self.kimax, self.kimax)
        else:
            self.integrator = 0.0

    def get_ff(self):
        return self.FF + self.DFF

    def reset_filter(self):
        self.reset_filter_flag = True

    def reset_I(self):
        self.integrator = 0.0

    def set_integrator(self, integrator):
        self.integrator = constrain(integrator, -self.kimax, self.kimax)

    def relax_integrator(self, integrator, dt, time_constant):
        integrator = constrain(integrator, -self.kimax, self.kimax)
        if dt > 0.0:
            self.integrator += (integrator - self.integrator) * (dt / (dt + time_constant))


class AC_PID_Basic:
    """PID with error / derivative filters and one-sided integrator limits."""

    def __init__(self, p, i, d, ff, imax, filt_E_hz, filt_D_hz):
        self.kp, self.ki, self.kd, self.kff = p, i, d, ff
        self.kimax = abs(imax)
        self.filt_E_hz, self.filt_D_hz = filt_E_hz, filt_D_hz
        self.integrator = 0.0
        self.target = 0.0
        self.error = 0.0
        self.derivative = 0.0
        self.reset_filter_flag = True

    def update_all(self, target, measurement, dt, limit_neg=False, limit_pos=False):
        if not (np.isfinite(target) and np.isfinite(measurement)):
            return 0.0
        self.target = target
        if self.reset_filter_flag:
            self.reset_filter_flag = False
            self.error = self.target - measurement
            self.derivative = 0.0
        else:
            error_last = self.error
            self.error += calc_lowpass_alpha_dt(dt, self.filt_E_hz) * ((self.target - measurement) - self.error)
            if dt > 0.0:
                derivative = (self.error - error_last) / dt
                self.derivative += calc_lowpass_alpha_dt(dt, self.filt_D_hz) * (derivative - self.derivative)

        if self.ki != 0.0:
            if not ((limit_neg and self.error < 0.0) or (limit_pos and self.error > 0.0)):
                self.integrator += self.error * self.ki * dt
                self.integrator = constrain(self.integrator, -self.kimax, self.kimax)
        else:
            self.integrator = 0.0

        return self.error * self.kp + self.integrator + self.derivative * self.kd + self.target * self.kff

    def reset_filter(self):
        self.reset_filter_flag = True

    def set_integrator(self, integrator):
        self.integrator = constrain(integrator, -self.kimax, self.kimax)


class AC_PID_2D:
    """2D PID on a vector error; the integrator is limited by length."""

    def __init__(self, p, i, d, ff, imax, filt_E_hz, filt_D_hz):
        self.kp, self.ki, self.kd, self.kff = p, i, d, ff
        self.kimax = abs(imax)
        self.filt_E_hz, self.filt_D_hz = filt_E_hz, filt_D_hz
        self.integrator = np.zeros(2)
        self.target = np.zeros(2)
        self.error = np.zeros(2)
        self.derivative = np.zeros(2)
        self.reset_filter_flag = True

    def update_all(self, target, measurement, dt, limit):
        if not (np.all(np.isfinite(target)) and np.all(np.isfinite(measurement))):
            return np.zeros(2)
        self.target = np.array(target, dtype=float)

        if self.reset_filter_flag:
            self.reset_filter_flag = False
            self.error = self.target - measurement
            self.derivative = np.zeros(2)
        else:
            error_last = self.error.copy()
            self.error = self.error + ((self.target - measurement) - self.error) \
                * calc_lowpass_alpha_dt(dt, self.filt_E_hz)
            if dt > 0.0:
                derivative = (self.error - error_last) / dt
                self.derivative = self.derivative + (derivative - self.derivative) \
                    * calc_lowpass_alpha_dt(dt, self.filt_D_hz)

        # update_i: anti-windup -- don't grow the integrator along the limit vector
        delta_integrator = self.error * self.ki * dt
        integrator_length = np.linalg.norm(self.integrator)
        self.integrator = self.integrator + delta_integrator
        if delta_integrator @ limit > 0.0:
            self.integrator, _ = limit_length(self.integrator, integrator_length)
        self.integrator, _ = limit_length(self.integrator, self.kimax)

        return self.error * self.kp + self.integrator + self.derivative * self.kd + self.target * self.kff

    def reset_filter(self):
        self.reset_filter_flag = True

    def reset_I(self):
        self.integrator = np.zeros(2)

    def set_integrator(self, i):
        self.integrator, _ = limit_length(np.array(i, dtype=float), self.kimax)


class AC_P_1D:
    """1D position P controller built on the sqrt controller."""

    def __init__(self, p):
        self.kp = p
        self.error = 0.0
        self.error_min = 0.0
        self.error_max = 0.0
        self.D1_max = 0.0

    def update_all(self, target, measurement):
        """Returns (output, possibly-clamped target)."""
        self.error = target - measurement
        if self.error_min < 0.0 and self.error < self.error_min:
            self.error = self.error_min
            target = measurement + self.error
        elif self.error_max > 0.0 and self.error > self.error_max:
            self.error = self.error_max
            target = measurement + self.error
        return sqrt_controller(self.error, self.kp, self.D1_max, 0.0), target

    def set_limits(self, output_min, output_max, D_Out_max=0.0, D2_Out_max=0.0):
        self.D1_max = 0.0
        self.error_min = 0.0
        self.error_max = 0.0
        if D_Out_max > 0.0:
            self.D1_max = D_Out_max
        if D2_Out_max > 0.0 and self.kp > 0.0:
            self.D1_max = min(self.D1_max, D2_Out_max / self.kp)
        if output_min < 0.0 and self.kp > 0.0:
            self.error_min = inv_sqrt_controller(output_min, self.kp, self.D1_max)
        if output_max > 0.0 and self.kp > 0.0:
            self.error_max = inv_sqrt_controller(output_max, self.kp, self.D1_max)


class AC_P_2D:
    """2D position P controller built on the sqrt controller."""

    def __init__(self, p):
        self.kp = p
        self.error = np.zeros(2)
        self.error_max = 0.0
        self.D1_max = 0.0

    def update_all(self, target, measurement):
        """Returns (output, possibly-clamped target)."""
        self.error = target - measurement
        if self.error_max > 0.0:
            self.error, limited = limit_length(self.error, self.error_max)
            if limited:
                target = measurement + self.error
        return sqrt_controller_vec(self.error, self.kp, self.D1_max, 0.0), target

    def set_limits(self, output_max, D_Out_max=0.0, D2_Out_max=0.0):
        self.D1_max = 0.0
        self.error_max = 0.0
        if D_Out_max > 0.0:
            self.D1_max = D_Out_max
        if D2_Out_max > 0.0 and self.kp > 0.0:
            self.D1_max = min(self.D1_max, D2_Out_max / self.kp)
        if output_max > 0.0 and self.kp > 0.0:
            self.error_max = inv_sqrt_controller(output_max, self.kp, self.D1_max)


############################################################################
#  AP_MOTORS
############################################################################
#
#  AP_MotorsMatrix port -- quad-X mixer, thrust linearisation, PWM output.
#
#  Python port of ArduPilot's ``AP_MotorsMatrix`` / ``AP_MotorsMulticopter`` /
#  ``Thrust_Linearization`` (**Copter-4.7.1**) for ``FRAME_CLASS = 1`` (quad),
#  ``FRAME_TYPE = 1`` (X):
#
#      roll/pitch/yaw/throttle in [-1, 1] / [0, 1]
#          -> output_armed_stabilizing()     mixer with yaw headroom and
#                                             throttle/attitude priority
#          -> thrust_to_actuator()           MOT_THST_EXPO curve inversion,
#                                             MOT_SPIN_MIN..MOT_SPIN_MAX
#          -> output_to_pwm()                MOT_PWM_MIN..MOT_PWM_MAX
#
#  Motor numbering is ArduPilot's (servo outputs 1..4)::
#
#          3(CW)   1(CCW)         x forward
#              \ /
#              / \
#          2(CCW)  4(CW)          y right
#
#  Simplifications: the spool state machine collapses to SHUT_DOWN /
#  GROUND_IDLE / THROTTLE_UNLIMITED (no spool-up ramp), no battery-voltage or
#  air-density compensation, no thrust boost / motor-loss handling.
#
############################################################################


HOVER_TC = 10.0
HOVER_MIN = 0.125
HOVER_MAX = 0.6875

YAW_FACTOR_CW = -1.0
YAW_FACTOR_CCW = 1.0

# (angle from forward [deg, positive to the right], yaw factor) per motor 1..4
QUAD_X_MOTORS = [(45.0, YAW_FACTOR_CCW),
                 (-135.0, YAW_FACTOR_CCW),
                 (-45.0, YAW_FACTOR_CW),
                 (135.0, YAW_FACTOR_CW)]


def default_mot_params():
    """ArduCopter 4.7.1 defaults for the ``MOT_*`` parameter group."""
    return {
        'MOT_THST_EXPO': 0.65,
        'MOT_SPIN_MIN': 0.15,
        'MOT_SPIN_MAX': 0.95,
        'MOT_SPIN_ARM': 0.10,
        'MOT_THST_HOVER': 0.35,
        'MOT_HOVER_LEARN': 2,      # 0: off, 1: learn, 2: learn and save
        'MOT_PWM_MIN': 1000,
        'MOT_PWM_MAX': 2000,
        'MOT_YAW_HEADROOM': 200,
        'MOT_SLEW_UP_TIME': 0.0,
        'MOT_SLEW_DN_TIME': 0.0,
    }


class AP_MotorsMatrix:

    SHUT_DOWN, GROUND_IDLE, THROTTLE_UNLIMITED = 0, 1, 2

    def __init__(self, params, dt):
        self.p = params
        self._dt_s = dt

        n = len(QUAD_X_MOTORS)
        roll = np.array([np.cos(np.radians(a + 90.0)) for a, _ in QUAD_X_MOTORS])
        pitch = np.array([np.cos(np.radians(a)) for a, _ in QUAD_X_MOTORS])
        yaw = np.array([y for _, y in QUAD_X_MOTORS])
        # normalise_rpy_factors()
        self._roll_factor = 0.5 * roll / np.max(np.abs(roll))
        self._pitch_factor = 0.5 * pitch / np.max(np.abs(pitch))
        self._yaw_factor = 0.5 * yaw / np.max(np.abs(yaw))
        self._throttle_factor = np.ones(n)

        self._roll_in = self._pitch_in = self._yaw_in = 0.0
        self._roll_in_ff = self._pitch_in_ff = self._yaw_in_ff = 0.0
        self._throttle_in = 0.0
        self._throttle_avg_max = 0.0
        self._throttle_out = 0.0
        self._throttle_thrust_max = 1.0
        self._throttle_filter = LowPassFilter(0.0)
        self._throttle_filter.reset(0.0)
        self._throttle_hover = params['MOT_THST_HOVER']

        self._thrust_rpyt_out = np.zeros(n)
        self._actuator = np.zeros(n)
        self.pwm = np.full(n, float(params['MOT_PWM_MIN']))

        self.armed = False
        self.spool_state = self.SHUT_DOWN
        self.limit = dict(roll=False, pitch=False, yaw=False,
                          throttle_lower=True, throttle_upper=False)

    # ----------------------------------------------------------- inputs
    def set_roll(self, v): self._roll_in = v
    def set_pitch(self, v): self._pitch_in = v
    def set_yaw(self, v): self._yaw_in = v
    def set_roll_ff(self, v): self._roll_in_ff = v
    def set_pitch_ff(self, v): self._pitch_in_ff = v
    def set_yaw_ff(self, v): self._yaw_in_ff = v
    def set_throttle(self, v): self._throttle_in = v
    def set_throttle_avg_max(self, v): self._throttle_avg_max = constrain(v, 0.0, 1.0)
    def set_throttle_filter_cutoff(self, hz): self._throttle_filter.set_cutoff_frequency(hz)

    def get_throttle(self):
        return constrain(self._throttle_filter.get(), 0.0, 1.0)

    def get_throttle_out(self):
        return self._throttle_out

    def get_throttle_hover(self):
        return constrain(self._throttle_hover, HOVER_MIN, HOVER_MAX)

    def get_throttle_thrust_max(self):
        return self._throttle_thrust_max

    def update_throttle_hover(self, dt):
        if self.p['MOT_HOVER_LEARN']:
            self._throttle_hover = constrain(
                self._throttle_hover + (dt / (dt + HOVER_TC)) * (self.get_throttle() - self._throttle_hover),
                HOVER_MIN, HOVER_MAX)

    # ------------------------------------------------ thrust linearisation
    def apply_thrust_curve(self, thrust):
        expo = constrain(self.p['MOT_THST_EXPO'], -1.0, 1.0)
        if expo == 0.0:
            return thrust
        ratio = ((expo - 1.0) + safe_sqrt((1.0 - expo)**2 + 4.0 * expo * thrust)) / (2.0 * expo)
        return constrain(ratio, 0.0, 1.0)

    def thrust_to_actuator(self, thrust_in):
        thrust_in = constrain(thrust_in, 0.0, 1.0)
        smin, smax = self.p['MOT_SPIN_MIN'], self.p['MOT_SPIN_MAX']
        return smin + (smax - smin) * self.apply_thrust_curve(thrust_in)

    def output_to_pwm(self, actuator):
        pmin, pmax = self.p['MOT_PWM_MIN'], self.p['MOT_PWM_MAX']
        if self.spool_state == self.SHUT_DOWN:
            return float(pmin)
        return pmin + (pmax - pmin) * actuator

    # ----------------------------------------------------------- mixer
    def output_armed_stabilizing(self):
        lim = self.limit
        lim['roll'] = lim['pitch'] = lim['yaw'] = False
        lim['throttle_lower'] = lim['throttle_upper'] = False

        roll_thrust = self._roll_in + self._roll_in_ff
        pitch_thrust = self._pitch_in + self._pitch_in_ff
        yaw_thrust = self._yaw_in + self._yaw_in_ff
        throttle_thrust = self.get_throttle()
        throttle_avg_max = self._throttle_avg_max
        throttle_thrust_max = self._throttle_thrust_max

        if throttle_thrust <= 0.0:
            throttle_thrust = 0.0
            lim['throttle_lower'] = True
        if throttle_thrust >= throttle_thrust_max:
            throttle_thrust = throttle_thrust_max
            lim['throttle_upper'] = True

        throttle_avg_max = constrain(throttle_avg_max, throttle_thrust, throttle_thrust_max)
        throttle_thrust_best_rpy = min(0.5, throttle_avg_max)

        # roll/pitch, and how much yaw fits
        out = roll_thrust * self._roll_factor + pitch_thrust * self._pitch_factor
        yaw_allowed = 1.0
        for i in range(len(out)):
            if self._yaw_factor[i] != 0.0:
                thrust_rp_best_throttle = throttle_thrust_best_rpy + out[i]
                if yaw_thrust * self._yaw_factor[i] > 0.0:
                    motor_room = 1.0 - thrust_rp_best_throttle
                else:
                    motor_room = thrust_rp_best_throttle
                yaw_allowed = min(yaw_allowed, max(motor_room, 0.0) / abs(self._yaw_factor[i]))

        yaw_allowed = max(yaw_allowed, self.p['MOT_YAW_HEADROOM'] * 0.001)
        if abs(yaw_thrust) > yaw_allowed:
            yaw_thrust = constrain(yaw_thrust, -yaw_allowed, yaw_allowed)
            lim['yaw'] = True

        out = out + yaw_thrust * self._yaw_factor
        rpy_low, rpy_high = min(1.0, out.min()), max(-1.0, out.max())

        # scale rpy so it fits; then add the throttle that best centres it
        rpy_scale = 1.0
        if rpy_high - rpy_low > 1.0:
            rpy_scale = 1.0 / (rpy_high - rpy_low)
        if throttle_avg_max + rpy_low < 0.0:
            rpy_scale = min(rpy_scale, -throttle_avg_max / rpy_low)

        rpy_high *= rpy_scale
        rpy_low *= rpy_scale
        throttle_thrust_best_rpy = -rpy_low
        thr_adj = throttle_thrust - throttle_thrust_best_rpy
        if rpy_scale < 1.0:
            lim['roll'] = lim['pitch'] = lim['yaw'] = True
            if thr_adj > 0.0:
                lim['throttle_upper'] = True
            thr_adj = 0.0
        elif thr_adj < 0.0:
            thr_adj = 0.0
        elif thr_adj > 1.0 - (throttle_thrust_best_rpy + rpy_high):
            thr_adj = 1.0 - (throttle_thrust_best_rpy + rpy_high)
            lim['throttle_upper'] = True

        throttle_thrust_best_plus_adj = throttle_thrust_best_rpy + thr_adj
        self._thrust_rpyt_out = throttle_thrust_best_plus_adj * self._throttle_factor + rpy_scale * out
        self._throttle_out = throttle_thrust_best_plus_adj

    # ----------------------------------------------------------- output
    def output(self):
        """One motors-output tick. Returns PWM [us] for motors 1..4."""
        # update_throttle_filter()
        if self.armed:
            self._throttle_filter.apply(self._throttle_in, self._dt_s)
            self._throttle_filter.reset(constrain(self._throttle_filter.get(), 0.0, 1.0))
        else:
            self._throttle_filter.reset(0.0)

        if self.spool_state == self.THROTTLE_UNLIMITED:
            self._throttle_thrust_max = 1.0
            self.output_armed_stabilizing()
            target = np.array([self.thrust_to_actuator(t) for t in self._thrust_rpyt_out])
        elif self.spool_state == self.GROUND_IDLE:
            self._throttle_thrust_max = 0.0
            self.limit.update(roll=True, pitch=True, yaw=True, throttle_lower=True, throttle_upper=True)
            self._throttle_out = 0.0
            target = np.full(len(self._actuator), self.p['MOT_SPIN_ARM'])
        else:
            self._throttle_thrust_max = 0.0
            self.limit.update(roll=True, pitch=True, yaw=True, throttle_lower=True, throttle_upper=True)
            self._throttle_out = 0.0
            target = np.zeros(len(self._actuator))

        # set_actuator_with_slew()
        up, dn = self.p['MOT_SLEW_UP_TIME'], self.p['MOT_SLEW_DN_TIME']
        hi = np.clip(self._actuator + self._dt_s / constrain(up, 0.0, 0.5), 0.0, 1.0) if up > 0.0 else 1.0
        lo = np.clip(self._actuator - self._dt_s / constrain(dn, 0.0, 0.5), 0.0, 1.0) if dn > 0.0 else 0.0
        self._actuator = np.clip(target, lo, hi)

        self.pwm = np.array([self.output_to_pwm(a) for a in self._actuator])
        return self.pwm


############################################################################
#  AC_ATTITUDECONTROL
############################################################################
#
#  AC_AttitudeControl_Multi port -- quaternion attitude controller + body-rate PIDs.
#
#  Python port of ArduPilot's ``AC_AttitudeControl`` / ``AC_AttitudeControl_Multi``
#  (**Copter-4.7.1**), restricted to the path a GUIDED-mode copter takes:
#
#      input_thrust_vector_heading_rad()      <- AC_PosControl thrust vector + yaw
#          attitude_command_model()           input shaping (ATC_INPUT_TC, ACC_*_MAX)
#          attitude_controller_run_quat()     att error -> body-rate target (sqrt ctrl)
#      rate_controller_run()                  body-rate PIDs -> motors roll/pitch/yaw
#      set_throttle_out()                     angle boost, throttle-rpy mix
#
#  Parameters are keyed by their ArduPilot names (``ATC_RAT_RLL_P`` ...), see
#  :func:`default_atc_params`.
#
############################################################################


ACCEL_RP_CONTROLLER_MIN_RADSS = np.radians(40.0)
ACCEL_RP_CONTROLLER_MAX_RADSS = np.radians(720.0)
ACCEL_Y_CONTROLLER_MIN_RADSS = np.radians(10.0)
ACCEL_Y_CONTROLLER_MAX_RADSS = np.radians(120.0)
THRUST_ERROR_ANGLE_RAD = np.radians(30.0)
YAW_MAX_ERROR_ANGLE_RAD = np.radians(45.0)
ANGLE_LIMIT_MIN_DEG = 10.0
ANGLE_LIMIT_THROTTLE_MAX = 0.8
THR_MIX_MAX_LIMIT = 5.0


def default_atc_params():
    """ArduCopter 4.7.1 defaults for the ``ATC_*`` parameter group."""
    return {
        # angle (P) controllers
        'ATC_ANG_RLL_P': 4.5, 'ATC_ANG_PIT_P': 4.5, 'ATC_ANG_YAW_P': 4.5,
        # rate PIDs -- roll
        'ATC_RAT_RLL_P': 0.135, 'ATC_RAT_RLL_I': 0.135, 'ATC_RAT_RLL_D': 0.0036,
        'ATC_RAT_RLL_FF': 0.0, 'ATC_RAT_RLL_IMAX': 0.5,
        'ATC_RAT_RLL_FLTT': 20.0, 'ATC_RAT_RLL_FLTE': 0.0, 'ATC_RAT_RLL_FLTD': 20.0,
        # rate PIDs -- pitch
        'ATC_RAT_PIT_P': 0.135, 'ATC_RAT_PIT_I': 0.135, 'ATC_RAT_PIT_D': 0.0036,
        'ATC_RAT_PIT_FF': 0.0, 'ATC_RAT_PIT_IMAX': 0.5,
        'ATC_RAT_PIT_FLTT': 20.0, 'ATC_RAT_PIT_FLTE': 0.0, 'ATC_RAT_PIT_FLTD': 20.0,
        # rate PIDs -- yaw
        'ATC_RAT_YAW_P': 0.18, 'ATC_RAT_YAW_I': 0.018, 'ATC_RAT_YAW_D': 0.0,
        'ATC_RAT_YAW_FF': 0.0, 'ATC_RAT_YAW_IMAX': 0.5,
        'ATC_RAT_YAW_FLTT': 20.0, 'ATC_RAT_YAW_FLTE': 2.5, 'ATC_RAT_YAW_FLTD': 20.0,
        # input shaping / limits
        'ATC_RATE_FF_ENAB': 1,
        'ATC_INPUT_TC': 0.10,          # [s]
        'ATC_ACC_R_MAX': 1100.0,       # [deg/s/s]
        'ATC_ACC_P_MAX': 1100.0,       # [deg/s/s]
        'ATC_ACC_Y_MAX': 270.0,        # [deg/s/s]
        'ATC_RATE_R_MAX': 0.0,         # [deg/s] 0 = unlimited
        'ATC_RATE_P_MAX': 0.0,
        'ATC_RATE_Y_MAX': 0.0,
        'ATC_RATE_WPY_MAX': 60.0,      # [deg/s]
        'ATC_ANGLE_MAX': 30.0,         # [deg]
        'ATC_ANGLE_BOOST': 1,
        'ATC_ANG_LIM_TC': 1.0,         # [s]
        'ATC_THR_MIX_MAX': 0.5,
        'PILOT_Y_RATE_TC': 0.0,        # [s] yaw command-model time constant
    }


class AC_AttitudeControl_Multi:
    """Multicopter attitude controller.

    Parameters
    ----------
    params : dict
        ``ATC_*`` parameters (see :func:`default_atc_params`).
    ahrs : object
        Provides ``quat`` (body->NED), ``gyro`` (FRD rad/s), ``roll``, ``pitch``, ``yaw``.
    motors : AP_MotorsMatrix
    dt : float
        Main loop period [s].
    """

    def __init__(self, params, ahrs, motors, dt):
        self.p = params
        self._ahrs = ahrs
        self._motors = motors
        self._dt_s = dt

        P = params
        self._pid_rate_roll = AC_PID(P['ATC_RAT_RLL_P'], P['ATC_RAT_RLL_I'], P['ATC_RAT_RLL_D'],
                                     P['ATC_RAT_RLL_FF'], P['ATC_RAT_RLL_IMAX'],
                                     P['ATC_RAT_RLL_FLTT'], P['ATC_RAT_RLL_FLTE'], P['ATC_RAT_RLL_FLTD'])
        self._pid_rate_pitch = AC_PID(P['ATC_RAT_PIT_P'], P['ATC_RAT_PIT_I'], P['ATC_RAT_PIT_D'],
                                      P['ATC_RAT_PIT_FF'], P['ATC_RAT_PIT_IMAX'],
                                      P['ATC_RAT_PIT_FLTT'], P['ATC_RAT_PIT_FLTE'], P['ATC_RAT_PIT_FLTD'])
        self._pid_rate_yaw = AC_PID(P['ATC_RAT_YAW_P'], P['ATC_RAT_YAW_I'], P['ATC_RAT_YAW_D'],
                                    P['ATC_RAT_YAW_FF'], P['ATC_RAT_YAW_IMAX'],
                                    P['ATC_RAT_YAW_FLTT'], P['ATC_RAT_YAW_FLTE'], P['ATC_RAT_YAW_FLTD'])

        self._kp_angle = np.array([P['ATC_ANG_RLL_P'], P['ATC_ANG_PIT_P'], P['ATC_ANG_YAW_P']])

        # targets
        self._attitude_target = np.array([1.0, 0.0, 0.0, 0.0])
        self._euler_angle_target_rad = np.zeros(3)
        self._euler_rate_target_rads = np.zeros(3)
        self._ang_vel_target_rads = np.zeros(3)
        self._ang_accel_target_rads = np.zeros(3)
        self._ang_vel_body_rads = np.zeros(3)
        self._attitude_ang_error = np.array([1.0, 0.0, 0.0, 0.0])

        self._thrust_angle_rad = 0.0
        self._thrust_error_angle_rad = 0.0
        self._feedforward_scalar = 1.0

        # throttle
        self._throttle_in = 0.0
        self._angle_boost = 0.0
        self._throttle_rpy_mix = P['ATC_THR_MIX_MAX']
        self._throttle_rpy_mix_desired = P['ATC_THR_MIX_MAX']
        self._althold_lean_angle_max_rad = 0.0

    # ------------------------------------------------------------------ limits
    def get_accel_roll_max_radss(self):
        return np.radians(self.p['ATC_ACC_R_MAX'])

    def get_accel_pitch_max_radss(self):
        return np.radians(self.p['ATC_ACC_P_MAX'])

    def get_accel_yaw_max_radss(self):
        return np.radians(self.p['ATC_ACC_Y_MAX'])

    def get_slew_yaw_max_rads(self):
        if not self.p['ATC_RATE_Y_MAX'] > 0.0:
            return np.radians(self.p['ATC_RATE_WPY_MAX'])
        return min(np.radians(self.p['ATC_RATE_Y_MAX']), np.radians(self.p['ATC_RATE_WPY_MAX']))

    def lean_angle_max_rad(self):
        return np.radians(constrain(self.p['ATC_ANGLE_MAX'], ANGLE_LIMIT_MIN_DEG, 80.0))

    def get_althold_lean_angle_max_rad(self):
        return max(self._althold_lean_angle_max_rad, np.radians(ANGLE_LIMIT_MIN_DEG))

    def get_att_target_euler_rad(self):
        return self._euler_angle_target_rad

    def get_throttle_in(self):
        return self._throttle_in

    # ------------------------------------------------------------- resets
    def reset_target_and_rate(self, reset_rate=True):
        self._attitude_target = self._ahrs.quat.copy()
        self._euler_angle_target_rad = q_to_euler(self._attitude_target)
        if reset_rate:
            self._ang_vel_target_rads = np.zeros(3)
            self._ang_accel_target_rads = np.zeros(3)
            self._euler_rate_target_rads = np.zeros(3)

    def reset_rate_controller_I_terms(self):
        self._pid_rate_roll.reset_I()
        self._pid_rate_pitch.reset_I()
        self._pid_rate_yaw.reset_I()

    # ------------------------------------------------------- input shaping
    def attitude_command_model(self, error_angle, desired_ang_vel, target_ang_vel, target_ang_accel,
                               max_ang_vel, accel_max, input_tc, dt):
        """Returns (target_ang_vel, target_ang_accel)."""
        if dt <= 0.0:
            return target_ang_vel, target_ang_accel
        if accel_max <= 0.0:
            accel_max = np.radians(1800.0)
        if input_tc <= 0.0:
            input_tc = dt * 10.0
        # max_ang_vel = 0 -> unlimited in shape_pos_vel_accel
        target_ang_accel = shape_angle_vel_accel(error_angle, desired_ang_vel, 0.0,
                                                 0.0, target_ang_vel, target_ang_accel,
                                                 -max_ang_vel, max_ang_vel, accel_max,
                                                 accel_max / input_tc, dt, True)
        target_ang_vel += target_ang_accel * dt
        return target_ang_vel, target_ang_accel

    def update_attitude_target(self):
        self._attitude_target = q_normalize(
            q_mul(self._attitude_target, q_from_axis_angle(self._ang_vel_target_rads * self._dt_s)))

    @staticmethod
    def attitude_from_thrust_vector(thrust_vector, heading_angle_rad):
        thrust_vector_up = np.array([0.0, 0.0, -1.0])
        n = np.linalg.norm(thrust_vector)
        thrust_vector = thrust_vector_up if n == 0.0 else thrust_vector / n

        thrust_vec_cross = np.cross(thrust_vector_up, thrust_vector)
        thrust_vector_angle = np.arccos(constrain(thrust_vector_up @ thrust_vector, -1.0, 1.0))
        l = np.linalg.norm(thrust_vec_cross)
        if l == 0.0 or thrust_vector_angle == 0.0:
            thrust_vec_cross = thrust_vector_up
        else:
            thrust_vec_cross = thrust_vec_cross / l

        thrust_vec_quat = q_from_axis_angle2(thrust_vec_cross, thrust_vector_angle)
        yaw_quat = q_from_axis_angle2(np.array([0.0, 0.0, 1.0]), heading_angle_rad)
        return q_mul(thrust_vec_quat, yaw_quat)

    def input_thrust_vector_heading_rad(self, thrust_vector, heading_angle_rad, heading_rate_rads=0.0):
        """Main GUIDED/AUTO entry: thrust direction (NED) + heading angle/rate."""
        self.update_attitude_target()
        self._euler_angle_target_rad = q_to_euler(self._attitude_target)

        desired_attitude_quat = self.attitude_from_thrust_vector(thrust_vector, heading_angle_rad)

        if self.p['ATC_RATE_FF_ENAB']:
            _, attitude_error, _, _ = self.thrust_vector_rotation_angles(desired_attitude_quat,
                                                                         self._attitude_target)
            tc, dt = self.p['ATC_INPUT_TC'], self._dt_s
            v, a = self._ang_vel_target_rads, self._ang_accel_target_rads
            v[0], a[0] = self.attitude_command_model(attitude_error[0], 0.0, v[0], a[0],
                                                     np.radians(self.p['ATC_RATE_R_MAX']),
                                                     self.get_accel_roll_max_radss(), tc, dt)
            v[1], a[1] = self.attitude_command_model(attitude_error[1], 0.0, v[1], a[1],
                                                     np.radians(self.p['ATC_RATE_P_MAX']),
                                                     self.get_accel_pitch_max_radss(), tc, dt)
            v[2], a[2] = self.attitude_command_model(attitude_error[2], heading_rate_rads, v[2], a[2],
                                                     self.get_slew_yaw_max_rads(),
                                                     self.get_accel_yaw_max_radss(),
                                                     self.p['PILOT_Y_RATE_TC'], dt)
        else:
            self._attitude_target = desired_attitude_quat
            self._euler_rate_target_rads = np.zeros(3)
            self._ang_vel_target_rads = np.zeros(3)
            self._ang_accel_target_rads = np.zeros(3)

        self.attitude_controller_run_quat()

    # ------------------------------------------------------- attitude loop
    def thrust_vector_rotation_angles(self, attitude_target, attitude_body):
        """Split the attitude error into a thrust-vector tilt and a heading part.

        Returns (thrust_vector_correction, attitude_error_rad, thrust_angle_rad,
        thrust_error_angle_rad).
        """
        thrust_vector_up = np.array([0.0, 0.0, -1.0])
        att_target_thrust_vec = q_rotate(attitude_target, thrust_vector_up)
        att_body_thrust_vec = q_rotate(attitude_body, thrust_vector_up)

        thrust_angle_rad = np.arccos(constrain(thrust_vector_up @ att_body_thrust_vec, -1.0, 1.0))
        thrust_vec_cross = np.cross(att_body_thrust_vec, att_target_thrust_vec)
        thrust_error_angle_rad = np.arccos(constrain(att_body_thrust_vec @ att_target_thrust_vec, -1.0, 1.0))

        l = np.linalg.norm(thrust_vec_cross)
        if l == 0.0 or thrust_error_angle_rad == 0.0:
            thrust_vec_cross = thrust_vector_up
        else:
            thrust_vec_cross = thrust_vec_cross / l

        thrust_vec_cross = q_rotate(q_inv(attitude_body), thrust_vec_cross)
        thrust_vector_correction = q_from_axis_angle2(thrust_vec_cross, thrust_error_angle_rad)

        attitude_error_rad = np.zeros(3)
        rotation = q_to_axis_angle(thrust_vector_correction)
        attitude_error_rad[0], attitude_error_rad[1] = rotation[0], rotation[1]

        heading_vec_correction_quat = q_mul(q_mul(q_inv(thrust_vector_correction), q_inv(attitude_body)),
                                            attitude_target)
        attitude_error_rad[2] = q_to_axis_angle(heading_vec_correction_quat)[2]

        return thrust_vector_correction, attitude_error_rad, thrust_angle_rad, thrust_error_angle_rad

    def thrust_heading_rotation_angles(self, attitude_body):
        """Like :meth:`thrust_vector_rotation_angles` but limits the heading error,
        dragging the stored attitude target along when the limit is hit."""
        (thrust_vector_correction, attitude_error_rad,
         thrust_angle_rad, thrust_error_angle_rad) = self.thrust_vector_rotation_angles(
            self._attitude_target, attitude_body)

        heading_accel_max = constrain(self.get_accel_yaw_max_radss() / 2.0,
                                      ACCEL_Y_CONTROLLER_MIN_RADSS, ACCEL_Y_CONTROLLER_MAX_RADSS)
        kp_rate_yaw = self._pid_rate_yaw.kp
        if kp_rate_yaw != 0.0:
            heading_error_max = min(inv_sqrt_controller(1.0 / kp_rate_yaw, self._kp_angle[2], heading_accel_max),
                                    YAW_MAX_ERROR_ANGLE_RAD)
            if self._kp_angle[2] != 0.0 and abs(attitude_error_rad[2]) > heading_error_max:
                attitude_error_rad[2] = constrain(wrap_PI(attitude_error_rad[2]),
                                                  -heading_error_max, heading_error_max)
                heading_vec_correction_quat = q_from_axis_angle(np.array([0.0, 0.0, attitude_error_rad[2]]))
                self._attitude_target = q_mul(q_mul(attitude_body, thrust_vector_correction),
                                              heading_vec_correction_quat)

        return attitude_error_rad, thrust_angle_rad, thrust_error_angle_rad

    def update_ang_vel_target_from_att_error(self, att_err):
        dt = self._dt_s
        kp = self._kp_angle
        rp_lim_r = constrain(self.get_accel_roll_max_radss() / 2.0,
                             ACCEL_RP_CONTROLLER_MIN_RADSS, ACCEL_RP_CONTROLLER_MAX_RADSS)
        rp_lim_p = constrain(self.get_accel_pitch_max_radss() / 2.0,
                             ACCEL_RP_CONTROLLER_MIN_RADSS, ACCEL_RP_CONTROLLER_MAX_RADSS)
        y_lim = constrain(self.get_accel_yaw_max_radss() / 2.0,
                          ACCEL_Y_CONTROLLER_MIN_RADSS, ACCEL_Y_CONTROLLER_MAX_RADSS)
        out = np.zeros(3)
        out[0] = sqrt_controller(att_err[0], kp[0], rp_lim_r, dt) if self.get_accel_roll_max_radss() else kp[0] * att_err[0]
        out[1] = sqrt_controller(att_err[1], kp[1], rp_lim_p, dt) if self.get_accel_pitch_max_radss() else kp[1] * att_err[1]
        out[2] = sqrt_controller(att_err[2], kp[2], y_lim, dt) if self.get_accel_yaw_max_radss() else kp[2] * att_err[2]
        return out

    @staticmethod
    def ang_vel_limit(v, roll_max, pitch_max, yaw_max):
        v = v.copy()
        if roll_max == 0.0 or pitch_max == 0.0:
            if roll_max != 0.0:
                v[0] = constrain(v[0], -roll_max, roll_max)
            if pitch_max != 0.0:
                v[1] = constrain(v[1], -pitch_max, pitch_max)
        else:
            tv = np.array([v[0] / roll_max, v[1] / pitch_max])
            l = np.linalg.norm(tv)
            if l > 1.0:
                v[0] = tv[0] * roll_max / l
                v[1] = tv[1] * pitch_max / l
        if yaw_max != 0.0:
            v[2] = constrain(v[2], -yaw_max, yaw_max)
        return v

    def attitude_controller_run_quat(self):
        attitude_body = self._ahrs.quat

        attitude_error, self._thrust_angle_rad, self._thrust_error_angle_rad = \
            self.thrust_heading_rotation_angles(attitude_body)

        ang_vel_body = self.update_ang_vel_target_from_att_error(attitude_error)
        ang_vel_body = self.ang_vel_limit(ang_vel_body,
                                          np.radians(self.p['ATC_RATE_R_MAX']),
                                          np.radians(self.p['ATC_RATE_P_MAX']),
                                          np.radians(self.p['ATC_RATE_Y_MAX']))

        # rotate the target angular velocity feedforward into the body frame
        rotation_target_to_body = q_mul(q_inv(attitude_body), self._attitude_target)
        ang_vel_body_feedforward = q_rotate(rotation_target_to_body, self._ang_vel_target_rads)

        gyro = self._ahrs.gyro
        self._feedforward_scalar = 1.0
        if self._thrust_error_angle_rad > THRUST_ERROR_ANGLE_RAD * 2.0:
            ang_vel_body[2] = gyro[2]
        elif self._thrust_error_angle_rad > THRUST_ERROR_ANGLE_RAD:
            self._feedforward_scalar = 1.0 - (self._thrust_error_angle_rad - THRUST_ERROR_ANGLE_RAD) / THRUST_ERROR_ANGLE_RAD
            ang_vel_body[0] += ang_vel_body_feedforward[0] * self._feedforward_scalar
            ang_vel_body[1] += ang_vel_body_feedforward[1] * self._feedforward_scalar
            ang_vel_body[2] += ang_vel_body_feedforward[2]
            ang_vel_body[2] = gyro[2] * (1.0 - self._feedforward_scalar) + ang_vel_body[2] * self._feedforward_scalar
        else:
            ang_vel_body = ang_vel_body + ang_vel_body_feedforward

        self._attitude_ang_error = q_mul(q_inv(attitude_body), self._attitude_target)
        self._ang_vel_body_rads = ang_vel_body

    # ------------------------------------------------------------ rate loop
    def update_throttle_rpy_mix(self):
        dt = self._dt_s
        if self._throttle_rpy_mix < self._throttle_rpy_mix_desired:
            self._throttle_rpy_mix += min(2.0 * dt, self._throttle_rpy_mix_desired - self._throttle_rpy_mix)
        elif self._throttle_rpy_mix > self._throttle_rpy_mix_desired:
            self._throttle_rpy_mix -= min(0.5 * dt, self._throttle_rpy_mix - self._throttle_rpy_mix_desired)
            throttle_hover = self._motors.get_throttle_hover()
            throttle_in = self._motors.get_throttle()
            throttle_out = max(self._motors.get_throttle_out(), throttle_in)
            if throttle_out < throttle_hover:
                mix_used = (throttle_out - throttle_in) / (throttle_hover - throttle_in)
            else:
                mix_used = throttle_out / throttle_hover
            self._throttle_rpy_mix = min(self._throttle_rpy_mix, max(mix_used, self._throttle_rpy_mix_desired))
        self._throttle_rpy_mix = constrain(self._throttle_rpy_mix, 0.1, THR_MIX_MAX_LIMIT)

    def rate_controller_run(self):
        """Body-rate PIDs on the latest gyro; writes roll/pitch/yaw to the motors."""
        self.update_throttle_rpy_mix()
        gyro = self._ahrs.gyro
        dt = self._dt_s
        ang_vel_body = self._ang_vel_body_rads
        lim = self._motors.limit

        self._motors.set_roll(self._pid_rate_roll.update_all(ang_vel_body[0], gyro[0], dt, lim['roll']))
        self._motors.set_roll_ff(self._pid_rate_roll.get_ff())
        self._motors.set_pitch(self._pid_rate_pitch.update_all(ang_vel_body[1], gyro[1], dt, lim['pitch']))
        self._motors.set_pitch_ff(self._pid_rate_pitch.get_ff())
        self._motors.set_yaw(self._pid_rate_yaw.update_all(ang_vel_body[2], gyro[2], dt, lim['yaw']))
        self._motors.set_yaw_ff(self._pid_rate_yaw.get_ff() * self._feedforward_scalar)

    # ------------------------------------------------------------- throttle
    def update_althold_lean_angle_max(self, throttle_in):
        thr_max = self._motors.get_throttle_thrust_max()
        if thr_max == 0.0:
            self._althold_lean_angle_max_rad = 0.0
            return
        althold_lean_angle_max = np.arccos(constrain(throttle_in / (ANGLE_LIMIT_THROTTLE_MAX * thr_max), 0.0, 1.0))
        tc = self.p['ATC_ANG_LIM_TC']
        self._althold_lean_angle_max_rad += (self._dt_s / (self._dt_s + tc)) * \
            (althold_lean_angle_max - self._althold_lean_angle_max_rad)

    def get_throttle_boosted(self, throttle_in):
        if not self.p['ATC_ANGLE_BOOST']:
            self._angle_boost = 0.0
            return throttle_in
        cos_tilt = np.cos(self._ahrs.pitch) * np.cos(self._ahrs.roll)
        inverted_factor = constrain(10.0 * cos_tilt, 0.0, 1.0)
        boost_factor = 1.0 / constrain(np.cos(self._thrust_angle_rad), 0.1, 1.0)
        throttle_out = throttle_in * inverted_factor * boost_factor
        self._angle_boost = constrain(throttle_out - throttle_in, -1.0, 1.0)
        return throttle_out

    def get_throttle_avg_max(self, throttle_in):
        throttle_in = constrain(throttle_in, 0.0, 1.0)
        return max(throttle_in, throttle_in * max(0.0, 1.0 - self._throttle_rpy_mix)
                   + self._motors.get_throttle_hover() * self._throttle_rpy_mix)

    def set_throttle_out(self, throttle_in, apply_angle_boost, filter_cutoff):
        self._throttle_in = throttle_in
        self.update_althold_lean_angle_max(throttle_in)
        self._motors.set_throttle_filter_cutoff(filter_cutoff)
        if apply_angle_boost:
            throttle_in = self.get_throttle_boosted(throttle_in)
        else:
            self._angle_boost = 0.0
        self._motors.set_throttle(throttle_in)
        self._motors.set_throttle_avg_max(self.get_throttle_avg_max(max(throttle_in, self._throttle_in)))


############################################################################
#  AC_POSCONTROL
############################################################################
#
#  AC_PosControl port -- copter position / velocity / acceleration controller.
#
#  Python port of ArduPilot's ``AC_PosControl`` (**Copter-4.7.1**, metres, NED).
#  Each axis group runs the same cascade:
#
#      input_pos_vel_accel_*()   jerk-limited kinematic shaping of the commanded
#                                path -> pos/vel/accel *desired*
#      *_update_controller()     P (sqrt) on position -> PID on velocity
#                                -> accel target
#         NE:  accel target -> lean angles / thrust vector
#         D :  accel target -> PID on measured accel -> normalised throttle
#
#  Not ported: position/velocity offsets (always zero here), terrain following,
#  EKF-reset handling, vibration compensation, the ``disturb`` injection hooks.
#
#  Parameters are keyed by their ArduPilot names (``PSC_NE_VEL_P`` ...), see
#  :func:`default_psc_params`.
#
############################################################################


THROTTLE_CUTOFF_FREQ_HZ = 2.0
OVERSPEED_GAIN_U = 2.0


def default_psc_params():
    """ArduCopter 4.7.1 defaults for ``PSC_*`` and the ``WP_*`` limits guided uses."""
    return {
        # horizontal
        'PSC_NE_POS_P': 1.0,
        'PSC_NE_VEL_P': 2.0, 'PSC_NE_VEL_I': 1.0, 'PSC_NE_VEL_D': 0.25,
        'PSC_NE_VEL_FF': 0.0, 'PSC_NE_VEL_IMAX': 10.0,
        'PSC_NE_VEL_FLTE': 5.0, 'PSC_NE_VEL_FLTD': 5.0,
        # vertical
        'PSC_D_POS_P': 1.0,
        'PSC_D_VEL_P': 5.0, 'PSC_D_VEL_I': 0.0, 'PSC_D_VEL_D': 0.0,
        'PSC_D_VEL_FF': 0.0, 'PSC_D_VEL_IMAX': 10.0,
        'PSC_D_VEL_FLTE': 5.0, 'PSC_D_VEL_FLTD': 5.0,
        'PSC_D_ACC_P': 0.05, 'PSC_D_ACC_I': 0.1, 'PSC_D_ACC_D': 0.0,
        'PSC_D_ACC_FF': 0.0, 'PSC_D_ACC_IMAX': 0.8,
        'PSC_D_ACC_FLTT': 0.0, 'PSC_D_ACC_FLTE': 20.0, 'PSC_D_ACC_FLTD': 0.0,
        # shaping
        'PSC_NE_JERK': 5.0,    # [m/s^3]
        'PSC_D_JERK': 5.0,     # [m/s^3]
        'PSC_ANGLE_MAX': 0.0,  # [deg] 0 -> use ATC_ANGLE_MAX
        # waypoint-navigation limits that GUIDED hands to the position controller
        'WP_SPD': 10.0,        # [m/s]
        'WP_SPD_UP': 2.5,      # [m/s]
        'WP_SPD_DN': 1.5,      # [m/s]
        'WP_ACC': 2.5,         # [m/s^2]
        'WP_ACC_Z': 1.0,       # [m/s^2]
    }


class AC_PosControl:
    """Copter position controller (NE + D).

    Parameters
    ----------
    params : dict
        ``PSC_*`` / ``WP_*`` parameters (see :func:`default_psc_params`).
    ahrs : object
        Provides ``pos_ned``, ``vel_ned``, ``accel_ef`` (NED specific force,
        m/s^2), ``yaw``.
    motors : AP_MotorsMatrix
    attitude_control : AC_AttitudeControl_Multi
    dt : float
        Main loop period [s].
    """

    def __init__(self, params, ahrs, motors, attitude_control, dt):
        P = params
        self.p = params
        self._ahrs = ahrs
        self._motors = motors
        self._attitude_control = attitude_control
        self._dt_s = dt

        self._p_pos_ne_m = AC_P_2D(P['PSC_NE_POS_P'])
        self._p_pos_d_m = AC_P_1D(P['PSC_D_POS_P'])
        self._pid_vel_ne_m = AC_PID_2D(P['PSC_NE_VEL_P'], P['PSC_NE_VEL_I'], P['PSC_NE_VEL_D'],
                                       P['PSC_NE_VEL_FF'], P['PSC_NE_VEL_IMAX'],
                                       P['PSC_NE_VEL_FLTE'], P['PSC_NE_VEL_FLTD'])
        self._pid_vel_d_m = AC_PID_Basic(P['PSC_D_VEL_P'], P['PSC_D_VEL_I'], P['PSC_D_VEL_D'],
                                         P['PSC_D_VEL_FF'], P['PSC_D_VEL_IMAX'],
                                         P['PSC_D_VEL_FLTE'], P['PSC_D_VEL_FLTD'])
        self._pid_accel_d_m = AC_PID(P['PSC_D_ACC_P'], P['PSC_D_ACC_I'], P['PSC_D_ACC_D'],
                                     P['PSC_D_ACC_FF'], P['PSC_D_ACC_IMAX'],
                                     P['PSC_D_ACC_FLTT'], P['PSC_D_ACC_FLTE'], P['PSC_D_ACC_FLTD'])

        # limits (POSCONTROL_* defaults; GUIDED overwrites them on entry)
        self._vel_max_ne_ms = 5.0
        self._vel_max_up_ms = 2.5
        self._vel_max_down_ms = 1.5
        self._accel_max_ne_mss = 1.0
        self._accel_max_d_mss = 2.5
        self._jerk_max_ne_msss = P['PSC_NE_JERK']
        self._jerk_max_d_msss = P['PSC_D_JERK']

        # NED kinematic state of the controller
        self._pos_estimate_ned_m = np.zeros(3)
        self._vel_estimate_ned_ms = np.zeros(3)
        self._pos_target_ned_m = np.zeros(3)
        self._pos_desired_ned_m = np.zeros(3)
        self._vel_target_ned_ms = np.zeros(3)
        self._vel_desired_ned_ms = np.zeros(3)
        self._accel_target_ned_mss = np.zeros(3)
        self._accel_desired_ned_mss = np.zeros(3)
        self._limit_vector_ned = np.zeros(3)

        self._roll_target_rad = 0.0
        self._pitch_target_rad = 0.0
        self._vel_d_control_ratio = 2.0

    # ---------------------------------------------------------------- limits
    def NE_set_max_speed_accel_m(self, speed_ne_ms, accel_ne_mss):
        self._vel_max_ne_ms = abs(speed_ne_ms)
        self._accel_max_ne_mss = abs(accel_ne_mss)

        att = self._attitude_control
        ang_vel_max = min(np.radians(att.p['ATC_RATE_R_MAX']), np.radians(att.p['ATC_RATE_P_MAX']))
        jerk_max_msss = ang_vel_max * GRAVITY_MSS
        snap_max_mssss = min(att.get_accel_roll_max_radss(), att.get_accel_pitch_max_radss()) * GRAVITY_MSS

        self._jerk_max_ne_msss = self.p['PSC_NE_JERK']
        bf_ff = att.p['ATC_RATE_FF_ENAB']
        if jerk_max_msss > 0.0 and bf_ff:
            self._jerk_max_ne_msss = min(self._jerk_max_ne_msss, jerk_max_msss)
        if snap_max_mssss > 0.0 and bf_ff:
            self._jerk_max_ne_msss = min(0.5 * safe_sqrt(self._accel_max_ne_mss * snap_max_mssss),
                                         self._jerk_max_ne_msss)

    def NE_set_correction_speed_accel_m(self, speed_ne_ms, accel_ne_mss):
        self._p_pos_ne_m.set_limits(speed_ne_ms, accel_ne_mss, 0.0)

    def D_set_max_speed_accel_m(self, speed_down_ms, speed_up_ms, accel_max_d_mss):
        if speed_down_ms != 0.0:
            self._vel_max_down_ms = abs(speed_down_ms)
        if speed_up_ms != 0.0:
            self._vel_max_up_ms = abs(speed_up_ms)
        if accel_max_d_mss != 0.0:
            self._accel_max_d_mss = abs(accel_max_d_mss)

        self._jerk_max_d_msss = self.p['PSC_D_JERK']
        lim = min(GRAVITY_MSS, self._accel_max_d_mss) * 2.0 * np.pi / 5.0
        if self._pid_accel_d_m.filt_T_hz > 0.0:
            self._jerk_max_d_msss = min(self._jerk_max_d_msss, lim * self._pid_accel_d_m.filt_T_hz)
        if self._pid_accel_d_m.filt_E_hz > 0.0:
            self._jerk_max_d_msss = min(self._jerk_max_d_msss, lim * self._pid_accel_d_m.filt_E_hz)

    def D_set_correction_speed_accel_m(self, speed_down_ms, speed_up_ms, accel_max_d_mss):
        self._p_pos_d_m.set_limits(-abs(speed_down_ms), abs(speed_up_ms), abs(accel_max_d_mss), 0.0)

    def get_lean_angle_max_rad(self):
        if self.p['PSC_ANGLE_MAX'] > 0.0:
            return np.radians(self.p['PSC_ANGLE_MAX'])
        return self._attitude_control.lean_angle_max_rad()

    def calculate_overspeed_gain(self):
        vd = self._vel_desired_ned_ms[2]
        if vd > self._vel_max_down_ms and self._vel_max_down_ms != 0.0:
            return OVERSPEED_GAIN_U * vd / self._vel_max_down_ms
        if vd < -self._vel_max_up_ms and self._vel_max_up_ms != 0.0:
            return -OVERSPEED_GAIN_U * vd / self._vel_max_up_ms
        return 1.0

    # ------------------------------------------------------------ estimates
    def update_estimates(self):
        self._pos_estimate_ned_m = np.array(self._ahrs.pos_ned, dtype=float)
        self._vel_estimate_ned_ms = np.array(self._ahrs.vel_ned, dtype=float)

    def get_estimated_accel_D_mss(self):
        return self._ahrs.accel_ef[2] + GRAVITY_MSS

    # ------------------------------------------------------------------ init
    def lean_angles_to_accel_NE_mss(self):
        roll, pitch, _ = self._attitude_control.get_att_target_euler_rad()
        yaw = self._ahrs.yaw
        sr, cr, sp, cp = np.sin(roll), np.cos(roll), np.sin(pitch), np.cos(pitch)
        sy, cy = np.sin(yaw), np.cos(yaw)
        den = max(cr * cp, 0.1)
        return np.array([GRAVITY_MSS * (-cy * sp * cr - sy * sr) / den,
                         GRAVITY_MSS * (-sy * sp * cr + cy * sr) / den])

    def NE_init_controller(self):
        self._pos_target_ned_m[:2] = self._pos_estimate_ned_m[:2]
        self._pos_desired_ned_m[:2] = self._pos_target_ned_m[:2]
        self._vel_target_ned_ms[:2] = self._vel_estimate_ned_ms[:2]
        self._vel_desired_ned_ms[:2] = self._vel_target_ned_ms[:2]
        self._accel_desired_ned_mss[:2] = 0.0

        self._accel_target_ned_mss[:2] = self.lean_angles_to_accel_NE_mss()
        angle_max_rad = min(self._attitude_control.get_althold_lean_angle_max_rad(), self.get_lean_angle_max_rad())
        self._accel_target_ned_mss[:2], _ = limit_length(self._accel_target_ned_mss[:2],
                                                         angle_rad_to_accel_mss(angle_max_rad))

        self._pid_vel_ne_m.reset_filter()
        self._pid_vel_ne_m.set_integrator(self._accel_target_ned_mss[:2]
                                          - self._vel_target_ned_ms[:2] * self._pid_vel_ne_m.kff)

    def D_init_controller(self):
        self._pos_target_ned_m[2] = self._pos_estimate_ned_m[2]
        self._pos_desired_ned_m[2] = self._pos_target_ned_m[2]
        self._vel_target_ned_ms[2] = self._vel_estimate_ned_ms[2]
        self._vel_desired_ned_ms[2] = self._vel_target_ned_ms[2]

        self._pid_vel_d_m.reset_filter()
        self._pid_vel_d_m.set_integrator(0.0)

        a_est = self.get_estimated_accel_D_mss()
        self._accel_target_ned_mss[2] = constrain(a_est, -self._accel_max_d_mss, self._accel_max_d_mss)
        self._accel_desired_ned_mss[2] = self._accel_target_ned_mss[2]
        self._pid_accel_d_m.reset_filter()

        # bumpless transfer from the current throttle
        self._pid_accel_d_m.set_integrator(
            -(self._attitude_control.get_throttle_in() - self._motors.get_throttle_hover())
            - self._pid_accel_d_m.kp * (self._accel_target_ned_mss[2] - a_est)
            - self._pid_accel_d_m.kff * self._accel_target_ned_mss[2])

    # ------------------------------------------------------- input shaping
    def input_pos_vel_accel_NE_m(self, pos_ne_m, vel_ne_ms, accel_ne_mss, limit_output=True):
        """Shape the NE path toward (pos, vel, accel). Returns the advanced (pos, vel)."""
        dt = self._dt_s
        self._pos_desired_ned_m[:2], self._vel_desired_ned_ms[:2] = update_pos_vel_accel_xy(
            self._pos_desired_ned_m[:2], self._vel_desired_ned_ms[:2], self._accel_desired_ned_mss[:2],
            dt, self._limit_vector_ned[:2], self._p_pos_ne_m.error, self._pid_vel_ne_m.error)

        self._accel_desired_ned_mss[:2] = shape_pos_vel_accel_xy(
            pos_ne_m, vel_ne_ms, accel_ne_mss,
            self._pos_desired_ned_m[:2], self._vel_desired_ned_ms[:2], self._accel_desired_ned_mss[:2],
            self._vel_max_ne_ms, self._accel_max_ne_mss, self._jerk_max_ne_msss, dt, limit_output)

        zero2 = np.zeros(2)
        return update_pos_vel_accel_xy(pos_ne_m, vel_ne_ms, accel_ne_mss, dt, zero2, zero2, zero2)

    def input_pos_vel_accel_D_m(self, pos_d_m, vel_d_ms, accel_d_mss, limit_output=True):
        """Shape the D path toward (pos, vel, accel). Returns the advanced (pos, vel)."""
        dt = self._dt_s
        overspeed_gain = self.calculate_overspeed_gain()
        accel_max_d_mss = self._accel_max_d_mss * overspeed_gain
        jerk_max_d_msss = self._jerk_max_d_msss * overspeed_gain

        self._pos_desired_ned_m[2], self._vel_desired_ned_ms[2] = update_pos_vel_accel(
            self._pos_desired_ned_m[2], self._vel_desired_ned_ms[2], self._accel_desired_ned_mss[2],
            dt, self._limit_vector_ned[2], self._p_pos_d_m.error, self._pid_vel_d_m.error)

        self._accel_desired_ned_mss[2] = shape_pos_vel_accel(
            pos_d_m, vel_d_ms, accel_d_mss,
            self._pos_desired_ned_m[2], self._vel_desired_ned_ms[2], self._accel_desired_ned_mss[2],
            -self._vel_max_up_ms, self._vel_max_down_ms,
            -accel_max_d_mss, constrain(accel_max_d_mss, 0.0, 7.5),
            jerk_max_d_msss, dt, limit_output)

        return update_pos_vel_accel(pos_d_m, vel_d_ms, accel_d_mss, dt, 0.0, 0.0, 0.0)

    # ------------------------------------------------------------ run loops
    def NE_update_controller(self):
        dt = self._dt_s

        # position (sqrt P) -> velocity correction
        vel_target_ne, self._pos_target_ned_m[:2] = self._p_pos_ne_m.update_all(
            self._pos_desired_ned_m[:2].copy(), self._pos_estimate_ned_m[:2])
        self._pos_desired_ned_m[:2] = self._pos_target_ned_m[:2]
        self._vel_target_ned_ms[:2] = vel_target_ne + self._vel_desired_ned_ms[:2]

        # velocity PID -> acceleration correction
        accel_target_ne = self._pid_vel_ne_m.update_all(self._vel_target_ned_ms[:2],
                                                        self._vel_estimate_ned_ms[:2], dt,
                                                        self._limit_vector_ned[:2])
        self._accel_target_ned_mss[:2] = accel_target_ne + self._accel_desired_ned_mss[:2]

        # limit acceleration to the lean-angle envelope
        angle_max_rad = min(self._attitude_control.get_althold_lean_angle_max_rad(), self.get_lean_angle_max_rad())
        accel_max_mss = angle_rad_to_accel_mss(angle_max_rad)
        self._limit_vector_ned[:2] = self._accel_target_ned_mss[:2]
        self._accel_target_ned_mss[:2], limited = limit_accel_xy(self._vel_desired_ned_ms[:2],
                                                                 self._accel_target_ned_mss[:2], accel_max_mss)
        if not limited:
            self._limit_vector_ned[:2] = 0.0

        # acceleration -> lean angles (for logging; GUIDED uses the thrust vector)
        cy, sy = np.cos(self._ahrs.yaw), np.sin(self._ahrs.yaw)
        a_n, a_e = self._accel_target_ned_mss[:2]
        accel_forward = a_n * cy + a_e * sy
        accel_right = -a_n * sy + a_e * cy
        self._pitch_target_rad = accel_mss_to_angle_rad(-accel_forward)
        self._roll_target_rad = accel_mss_to_angle_rad(accel_right * np.cos(self._pitch_target_rad))

    def D_update_controller(self):
        dt = self._dt_s

        # position (sqrt P) -> climb-rate correction
        vel_corr, self._pos_target_ned_m[2] = self._p_pos_d_m.update_all(self._pos_desired_ned_m[2],
                                                                         self._pos_estimate_ned_m[2])
        self._pos_desired_ned_m[2] = self._pos_target_ned_m[2]
        self._vel_target_ned_ms[2] = vel_corr + self._vel_desired_ned_ms[2]

        # velocity PID -> acceleration target
        # NOTE: argument order (limit_neg=throttle_lower, limit_pos=throttle_upper) as in 4.7.1
        lim = self._motors.limit
        self._accel_target_ned_mss[2] = self._pid_vel_d_m.update_all(
            self._vel_target_ned_ms[2], self._vel_estimate_ned_ms[2], dt,
            lim['throttle_lower'], lim['throttle_upper'])
        self._accel_target_ned_mss[2] += self._accel_desired_ned_mss[2]

        # acceleration PID -> normalised throttle
        if self._motors.get_throttle_hover() > self._pid_accel_d_m.kimax:
            self._pid_accel_d_m.kimax = self._motors.get_throttle_hover()
        thrust_d_norm = self._pid_accel_d_m.update_all(self._accel_target_ned_mss[2],
                                                       self.get_estimated_accel_D_mss(), dt,
                                                       lim['throttle_lower'] or lim['throttle_upper'])
        thrust_d_norm += self._pid_accel_d_m.get_ff()
        thrust_d_norm -= self._motors.get_throttle_hover()

        self._attitude_control.set_throttle_out(-thrust_d_norm, True, THROTTLE_CUTOFF_FREQ_HZ)

        # helper ratio used by the throttle-mix logic
        error_ratio = self._pid_vel_d_m.error / self._vel_max_down_ms
        self._vel_d_control_ratio += dt * 0.1 * (0.5 - error_ratio)
        self._vel_d_control_ratio = constrain(self._vel_d_control_ratio, 0.0, 2.0)

        if lim['throttle_upper']:
            self._limit_vector_ned[2] = -1.0
        elif lim['throttle_lower']:
            self._limit_vector_ned[2] = 1.0
        else:
            self._limit_vector_ned[2] = 0.0

    def get_thrust_vector(self):
        """Thrust direction for the attitude controller (NED, not normalised)."""
        return np.array([self._accel_target_ned_mss[0], self._accel_target_ned_mss[1], -GRAVITY_MSS])

    # -------------------------------------------------------------- getters
    def get_pos_target_NED_m(self):
        return self._pos_target_ned_m

    def get_vel_target_NED_ms(self):
        return self._vel_target_ned_ms

    def get_accel_target_NED_mss(self):
        return self._accel_target_ned_mss

    def get_pos_desired_NED_m(self):
        return self._pos_desired_ned_m

    def get_vel_desired_NED_ms(self):
        return self._vel_desired_ned_ms


############################################################################
#  ARDUCOPTER
############################################################################
#
#  ArduCopter -- the flight-controller side of the simulation.
#
#  Wires the ported libraries into the Copter-4.7.1 fast loop and exposes two
#  interfaces, mirroring the two sides of a real flight controller:
#
#  **Sensor / actuator side** (what the simulator drives each tick)::
#
#      pwm = copter.update(t, imu, nav)     # one 400 Hz fast-loop tick
#
#  **Companion side** (what a MAVLink companion computer would send)::
#
#      copter.set_mode('GUIDED')
#      copter.arm()
#      copter.takeoff(alt_m)                       # MAV_CMD_NAV_TAKEOFF
#      copter.set_position_target_local_ned(...)   # SET_POSITION_TARGET_LOCAL_NED
#
#  The fast-loop ordering follows ``ArduCopter/Copter.cpp``::
#
#      ins.update -> run_rate_controller -> motors_output -> read_AHRS
#                 -> update_flight_mode -> update_land_and_crash_detectors
#
#  so the rate PIDs act on the body-rate target computed in the *previous*
#  tick, as on the real vehicle.
#
#  State estimation is the main simplification of this draft: ``AP_AHRS`` here
#  takes the attitude / position / velocity solution from the simulator
#  (truth plus optional noise) instead of running EKF3, and only applies the
#  INS gyro / accel low-pass filters.
#
############################################################################


GUIDED_TIMEOUT_S = 3.0
LAND_DETECTOR_TRIGGER_SEC = 1.0


def default_params():
    """Full ArduCopter 4.7.1 default parameter set used by this port."""
    p = {
        'SCHED_LOOP_RATE': 400,     # [Hz]
        'INS_GYRO_FILTER': 20.0,    # [Hz]
        'INS_ACCEL_FILTER': 20.0,   # [Hz]
    }
    p.update(default_atc_params())
    p.update(default_psc_params())
    p.update(default_mot_params())
    return p


class LowPassFilter2p:
    """Filter/LowPassFilter2p -- 2nd-order Butterworth biquad on a vector."""

    def __init__(self, sample_freq, cutoff_freq, n=3):
        self.n = n
        self.enabled = cutoff_freq > 0.0
        if self.enabled:
            fr = sample_freq / cutoff_freq
            ohm = np.tan(np.pi / fr)
            c = 1.0 + 2.0 * np.cos(np.pi / 4.0) * ohm + ohm**2
            self.b0 = ohm**2 / c
            self.b1 = 2.0 * self.b0
            self.b2 = self.b0
            self.a1 = 2.0 * (ohm**2 - 1.0) / c
            self.a2 = (1.0 - 2.0 * np.cos(np.pi / 4.0) * ohm + ohm**2) / c
        self.d1 = None
        self.d2 = None

    def apply(self, x):
        x = np.asarray(x, dtype=float)
        if not self.enabled:
            return x
        if self.d1 is None:
            # initialise to steady state on the first sample
            self.d1 = self.d2 = x / (self.b0 + self.b1 + self.b2)
        d0 = x - self.d1 * self.a1 - self.d2 * self.a2
        y = d0 * self.b0 + self.d1 * self.b1 + self.d2 * self.b2
        self.d2 = self.d1
        self.d1 = d0
        return y


class AP_AHRS:
    """Attitude / navigation solution as seen by the controllers.

    Attributes match what the controllers read: ``quat`` (body->NED),
    ``roll``, ``pitch``, ``yaw``, ``gyro`` (filtered, FRD), ``accel_ef``
    (filtered specific force rotated to NED), ``pos_ned``, ``vel_ned``.
    """

    def __init__(self, loop_rate_hz, gyro_filt_hz, accel_filt_hz):
        self._gyro_filter = LowPassFilter2p(loop_rate_hz, gyro_filt_hz)
        self._accel_filter = LowPassFilter2p(loop_rate_hz, accel_filt_hz)
        self.quat = np.array([1.0, 0.0, 0.0, 0.0])
        self.roll = self.pitch = self.yaw = 0.0
        self.gyro = np.zeros(3)
        self.accel = np.array([0.0, 0.0, -GRAVITY_MSS])
        self.accel_ef = np.array([0.0, 0.0, -GRAVITY_MSS])
        self.pos_ned = np.zeros(3)
        self.vel_ned = np.zeros(3)

    def ins_update(self, imu):
        """AP_InertialSensor::update -- filter the raw gyro / accel samples."""
        self.gyro = self._gyro_filter.apply(imu['gyro'])
        self.accel = self._accel_filter.apply(imu['accel'])

    def update(self, nav):
        """AP_AHRS::update -- take the navigation solution (EKF3 stand-in)."""
        self.roll, self.pitch, self.yaw = nav['euler']
        self.quat = q_from_euler(self.roll, self.pitch, self.yaw)
        self.pos_ned = np.asarray(nav['pos_ned'], dtype=float)
        self.vel_ned = np.asarray(nav['vel_ned'], dtype=float)
        self.accel_ef = q_rotate(self.quat, self.accel)


class ArduCopter:
    """ArduCopter 4.7.1 control stack for a quad-X frame.

    Parameters
    ----------
    params : dict, optional
        Overrides on top of :func:`default_params`, by ArduPilot parameter name.
    """

    def __init__(self, params=None):
        self.params = default_params()
        if params:
            unknown = set(params) - set(self.params)
            if unknown:
                raise KeyError(f'unknown ArduPilot parameter(s): {sorted(unknown)}')
            self.params.update(params)
        P = self.params

        self.loop_rate_hz = P['SCHED_LOOP_RATE']
        self.dt = 1.0 / self.loop_rate_hz

        self.ahrs = AP_AHRS(self.loop_rate_hz, P['INS_GYRO_FILTER'], P['INS_ACCEL_FILTER'])
        self.motors = AP_MotorsMatrix(P, self.dt)
        self.attitude_control = AC_AttitudeControl_Multi(P, self.ahrs, self.motors, self.dt)
        self.pos_control = AC_PosControl(P, self.ahrs, self.motors, self.attitude_control, self.dt)

        self.mode = 'STABILIZE'
        self.armed = False
        self.land_complete = True
        self._land_detector_count = 0

        # GUIDED state
        self.guided_submode = None          # 'TakeOff' | 'PosVelAccel'
        self._takeoff_alt_d_m = 0.0
        self._guided_pos_target_ned_m = np.zeros(3)
        self._guided_vel_target_ned_ms = np.zeros(3)
        self._guided_accel_target_ned_mss = np.zeros(3)
        self._guided_yaw_rad = 0.0
        self._guided_yaw_rate_rads = 0.0
        self._guided_update_time = -np.inf
        self._t = 0.0

    # ======================================================================
    #  COMPANION (MAVLink) SIDE
    # ======================================================================

    def set_mode(self, mode):
        if mode != 'GUIDED':
            raise NotImplementedError(f'only GUIDED is ported so far (got {mode!r})')
        self.mode = mode
        self._guided_init()
        return True

    def arm(self):
        self.armed = True
        self.motors.armed = True
        self.motors.spool_state = AP_MotorsMatrix.GROUND_IDLE
        return True

    def disarm(self):
        self.armed = False
        self.motors.armed = False
        self.motors.spool_state = AP_MotorsMatrix.SHUT_DOWN
        return True

    def takeoff(self, alt_m):
        """MAV_CMD_NAV_TAKEOFF in GUIDED: climb to ``alt_m`` above the current position."""
        if self.mode != 'GUIDED' or not self.armed or not self.land_complete:
            return False
        self.pos_control.update_estimates()
        self._takeoff_alt_d_m = self.ahrs.pos_ned[2] - alt_m
        self.land_complete = False
        self.motors.spool_state = AP_MotorsMatrix.THROTTLE_UNLIMITED

        # start from hover throttle so the accel loop's integrator is bumpless
        self.attitude_control._throttle_in = self.motors.get_throttle_hover()
        self.attitude_control.reset_target_and_rate()
        self.attitude_control.reset_rate_controller_I_terms()
        self.pos_control.NE_init_controller()
        self.pos_control.D_init_controller()
        self._guided_pos_target_ned_m = np.array([self.ahrs.pos_ned[0], self.ahrs.pos_ned[1],
                                                  self._takeoff_alt_d_m])
        self._guided_vel_target_ned_ms = np.zeros(3)
        self._guided_accel_target_ned_mss = np.zeros(3)
        self._guided_yaw_rad = self.ahrs.yaw
        self.guided_submode = 'TakeOff'
        return True

    def takeoff_complete(self):
        return self.guided_submode == 'PosVelAccel'

    def set_position_target_local_ned(self, pos_ned=None, vel_ned=None, accel_ned=None,
                                      yaw=None, yaw_rate=0.0):
        """SET_POSITION_TARGET_LOCAL_NED (MAV_FRAME_LOCAL_NED), routed to
        ``ModeGuided::set_destination_posvelaccel``."""
        if self.mode != 'GUIDED' or self.guided_submode != 'PosVelAccel':
            return False
        if pos_ned is not None:
            self._guided_pos_target_ned_m = np.array(pos_ned, dtype=float)
        self._guided_vel_target_ned_ms = np.zeros(3) if vel_ned is None else np.array(vel_ned, dtype=float)
        self._guided_accel_target_ned_mss = np.zeros(3) if accel_ned is None else np.array(accel_ned, dtype=float)
        if yaw is not None:
            self._guided_yaw_rad = yaw
        self._guided_yaw_rate_rads = yaw_rate
        self._guided_update_time = self._t
        return True

    # ======================================================================
    #  SENSOR / ACTUATOR SIDE
    # ======================================================================

    def update(self, t, imu, nav):
        """One fast-loop tick.

        Parameters
        ----------
        t : float
            Time [s].
        imu : dict
            ``gyro`` [rad/s] and ``accel`` (specific force) [m/s^2], body FRD.
        nav : dict
            ``euler`` (roll, pitch, yaw) [rad], ``pos_ned`` [m], ``vel_ned`` [m/s].

        Returns
        -------
        pwm : ndarray (4,)
            Motor outputs 1..4 [us].
        """
        self._t = t
        self.ahrs.ins_update(imu)
        self.attitude_control.rate_controller_run()
        pwm = self.motors.output()
        self.ahrs.update(nav)
        self.pos_control.update_estimates()
        self._update_flight_mode()
        self._update_land_detector()
        self._update_throttle_hover()
        return pwm

    # ======================================================================
    #  FLIGHT MODE: GUIDED
    # ======================================================================

    def _guided_init(self):
        P = self.params
        pc = self.pos_control
        pc.NE_set_max_speed_accel_m(P['WP_SPD'], P['WP_ACC'])
        pc.NE_set_correction_speed_accel_m(P['WP_SPD'], P['WP_ACC'])
        pc.D_set_max_speed_accel_m(P['WP_SPD_DN'], P['WP_SPD_UP'], P['WP_ACC_Z'])
        pc.D_set_correction_speed_accel_m(P['WP_SPD_DN'], P['WP_SPD_UP'], P['WP_ACC_Z'])
        self.guided_submode = None

    def _update_flight_mode(self):
        if self.mode != 'GUIDED':
            return
        if not self.armed or (self.land_complete and self.guided_submode != 'TakeOff'):
            self._make_safe_ground_handling()
            return
        if self.guided_submode in ('TakeOff', 'PosVelAccel'):
            self._posvelaccel_control_run()

    def _make_safe_ground_handling(self):
        self.motors.spool_state = (AP_MotorsMatrix.GROUND_IDLE if self.armed
                                   else AP_MotorsMatrix.SHUT_DOWN)
        self.attitude_control.reset_target_and_rate()
        self.attitude_control.reset_rate_controller_I_terms()
        self.attitude_control.set_throttle_out(0.0, False, 2.0)
        self.pos_control.NE_init_controller()
        self.pos_control.D_init_controller()

    def _posvelaccel_control_run(self):
        """ModeGuided::posvelaccel_control_run (takeoff reuses it with a
        fixed climb target, standing in for ``auto_takeoff_run``)."""
        self.motors.spool_state = AP_MotorsMatrix.THROTTLE_UNLIMITED
        pc = self.pos_control

        if self.guided_submode == 'PosVelAccel' and self._t - self._guided_update_time > GUIDED_TIMEOUT_S:
            self._guided_vel_target_ned_ms = np.zeros(3)
            self._guided_accel_target_ned_mss = np.zeros(3)
            self._guided_yaw_rate_rads = 0.0

        pos, vel = pc.input_pos_vel_accel_NE_m(self._guided_pos_target_ned_m[:2],
                                               self._guided_vel_target_ned_ms[:2],
                                               self._guided_accel_target_ned_mss[:2], False)
        self._guided_pos_target_ned_m[:2], self._guided_vel_target_ned_ms[:2] = pos, vel

        pz, vz = pc.input_pos_vel_accel_D_m(self._guided_pos_target_ned_m[2],
                                            self._guided_vel_target_ned_ms[2],
                                            self._guided_accel_target_ned_mss[2], False)
        self._guided_pos_target_ned_m[2], self._guided_vel_target_ned_ms[2] = pz, vz

        pc.NE_update_controller()
        pc.D_update_controller()

        # AutoYaw ANGLE_RATE: integrate the commanded rate into the heading
        self._guided_yaw_rad += self._guided_yaw_rate_rads * self.dt
        self.attitude_control.input_thrust_vector_heading_rad(pc.get_thrust_vector(),
                                                              self._guided_yaw_rad,
                                                              self._guided_yaw_rate_rads)

        if self.guided_submode == 'TakeOff':
            # takeoff completes when the shaped path reaches the target altitude
            if abs(pc.get_pos_desired_NED_m()[2] - self._takeoff_alt_d_m) < 0.05 \
                    and abs(pc.get_vel_desired_NED_ms()[2]) < 0.05:
                self.guided_submode = 'PosVelAccel'
                self._guided_update_time = self._t

    # ======================================================================
    #  HOUSEKEEPING
    # ======================================================================

    def _update_land_detector(self):
        """Simplified land_detector.cpp: low throttle + no vertical motion for 1 s."""
        if not self.armed or self.land_complete or self.guided_submode == 'TakeOff':
            self._land_detector_count = 0
            return
        motor_at_lower_limit = self.motors.limit['throttle_lower'] or \
            self.motors.get_throttle_out() < 0.25 * self.motors.get_throttle_hover()
        descent_rate_low = abs(self.ahrs.vel_ned[2]) < 1.0
        if motor_at_lower_limit and descent_rate_low:
            self._land_detector_count += 1
            if self._land_detector_count >= LAND_DETECTOR_TRIGGER_SEC * self.loop_rate_hz:
                self.land_complete = True
        else:
            self._land_detector_count = 0

    def _update_throttle_hover(self):
        """Copter::update_throttle_hover -- learn MOT_THST_HOVER in steady flight."""
        if not self.armed or self.land_complete:
            return
        if abs(self.pos_control.get_vel_desired_NED_ms()[2]) > 1e-6:
            return
        if self.motors.get_throttle() > 0.0 and abs(self.ahrs.vel_ned[2]) < 0.6 \
                and abs(self.ahrs.roll) < np.radians(5.0) and abs(self.ahrs.pitch) < np.radians(5.0):
            self.motors.update_throttle_hover(self.dt)
