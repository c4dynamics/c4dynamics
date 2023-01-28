import numpy as np
from scipy.integrate import solve_ivp 

import C4dynamics as c4d

class rigidbody(c4d.datapoint):  # 
  """ 
    the rigidbody object is the most basic element in the rotational dynamics domain.
    a rigidbody object is also a datapoint. 
  """
  
  # 
  # euler angles 
  ##
  phi   = 0
  theta = 0
  psi   = 0
  
  # 
  # angular rates 
  ##
  p     = 0
  q     = 0
  r     = 0
  
  # 
  # abgular accelerations
  p_dot = 0
  q_dot = 0
  r_dot = 0
  
  # 
  # initial attitude
  ##
  phi0   = 0
  theta0 = 0
  psi0   = 0
  
  # 
  # body from inertial direction cosine matrix   
  ## 
  dcm = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
  
  # 
  # properties for integration
  ##  
  # _xs = np.zeros((1, 10))   # current state for integration
  _dt = 1e-2

  # 
  # bounded methods 
  ##
  def __init__(obj, **kwargs):
    obj.__dict__.update(kwargs)

    obj.phi0   = obj.phi
    obj.theta0 = obj.theta
    obj.psi0   = obj.psi
    
    obj._xs = [obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r]
   
   
  def IB(obj): 
    # inertial from body dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return np.transpose(c4d.dcm321(obj.phi, obj.theta, obj.psi))
  
  def BI(obj): 
    # body from inertial dcm
    # bound method 
    # Bound methods have been "bound" to an instance, and that instance will be passed as the first argument whenever the method is called.
    return c4d.dcm321(obj.phi, obj.theta, obj.psi)


  def update(obj, x):
    obj.x, obj.y, obj.z, obj.vx, obj.vy, obj.vz, obj.ax, obj.ay, obj.az, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r, obj.p_dot, obj.q_dot, obj.r_dot = x
    
    alpha = np.arctan(w / u)
    beta  = np.arctan(-v / u)
    
    alpha_total = np.arccos()
 
 
  def run(obj, t0, tf):
   
    t = t0
    u, v, w = 100, 1, 1
    while t <= tf:
      
      x = obj.x, obj.y, obj.z, u, v, w, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r
      
      x = solve_ivp(c4d.rigidbody.eqm, [t, t + obj._dt], x, args = (obj, )).y[:, -1]
      
      obj.x, obj.y, obj.z, u, v, w, obj.phi, obj.theta, obj.psi, obj.p, obj.q, obj.r = x
      
      t += obj._dt
      obj.store(t)
                

   
  
 

  @staticmethod
  def eqm(t, xs, rb):    
    
    # 
    # see military handbook for missile flight simulation ch.12 simulation synthesis (205)
    # 
    # state vector xs variables:
    #   0   x
    #   1   y
    #   2   z
    #   3   u
    #   4   v
    #   5   w
    #   6   phi
    #   7   theta
    #   8   psi
    #   9   p
    #   10  q
    #   11  r
    ##
    
    # 
    # parameters for initial example
    ##
    Gn = 250 

    s = 0.0127
    d = 0.127
    mach = 0.8
    
    cD0 = 0.8
    cLa = 39
    cMa = -170 
    cMd = 250
    cMqcMadot = -13000
    
    k = 0.0305
    
    m = 57
    xcm = 1.35
    xref = 1.35
    
    g = 9.8


    ixx = 1
    iyy = izz = 61 

    #
    # calc
    ## 
    
    x, y, z, u, v, w, phi, theta, psi, p, q, r = xs
    
    BI = c4d.dcm321(phi, theta, psi)
    ucl = BI @ [[1], [0], [0]] # is it? 
    ucl = np.array([[np.cos(theta) * np.cos(psi)]
            , [np.cos(theta) * np.sin(psi)] 
            , [np.sin(-theta)]])
    vm = np.transpose(BI) @ [[u], [v], [w]]
    vm_total = np.sqrt(vm[0]**2 + vm[0]**2 + vm[0]**2)
    
    alpha = np.arctan2(w, u)
    beta  = np.arctan2(-v, u)
    uvm = vm / vm_total
    alpha_total = 0# np.arccos(uvm @ ucl)
    
    # 
    # aerodynamic forces
    ##
    
    # atmospheric properties up to 2000m
    h = z
    pressure = 101325 # pressure pascals
    rho = 1.225       # density kg/m^3
    vs = 340.29       # speed of sound m/s
    
    mach = vm_total / vs 
    
    # dynamic pressure
    Q = 1 / 2 * rho * vm_total**2
    
    
    # 
    # guidance and control
    ## 
    # d1, d2, d3, d4 = 0, 0, 0, 0
    acmd_yb, acmd_zb = 0, 0
    dpitch = -Gn * acmd_zb / Q
    dyaw = -Gn * acmd_yb / Q



    
    # lift and drag
    cL = cLa * alpha_total
    L = Q * s * cL 
    
    cD = cD0 + k * cL**2
    D = Q * s * cD
    
    # in body frame
    A = D * np.cos(alpha_total) - L * np.sin(alpha_total)
    N = D * np.sin(alpha_total) + L * np.cos(alpha_total)
    
    fAb = np.array([[-A]
                    , [N * (-v / np.sqrt(v**2 + w**2))]
                    , [N * (-w / np.sqrt(v**2 + w**2))]])

    cNy = fAb[1] / Q / s
    cNz = fAb[2] / Q / s

    # 
    # aerodynamic moments 
    ## 
    
    cNb = cMa
    cNd = cMd 
    # cNr = cMq 
    # cNbdot = cMadot 
    cNrcNbdot = cMqcMadot
    cMref = cMa * alpha + cMd * dpitch
    cNref = cNb * beta  + cNd * dyaw
    
    
    # wrt center of mass
    cM = cMref - cNz * (xcm - xref) / d + d / (2 * v) * cMqcMadot * q
    cN = cNref - cNy * (xcm - xref) / d + d / (2 * v) * cNrcNbdot * r
    
    lA = 0              # aerodynamic moemnt in roll
    mA = Q * cM * s * d # aerodynamic moment in pitch
    nA = Q * cN * s * d # aerodynamic moment in yaw 
    
    
    # 
    # gravity
    ## 
    fGe = [[0], [0], [m * g]]
    fGb = BI @ fGe 

    
    
    #
    # translational motion derivatives
    ##
    dx = vm[0]
    dy = vm[1]
    dz = vm[2]
    
    du = (fAb[0] + fGb[0]) / m - (q * w - r * v)
    dv = (fAb[1] + fGb[1]) / m - r * u
    dw = (fAb[2] + fGb[2]) / m + q * u
    
    
    
    # 
    # euler angles derivatives 
    ## 
    
    dphi   = (q * np.sin(phi) + r * np.cos(phi)) * np.tan(theta)
    dtheta =  q * np.cos(phi) - r * np.sin(phi)
    dpsi   = (q * np.sin(phi) + r * np.cos(phi)) / np.cos(theta)

    # 
    # angular motion derivatives 
    ## 
    dp     = (lA - q * r * (izz - iyy)) / ixx
    dq     = (mA - p * r * (ixx - izz)) / iyy
    dr     = (nA - p * q * (iyy - ixx)) / izz
    
    return dx, dy, dz, du, dv, dw, dphi, dtheta, dpsi, dp, dq, dr
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   




   
   
   
   
   
   
   