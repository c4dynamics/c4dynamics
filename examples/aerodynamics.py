import numpy as np

class aerodynamics():
  
    cD0 = 0.8
    cLa = 39
    cMa = cNb = -170 
    cMd = cNd = 250
    cMqcMadot = cNrcNbdot = -13000
 
    k    = 0.0305
    
    s    = 0.0127
    d    = 0.127
    xref = 1.35
    
        
    def f_coef(obj, alpha_total):
        
        # lift and drag
        cL = obj.cLa * alpha_total
        cD = obj.cD0 + obj.k * cL**2
        
        return cL, cD


    def m_coef(obj, alpha, beta
                    , d_pitch, d_yaw, xcm 
                    , Q, v, fAby, fAbz, q, r):
        # 
        # pitch and yaw moments 
        ## 
        
        # yb, zb normal force aero coefficient 
        cNy = fAby / Q / obj.s
        cNz = fAbz / Q / obj.s

        cMref = obj.cMa * alpha + obj.cMd * d_pitch
        cNref = obj.cNb * beta  + obj.cNd * d_yaw

        # to center of mass
        cM = cMref - cNz * (xcm - obj.xref) / obj.d + obj.d / (2 * v) * obj.cMqcMadot * q
        cN = cNref - cNy * (xcm - obj.xref) / obj.d + obj.d / (2 * v) * obj.cNrcNbdot * r
      
        return cM, cN


