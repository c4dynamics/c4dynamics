'''

`c4dynamics` provides sensor models to simulate real world applications.   
The models include the functionality and the errors model 
of electro-optic, lasers, and electro-magnetic devices. 


.. list-table:: 
  :header-rows: 0

  * - :class:`seeker <c4dynamics.sensors.seeker.seeker>`
    - Direction detector
  * - :class:`radar <c4dynamics.sensors.radar.radar>`
    - Range-direction detector




'''
#
# i think maybe to include also detectors in this module
# and rename it to something like perception \ source \ input 
# measures \ 
# 

import sys 
sys.path.append('.')

from c4dynamics.sensors.radar import radar
from c4dynamics.sensors.lineofsight import lineofsight 
from c4dynamics.sensors.seeker import seeker


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



if __name__ == "__main__":

  # import doctest, contextlib, os
  # from c4dynamics import IgnoreOutputChecker, cprint
  
  # # Register the custom OutputChecker
  # doctest.OutputChecker = IgnoreOutputChecker

  # tofile = False 
  # optionflags = doctest.FAIL_FAST

  # if tofile: 
  #   with open(os.path.join('tests', '_out', 'output.txt'), 'w') as f:
  #     with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
  #       result = doctest.testmod(optionflags = optionflags) 
  # else: 
  #   result = doctest.testmod(optionflags = optionflags)

  # if result.failed == 0:
  #   cprint(os.path.basename(__file__) + ": all tests passed!", 'g')
  # else:
  #   print(f"{result.failed}")

  from c4dynamics import rundoctests
  rundoctests(sys.modules[__name__])


