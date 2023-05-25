import numpy as np

class aerodynamics():
      
    
    mach_table = np.array([0, 0.8, 1.14, 1.75, 2.5, 3.5]) 
    #
    # tables of mach number
    ##
    cD0_table  = np.array([0.8, 0.8, 1.2, 1.15, 1.05, 0.94])
    cLa_table  = np.array([38,  39,  56,  55,   40,   33])
    cMa_table  = np.array([-160, -170, -185, -235, -190, -150]) 
    cMd_table  = np.array([180, 250, 230, 130, 80, 45])
    cMqcMadot_table = np.array([-6000, -13000, -16000, -13500, -10000, -6000]) 
    k_table    = np.array([0.0255, 0.0305, 0.0361, 0.0441, 0.0540, 0.0665])
    
    alt_table = np.array([0, 2000, 4000, 6000])
    #
    # tables of altitude 
    ##
    pressure_table = np.array([101325, 79501, 61660, 47217])
    density_table  = np.array([1.225, 1.0066, 0.81935, 0.66011])
    speed_of_sound_table = np.array([340.29, 332.53, 324.59, 316.45])
    
    
    s    = 0.0127
    d    = 0.127
    xref = 1.35
    
        
    def f_coef(obj, mach, alpha_total):
        
        # idx = aerodynamics.m2idx(mach)
        # cLa = obj.cLa_table[idx]
        # cD0 = obj.cD0_table[idx]
        # k   = obj.k_table[idx]
        
        cLa = np.interp(mach, obj.mach_table, obj.cLa_table)
        cD0 = np.interp(mach, obj.mach_table, obj.cD0_table)
        k = np.interp(mach, obj.mach_table, obj.k_table)
                
        # lift and drag
        cL = cLa * alpha_total
        cD = cD0 + k * cL**2
        
        return cL, cD


    def m_coef(obj, mach, alpha, beta
                    , d_pitch, d_yaw, xcm 
                    , Q, v, fAby, fAbz, q, r):
        
        # idx = aerodynamics.m2idx(mach)
        # cMa = obj.cMa_table[idx]
        # cNb = obj.cMa_table[idx]
        # cMd = obj.cMd_table[idx]
        # cNd = obj.cMd_table[idx]
        # cMqcMadot = obj.cMqcMadot_table[idx]
        # cNrcNbdot = obj.cMqcMadot_table[idx]
       
        cNb = cMa = np.interp(mach, obj.mach_table, obj.cMa_table)
        cNd = cMd = np.interp(mach, obj.mach_table, obj.cMd_table)
        cNrcNbdot = cMqcMadot = np.interp(mach, obj.mach_table, obj.cMqcMadot_table)
        
        # 
        # pitch and yaw moments 
        ## 
        
        # yb, zb normal force aero coefficient 
        cNy = fAby / Q / obj.s
        cNz = fAbz / Q / obj.s

        cMref = cMa * alpha + cMd * d_pitch
        cNref = cNb * beta  + cNd * d_yaw

        # to center of mass
        cM = cMref - cNz * (xcm - obj.xref) / obj.d + obj.d / (2 * v) * cMqcMadot * q
        cN = cNref - cNy * (xcm - obj.xref) / obj.d + obj.d / (2 * v) * cNrcNbdot * r
      
        return cM, cN

    @staticmethod
    def m2idx(m):
        return np.argmin(np.abs(aerodynamics.mach_table - m))
    
    @staticmethod
    def alt2atmo(alt):
        p = np.interp(alt, aerodynamics.alt_table, aerodynamics.pressure_table)
        rho = np.interp(alt, aerodynamics.alt_table, aerodynamics.density_table)
        vs = np.interp(alt, aerodynamics.alt_table, aerodynamics.speed_of_sound_table)
        return p, rho, vs