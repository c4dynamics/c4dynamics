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
from scipy.integrate import solve_ivp 
import numpy as np

import sys, os, importlib
sys.path.append(os.path.join(os.getcwd(), '..'))

import C4dynamics as c4d
importlib.reload(c4d)

import control_system as mcontrol_system 
importlib.reload(mcontrol_system)

import engine as mengine 
importlib.reload(mengine)

import aerodynamics as maerodynamics
importlib.reload(maerodynamics)


#
# define objects 
##
missile = c4d.rigidbody()
target = c4d.datapoint(x = 4000, y = 1000, z = -3000
                        , vx = -250, vy = 0, vz = 0)
seeker = c4d.seekers.lineofsight(tau1 = 0.01, tau2 = 0.01)
ctrl = mcontrol_system.control_system()
eng = mengine.engine()
aero = maerodynamics.aerodynamics()

t = 0
dt = 5e-3
tf = 60

g = 9.8
# x = np.zeros(12)




# input 
vm = 30


# 
# atmospheric properties up to 2000m
##
pressure = 101325 # pressure pascals
rho = 1.225       # density kg/m^3
vs = 340.29       # speed of sound m/s

# 
# parameters for first example
##
mach = 0.8

missile.m = m0 = 85         # initial mass, kg
mbo = 57                    # burnout mass, kg 
missile.xcm = xcm0 = 1.55   # nose to center of mass length, m
xcmbo = 1.35                # nose to cm after burnout, m
missile.iyy = missile.izz = i0 = 61      
ibo = 47                    # iyy izz at burnout 



#
# init
#
# The initial missile pointing direction and angular rates are calculated in the fire-control block. 
# For the example simulation, a simple algorithm is employed in which the missile is
# pointed directly at the target at the instant of launch, and missile angular rates at launch are assumed to be negligible.
# The unit vector uR in the direction from the missile to the target is calculated by normalizing the range vector R.
## 
rTM = target.pos() - missile.pos()
ucl = rTM / np.linalg.norm(rTM) # center line unit vector 
missile.vx, missile.vy, missile.vz = vm * ucl 
missile.psi = np.arctan(ucl[1] / ucl[0])
missile.theta = np.arctan(-ucl[2] / np.sqrt(ucl[1]**2 + ucl[0]**2))
missile.phi = 0
u, v, w = missile.BI() @ missile.vel()



##
##

# this is wrong:
# ucl = missile.BI() @ np.array([1, 0, 0]) # unit centerline vector

# #
# # atmospheric calculations    
# ##
# h = -missile.z   # missile altitude above sea level, m
# mach = missile.V() / vs # mach number 
# Q = 1 / 2 * rho * missile.V()**2 # dynamic pressure 

# 
# # relative position
# ##
# vTM = target.vel() - missile.vel() # missile-target relative velocity 
# rTM = target.pos() - missile.pos() # relative position 
# uR = rTM / np.linalg.norm(rTM) # unit range vector 
# vc = -uR * vTM # closing velocity 
# ##
# ## 


alpha = 0
beta = 0
alpha_total = 0


def eqm(t, xs, f, m, rb): 
    
    x, y, z, u, v, w, phi, theta, psi, p, q, r = xs

    #
    # translational motion derivatives
    ##
    dx = rb.vx
    dy = rb.vy
    dz = rb.vz

    du = f[0] / rb.m - (q * w - r * v)
    dv = f[1] / rb.m - r * u
    dw = f[2] / rb.m + q * u



    # 
    # euler angles derivatives 
    ## 

    dphi   = (q * np.sin(phi) + r * np.cos(phi)) * np.tan(theta)
    dtheta =  q * np.cos(phi) - r * np.sin(phi)
    dpsi   = (q * np.sin(phi) + r * np.cos(phi)) / np.cos(theta)

    # 
    # angular motion derivatives 
    ## 
    # dp     = (lA - q * r * (izz - iyy)) / ixx
    dp = 0 if rb.ixx == 0 else (m[0] - q * r * (rb.izz - rb.iyy)) / rb.ixx
    dq     = (m[1] - p * r * (rb.ixx - rb.izz)) / rb.iyy
    dr     = (m[2] - p * q * (rb.iyy - rb.ixx)) / rb.izz

    return dx, dy, dz, du, dv, dw, dphi, dtheta, dpsi, dp, dq, dr


while t <= tf:

    #
    # atmospheric calculations    
    ##
    h = -missile.z   # missile altitude above sea level, m
    mach = missile.V() / vs # mach number 
    Q = 1 / 2 * rho * missile.V()**2 # dynamic pressure 
    
    # 
    # relative position
    ##
    vTM = target.vel() - missile.vel() # missile-target relative velocity 
    rTM = target.pos() - missile.pos() # relative position 
    uR = rTM / np.linalg.norm(rTM) # unit range vector 
    vc = -uR * vTM # closing velocity 

    # 
    # seeker 
    ## 
    wf = seeker.measure(rTM, vTM)
    
    # 
    # guidance and control 
    ##
    Gs = 4 * missile.V()
    acmd = Gs * np.cross(wf, ucl)
    ab_cmd = missile.BI() @ acmd 
    afp, afy = ctrl.update(ab_cmd, Q)
    d_pitch = afp - alpha 
    d_yaw = afy - beta  


    #
    # aerodynamics
    ##    
    
    # forces
    cL, cD = aero.f_coef(alpha_total)
    
    L = Q * aero.s * cL
    D = Q * aero.s * cD
    
    A = D * np.cos(alpha_total) - L * np.sin(alpha_total) # aero axial force 
    N = D * np.sin(alpha_total) + L * np.cos(alpha_total) # aero normal force 
    
    fAb = np.array([ -A
                    , N * (-v / np.sqrt(v**2 + w**2))
                    , N * (-w / np.sqrt(v**2 + w**2))])
   
   
    # moments 
    cM, cN = aero.m_coef(alpha, beta, d_pitch, d_yaw 
                         , missile.xcm, Q, v, fAb[1], fAb[2]
                         , missile.q, missile.r)
    
    
    mA = np.array([0                     # aerodynamic moemnt in roll
                , Q * cM * aero.s * aero.d         # aerodynamic moment in pitch
                , Q * cN * aero.s * aero.d])       # aerodynamic moment in yaw 
        



    # 
    # propulsion 
    ##
    thrust, thref = eng.update(t, pressure)
    fPb = np.array([thrust, 0, 0])
    
    
    # 
    # gravity
    ## 
    fGe = np.array([0, 0, missile.m * g])
    fGb = missile.BI() @ fGe 




    # 
    # integration 
    ## 
    forces = np.array([fAb[0] + fPb[0] + fGb[0]
                        , fAb[1] + fPb[1] + fGb[1]
                        , fAb[2] + fPb[2] + fGb[2]])
    
    # x = missile.x, missile.y, missile.z, u, v, w, missile.phi, missile.theta, missile.psi, missile.p, missile.q, missile.r
    # x = solve_ivp(eqm, [t, t + dt], x, args = (forces, mA, missile)).y[:, -1]
    
    # https://www.mathworks.com/matlabcentral/answers/411616-how-to-use-a-for-loop-to-solve-ode
    # Y = [y0 zeros(length(y0), length(tspan))];
    # for i=1:length(tspan)
    #     ti = tspan(i); yi = Y(:,i);
    #     k1 = f(ti, yi);
    #     k2 = f(ti+dt/2, yi+dt*k1/2);
    #     k3 = f(ti+dt/2, yi+dt*k2/2);
    #     k4 = f(ti+dt  , yi+dt*k3);
    #     dy = 1/6*(k1+2*k2+2*k3+k4);
    #     Y(:,i+1) = yi +dy;
    
    # $ runge kuta 
    y = missile.x, missile.y, missile.z, u, v, w, missile.phi, missile.theta, missile.psi, missile.p, missile.q, missile.r
    
    # step 1
    dydx = np.asarray(eqm(0, y, forces, mA, missile))
    yt = y + dt / 2 * dydx 
    
    # step 2 
    dyt = np.asarray(eqm(0, yt, forces, mA, missile))
    yt = y + dt / 2 * dyt 
    
    # step 3 
    dym = np.asarray(eqm(0, yt, forces, mA, missile))
    yt = y + dt * dym 
    dym += dyt 
    
    # step 4
    dyt =  np.asarray(eqm(0, yt, forces, mA, missile))
    yout = y + dt / 6 * (dydx + dyt + 2 * dym)    
    
    # 
    missile.x, missile.y, missile.z, u, v, w, missile.phi, missile.theta, missile.psi, missile.p, missile.q, missile.r = yout 

    # 
    # update  
    ##
    t += dt
    missile.store(t)
    
    
    missile.m -= thref * dt / eng.Isp        
    missile.xcm = xcm0 - (xcm0 - xcmbo) * (m0 - missile.m) / (m0 - mbo)
    missile.izz = missile.iyy = i0 - (i0 - ibo) * (m0 - missile.m) / (m0 - mbo)
        

    missile.vx, missile.vy, missile.vz = missile.BI() @ np.array([u, v, w])

    alpha = np.arctan2(w, u)
    beta  = np.arctan2(-v, u)
    uvm = missile.vel() / missile.V()
    ucl = np.array([np.cos(missile.theta) * np.cos(missile.psi)
                    , np.cos(missile.theta) * np.sin(missile.psi)
                    , np.sin(-missile.theta)])
    alpha_total = np.arccos(uvm @ ucl)
    
    

    
    
missile.draw('x')
missile.draw('top')
missile.draw('z')
    
    
    
    
    
    
    
    
    
    
    
    
    




    
    
    
    
    
    
    