'''

.. list-table:: 
  :header-rows: 0

  * - :class:`State <c4dynamics.states.state.state>`
    - The state class
  * - :mod:`States Library <c4dynamics.states.lib>`
    - A collection of predefined states



'''

# TODO how come the overall title is not word-capatilized and the smaller are.  


import sys 
sys.path.append('.')
from c4dynamics.states.lib import * 




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




