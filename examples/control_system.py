import numpy as np
# import C4dynamics as c4d

class control_system:
    
    Gn = 250 # gain factor relating aoa of ctrl surface to acc cmd per unit dynamic pressure, [rad*Pa/(m/s)^2]
    afp = 0
    afy = 0
    tau = 0.04 



    def __init__(obj, **kwargs):
        obj.__dict__.update(kwargs)



    def update(obj, ab_cmd, Q):
        # p_act1 = -obj.Gp * ab_cmd[2] # actuator pressure for the pitch channel
        # p_act2 = -obj.Gp * ab_cmd[1]    # for the yaw channel
        
        # mH = p_act1 * Ap * Larm # hinge moment applired to control surface by actuator 

        # # mf aerodynamic moment on ctrl surface about hinge line
        # # Q dynamic pressure
        # # af angle of attack of ctrl surfce 
        # # sf aerodynamic referernce area of ctrl surface 
        # # cHaf partial deriv of fin moment coef wrt fin aoa
        # mf = cHaf * af * Q * sf * df 
        
        obj.afp = -1 / obj.tau * obj.afp + 1 / obj.tau * (-obj.Gn * ab_cmd[2] / Q)
        obj.afy = -1 / obj.tau * obj.afy + 1 / obj.tau * ( obj.Gn * ab_cmd[1] / Q)
        
        return obj.afp, obj.afy 