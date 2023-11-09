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
import numpy as np
import control_system as mcontrol_system 
import engine as mengine 
import aerodynamics as maerodynamics
import c4dynamics as c4d
from c4dynamics.utils.params import * 

dt = 5e-3 
vm = 30




def dof6sim(xtgt = 6500, tauseeker = 0.01, tauctrl = dt):

    #
    # define objects 
    ##
    missile = c4d.rigidbody()
    target  = c4d.datapoint(x = xtgt, y = 1000, z = -3000, vx = -250, vy = 0, vz = 0)
    seeker = c4d.seekers.lineofsight(dt, tau1 = 0.01, tau2 = tauseeker, ideal = False)
    ctrl   = mcontrol_system.control_system(tauctrl)
    eng    = mengine.engine()
    aero   = maerodynamics.aerodynamics()


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


    return missile, target, md, tfinal, (np.asarray(delta_data), np.asarray(omegaf_data), np.asarray(acc_data)
            , np.asarray(aoa_data), np.asanyarray(moments_data))

