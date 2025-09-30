'''

Pre-defined state objects


.. list-table:: 
  :header-rows: 0

  * - :class:`datapoint <c4dynamics.states.lib.datapoint.datapoint>`
    - A point in space
  * - :class:`rigidbody <c4dynamics.states.lib.rigidbody.rigidbody>`
    - Rigid body object
  * - :class:`pixelpoint <c4dynamics.states.lib.pixelpoint.pixelpoint>`
    - A pixel point in an image

'''

import sys 
sys.path.append('.')





# :class:`pixelspoint <c4dynamics.states.lib.pixelpoint.pixelpoint>` has 
# two types of coordinate :attr:`units <c4dynamics.states.lib.pixelpoint.pixelpoint.units>`: 
# `pixels` (default) and `normalized`. 
# When `normalized` mode is selected, the method 
# :attr:`Xpixels <c4dynamics.states.lib.pixelpoint.pixelpoint.Xpixels>` 
# uses to retrun the state vector in pixel coordinates. 

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





