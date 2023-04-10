# 
# see military handbook for missile flight simulation ch.12 simulation synthesis (205)
## 
from scipy.integrate import solve_ivp 
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

from math import isnan 


from matplotlib import pyplot as plt
# This is a bit of magic to make matplotlib figures appear inline in the notebook
# rather than in a new window.
# %matplotlib inline
plt.rcParams['figure.figsize'] = (5.0, 4.0) # set default size of plots
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'
# plt.rcParams['text.usetex'] = True

# Some more magic so that the notebook will reload external python modules;
# see http://stackoverflow.com/questions/1907993/autoreload-of-modules-in-ipython
# %load_ext autoreload
# %autoreload 2

output = 1

# 
# plt.show() plots all the figures present in the state machine. Calling it only at the end of 
#       the script, ensures that all previously created figures are plotted.
# Now you need to make sure that each plot indeed is created in a different figure. That can be 
#       achieved using plt.figure(fignumber) where fignumber is a number starting at index 1.
#

for xtgt in range(4000, 10000, 1000):

    t = 0
    dt = 5e-3
    tf = 10 # 10 # 60

    #
    # define objects 
    ##
    missile = c4d.rigidbody()
    target = c4d.datapoint(x = xtgt, y = 1000, z = -3000
                            , vx = -250, vy = 0, vz = 0)
    seeker = c4d.seekers.lineofsight(dt, tau1 = 0.01, tau2 = 0.01)
    ctrl = mcontrol_system.control_system(dt)
    eng = mengine.engine()
    aero = maerodynamics.aerodynamics()
    # aero_fm = np.zeros(6)


    #
    # input 
    ## 
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
    missile.theta = np.arctan(-ucl[2] / np.sqrt(ucl[0]**2 + ucl[1]**2))
    missile.phi = 0
    u, v, w = missile.BI() @ missile.vel()
    vc = np.array([0, 0, 0])
    # v_data = np.array([u, v, w])

    alpha = 0
    beta = 0
    alpha_total = 0
    # alpha_total_data = alpha_total
    # prp_data = np.array([0, 0])

    h = -missile.z   # missile altitude above sea level, m

    while t <= tf and h >= 0 and vc[0] >= 0:

        #
        # atmospheric calculations    
        ##
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
        wf = seeker.measure(rTM, vTM) # filtered los vector 
        
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
        # missile dynamics 
        ##
        
        
        #
        # aerodynamics forces 
        ##    
        cL, cD = aero.f_coef(alpha_total)
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
        cM, cN = aero.m_coef(alpha, beta, d_pitch, d_yaw 
                            , missile.xcm, Q, missile.V(), fAb[1], fAb[2]
                            , missile.q, missile.r)
        
        
        mA = np.array([0                     # aerodynamic moemnt in roll
                    , Q * cM * aero.s * aero.d         # aerodynamic moment in pitch
                    , Q * cN * aero.s * aero.d])       # aerodynamic moment in yaw 

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
        
        missile.m -= thref * dt / eng.Isp        
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
        
        h = -missile.z   # missile altitude above sea level, m
        

    tfinal = t
    md = np.linalg.norm(target.pos() - missile.pos())
    print('miss: %.2f, flight time: %.1f' % (md, tfinal))

    if output == 0: # do nothing
        pass 
    elif output == 1: # print to file 
        with open('c4dout.txt', 'at') as f:
            f.write('target range: %.0f \n' % np.sqrt(target.x0**2 + target.y0**2 + target.z0**2))
            f.write('miss distance: %.2f \n' % md)
            f.write('--------------------\n')
            f.write('%10s %10s %10s %10s %10s %10s %10s \n' % ('time', 'ax-missile', 'ay-missile', 'az-missile', 'ax-target', 'ay-target', 'az-target'))
        #     f.write('%10.1f %10.1f %10.1f %10.1f %10.1f %10.1f \n' % (missile._data[1:, 7], missile._data[1:, 8] 
        #                                                               , missile._data[1:, 9], target._data[1:, 7]
        #                                                               , target._data[1:, 8], target._data[1:, 9]))
            np.savetxt(f, (np.array([missile._data[1:, 0], missile._data[1:, 7], missile._data[1:, 8] 
                            , missile._data[1:, 9], target._data[1:, 7]
                            , target._data[1:, 8], target._data[1:, 9]]).T)
                    , '%10.2f')
            f.write('--------------------\n')
            f.write('--------------------\n')
            f.write('\n')
            f.write('\n')



    elif output == 2: # plot figures 
        fig = plt.figure()
        plt.plot(missile._data[1:, 2], missile._data[1:, 1], 'k', linewidth = 2, label = 'missile')
        plt.plot(target._data[1:, 2], target._data[1:, 1], 'r', linewidth = 2, label = 'target')
        plt.title('top view')
        plt.xlabel('crossrange')
        plt.ylabel('downrange')
        plt.grid()
        plt.legend()
        fig.tight_layout()
        plt.show()

        fig = plt.figure()
        plt.plot(missile._data[1:, 1], missile._data[1:, 3], 'k', linewidth = 2, label = 'missile')
        plt.plot(target._data[1:, 1], target._data[1:, 3], 'r', linewidth = 2, label = 'target')
        plt.title('side view')
        plt.xlabel('downrange')
        plt.ylabel('altitude')
        plt.gca().invert_yaxis()
        plt.grid()
        plt.legend()
        fig.tight_layout()
        plt.show()


        missile.draw('theta')

        target.draw('vx')
        target.draw('vy')



        # gif_tools.make_plot(missile, target, 'D:\\gh_repo\\C4dynamics\\examples\\New folder')

        fig = plt.figure()
        ax = fig.gca(projection = '3d')
        ax.invert_zaxis()

        plt.plot(missile._data[1:, 1], missile._data[1:, 2], missile._data[1:, 3] 
                , 'k', linewidth = 2, label = 'missile')
        plt.plot(target._data[1:, 1], target._data[1:, 2], target._data[1:, 3]
                , 'r', linewidth = 2, label = 'target')
            
        
        
    
    
    
    
    
    
    
    
    
    