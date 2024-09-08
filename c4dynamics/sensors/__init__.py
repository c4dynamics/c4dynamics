'''

`c4dynamics` provides sensor models to simulate real world applications.   
The models include the functionality and the errors model 
of electro-optic, lasers, and electro-magnetic devices. 

'''

from .radar import radar, dzradar
from .lineofsight import lineofsight 
from .seeker import seeker


# '''
# Sensors (:mod:`c4dynamics.sensors`)
# ===================================

# .. currentmodule:: c4dynamics.sensors


# Sensors
# -------

# .. autosummary::
#    :toctree: generated/

#    # seeker


# Background Material
# -------------------

# Introduction
# ^^^^^^^^^^^^
# '''

# seekers:
#   matter:
# 	    radar
# 	    laser
# 	    optic
#   functionallity:
#       altitude radar 
#       lineofsight seeker
	
# sensors:
# 	imu 
# 		accelerometers
# 		roll gyro
# 		rate gyro
# 	gps
# 	lidar

