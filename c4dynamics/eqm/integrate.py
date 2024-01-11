from .derivs import eqm3, eqm6 
import numpy as np


def int3(pt, forces, dt, derivs_out = False):
  ''' 
  A step integration of the equations of translational motion.  
  
  This method makes a numerical integration using the 
  fourth-order Runge-Kutta method.

  The integrated derivatives are of three dimensional translational motion as 
  given by 
  :func:`eqm6 <eqm6>`. 


  The result is an integrated state in a single interval of time where the 
  size of the step is determined by the parameter `dt`.

  
  Parameters
  ----------
  pt : c4dynamics.datapoint
      The datapoint which state vector is to be integrated. 
  forces : numpy.array or list
      An external forces array acting on the body.  
  dt : float
      Time step for integration.
  derivs_out : boolen, optional
      If true, returns the last three derivatives as an estimation for 
      the acceleration of the datapoint. 
      

  Returns
  -------
  X : numpy.float64
      An integrated state. 
  dxdt4 : numpy.float64, optional
      The last three derivatives of the equations of motion.
      These derivatives can use as an estimation for the acceleration of the datapoint. 
      Returned if `derivs_out` is set to `True`.



  Algorithm 
  ---------
  
  The integration steps follow the Runge-Kutta method:

  1. Compute k1 = f(ti, yi)

  2. Compute k2 = f(ti + dt / 2, yi + dt * k1 / 2)

  3. Compute k3 = f(ti + dt / 2, yi + dt * k2 / 2)

  4. Compute k4 = f(ti + dt, yi + dt * k3)

  5. Update yi = yi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
  

  
  Examples
  --------

  Run the equations of motion on a  
  mass in a free fall:
  
  .. code:: 

    >>> h0 = 100
    >>> pt = c4d.datapoint(z = h0)
    >>> dt = 1e-2
    >>> t = np.arange(0, 10, dt) 
    >>> for ti in t:
    ...    if pt.z < 0: break
    ...    pt.X = int3(pt, [0, 0, -c4d.g_ms2], dt) 
    ...    pt.store(ti)
    >>> pt.draw('z')
  
  .. figure:: /_static/figures/int3_z.png

  Compare `c4dynamics.eqm.int3` with an analytic soultion
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. code::

    >>> z = h0 - .5 * c4d.g_ms2 * t**2 
    >>> fig = plt.subplots()
    >>> plt.plot(t[z > 0], z[z > 0], 'm', linewidth = 3, label = 'analytic')
    >>> ptz = pt.get_data('z')
    >>> plt.plot(pt.get_data('t')[ptz > 0], ptz[ptz > 0], 'c', linewidth = 1, label = 'c4dynamics.eqm.int3')
      
  .. figure:: /_static/figures/int3_vs_analytic.png

  
  '''
  

  x0 = X = pt.X

  
  # step 1
  dxdt1 = eqm3(pt, forces)
  # pt.update(x0 + dt / 2 * dxdt1)
  X = x0 + dt / 2 * dxdt1
  
  # step 2 
  dxdt2 = eqm3(pt, forces)
  # pt.update(x0 + dt / 2 * dxdt2)
  X = x0 + dt / 2 * dxdt2
  
  # step 3 
  dxdt3 = eqm3(pt, forces)
  # pt.update(x0 + dt * dxdt3)
  X = x0 + dt * dxdt3
  dxdt3 += dxdt2 
  
  # step 4
  dxdt4 = eqm3(pt, forces)

  # 
  # pt.update(np.concatenate((x0 + dt / 6 * (dxdt1 + dxdt4 + 2 * dxdt3), dxdt4[-3:]), axis = 0))
  X = x0 + dt / 6 * (dxdt1 + dxdt4 + 2 * dxdt3)
  # pt.ax, pt.ay, pt.az = dxdt4[-3:]


  if not derivs_out: 
    return X
  
  # return also the derivatives. 
  return X, dxdt4[-3:]
  
  ##


# 

def int6(rb, forces, moments, dt, derivs_out = False): 
  '''
  A step integration of the equations of motion.  
    
  This method makes a numerical integration using the 
  fourth-order Runge-Kutta method.

  The integrated derivatives are of three dimensional translational motion as 
  given by
  :func:`eqm6 <eqm6>`.


  The result is an integrated state in a single interval of time where the 
  size of the step is determined by the parameter `dt`.

  
  Parameters
  ----------
  pt : c4dynamics.datapoint
      The datapoint which state vector is to be integrated. 
  forces : numpy.array or list
      An external forces array acting on the body.  
  dt : float
      Time step for integration.
  derivs_out : boolen, optional
      If true, returns the last three derivatives as an estimation for 
      the acceleration of the datapoint. 
      

  Returns
  -------
  X : numpy.float64
      An integrated state. 
  dxdt4 : numpy.float64, optional
      The last six derivatives of the equations of motion.
      These derivatives can use as an estimation for the
      translational and angular acceleration of the datapoint. 
      Returned if `derivs_out` is set to `True`.


  Algorithm 
  ---------
  
  The integration steps follow the Runge-Kutta method:

  1. Compute k1 = f(ti, yi)

  2. Compute k2 = f(ti + dt / 2, yi + dt * k1 / 2)

  3. Compute k3 = f(ti + dt / 2, yi + dt * k2 / 2)

  4. Compute k4 = f(ti + dt, yi + dt * k3)

  5. Update yi = yi + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
  

  Examples
  --------

  In the following example, the equations of motion of a 
  cylinderical body are integrated by using the 
  :func:`int6 <c4dynamics.eqm.int6>`. 

  The results are compared to the results of the same equations 
  integrated by using `scipy.odeint`.

  1. `c4dynamics.eqm.int6`

  .. code:: 

    >>> # settings and initial conditions 
    >>> dt = .5e-3 
    >>> t = np.arange(0, 10, dt)
    >>> theta0 =  80 * c4d.d2r       # deg 
    >>> q0     =  0 * c4d.d2r        # deg to sec
    >>> Iyy    =  .4                  # kg * m^2 
    >>> length =  1                  # meter 
    >>> mass   =  0.5                # kg 
    >>> # define the cylinderical-rigidbody object 
    >>> rb = c4d.rigidbody(theta = theta0, q = q0, iyy = Iyy, mass = mass)
    >>> # integrate the equations of motion 
    >>> for ti in t: 
    ...   tau_g = -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(rb.theta)
    ...   rb.X = c4d.eqm.int6(rb, np.zeros(3), [0, tau_g, 0], dt)
    ...   rb.store(ti)
    >>> rb.draw('theta')
  
  .. figure:: /_static/figures/eqm6_theta.png


  2. `scipy.odeint`

  .. code:: 

    >>> def pend(y, t):
    ...  theta, omega = y
    ...  dydt = [omega, -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(theta) / Iyy]
    ...  return dydt
    >>> sol = odeint(pend, [theta0, q0], t)
    >>> fig = plt.subplots()
    >>> plt.plot(rb.get_data('t'), rb.get_data('theta') * c4d.r2d, 'c', linewidth = 2, label = 'c4dynamics.eqm.int6')
    >>> plt.plot(t, sol[:, 0] * c4d.r2d, 'm', linewidth = 2, label = 'scipy.odeint')


  .. figure:: /_static/figures/int6_scipy_vs_c4d.png

  Note - Differences Between Scipy and C4dynamics Integration 
  -----------------------------------------------------------
  
  The difference in results derive from the method of delivering the 
  forces and moments.
  scipy.odeint gets as input the function that caluclates the derivatives, 
  where the forces and moments are included in it: 
  
  `dydt = [omega, -rb.mass * c4d.g_ms2 * length / 2 * c4d.cos(theta) / Iyy]`

  This way, the forces and moments are recalculated for each step of 
  the integration.

  c4dynamics.eqm.int6 on the other hand, gets the vectors of forces and moments
  only once when the function is called and therefore refer to them as constant 
  for the four steps of integration. 

  When external factors may vary quickly over time and a high level of
  accuracy is required, using other methods, like scipy.odeint, is recommanded. 
  If computational resources are available, a decrement of the step-size 
  may be a workaround to achieve high accuracy results.

  Results for `dt = 1msec`
  ^^^^^^^^^^^^^^^^^^^^^^^^

  .. figure:: /_static/figures/int6_scipy_vs_c4d_dt001.png


  '''

  # x, y, z, vx, vy, vz, phi, theta, psi, p, q, r 
  x0 = X = rb.X
      
  # print('t: ' + str(t) + ', f: ' + str(forces) + ', m: ' + str(moments))

  # step 1
  h1 = eqm6(rb, forces, moments)
  # yt = 
  # rb.update(np.concatenate((yt[0 : 6], np.zeros(3), yt[6 : 12], np.zeros(3)), axis = 0))
  X = x0 + dt / 2 * h1 
  
  # print('dydx: ' + str(dydx))
  # print('yt: ' + str(yt))

  # step 2 
  h2 = eqm6(rb, forces, moments)
  # yt = 
  # rb.update(np.concatenate((yt[0 : 6], np.zeros(3), yt[6 : 12], np.zeros(3)), axis = 0))
  X = x0 + dt / 2 * h2 
  
  # print('dyt: ' + str(dyt))
  # print('yt: ' + str(yt))
  
  # step 3 
  h3 = eqm6(rb, forces, moments)
  # yt =
  # rb.update(np.concatenate((yt[0 : 6], np.zeros(3), yt[6 : 12], np.zeros(3)), axis = 0))
  X = x0 + dt * h3 
  
  # print('dym: ' + str(dym))
  # print('yt: ' + str(yt))
  
  # print('dym: ' + str(dym))
  
  # step 4
  h4 = eqm6(rb, forces, moments)
  # print('dyt: ' + str(dyt))
  # print('yout: ' + str(yout))

  if (h1[10] - h2[10]) != 0:
    print(np.linalg.norm((h2[10] - h3[10]) / (h1[10] - h2[10])))

  # rb.update(np.concatenate((yout[0 : 6], dyt[3 : 6], yout[6 : 12], dyt[9 : 12]), axis = 0))
  
  X = x0 + dt / 6 * (h1 + 2 * h2 + 2 * h3 + h4) 
    
  # # rb.ax, rb.ay, rb.az = dxdt4[3 : 6] # dyt[-3:]
  # # rb.p_dot, rb.q_dot, rb.r_dot = dxdt4[9 : 12] # dyt[-3:]
  # return h4[3 : 6] + h4[9 : 12]
  # ##




  if not derivs_out: 
    return X
  
  # return also the derivatives. 
  return X, h4[3 : 6] + h4[9 : 12]
  
  ##

