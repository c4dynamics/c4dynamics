import sys
from typing import Optional

import numpy as np

# sys.path.append(".")
# import c4dynamics as c4d
from c4dynamics.filters import kalman


# =============================================================================
# SO(3) / Lie-algebra utilities
# =============================================================================
def skewSym(v: np.ndarray) -> np.ndarray:
    """
    Skew-symmetric matrix ``[v]_x`` associated with a 3-vector.

    ``skewSym(v) @ w == np.cross(v, w)``. This is the isomorphism between
    R^3 and the Lie algebra so(3).

    See Also
    --------
    expSO3, logSO3
    """
    v = np.asarray(v, dtype=float).ravel()
    return np.array(
        [
            [0.0, -v[2], v[1]],
            [v[2], 0.0, -v[0]],
            [-v[1], v[0], 0.0],
        ]
    )


def expSO3(phi: np.ndarray) -> np.ndarray:
    """
    Exponential map from the Lie algebra so(3) to the Lie group SO(3).

    Maps a rotation vector ``phi`` (3, axis-angle: direction is the
    rotation axis, norm is the rotation angle in radians) to the
    corresponding rotation matrix, via Rodrigues' formula:

    ``R = I + sin(t)*K + (1 - cos(t))*K@K``, ``K = skewSym(phi/t)``,
    ``t = norm(phi)``.

    For small angles a first-order approximation is used to avoid the
    0/0 singularity at ``t = 0``.

    See Also
    --------
    logSO3, skewSym

    Examples
    --------
    >>> expSO3(np.zeros(3))   # doctest: +NUMPY_FORMAT
    [[1 0 0]
     [0 1 0]
     [0 0 1]]
    """
    phi = np.asarray(phi, dtype=float).ravel()
    t = np.linalg.norm(phi)

    if t < 1e-9:
        return np.eye(3) + skewSym(phi)

    K = skewSym(phi / t)
    return np.eye(3) + np.sin(t) * K + (1 - np.cos(t)) * (K @ K)


def logSO3(R: np.ndarray) -> np.ndarray:
    """
    Logarithm map from the Lie group SO(3) to the Lie algebra so(3).

    Returns the rotation vector (3,) such that ``expSO3(logSO3(R)) == R``.
    ``norm(logSO3(R))`` is the geodesic distance on SO(3) between ``R``
    and the identity, i.e. the total rotation angle in radians.

    See Also
    --------
    expSO3, skewSym
    """
    R = np.asarray(R, dtype=float)
    c = np.clip((np.trace(R) - 1) / 2, -1.0, 1.0)
    t = np.arccos(c)

    if t < 1e-9:
        return np.zeros(3)

    if abs(t - np.pi) < 1e-6:
        # Near-pi case: sin(t) -> 0, the generic formula loses precision.
        # Recover the axis from the diagonal of (R + I)/2.
        A = (R + np.eye(3)) / 2
        ax = np.sqrt(np.maximum(np.diag(A), 0.0))
        imax = int(np.argmax(ax))
        v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
        if abs(v[imax]) > 1e-12 and ax[imax] > 0:
            ax = ax * np.sign(v[imax])
        return t * ax / np.linalg.norm(ax)

    v = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return (t / (2 * np.sin(t))) * v


# =============================================================================
# Invariant EKF
# =============================================================================
class iekf(kalman):
    """
    Invariant Extended Kalman Filter for attitude estimation on SO(3).

    VERIFIED AGAINST THE ACTUAL ``c4dynamics.filters.kalman`` SOURCE
    -------------------------------------------------------------------
    (An earlier version of this port worked from inferred assumptions;
    the notes below are confirmed by reading the real ``kalman.py`` and
    ``lowpass.py``.)

    * ``kalman`` subclasses ``c4d.state``; ``kalman.__init__(**X)``
      passes each named variable up as an individual state attribute,
      and ``self.X`` behaves as an assignable array-like view over
      them (in the dict's insertion order) -- confirmed by every
      ``self.X = ...`` / ``self.X += ...`` in the source, which this
      class relies on in exactly the same way.
    * ``kalman.predict(u=None, Q=None)`` propagates
      ``self.P = F @ P @ F.T + Q`` using the currently-set ``self.F``,
      and additionally does ``self.X = self.F @ self.X`` *unless*
      ``self._nonlinearF`` is truthy. This class never sets
      ``self._nonlinearF`` (that flag belongs to :class:`ekf`'s `fx`
      mechanism, which does not apply to a group-valued state), so it
      is always `False` here and that line always runs -- harmlessly,
      since ``self.X`` is always exactly zero going into `predict`
      (see "error-state reset" below), so ``F @ 0 == 0`` regardless of
      `F`.
    * ``kalman.update(z=None, R=None, hx=None, innov=None, gate=None)``
      forms the innovation directly from `innov` when given, computes
      the Kalman gain from the currently-set ``self.H``, updates
      ``self.P``, then does ``self.X += K @ innov``, and returns `K`
      (or `None` if `gate` rejects the update or `S` is singular, in
      which case `X` and `P` are left untouched).
    * **Covariance update form**: the parent uses the textbook form
      ``P = P - K @ H @ P``, *not* the Joseph form
      (``P = (I-KH) P (I-KH).T + K R K.T``) this project's MATLAB code
      uses. The two are mathematically equivalent for an exact `K`, but
      Joseph form stays positive-semidefinite under roundoff while the
      textbook form does not necessarily. Attitude recovery from a
      large initial error (see `runSyntheticBenchmark.m` Experiment B)
      is exactly the regime with large transient corrections where this
      matters most -- **set `P_jitter` when using this class for that
      kind of scenario**, or subclass and override the covariance step
      if strict Joseph form is required.
    * A bare scalar `P0` is **not** auto-expanded to ``scalar * eye(n)``
      by the parent for `n` > 1 (see `P0` below) -- this class expands
      it before construction so the convenience default still works.

    THEORY
    ------
    Attitude does not live in a vector space but on the Lie group SO(3),
    so the estimation error is NOT a subtraction. It is defined through
    the group action, as a body-frame ("left-invariant") error:

    ``R_true = R_hat @ expSO3(delta)``  =>  ``delta = logSO3(R_hat.T @ R_true)``

    ``delta`` lives in the Lie algebra so(3) ~ R^3, which *is* a vector
    space -- that is where the linear Kalman machinery in the parent
    ``kalman`` class is applied.

    Because gyro-driven attitude propagation is group-affine, the error
    dynamics are autonomous ("log-linear"): the transition Jacobian
    depends only on the *measured* angular rate, never on the
    *estimated* attitude. This is what separates the IEKF from a
    classical multiplicative EKF and gives it much stronger convergence
    from a poor initial estimate.

    IMPLEMENTATION PATTERN -- error-state reset
    --------------------------------------------
    Because the parent ``kalman`` class only knows how to add a state
    vector linearly, the *nominal* state (the rotation ``self.Rot``, and
    optionally the gyro bias ``self.b``) is kept as a plain attribute on
    this object, separate from ``self.X``. ``self.X`` is the
    Lie-algebra error state, always zero-mean:

    * ``predict()`` advances ``self.Rot`` on the group directly
      (``self.Rot = self.Rot @ expSO3(omega_hat * dt)``), sets the
      Jacobian ``self.F`` for this step, then calls
      ``super().predict(Q=Q)`` so the parent grows ``self.P`` only --
      ``self.X`` stays at zero because ``F @ 0 == 0``.
    * ``update()`` sets ``self.H`` for this measurement, calls
      ``super().update(innov=..., R=...)`` so the parent computes the
      Kalman gain and updates ``self.X`` and ``self.P``, then *injects*
      the resulting error state into ``self.Rot`` / ``self.b`` via the
      exponential map and resets ``self.X`` back to zero.

    NOTE ON THE NAME ``self.Rot``: the parent ``kalman`` class already
    uses ``self.R`` for the measurement-noise covariance (see its `R`
    constructor argument, used throughout ``ekf.py``), so the attitude
    rotation matrix is deliberately kept on a differently-named
    attribute here to avoid silently clobbering it.

    This is exactly the same kind of accommodation
    :class:`ekf <c4dynamics.filters.ekf.ekf>` makes for a nonlinear
    ``fx``, except the nonlinearity here is the group structure of
    SO(3) rather than a nonlinear vector field.


    Parameters
    ----------
    R0 : np.ndarray, optional
        Initial attitude estimate, a 3x3 rotation matrix (body -> world),
        stored on ``self.Rot`` (not ``self.R`` -- see the note above).
        Defaults to the identity.
    b0 : np.ndarray, optional
        Initial gyro bias estimate (3,). Defaults to zero.
    estimate_bias : bool, optional
        Augment the error state with a gyro bias (recommended). Default
        `True`.
    P0 : np.ndarray or float
        Initial error-state covariance. Shape (6, 6) if
        `estimate_bias` else (3, 3). A bare scalar is expanded to
        ``scalar * eye(n)`` (done in this class, see the note above --
        the parent does not do this correctly for n > 1). A 1-D array
        is treated by the parent as per-component standard deviations
        (squared into a diagonal covariance); a full (n, n) matrix is
        used as-is.

        CAVEAT: a single scalar gives the attitude block (rad^2) and the
        bias block (rad^2/s^2) the *same* numerical variance, even
        though they are different physical quantities on very different
        natural scales -- a scalar generous enough for the attitude
        (e.g. a large initial attitude error) is typically wildly too
        generous for the bias, and produces a large, unphysical initial
        correction on `self.b`. When `estimate_bias` is `True` and the
        two blocks need different initial uncertainty (the usual case),
        build a block-diagonal matrix instead, e.g.::

            P0 = np.zeros((6, 6))
            P0[0:3, 0:3] = np.deg2rad(sigma_att_deg)**2 * np.eye(3)
            P0[3:6, 3:6] = np.deg2rad(sigma_bias_deg_s)**2 * np.eye(3)
    sigmaGyro : float, optional
        Gyro white noise std [rad/s]. Default ``deg2rad(0.5)``.
    sigmaBias : float, optional
        Bias random-walk std [rad/s^2]. Default ``1e-3``. Ignored if
        `estimate_bias` is `False`.
    P_jitter : float, optional
        Opt-in covariance stabilization; see
        :class:`kalman <c4dynamics.filters.kalman.kalman>`.


    Example
    -------
    Static IMU, accelerometer-only correction, starting from a small
    attitude error:

    .. code::

      >>> filt = iekf(P0 = 1.0, estimate_bias = False)
      >>> filt.Rot = expSO3(np.array([0.1, 0.0, 0.0]))   # 5.7 deg roll error
      >>> gRef = np.array([0.0, 0.0, -1.0])
      >>> for _ in range(50):
      ...     filt.predict(gyro = np.zeros(3), dt = 0.01)
      ...     _ = filt.update(y = filt.R.T @ gRef, ref = gRef, Rmeas = 0.01 * np.eye(3))
      >>> float(np.linalg.norm(logSO3(filt.Rot)))  # doctest: +SKIP
      0.0...

    See Also
    --------
    expSO3, logSO3, skewSym
    """

    def __init__(
        self,
        R0: Optional[np.ndarray] = None,
        b0: Optional[np.ndarray] = None,
        estimate_bias: bool = True,
        P0=1.0,
        sigmaGyro: float = np.deg2rad(0.5),
        sigmaBias: float = 1e-3,
        P_jitter: Optional[float] = None,
    ):
        self.Rot = np.eye(3) if R0 is None else np.array(R0, dtype=float, copy=True)
        self.b = np.zeros(3) if b0 is None else np.array(b0, dtype=float).ravel().copy()

        self._estimateBias = bool(estimate_bias)
        self._sigmaGyro = sigmaGyro
        self._sigmaBias = sigmaBias

        if self._estimateBias:
            X = {"dthx": 0.0, "dthy": 0.0, "dthz": 0.0, "bx": 0.0, "by": 0.0, "bz": 0.0}
        else:
            X = {"dthx": 0.0, "dthy": 0.0, "dthz": 0.0}

        n = len(X)

        # IMPORTANT (verified against the real kalman.py source): a bare
        # scalar P0 is NOT auto-expanded to scalar*eye(n) by the parent
        # class -- np.atleast_2d(scalar) gives a (1,1) matrix regardless of
        # n, which only happens to be correct for a 1-dimensional state (as
        # in ekf.py's own single-variable doctest examples). Our error
        # state has n = 3 or 6, so a bare scalar must be expanded here,
        # before handing it to the parent. A 1-D array of standard
        # deviations or a full (n, n) covariance matrix is passed through
        # unchanged -- the parent already handles both of those correctly.
        if np.isscalar(P0):
            P0 = float(P0) * np.eye(n)

        F = np.eye(n)
        H = np.zeros((3, n))

        super().__init__(X, F, H, P0=P0, P_jitter=P_jitter)

    # ------------------------------------------------------------------
    def predict(
        self,
        gyro: np.ndarray,
        dt: float,
        sigmaGyro: Optional[float] = None,
        sigmaBias: Optional[float] = None,
    ):
        """
        Propagate the attitude estimate with a gyro measurement.

        Advances ``self.Rot`` exactly on the group (bias-corrected
        angular rate, exponential integration), then propagates the
        error-state covariance through the (state-independent, hence
        "invariant") transition Jacobian.

        Parameters
        ----------
        gyro : np.ndarray
            Angular rate measurement in the body frame (3,) [rad/s].
        dt : float
            Time step [s].
        sigmaGyro : float, optional
            Override the gyro noise std set at construction, for this
            step only.
        sigmaBias : float, optional
            Override the bias random-walk std set at construction, for
            this step only. Ignored if `estimate_bias` is `False`.
        """
        om = np.asarray(gyro, dtype=float).ravel() - self.b
        self.Rot = self.Rot @ expSO3(om * dt)

        sg = self._sigmaGyro if sigmaGyro is None else sigmaGyro
        Qg = (sg**2) * np.eye(3)

        if self._estimateBias:
            sb = self._sigmaBias if sigmaBias is None else sigmaBias
            F = np.eye(6)
            F[0:3, 0:3] = expSO3(-om * dt)
            F[0:3, 3:6] = -np.eye(3) * dt
            Qb = (sb**2) * np.eye(3)
            Q = np.zeros((6, 6))
            Q[0:3, 0:3] = Qg * dt
            Q[3:6, 3:6] = Qb * dt
        else:
            F = expSO3(-om * dt)
            Q = Qg * dt

        self.F = F
        super().predict(Q=Q)

        # Verified redundant-but-harmless: kalman.predict() itself already
        # does self.X = self.F @ self.X whenever self._nonlinearF is falsy
        # (which it always is here -- this class never sets that flag, it
        # belongs to ekf's `fx` mechanism). Since self.X is always exactly
        # zero going into predict(), F @ 0 == 0 regardless of F, so this
        # line changes nothing today. Kept as an explicit, self-documenting
        # invariant in case that internal behaviour ever changes.
        self.X *= 0.0

    # ------------------------------------------------------------------
    def update(
        self,
        y: np.ndarray,
        ref: np.ndarray,
        Rmeas: np.ndarray,
        adaptive: bool = False,
        tol: float = 0.05,
        nominalNorm: float = 1.0,
        gate: Optional[float] = None,
    ):
        """
        Correct the attitude estimate with a body-frame vector observation.

        A single-vector measurement of a known world-frame direction
        (accelerometer -> gravity, magnetometer -> magnetic field),
        following ``y = R.T @ ref + noise``. Call once per available
        sensor at each time step (accelerometer, then magnetometer) for
        a sequential update, matching the MATLAB reference
        implementation (``iekfAttitude.m``).

        Parameters
        ----------
        y : np.ndarray
            Measured body-frame vector (3,). Does not need to be
            pre-normalised; normalised internally.
        ref : np.ndarray
            Known world-frame reference direction (3,), e.g. gravity or
            magnetic field. Does not need to be pre-normalised.
        Rmeas : np.ndarray
            Measurement noise covariance (3, 3), for the *normalised*
            vector.
        adaptive : bool, optional
            If `True`, inflate `Rmeas` when the raw measurement's norm
            departs from `nominalNorm` -- the vector is likely
            contaminated (external acceleration / magnetic disturbance)
            and should be trusted less rather than rejected outright.
            Default `False`.
        tol : float, optional
            Relative-deviation scale for the adaptive inflation. Default
            0.05.
        nominalNorm : float, optional
            Expected raw (un-normalised) measurement norm, for the
            adaptive gating. Default 1.0.
        gate : float, optional
            Chi-squared NIS gating threshold, passed straight through to
            the parent's `update`; see
            :meth:`kalman.update <c4dynamics.filters.kalman.kalman.update>`.
            If the innovation fails the gate, the update is rejected
            (nothing is injected into `self.Rot`/`self.b`) and this
            method returns `None`.

        Returns
        -------
        K : np.ndarray or None
            The Kalman gain, or `None` if the measurement's norm is
            (numerically) zero and the update was skipped.
        """
        y = np.asarray(y, dtype=float).ravel()
        nrm = np.linalg.norm(y)
        if nrm < 1e-12:
            return None

        refDir = np.asarray(ref, dtype=float).ravel()
        refDir = refDir / np.linalg.norm(refDir)

        yhat = self.Rot.T @ refDir
        yMeas = y / nrm

        n = self.P.shape[0]
        H = np.zeros((3, n))
        H[:, 0:3] = skewSym(yhat)
        self.H = H

        Rm = np.array(Rmeas, dtype=float, copy=True)
        if adaptive:
            dev = abs(nrm - nominalNorm) / nominalNorm
            Rm = Rm * (1 + (dev / tol) ** 2)

        K = super().update(innov=(yMeas - yhat), R=Rm, gate=gate)

        if K is None:
            # gated out by the parent class -- nothing to inject.
            return None

        dx = np.asarray(self.X, dtype=float).ravel().copy()
        self.Rot = self.Rot @ expSO3(dx[0:3])
        if self._estimateBias:
            self.b = self.b + dx[3:6]

        # Inject-then-reset: the correction has been folded into the
        # nominal state (R, b); the linear error-state goes back to zero
        # so the next predict/update starts from a clean local frame.
        self.X *= 0.0

        return K


if __name__ == "__main__":

    from c4dynamics import rundoctests

    rundoctests(sys.modules[__name__])
