import sys, os 
sys.path.append('.')


from c4dynamics.eqm.derivs import * 
from c4dynamics.eqm.integrate import * 




if __name__ == "__main__":

  import doctest, contextlib
  from c4dynamics import IgnoreOutputChecker, cprint
  
  # Register the custom OutputChecker
  doctest.OutputChecker = IgnoreOutputChecker

  tofile = False 
  optionflags = doctest.FAIL_FAST

  if tofile: 
    with open(os.path.join('tests', '_out', 'output.txt'), 'w') as f:
      with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        result = doctest.testmod(optionflags = optionflags) 
  else: 
    result = doctest.testmod(optionflags = optionflags)

  if result.failed == 0:
    cprint(os.path.basename(__file__) + ": all tests passed!", 'g')
  else:
    print(f"{result.failed}")




