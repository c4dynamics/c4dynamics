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


from .radar import radar, dzradar
from .lineofsight import lineofsight 
from .seeker import seeker

