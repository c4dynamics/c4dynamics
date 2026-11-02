# type: ignore

from matplotlib import pyplot as plt
import sys
import os
import socket

sys.path.append(".")
import c4dynamics as c4d
import numpy as np

savedir = c4d.j(os.getcwd(), "docs", "source", "_examples", "quatbody")
example_imgs = c4d.j(os.getcwd(), "examples", "_out", "quatbody", "gif_images")

# x y z vx vy vz qw qx qy qz p  q  r
# 0 1 2 3  4  5  6  7  8  9  10 11 12

drone_I = [0.0082, 0.0082, 0.0149]


def intro():

    c4d.cprint("intro", "y")
    qb = c4d.quatbody(z=10, psi=90 * c4d.d2r, r=0.5)
    print(qb.X0)
    # [0  0  10  0  0  0  0.707  0  0  0.707  0  0  0.5]

    c4d.cprint("intro example - back flip", "y")

    dt = 0.001
    drone = c4d.quatbody(z=10, q=2 * np.pi)
    drone.I = drone_I
    drone.mass = 1.2

    for t in np.arange(0, 1, dt):
        drone.store(t)
        drone.inteqm(np.zeros(3), np.zeros(3), dt)
    drone.store(1)

    print(np.abs(drone.quat))
    # [1  0  0  0]

    plt.style.use("dark_background")
    factorsize = 4
    aspectratio = 1080 / 1920
    _, ax = plt.subplots(
        2,
        1,
        dpi=200,
        figsize=(factorsize, factorsize * aspectratio),
        gridspec_kw={"left": 0.15, "right": 0.9, "top": 0.9, "bottom": 0.2, "hspace": 0.8},
    )

    drone.plot("qw", ax=ax[0])
    ax[0].set(xlabel="")
    drone.plot("qy", ax=ax[1], filename=c4d.j(savedir, "intro_backflip"))

    if socket.gethostname() != "ZivMeri-PC":

        modelpath = c4d.datasets.d3_model("f16")
        drone.animate(modelpath, angle0=[90 * c4d.d2r, 0, 180 * c4d.d2r], savedir=example_imgs)
        c4d.gif(example_imgs, "qb_intro_backflip", duration=1)

    plt.show(block=True)


def izz():
    c4d.cprint("izz", "y")

    dt = 0.01
    torque = [0, 0, 0.01]

    light = c4d.quatbody()
    light.I = drone_I

    heavy = c4d.quatbody()
    heavy.I = [2 * i for i in drone_I]

    for ti in np.arange(0, 2, dt):
        light.inteqm(np.zeros(3), torque, dt)
        light.store(ti)
        heavy.inteqm(np.zeros(3), torque, dt)
        heavy.store(ti)

    light.plot("psi")
    heavy.plot("psi", ax=plt.gca(), color="c", filename=c4d.j(savedir, "Izz_yaw"))
    plt.show(block=True)


def quat():
    c4d.cprint("quat", "y")
    qb = c4d.quatbody(phi=90 * c4d.d2r)
    print(qb.quat)
    # [0.707  0.707  0  0]
    qb.quat = [1, 0, 0, 1]
    print(qb.quat)
    # [0.707  0  0  0.707]
    print(qb.angles * c4d.r2d)
    # [0  0  90]


def angles():
    c4d.cprint("angles", "y")
    qb = c4d.quatbody(phi=135 * c4d.d2r)
    print(qb.angles * c4d.r2d)
    # [135  0  0]


def euler_setters():
    c4d.cprint("euler setters", "y")
    qb = c4d.quatbody(theta=10 * c4d.d2r)
    qb.phi = 20 * c4d.d2r
    print(qb.angles * c4d.r2d)
    # [20  10  0]
    qb.psi = 45 * c4d.d2r
    print(qb.angles * c4d.r2d)
    # [20  10  45]


def anglerates():
    c4d.cprint("angle rates", "y")
    qb = c4d.quatbody(q=30 * c4d.d2r)
    print(qb.ang_rates * c4d.r2d)
    # [0  30  0]


def RB():
    c4d.cprint("RB", "y")
    qb = c4d.quatbody(theta=30 * c4d.d2r)
    v_body = [np.sqrt(3), 0, 1]
    print(qb.RB @ v_body)
    # [2  0  0]


def BR():
    c4d.cprint("BR", "y")
    qb = c4d.quatbody(psi=45 * c4d.d2r)
    v_inertial = [1, 0, 0]
    print(qb.BR @ v_inertial)
    # [0.707  -0.707  0]


def inteqm():
    c4d.cprint("inteqm - half roll", "y")

    dt = 0.001
    drone = c4d.quatbody()
    drone.I = drone_I

    for ti in np.arange(0, 1, dt):
        torque = [0.1, 0, 0] if ti < 0.5 else [-0.1, 0, 0]
        drone.inteqm(np.zeros(3), torque, dt)
        drone.store(ti)

    _, ax = plt.subplots(2, 1, gridspec_kw={"hspace": 0.5})
    drone.plot("p", ax=ax[0])
    ax[0].set(xlabel="")
    drone.plot("qx", ax=ax[1], filename=c4d.j(savedir, "inteqm_halfroll"))
    plt.show(block=True)


def data():
    c4d.cprint("data", "y")
    qb = c4d.quatbody()
    for t in [0, 1, 2]:
        qb.psi = t * 10 * c4d.d2r
        qb.store(t)
    print(qb.data("psi", c4d.r2d))
    # (array([0, 1, 2]), array([0, 10, 20]))


def plot():
    c4d.cprint("plot", "y")

    dt = 0.01
    drone = c4d.quatbody(r=90 * c4d.d2r)
    drone.I = drone_I

    for ti in np.arange(0, 1, dt):
        drone.inteqm(np.zeros(3), np.zeros(3), dt)
        drone.store(ti)

    drone.plot("psi", filename=c4d.j(savedir, "plot_yaw.png"))
    plt.show(block=True)


def gimbal_lock():
    # quatbody vs rigidbody in a flip about a tilted axis:
    # the euler angles kinematics of the rigidbody are singular at theta = 90 deg.
    c4d.cprint("gimbal lock - quatbody vs rigidbody", "y")

    dt = 0.001
    qb = c4d.quatbody(phi=0.3, q=2 * np.pi)
    rb = c4d.rigidbody(phi=0.3, q=2 * np.pi)
    qb.I = rb.I = drone_I

    for ti in np.arange(0, 1, dt):
        qb.store(ti)
        rb.store(ti)
        qb.inteqm(np.zeros(3), np.zeros(3), dt)
        rb.inteqm(np.zeros(3), np.zeros(3), dt)

    print("quatbody final angles: ", qb.angles * c4d.r2d)
    # [17.19  0  0]  (back to the initial attitude)
    print("rigidbody final angles:", rb.angles * c4d.r2d)


if __name__ == "__main__":

    # intro()
    izz()
    # quat()
    # angles()
    # euler_setters()
    # anglerates()
    # RB()
    # BR()
    # inteqm()
    # data()
    # plot()
    # gimbal_lock()
