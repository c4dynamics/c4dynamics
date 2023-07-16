from enum import Enum

class filtertype(Enum):
    ex_kalman   = 1  # extended kalman filter 
    luenberger  = 2  # luenberger observer 
    lowpass     = 3  # low pass filter 
    