# c4dynamics Documentation Map and Use Cases

This page exists to ground the documentation assistant on the vocabulary and structure of the
c4dynamics documentation site (https://c4dynamics.github.io/c4dynamics/). It is not a tutorial —
it is a reference index for locating the right page.

## Documentation sections

The c4dynamics documentation is organized into five sections:

- **Concepts**: theoretical explanations of the state-space modeling principles used in
  c4dynamics — State Objects, Kinematics, Rigid Body Transformations, Sensors, Filters, and the
  Reinforcement Learning Environment.
- **Tutorials**: interactive, step-by-step guides for learning the core workflow —
  the Setup Guide and the Introduction Guide (Interactive Guide to State Space and State Objects
  Modeling).
- **Use Cases**: complete, runnable example notebooks that apply c4dynamics to a real problem
  end-to-end. This is a specific, distinguished term in this documentation — it refers to exactly
  the 8 notebooks listed below, not to API pages, not to concepts pages, and not to generic
  "usage examples" inside a class's docstring.
- **API Reference**: per-class and per-method technical documentation (signatures, parameters,
  return values) for every public class and function in c4dynamics.
- **Installation** and **Getting Started**: setup instructions and a first overview of the
  framework.

## The 8 Use Cases

When a user asks to "explore a use case", "see an example", "show me a notebook", or similar,
answer with one or more of these — never substitute an unrelated API reference page.

1. **Quadcopter Cascade PID — Figure-8 Trajectory Tracking**
   (`programs/pid_cascade/quadcopter_pid`)
   A three-loop cascade PID simulation of a quadcopter tracking a figure-8 (∞) trajectory: models
   the quadcopter dynamics, builds the control hierarchy, and runs the closed-loop simulation.
   https://c4dynamics.github.io/c4dynamics/programs/pid_cascade/quadcopter_pid.html

2. **Quadcopter EKF — State Estimation for Figure-8 Trajectory Tracking**
   (`programs/ekf_estimation/quad_ekf`)
   An estimation-control companion to the Cascade-PID use case: the quadcopter no longer has
   access to its true state, and instead an Extended Kalman Filter reconstructs the full state
   vector from noisy GPS and IMU measurements, closing the control loop on that estimate.
   https://c4dynamics.github.io/c4dynamics/programs/ekf_estimation/quad_ekf.html

3. **Proportional Navigation Guidance — 6 Degrees of Freedom Simulation**
   (`programs/pn_guidance/dof6sim`)
   A 6-DOF simulation of a guided aircraft, modeling its dynamics, aerodynamics, and control
   system under proportional navigation guidance.
   https://c4dynamics.github.io/c4dynamics/programs/pn_guidance/dof6sim.html

4. **Ballistic Coefficient Estimation — Extended Kalman Filter**
   (`programs/ballistic_ekf/ballistic_coefficient`)
   Estimates the ballistic coefficient of a target in free fall, tracked by a noisy altimeter
   radar, using an Extended Kalman Filter.
   https://c4dynamics.github.io/c4dynamics/programs/ballistic_ekf/ballistic_coefficient.html

5. **Vehicle Steering — Model Predictive Control**
   (`programs/mpc_steering/mpc_steering`)
   Implements a Model Predictive Controller for vehicle steering: a simplified model tracks a
   straight reference line by solving a constrained finite-horizon quadratic program at every
   time step, simulated in closed loop with c4dynamics.
   https://c4dynamics.github.io/c4dynamics/programs/mpc_steering/mpc_steering.html

6. **Car Tracker — YOLOv3 Detector and Kalman Filter**
   (`programs/car_tracker/car_tracker`)
   Enhances object tracking by pairing a YOLOv3 object detector with a Kalman filter, smoothing
   jittery bounding boxes and bridging momentary occlusions or missed detections.
   https://c4dynamics.github.io/c4dynamics/programs/car_tracker/car_tracker.html

7. **Car Tracker — YOLO11 Detector and Kalman Filter**
   (`programs/car_tracker_yolo11/car_tracker_yolo11`)
   A modern-detector refresh of the YOLOv3 Car Tracker use case: the same estimation problem,
   dynamic model, and Kalman filtering strategy, but with the detector swapped for YOLO11.
   https://c4dynamics.github.io/c4dynamics/programs/car_tracker_yolo11/car_tracker_yolo11.html

8. **Neural Learning Control for Online Uncertain Dynamics Estimation**
   (`programs/learning_controller/learning_controller`)
   A reusable framework for prototyping neural learning controllers that estimate model
   uncertainty online, built around an environment abstraction (a 2-DOF helicopter in the
   example) that separates the controller from the plant.
   https://c4dynamics.github.io/c4dynamics/programs/learning_controller/learning_controller.html

## Answering "show me a use case" style questions

- If the user hasn't specified a topic, briefly list several (or all) of the 8 use cases above by
  name so they can pick one — do not jump into an unrelated API page.
- If the user's interest suggests a specific domain (e.g. "computer vision" → car trackers,
  "control" → PID/MPC/learning controller, "estimation"/"filtering" → EKF use cases, "guidance" →
  proportional navigation), recommend the matching use case(s) from the list above.
- Once a use case is chosen, ground further answers in that notebook's actual content (state
  objects, sensors, filters, and controller logic it defines) rather than inventing steps.
