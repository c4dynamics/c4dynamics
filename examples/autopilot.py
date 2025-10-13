import numpy as np
from scipy.integrate import solve_ivp
from matplotlib import pyplot as plt
import c4dynamics as c4d 

# Example parameters
Kp_az, Ki_az = 1.0, 0.5
Kp_q, Kd_q = 2.0, 0.3
dt = 0.01

# Initialize integral term outside ODE (needs closure)
integral_e_az = 0.0
prev_q_error = 0.0

# ODE function
def two_loop_autopilot(t, X, az_ref):

  global integral_e_az, prev_q_error
  
  az, q = X  # unpack state
  
  # ---- Outer Loop: desired pitch rate ----
  e_az = az_ref - az
  integral_e_az += e_az * dt
  q_des = Kp_az * e_az + Ki_az * integral_e_az
  
  # ---- Inner Loop: actuator/torque control ----
  e_q = q_des - q
  derivative_e_q = (e_q - prev_q_error) / dt
  delta_fin = Kp_q * e_q + Kd_q * derivative_e_q
  prev_q_error = e_q
  
  # ---- Plant dynamics (simplified first-order) ----
  # assuming az_dot ~ actuator input delta_fin, q_dot ~ delta_fin / inertia
  tau_q = delta_fin
  Iyy = 0.1  # example moment of inertia
  
  daz_dt = tau_q        # simplified: vertical accel rate driven by actuator
  dq_dt = tau_q / Iyy   # simplified pitch acceleration
  
  return [daz_dt, dq_dt]



if  False: 
  # Initial state
  autopilot = c4d.state(az = 0, q = 0)
  t_span = (0, 5)  # 5 seconds
  dt = 0.05 
  az_ref = 1.0     # desired vertical acceleration

  for ti in np.arange(t_span[0], t_span[1], dt):

    autopilot.store(ti)

    autopilot.X = solve_ivp(
        fun = two_loop_autopilot,
        t_span = [ti, ti + dt],
        y0 = autopilot.X,
        args = (az_ref,)
    ).y[:, -1]



  autopilot.plot('az', darkmode = False)
  autopilot.plot('q', darkmode = False)
  plt.show()

else: 

  # Initial state
  X0 = [0.0, 0.0]  # az=0, q=0
  t_span = (0, 5)  # 5 seconds
  az_ref = 1.0     # desired vertical acceleration

  sol = solve_ivp(
      fun=lambda t, X: two_loop_autopilot(t, X, az_ref),
      t_span=t_span,
      y0=X0,
      max_step=dt
  )

  # Extract results
  time = sol.t
  az = sol.y[0]
  q = sol.y[1]

  plt.plot(time, az)
  plt.show()

