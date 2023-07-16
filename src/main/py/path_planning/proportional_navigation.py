import numpy as np

class proportional_navigation():    

    flyby = False
    rr = False
         
    def __init__(obj, N, ts):
        obj.N = N
        obj.ts = ts

    def PN(obj, v, lambda_dot):
        return obj.N * v * lambda_dot
    
    def tgo():
        # TBD 
        pass 
    
    def set_flyby(obj, rnew, r):
        
        rdot = (np.abs(rnew) - np.abs(r)) / obj.ts
        
        if obj.rr == False:
            if rdot < 0:
                obj.rr = True
        else:
            if rdot >= 0:
                obj.flyby = True
                
                
                   