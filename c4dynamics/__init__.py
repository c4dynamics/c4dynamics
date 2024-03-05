'''

C4dynamics
==========

C4dynamics Provides
  1. Datapoint objects and sensors for algorithms development.  
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
# routines and utils must come first otherwise the modules cannot be initalized.  
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
from .utils.plottools import plotdefaults
from .utils import tictoc
from .utils.tictoc import tic, toc 

#
# body objects 
## 
from .body.datapoint import datapoint, fdatapoint, create
from .body.rigidbody import rigidbody 


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

