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
  Kalman filter, asytmptotic observer (Luenberger), and lowpass filter.
eqm 
  Runge Kutta solvers for integrating the equations of motion on the datapoint and rigidbody objects. 
rotmat
  Rotation matrices and rotational operations. 
'''

#
# NOTE
# routines and utils must come first otherwise 
# the modules cannot be initalized.  
##

#
# routines 
## 
# from .src.main import py
from . import eqm 
# from .src.main.py.eqm import eqm  
from . import rotmat
# from .src.main.py.rotmat import *

#
# utils
##
from .utils.const import * 
from .utils.math import * 
from .utils.gen_gif import gif
from .utils.cprint import cprint
from .utils.plottools import plotdefaults, _figdef
from .utils import tictoc
from .utils.tictoc import tic, toc 
from .utils._struct import struct 
from .utils.idx2keys import idx2keys 
from . import datasets 


# 
# body objects 
## 
from .states.state import state
from .states.lib.pixelpoint import pixelpoint
from .states.lib.datapoint import datapoint, create
from .states.lib.rigidbody import rigidbody 

#
# sensors
## 
from . import sensors
from . import filters
from . import detectors




#
# version
##
__version__ = '1.2.00'


#
# some convinient mirroring 
## 
import os 
j = os.path.join



#
# warnings 
##
import warnings 
class c4warn(UserWarning): pass

# customize the warning messages:  
YELLOW = "\033[93m"  
RESET  = "\033[0m"   # Reset color to default
# Override showwarning to globally apply custom formatting
def show_warning(message, category, filename, lineno, file = None, line = None):
  

  if issubclass(category, c4warn):
    # Apply formatting for c4warn warnings

    # FIXME suppressing is absolutely not working. 
    message = str(message) + (f"\nTo suppress c4dynamics' warnings, run: import warnings, import c4dynamics as c4d, warnings.simplefilter('ignore', c4d.c4warn)\n")

    print(f"{YELLOW}{message}{RESET} (File: {filename}, Line: {lineno})")
  else:
    # For other warnings, use the default behavior
    print(f"{category.__name__}: {message} (File: {filename}, Line: {lineno})")

warnings.showwarning = show_warning










