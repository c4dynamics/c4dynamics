import numpy as np

class kalman:
    # x = 0 # state vector. 
    # P = 0   # covariance matrix
    # Q = 0   # process noise matrix
    # H = 0   # measurement matrix 
    # R = 0   # measurement noise matrix 

    def __init__(obj, x0, P0, A, H, Q, R, b = None): 
    
        obj.x = x0
        obj.P = P0  # Initial error covariance matrix
        obj.A = A    # State transition matrix
        obj.H = H    # Measurement matrix
        obj.Q = Q    # Process noise covariance matrix
        obj.R = R    # Measurement noise covariance matrix
        
        obj.b = b    
      
    def predict(obj, u = None):
        #
        # Predict step
        ##
        obj.x = obj.A @ obj.x

        if u is not None:
            obj.x += obj.B @ u

        obj.P = obj.A @ obj.P @ obj.A.T + obj.Q
        
 
    def correct(obj, z):
        # 
        # Correct step
        ## 
        K = obj.P @ obj.H.T @ np.linalg.inv(obj.H @ obj.P @ obj.H.T + obj.R)
        obj.x += K @ (z - obj.H @ obj.x)
        obj.P = obj.P - K @ obj.H @ obj.P
