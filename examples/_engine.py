import numpy as np

class engine():
    # sec
    times = np.array([0, .01, .04, .05, .08, .1, .2, .3, .6, 1, 1.5, 2.5, 3.5, 3.8, 4, 4.1, 4.3, 4.5, 4.7, 4.9, 5.2, 5.6])
    # Newton
    thrust = np.array([0, 450, 17800, 23100, 21300, 20000, 18200, 17000, 15000, 13800, 13300, 13800, 14700, 14300, 12900, 11000, 7000, 4500, 2900, 1500, 650, 0])
    
    # tbo = 5.6       # t burnout 
    pref = 101314   # reference ambient pressure
    Ae = .011       # exit area of rocket nozzle 
    Isp = 2224      # specific impulse 
    
    
    
    def update(obj, t, pa):
        # return thrust force at time t and pressure pa 
        # pa pressure at altitude h 
        thrust_ref = np.interp(t, obj.times, obj.thrust) # thrust at time t 
        thrust_atm = thrust_ref + (obj.pref - pa) * obj.Ae # correction for atmosphere conditions 
        return thrust_atm, thrust_ref
        
    