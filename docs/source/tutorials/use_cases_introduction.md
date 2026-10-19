# Use Cases — Introduction

The introduction page of the Use Cases section of the c4dynamics documentation, where it appears
in the sidebar as "Introduction" (and "More…").
https://c4dynamics.github.io/c4dynamics/programs/index.html

This is the corpus copy of `programs/index.rst`: the same text, without the page's layout markup.

## What the use cases have in common

The use cases of c4dynamics span different systems:
a quadcopter, a missile, a ballistic object, a car, and a laboratory helicopter.
They run different algorithms:
PID and model predictive control, Kalman filters, proportional navigation,
and neural network control.
Yet they are all built the same way.

### One representation

Every system is described in state space.
A state vector $X$ holds the variables that define the system at a given moment,
the equations of motion describe how it evolves, $\dot{X} = f(X, u)$,
and the sensors measure a function of it, $z = h(X)$.

In c4dynamics, the state vector is an object.
A `state` object, or one of its library forms (`datapoint`, `rigidbody`, `pixelpoint`),
has the same interface for any system:
`X` to get and set the state vector,
`store` and `data` to record and retrieve its history,
and `plot` to view it.

### One loop

Each use case follows the same loop:

1. **State**: define the state object of the system.
2. **Dynamics**: propagate the state by the equations of motion.
3. **Algorithm**: estimate the state from the measurements, and compute the control command.
4. **Action**: apply the command, store the state, and repeat.

The structure repeats. Only the physics changes.

### The switch

Because the interface stays the same, moving from one system to another
means replacing the physics: the state variables and the equations of motion.
The algorithm, the simulation loop, the storage, and the plots stay intact.

The use cases show this in both directions.
The same quadcopter model is flown by a cascade PID, estimated by an extended Kalman filter,
and controlled by the ArduPilot flight controller.
The same `ekf` object estimates the full state of a quadcopter
and the ballistic coefficient of a falling object,
and its linear sibling, `kalman`, tracks a car in a video.

Pick a use case below, and look for what stays the same.

## The use-case cards on the page

Each card shows a short title, a subtitle, and tags (system · discipline):

1. **Cascade PID** — Quadcopter figure-8 trajectory tracking. Tags: Quadcopter · Control.
   https://c4dynamics.github.io/c4dynamics/programs/pid_cascade/quadcopter_pid.html
2. **EKF State Estimation** — Quadcopter GPS/IMU/MAG sensor fusion. Tags: Quadcopter · Estimation.
   https://c4dynamics.github.io/c4dynamics/programs/ekf_estimation/quad_ekf.html
3. **ArduPilot Simulation** — Quadcopter figure-8 under ArduCopter control.
   Tags: Quadcopter · Control · Software in the loop.
   https://c4dynamics.github.io/c4dynamics/programs/ardupilot_sim/ardupilot_fig8.html
4. **6-DOF** — Proportional navigation guidance. Tags: Missile · Guidance.
   https://c4dynamics.github.io/c4dynamics/programs/pn_guidance/dof6sim.html
5. **Extended Kalman Filter** — Ballistic coefficient estimation. Tags: Ballistic object · Estimation.
   https://c4dynamics.github.io/c4dynamics/programs/ballistic_ekf/ballistic_coefficient.html
6. **Model Predictive Control** — Vehicle steering. Tags: Car · Control.
   https://c4dynamics.github.io/c4dynamics/programs/mpc_steering/mpc_steering.html
7. **YOLO3 Detector & Kalman Filter** — Car tracker. Tags: Car · Computer vision · Estimation.
   https://c4dynamics.github.io/c4dynamics/programs/car_tracker/car_tracker.html
8. **YOLO11 Detector & Kalman Filter** — Car tracker, modern detector refresh.
   Tags: Car · Computer vision · Estimation.
   https://c4dynamics.github.io/c4dynamics/programs/car_tracker_yolo11/car_tracker_yolo11.html
9. **Neural Network Based Controller** — Helicopter learning control.
   Tags: Helicopter · Control · Machine learning.
   https://c4dynamics.github.io/c4dynamics/programs/learning_controller/learning_controller.html
