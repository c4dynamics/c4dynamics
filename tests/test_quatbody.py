# type: ignore

import unittest
import warnings
import numpy as np
import sys

sys.path.append(".")
from c4dynamics import quatbody, rigidbody
import c4dynamics as c4d
import os

import matplotlib

matplotlib.use("Agg")
from matplotlib import pyplot as plt

try:
    import open3d as o3d

    o3d.utility.set_verbosity_level(o3d.utility.VerbosityLevel.Error)
    OPEN3D_AVAILABLE = True
except ImportError:
    OPEN3D_AVAILABLE = False


class TestQuatbody(unittest.TestCase):

    def setUp(self):
        """Set up a basic quatbody instance for testing."""
        self.qb = quatbody(
            x=1.0,
            y=2.0,
            z=3.0,
            vx=4.0,
            vy=5.0,
            vz=6.0,
            phi=0.1,
            theta=0.2,
            psi=0.3,
            p=0.4,
            q=0.5,
            r=0.6,
        )

    def tearDown(self):
        plt.close("all")

    def test_initialization(self):
        """Test initialization of quatbody with given parameters."""
        self.assertEqual(self.qb.x, 1.0)
        self.assertEqual(self.qb.y, 2.0)
        self.assertEqual(self.qb.z, 3.0)
        self.assertEqual(self.qb.vx, 4.0)
        self.assertEqual(self.qb.vy, 5.0)
        self.assertEqual(self.qb.vz, 6.0)
        self.assertAlmostEqual(self.qb.phi, 0.1)
        self.assertAlmostEqual(self.qb.theta, 0.2)
        self.assertAlmostEqual(self.qb.psi, 0.3)
        self.assertEqual(self.qb.p, 0.4)
        self.assertEqual(self.qb.q, 0.5)
        self.assertEqual(self.qb.r, 0.6)

    def test_state_vector(self):
        """Test the state vector layout and the initial conditions."""
        self.assertEqual(len(self.qb.X), 13)
        self.assertEqual(str(self.qb), "[ x  y  z  vx  vy  vz  qw  qx  qy  qz  p  q  r ]")
        np.testing.assert_array_almost_equal(self.qb.X0, self.qb.X)
        np.testing.assert_array_almost_equal(self.qb.X[6:10], c4d.rotmat.euler2quat(0.1, 0.2, 0.3))

    def test_default_initialization(self):
        """Test that the default attitude is the identity quaternion."""
        qb = quatbody()
        np.testing.assert_array_equal(qb.X, [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0])

    def test_quat_initialization(self):
        """Test initialization with a quaternion, which overrides the Euler angles."""
        qb = quatbody(phi=1, quat=[2, 0, 0, 0])
        np.testing.assert_array_equal(qb.quat, [1, 0, 0, 0])
        with self.assertRaises(ValueError):
            quatbody(quat=[0, 0, 0, 0])
        with self.assertRaises(ValueError):
            quatbody(quat=[1, 0, 0])

    def test_quat_property(self):
        """Test the quaternion getter and the normalizing setter."""
        self.qb.quat = [1, 0, 0, 1]
        np.testing.assert_array_almost_equal(self.qb.quat, [np.sqrt(0.5), 0, 0, np.sqrt(0.5)])
        self.assertAlmostEqual(np.linalg.norm(self.qb.quat), 1)
        np.testing.assert_array_almost_equal(self.qb.angles, [0, 0, np.pi / 2])

    def test_euler_setters(self):
        """Test that setting an Euler angle keeps the other two."""
        self.qb.phi = -0.2
        np.testing.assert_array_almost_equal(self.qb.angles, [-0.2, 0.2, 0.3])
        self.qb.theta = 0.7
        np.testing.assert_array_almost_equal(self.qb.angles, [-0.2, 0.7, 0.3])
        self.qb.psi = 2.0
        np.testing.assert_array_almost_equal(self.qb.angles, [-0.2, 0.7, 2.0])
        self.assertAlmostEqual(np.linalg.norm(self.qb.quat), 1)

    def test_inertia_tensor_property(self):
        """Test inertia tensor property."""
        self.qb.I = [1, 2, 3]
        np.testing.assert_array_equal(self.qb.I, np.array([1, 2, 3]))

    def test_angles_property(self):
        """Test angles property returns correct values."""
        expected_angles = np.array([self.qb.phi, self.qb.theta, self.qb.psi])
        np.testing.assert_array_almost_equal(self.qb.angles, expected_angles)
        np.testing.assert_array_almost_equal(self.qb.angles, [0.1, 0.2, 0.3])

    def test_ang_rates_property(self):
        """Test angular rates property returns correct values."""
        expected_rates = np.array([self.qb.p, self.qb.q, self.qb.r])
        np.testing.assert_array_equal(self.qb.ang_rates, expected_rates)

    def test_rotation_matrix(self):
        """Test rotation matrix property is identical to the rigidbody's 3-2-1 DCM."""
        br = self.qb.BR
        self.assertIsInstance(br, np.ndarray)  # Check if BR is an ndarray
        rb = rigidbody(phi=0.1, theta=0.2, psi=0.3)
        np.testing.assert_array_almost_equal(br, rb.BR)

    def test_transpose_rotation_matrix(self):
        """Test transpose of rotation matrix."""
        rb = self.qb.RB
        self.assertIsInstance(rb, np.ndarray)  # Check if RB is an ndarray
        np.testing.assert_array_equal(rb, np.transpose(self.qb.BR))

    def test_integration_method(self):
        """Test the integration method."""
        forces = np.array([0.0, 0.0, 0.0])
        moments = np.array([0.0, 0.0, 0.0])
        dt = 0.1  # Time step
        acc = self.qb.inteqm(forces, moments, dt)
        self.assertIsInstance(acc, np.ndarray)  # Check if acceleration is returned as numpy array
        self.assertEqual(acc.shape, (6,))
        self.assertAlmostEqual(np.linalg.norm(self.qb.quat), 1)

    def test_integration_matches_rigidbody(self):
        """Test the quaternion dynamics against the Euler angles dynamics (away from gimbal lock)."""
        from scipy.integrate import solve_ivp

        mass, inertia = 1.2, [0.0082, 0.0091, 0.0149]
        forces, moments = np.array([0.1, -0.2, 0.3]), np.array([0.001, -0.002, 0.0005])
        dt, tf = 1e-3, 1.0

        qb = quatbody(phi=0.1, theta=0.2, psi=0.3, p=0.4, q=-0.3, r=0.6)
        qb.mass, qb.I = mass, inertia
        for _ in range(round(tf / dt)):
            qb.inteqm(forces, moments, dt)

        # reference: the rigidbody (Euler angles) equations of motion, integrated by scipy.
        rb = rigidbody()
        rb.mass, rb.I = mass, inertia

        def f(t, y):
            rb.X = y
            return c4d.eqm.eqm6(rb, forces, moments)

        sol = solve_ivp(
            f, [0, tf], [0, 0, 0, 0, 0, 0, 0.1, 0.2, 0.3, 0.4, -0.3, 0.6], rtol=1e-10, atol=1e-12
        )
        yref = sol.y[:, -1]

        np.testing.assert_allclose(qb.X[:6], yref[:6], atol=1e-6)
        np.testing.assert_allclose(qb.angles, yref[6:9], atol=1e-6)
        np.testing.assert_allclose(qb.ang_rates, yref[9:12], atol=1e-6)

    def test_integration_through_gimbal_lock(self):
        """Test a full flip about a tilted axis, where the Euler angles are singular."""
        dt = 1e-3
        qb = quatbody(phi=0.3, q=2 * np.pi)
        qb.I = [0.01, 0.01, 0.02]
        for _ in range(1000):
            qb.inteqm(np.zeros(3), np.zeros(3), dt)
            self.assertTrue(np.all(np.isfinite(qb.X)))
        # a full revolution returns to the initial attitude (up to the quaternion sign).
        np.testing.assert_allclose(np.abs(qb.quat), np.abs(c4d.rotmat.euler2quat(0.3)), atol=1e-6)

    def test_data_angles(self):
        """Test data() returns the Euler angles histories derived from the quaternion."""
        for t, psi in enumerate([0.0, 0.1, 0.2]):
            self.qb.psi = psi
            self.qb.store(t)
        t, psi = self.qb.data("psi")
        np.testing.assert_array_equal(t, [0, 1, 2])
        np.testing.assert_array_almost_equal(psi, [0.0, 0.1, 0.2])
        _, phi = self.qb.data("phi", scale=2)
        np.testing.assert_array_almost_equal(phi, [0.2, 0.2, 0.2])
        _, qw = self.qb.data("qw")
        self.assertEqual(len(qw), 3)

    def test_data_angles_no_history(self):
        """Test data() of the Euler angles with no stored history."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            out = quatbody().data("theta")
        self.assertEqual(out.size, 0)

    def test_plot(self):
        """Test plotting of every variable type."""
        for ti in range(5):
            self.qb.inteqm(np.zeros(3), np.zeros(3), 0.01)
            self.qb.store(ti)
        for var in ["x", "vz", "top", "side", "qw", "qy", "phi", "theta", "psi", "p", "r"]:
            self.qb.plot(var)

    def test_plot_invalid(self):
        """Test plotting of a non state variable or with no history."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.assertIsNone(quatbody().plot("theta"))
            self.assertIsNone(self.qb.plot("nonexistent"))

    @unittest.skipUnless(OPEN3D_AVAILABLE, "Skipping Open3D tests because Open3D is not installed")
    @unittest.skipIf("DISPLAY" not in os.environ, "Skipping GUI test in headless mode")
    def test_animate_method(self):
        """Test the animate method."""
        modelpath = c4d.datasets.d3_model("bunny")
        angle0 = [0, 0, 0]
        modelcolor = None
        dt = 1e-3
        savedir = None
        cbackground = [1, 1, 1]
        for i in range(11):
            self.qb.theta = i * np.pi / 100
            self.qb.store()
        try:
            self.qb.animate(modelpath, angle0, modelcolor, dt, savedir, cbackground)
        except Exception as e:
            self.fail(f"animate() raised an exception: {e}")


if __name__ == "__main__":
    unittest.main()
