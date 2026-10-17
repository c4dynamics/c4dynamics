Use Cases
=========

.. raw:: html

   <style>

   .uc-grid{
       display:flex;
       flex-direction:column;
       gap:18px;
       margin:20px 0 30px 0;
   }

   .uc-card{
       display:flex;
       align-items:center;
       gap:18px;
       width:100%;
       background:var(--pst-color-surface);
       border-radius:12px;
       padding:14px 18px;
       text-decoration:none !important;
       color:var(--pst-color-text-base);
       border:1px solid var(--pst-color-border);
       box-shadow:0 6px 14px rgba(0,0,0,0.08);
       transition:all 0.18s ease;
       overflow:hidden;
   }

   .uc-card:hover{
       transform:translateY(-4px);
       box-shadow:0 16px 34px rgba(0,0,0,0.18);
       border-color:#2962ff;
   }

   .uc-img{
       width:120px;
       height:70px;
       object-fit:cover;
       border-radius:6px;
       flex-shrink:0;
       background:#f4f6f8;
   }

   .uc-text{
       display:flex;
       flex-direction:column;
       justify-content:center;
       min-width:0;
   }

   .uc-text h3{
       margin:0 0 4px 0;
       font-size:17px;
       font-weight:bold;
       color:#2962ff;
   }

   .uc-text p{
       margin:0;
       font-size:14px;
       font-weight:bold;
       color:var(--pst-color-text-base);
   }

   .uc-text .uc-tags{
       margin-top:4px;
       font-size:12px;
       font-weight:normal;
       color:var(--pst-color-text-muted);
   }

   @media (max-width:520px){
       .uc-img{ width:84px; height:56px; }
   }

   </style>


The use cases of c4dynamics span different systems:
a quadcopter, a missile, a ballistic object, a car, and a laboratory helicopter.
They run different algorithms:
PID and model predictive control, Kalman filters, proportional navigation,
and neural network control.
Yet they are all built the same way.


**One representation**

Every system is described in state space.
A state vector :math:`X` holds the variables that define the system at a given moment,
the equations of motion describe how it evolves, :math:`\dot{X} = f(X, u)`,
and the sensors measure a function of it, :math:`z = h(X)`.

In c4dynamics, the state vector is an object.
A :class:`state <c4dynamics.states.state.state>` object, or one of its library forms
(:class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`,
:class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`,
:class:`pixelpoint <c4dynamics.states.lib.pixelpoint.pixelpoint>`),
has the same interface for any system:
:attr:`X <c4dynamics.states.state.state.X>` to get and set the state vector,
:meth:`store <c4dynamics.states.state.state.store>` and
:meth:`data <c4dynamics.states.state.state.data>` to record and retrieve its history,
and :meth:`plot <c4dynamics.states.state.state.plot>` to view it.


**One loop**

Each use case follows the same loop:

1. **State**: define the state object of the system.
2. **Dynamics**: propagate the state by the equations of motion.
3. **Algorithm**: estimate the state from the measurements, and compute the control command.
4. **Action**: apply the command, store the state, and repeat.

The structure repeats. Only the physics changes.


**The switch**

Because the interface stays the same, moving from one system to another
means replacing the physics: the state variables and the equations of motion.
The algorithm, the simulation loop, the storage, and the plots stay intact.

The use cases show this in both directions.
The same quadcopter model is flown by a cascade PID, estimated by an extended Kalman filter,
and controlled by the ArduPilot flight controller.
The same :class:`ekf <c4dynamics.filters.ekf.ekf>` object estimates the full state of a quadcopter
and the ballistic coefficient of a falling object,
and its linear sibling, :class:`kalman <c4dynamics.filters.kalman.kalman>`,
tracks a car in a video.

Pick a use case below, and look for what stays the same.


.. raw:: html

    <div class="uc-grid">

    <a href="pid_cascade/quadcopter_pid.html" class="uc-card">
        <img src="../_static/fig8_quad.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>Cascade PID</h3>
            <p>Quadcopter figure-8 trajectory tracking</p>
            <span class="uc-tags">Quadcopter · Control</span>
        </div>
    </a>

    <a href="ekf_estimation/quad_ekf.html" class="uc-card">
        <img src="../_static/quad_ekf_flightpath.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>EKF State Estimation</h3>
            <p>Quadcopter GPS/IMU/MAG sensor fusion</p>
            <span class="uc-tags">Quadcopter · Estimation</span>
        </div>
    </a>

    <a href="ardupilot_sim/ardupilot_fig8.html" class="uc-card">
        <img src="../_static/ardupilot_architecture.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>ArduPilot Simulation</h3>
            <p>Quadcopter figure-8 under ArduCopter control</p>
            <span class="uc-tags">Quadcopter · Control · Software in the loop</span>
        </div>
    </a>

    <a href="pn_guidance/dof6sim.html" class="uc-card">
        <img src="../_static/missdistance.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>6-DOF</h3>
            <p>Proportional navigation guidance</p>
            <span class="uc-tags">Missile · Guidance</span>
        </div>
    </a>

    <a href="ballistic_ekf/ballistic_coefficient.html" class="uc-card">
        <img src="../_static/ballistic_trajectory.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>Extended Kalman Filter</h3>
            <p>Ballistic coefficient estimation</p>
            <span class="uc-tags">Ballistic object · Estimation</span>
        </div>
    </a>

    <a href="mpc_steering/mpc_steering.html" class="uc-card">
        <img src="../_static/mpc_diagram_thumbnail.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>Model Predictive Control</h3>
            <p>Vehicle steering</p>
            <span class="uc-tags">Car · Control</span>
        </div>
    </a>

    <a href="car_tracker/car_tracker.html" class="uc-card">
        <img src="../_static/drifting_car_snapshot.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>YOLO3 Detector & Kalman Filter</h3>
            <p>Car tracker</p>
            <span class="uc-tags">Car · Computer vision · Estimation</span>
        </div>
    </a>

    <a href="car_tracker_yolo11/car_tracker_yolo11.html" class="uc-card">
        <img src="../_static/drifting_car_yolo11_snapshot.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>YOLO11 Detector & Kalman Filter</h3>
            <p>Car tracker, modern detector refresh</p>
            <span class="uc-tags">Car · Computer vision · Estimation</span>
        </div>
    </a>

    <a href="learning_controller/learning_controller.html" class="uc-card">
        <img src="../_static/helicopter.png" class="uc-img" alt="">
        <div class="uc-text">
            <h3>Neural Network Based Controller</h3>
            <p>Helicopter learning control</p>
            <span class="uc-tags">Helicopter · Control · Machine learning</span>
        </div>
    </a>

    </div>


.. toctree::
  :hidden:
  :maxdepth: 0

  pn_guidance/dof6sim.ipynb
  ballistic_ekf/ballistic_coefficient.ipynb
  mpc_steering/mpc_steering.ipynb
  car_tracker/car_tracker.ipynb
  car_tracker_yolo11/car_tracker_yolo11.ipynb
  learning_controller/learning_controller.ipynb
