'''

C4DYNAMICS
==========

c4dynamics provides
  1. State objects as fundamental data structure for dynamic systems.  
  2. Internal systems and 3rd party integrated libraries.
  3. Fast algorithmic operations over objects and systems. 


How to use the documentation
----------------------------
Documentation is currently availble through examples, 
readme pages, and inline comments.


Available subpackages
---------------------
sensors
  Models of EO and EM sensors. 
detectors
  Objects detection models to computer vision manipulations.
filters
  Kalman and lowpass filters.
eqm 
  Runge Kutta solvers for integrating the equations of motion on the datapoint and rigidbody objects. 
rotmat
  Rotation matrices and rotational operations. 
'''


import os 
import doctest
import warnings 



# 
# body objects 
## 
from .states.state import state
from .states.lib.pixelpoint import pixelpoint
from .states.lib.datapoint import datapoint, create
from . import rotmat
# rotmat is required to import rigidbody:  
from .states.lib.rigidbody import rigidbody # rotmat is required to import rigidbody.  

#
# routines 
## 
from . import eqm 

#
# utils
##
from .utils.const import * 
from .utils.math import * 
from .utils.gen_gif import gif
from .utils.cprint import cprint
from .utils.plottools import plotdefaults, _figdef, _legdef
from .utils import tictoc
from .utils.tictoc import tic, toc 
from .utils._struct import struct 
from .utils.idx2keys import idx2keys 
from . import datasets 


#
# sensors
## 
from . import sensors
from . import filters
from . import detectors




#
# version
##
__version__ = '2.0.00'


#
# some convinient mirroring 
## 
j = os.path.join



#
# warnings 
##
class c4warn(UserWarning): pass

# customize the warning messages:  
YELLOW = "\033[93m"  
RESET  = "\033[0m"   # Reset color to default
# Override showwarning to globally apply custom formatting
def show_warning(message, category, filename, lineno, file = None, line = None):

  if issubclass(category, c4warn):
    # Apply formatting for c4warn warnings

    # FIXME suppressing is absolutely not working. 
    message1 = str(message) + f"\n"
    message2 = f"To suppress c4dynamics' warnings, run: import warnings, import c4dynamics as c4d, warnings.simplefilter('ignore', c4d.c4warn)\n"

    print(f"\n{YELLOW}{message1}{RESET}{message2} (File: {filename}, Line: {lineno})")
  else:
    # For other warnings, use the default behavior
    print(f"{category.__name__}: {message} (File: {filename}, Line: {lineno})")

warnings.showwarning = show_warning



class IgnoreOutputChecker(doctest.OutputChecker):
  from typing import Union

  IGNORE_OUTPUT = doctest.register_optionflag("IGNORE_OUTPUT") # 2048
  NUMPY_FORMAT = doctest.register_optionflag("NUMPY_FORMAT")  # 4096 

  def check_output(self, want, got, optionflags): 

    # If the IGNORE_OUTPUT flag is set, always return True
    if optionflags & self.IGNORE_OUTPUT:
      return True

    # If NUMPY_FORMAT flag is set, compare NumPy arrays with formatting tolerance
    if optionflags & self.NUMPY_FORMAT:
      want = self._convert_to_array(want)
      got = self._convert_to_array(got)
      if want is not None and got is not None:

        abs_tol = 1e-3
        rel_tol = 1e-3 

        if False: 

          # Calculate element-wise absolute and relative differences
          # if diff < abs (for small values) OR diff/want < rel (for large values)
          np.abs(want - got) < abs_tol
          np.abs((want - got) / np.where(want != 0, want, np.inf)) < rel_tol


        return np.allclose(want, got, atol = abs_tol, rtol = rel_tol)

    # Otherwise, fall back to the original behavior
    return super().check_output(want, got, optionflags) # type: ignore
  

  def _convert_to_array(self, text):

    import re 


    """Attempt to convert text to a NumPy array for comparison."""
    try:

      if ',' not in text:
        text = re.sub(r'\s+', ',', text.strip())

      # Remove extraneous text like 'array(' and closing ')' using regex
      clean_text = re.sub(r'(array\(|\))', '', text).strip()
      # Remove brackets
      clean_text = re.sub(r'[\[\]]', '', clean_text)

      # Convert to NumPy array
      return np.fromstring(clean_text, sep = ',')
    
    except ValueError:
      return None  # Return None if conversion fails


# just find the package root folder: 

def c4dir(dir, addpath = ''):
  # dirname and basename are supplamentary:
  # c:\dropbox\c4dynamics\text.txt
  # dirname: c:\dropbox\c4dynamics
  # basename: text.txt 

  inc4d = os.path.basename(dir) == 'c4dynamics'
  hasc4d = any(f == 'c4dynamics' for f in os.listdir(dir) 
                if os.path.isdir(os.path.join(dir, f)))

  if inc4d and hasc4d: 
    addpath += ''
    return addpath
  
  addpath += '..\\'
  return c4dir(os.path.dirname(dir), addpath)


# 
# TODO BUG FIXME HACK NOTE XXX 
# 
# TODO IMPROVMEMNT
#
# BUG LOGICAL FAILURE PROBABLY COMES WITH XXX
#     Highlights the presence of a bug or an issue.
# FIXME NOT SEVERE BUT A BETTER IDEA IS TO DO SO
#       Indicates that there is a problem or bug that needs to be fixed.
# HACK I KNOW ITS NOT BEST SOLUTION TREAT IF U HAVE SPARE TIME
#      Suggests that a workaround or temporary solution has been implemented and should be revisited.
# NOTE MORE IMPORTANT THAN A CASUAL COMMENT
#      Provides additional information or context about the code.
# XXX TREAT THIS BEFORE OTHERS
#     Used to highlight something that is problematic, needs attention, or should be addressed later.
