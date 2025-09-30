# spacecraft dyanmics and control 

# Rotating Reference Frame
# ^^^^^^^^^^^^^^^^^^^^^^^^

# A vector resolved in a given reference frame is said to be 
# **expressed** in that frame (sometimes said **referred to**). 

# The rate of change of a vector, as viewed by an observer fixed to and moving 
# with a given reference frame, 
# is said to be **relative to** or **with respect to** that reference frame. 

# It's important to note here that the rate of change of a vector must be 
# relative to an inertial reference frame, 
# but it can be expressed in any reference frame. 


import sys 
sys.path.append('.')

from c4dynamics.rotmat.rotmat import rotx, roty, rotz, dcm321, dcm321euler
from c4dynamics.rotmat.animate import animate  



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







