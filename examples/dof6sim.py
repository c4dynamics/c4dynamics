# 
# updates may 2023
# fix large md
# ideal seeker? no change 
# ideal engine?
# ideal cas?
# ideal rocket. 
# ideal tgt. imporved 
# vm = 300 no 30. worse. 
# missile higher than target - imporved. 
##


# 
# see military handbook for missile flight simulation ch.12 simulation synthesis (205)
## 
import time
tic = time.time()

# from scipy.integrate import solve_ivp 
import numpy as np

import sys, os, importlib
sys.path.append(os.path.join(os.getcwd(), '..'))

# 
# load C4dynamics
## 
import C4dynamics as c4d
importlib.reload(c4d)
from C4dynamics.params import * 

##

import control_system as mcontrol_system 
importlib.reload(mcontrol_system)

import engine as mengine 
importlib.reload(mengine)

import aerodynamics as maerodynamics
importlib.reload(maerodynamics)

# from C4dynamics.tools import gif_tools

# from math import isnan 


from matplotlib import pyplot as plt
# This is a bit of magic to make matplotlib figures appear inline in the notebook
# rather than in a new window.
# %matplotlib inline
plt.rcParams['figure.figsize'] = (5.0, 4.0) # set default size of plots
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'
plt.ion()
plt.close('all')

# plt.rcParams['text.usetex'] = True

# Some more magic so that the notebook will reload external python modules;
# see http://stackoverflow.com/questions/1907993/autoreload-of-modules-in-ipython
# %load_ext autoreload
# %autoreload 2

# 
# plt.show() plots all the figures present in the state machine. Calling it only at the end of 
#       the script, ensures that all previously created figures are plotted.
# Now you need to make sure that each plot indeed is created in a different figure. That can be 
#       achieved using plt.figure(fignumber) where fignumber is a number starting at index 1.
#


dt = 5e-3

#
# input 
## 
vm = 30



#
# define objects 
##
missile = c4d.rigidbody()
target  = c4d.datapoint(x = 4000, y = 1000, z = -3000, vx = -250, vy = 0, vz = 0)
seeker = c4d.seekers.lineofsight(dt, tau1 = 0.01, tau2 = 0.01, ideal = False)
ctrl   = mcontrol_system.control_system(dt)
eng    = mengine.engine()
aero   = maerodynamics.aerodynamics()
# aero_fm = np.zeros(6)






# 
# atmospheric properties up to 2000m
##
# pressure = 101325 # pressure pascals
# rho      = 1.225       # density kg/m^3
# vs       = 340.29       # speed of sound m/s

# 
# parameters for first example
##
# mach        = 0.8

missile.m   = m0   = 85         # initial mass, kg
mbo         = 57                # burnout mass, kg 
missile.xcm = xcm0 = 1.55       # nose to center of mass length, m
xcmbo       = 1.35              # nose to cm after burnout, m
missile.iyy = missile.izz = i0 = 61      
ibo         = 47                # iyy izz at burnout 



#
# init
#
# The initial missile pointing direction and angular rates are calculated in the fire-control block. 
# For the example simulation, a simple algorithm is employed in which the missile is
# pointed directly at the target at the instant of launch, and missile angular rates at launch are assumed to be negligible.
# The unit vector uR in the direction from the missile to the target is calculated by normalizing the range vector R.
## 
rTM           = target.pos() - missile.pos()
rTMnorm        = np.linalg.norm(rTM)
ucl           = rTM / rTMnorm # center line unit vector 
missile.vx, missile.vy, missile.vz = vm * ucl 
missile.psi   = np.arctan(ucl[1] / ucl[0])
missile.theta = np.arctan(-ucl[2] / np.sqrt(ucl[0]**2 + ucl[1]**2))
missile.phi   = 0
u, v, w       = missile.BI() @ missile.vel()
vc            = np.array([0, 0, 0])
# these copy of md calc actually didnt change a bit in the results
# bf = True # before flyby
# rr = False # negative range rate flag

alpha       = 0
beta        = 0
alpha_total = 0
# alpha_total_data = alpha_total
# prp_data = np.array([0, 0])

# h = missile.z   # missile altitude above sea level, m
d_pitch  = 0
d_yaw    = 0

ab_cmd = np.zeros(3)



delta_data   = []
omegaf_data  = []
acc_data     = []
aoa_data     = []
moments_data = []


t  = 0
tf = 100 # 10 # 60

h = -missile.z # missile altitude above sea level 


while t <= tf and h >= 0 and vc[0] >= 0: # bf:

    #
    # atmospheric calculations    
    ##
    
    
    pressure, rho, vs = maerodynamics.aerodynamics.alt2atmo(h)
    
        
    mach = missile.V() / vs # mach number 
    Q = 1 / 2 * rho * missile.V()**2 # dynamic pressure 
    
    # 
    # relative position
    ##
    vTM = target.vel() - missile.vel() # missile-target relative velocity 
    rTM = target.pos() - missile.pos() # relative position 
    
    # # 
    # # miss distance 
    # ##       
    # rdot = (np.linalg.norm(rTM) - rTMnorm) / dt
    # if rr == False:
    #     if rdot < 0:
    #         rr = True;     # first time of negative range rate
    # else:
    #     if rdot >= 0:
    #         bf = False     # non-negative range rate after period of negative range rate
            
    #
    # relative velcoity
    ##
    rTMnorm = np.linalg.norm(rTM) # for next round 
    uR     = rTM / rTMnorm # unit range vector 
    vc     = -uR * vTM # closing velocity 
    
        


    # 
    # seeker 
    ## 
    wf = seeker.measure(rTM, vTM) # filtered los vector 
    omegaf_data.append([wf[1], wf[2]]) 
    
    # 
    # guidance and control 
    ##
    if t >= 0.5:
        Gs       = 4 * missile.V()
        acmd     = Gs * np.cross(wf, ucl)
        ab_cmd   = missile.BI() @ acmd 
        afp, afy = ctrl.update(ab_cmd, Q)
        d_pitch  = afp - alpha 
        d_yaw    = afy - beta  
    # delta_data = np.vstack((delta_data, np.array([d_pitch, d_yaw])))
    
    acc_data.append(ab_cmd)
    delta_data.append([d_pitch, d_yaw])

    # 
    # missile dynamics 
    ##
    
    
    #
    # aerodynamics forces 
    ##    
    cL, cD = aero.f_coef(mach, alpha_total)
    L = Q * aero.s * cL
    D = Q * aero.s * cD
    
    A = D * np.cos(alpha_total) - L * np.sin(alpha_total) # aero axial force 
    N = D * np.sin(alpha_total) + L * np.cos(alpha_total) # aero normal force 
    
    fAb = np.array([ -A
                    , N * (-v / np.sqrt(v**2 + w**2))
                    , N * (-w / np.sqrt(v**2 + w**2))])
    fAe = missile.IB() @ fAb
   
    # 
    # aerodynamics moments 
    ##
    cM, cN = aero.m_coef(mach, alpha, beta, d_pitch, d_yaw 
                         , missile.xcm, Q, missile.V(), fAb[1], fAb[2]
                         , missile.q, missile.r)
    
    
    mA = np.array([0                     # aerodynamic moemnt in roll
                , Q * cM * aero.s * aero.d         # aerodynamic moment in pitch
                , Q * cN * aero.s * aero.d])       # aerodynamic moment in yaw 

    moments_data.append(mA)
    # 
    # propulsion 
    ##
    thrust, thref = eng.update(t, pressure)
    fPb = np.array([thrust, 0, 0])# 
    # fPb = np.array([0, 0, 0])# 
    # prp_data = np.r_[prp_data, prp_data] doesnt work. bullshit. 
    # prp_data = np.vstack((prp_data, (thrust, thref))) 
    fPe = missile.IB() @ fPb

    # 
    # gravity
    ## 
    fGe = np.array([0, 0, missile.m * g])

    # 
    # total forces
    ##      
    forces = np.array([fAe[0] + fPe[0] + fGe[0]
                        , fAe[1] + fPe[1] + fGe[1]
                        , fAe[2] + fPe[2] + fGe[2]])
    
    # 
    # missile motion integration
    ##
    missile.run(dt, forces, mA)
    u, v, w = missile.BI() @ np.array([missile.vx, missile.vy, missile.vz])
    
    # 
    # target dynmaics 
    ##
    target.run(dt, np.array([0, 0, 0]))

    # 
    # update  
    ##
    t += dt
    missile.store(t)
    target.store(t)

    # v_data = np.vstack((v_data, np.array([u, v, w]))).copy()
    # aero_fm = np.vstack((aero_fm, np.concatenate((fAb, mA)))).copy()
    
    missile.m  -= thref * dt / eng.Isp        
    missile.xcm = xcm0 - (xcm0 - xcmbo) * (m0 - missile.m) / (m0 - mbo)
    missile.izz = missile.iyy = i0 - (i0 - ibo) * (m0 - missile.m) / (m0 - mbo)

    alpha = np.arctan2(w, u)
    beta  = np.arctan2(-v, u)
    
    uvm = missile.vel() / missile.V()
    ucl = np.array([np.cos(missile.theta) * np.cos(missile.psi)
                    , np.cos(missile.theta) * np.sin(missile.psi)
                    , np.sin(-missile.theta)])
    alpha_total = np.arccos(uvm @ ucl)
    # alpha_total_data = np.r_[alpha_total_data, alpha_total]# np.vstack((aero_fm, np.concatenate((fAb, mA)))).copy()
    aoa_data.append([alpha, beta, alpha_total])
    
    
    h = -missile.z

   




# tfinal = t
# md = np.linalg.norm(target.pos() - missile.pos())
vTM = target.vel() - missile.vel() # missile-target relative velocity 
uvTM = vTM / np.linalg.norm(vTM)

rTM = target.pos() - missile.pos() # relative position 

md = np.linalg.norm(rTM - np.dot(rTM, uvTM) * uvTM)
tfinal = t - np.dot(rTM, uvTM) / np.linalg.norm(vTM)


print('miss: %.2f, flight time: %.1f' % (md, tfinal))

 
    
delta_data = np.asarray(delta_data)
omegaf_data = np.asarray(omegaf_data)
acc_data = np.asarray(acc_data)
aoa_data = np.asarray(aoa_data)
moments_data = np.asanyarray(moments_data)



fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_x(), missile.get_y(), 'k', linewidth = 2, label = 'missile')
ax1.plot(target.get_x(), target.get_y(), 'r', linewidth = 2, label = 'target')
ax1.set_title('top view')
ax1.set(xlabel = 'downrange', ylabel = 'crossrange')
ax1.set_xlim(-500, 4500)
ax1.set_ylim(-1500, 1500)
ax1.grid()
ax1.legend()
ax1.invert_yaxis()

ax2.plot(missile.get_x(), -missile.get_z(), 'k', linewidth = 2, label = 'missile')
ax2.plot(target.get_x(), -target.get_z(), 'r', linewidth = 2, label = 'target')
ax2.set_title('side view')
ax2.set(xlabel = 'downrange', ylabel = 'altitude')
ax2.grid()
ax2.legend()
ax2.set_xlim(-500, 4500)
ax2.set_ylim(0, 4000)

# fig.tight_layout()
# plt.show()


# missile.draw('theta')

# target.draw('vx')
# target.draw('vy')


#
# total velocity 
##
plt.figure()
plt.plot(missile.get_t(), np.sqrt(missile.get_vx()**2 + missile.get_vy()**2 + missile.get_vz()**2))
plt.title('Vm')
plt.xlabel('t')
plt.ylabel('m/s')
plt.grid()
plt.legend()

# 
# omega los 
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_t(), omegaf_data[:, 0] * c4d.r2d, 'k', linewidth = 2)
ax1.set_title('$omega_p$')
ax1.grid()
ax1.set_xlim(0, 10)
ax1.set_ylim(-10, 10)
ax1.set(xlabel = 'time', ylabel = '')

ax2.plot(missile.get_t(), omegaf_data[:, 1] * c4d.r2d, 'k', linewidth = 2)
ax2.set_title('$omega_y$')
ax2.grid()
ax2.set_xlim(0, 10)
ax2.set_ylim(-10, 10)
ax2.set(xlabel = 'time', ylabel = '')

plt.subplots_adjust(hspace=0.5)


# 
# wing deflctions
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_t(), delta_data[:, 0] * c4d.r2d, 'k', linewidth = 2)
ax1.set_title('\delta p')
ax1.grid()
ax2.plot(missile.get_t(), delta_data[:, 1] * c4d.r2d, 'k', linewidth = 2)
ax2.set_title('\delta y')
ax2.grid()

# 
# body-frame acceleration cmds
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_t(), acc_data[:, 2] / c4d.g, 'k', linewidth = 2)
ax1.set_title('aczb')
ax1.grid()
ax2.plot(missile.get_t(), acc_data[:, 1] / c4d.g, 'k', linewidth = 2)
ax2.set_title('acyb')
ax2.grid()



# 
# angles of attack
##
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
fig.tight_layout()

ax1.plot(missile.get_t(), aoa_data[:, 0] * c4d.r2d, 'k', linewidth = 2)
ax1.set_title('alpha')
ax1.grid()
ax2.plot(missile.get_t(), aoa_data[:, 1] * c4d.r2d, 'k', linewidth = 2)
ax2.set_title('beta')
ax2.grid()
ax3.plot(missile.get_t(), aoa_data[:, 2] * c4d.r2d, 'k', linewidth = 2)
ax3.set_title('total')
ax3.grid()


# 
# body-frame acceleration cmds
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_t(), moments_data[:, 1], 'k', linewidth = 2)
ax1.set_title('pitch moment')
ax1.grid()
ax2.plot(missile.get_t(), moments_data[:, 2], 'k', linewidth = 2)
ax2.set_title('yaw moment')
ax2.grid()

# 
# euler angles
##
missile.draw('psi')
missile.draw('theta')
missile.draw('phi')

# 
# body rates 
##
missile.draw('r')
missile.draw('q')
missile.draw('p')
 




# # 
# # 3d plot
# ##

# fig = plt.figure()
# ax = plt.subplot(projection = '3d')
# # ax.invert_zaxis()

# plt.plot(missile._data[1:, 1], missile._data[1:, 2], missile._data[1:, 3] 
#         , 'k', linewidth = 2, label = 'missile')
# plt.plot(target._data[1:, 1], target._data[1:, 2], target._data[1:, 3]
#         , 'r', linewidth = 2, label = 'target')
    
    
    
   
print(time.time() - tic)

plt.show(block = True)
# plt.close('all')
    

    
    
    
    
    