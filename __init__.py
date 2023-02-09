"""
C4dynamics
=====
Provides
  1. data-points and rigid-body objects 
  2. Fast algorithmic operations over objects and systems 
  3. State of the art algorithms for developing systems
How to use the documentation
----------------------------
Documentation is currently availble through examples, readme pages, and inline comments.
 iewing documentation using IPython

-----------------------------
"""

# import sys
# import warnings

# # make all python files in this folder available when loading pri
# from os.path import dirname, basename, isfile, join
# import glob
# modules = glob.glob(join(dirname(__file__), '*.py'))
# __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]

'''
# modules - classes 
# body objects
#   data point
#   rigid body
# seekers 
#   radar 
#   laser
#   camera 
# sensors  
#   imu
#   gps
#   leedar
# filters 
#   low pass 
#   luenberger 
#   kalman
# path planning
#   pn 
# classifiers
#   knn
# 
#   '''

# make c_datapoint, c_rigidbody, rotmat belong to pri rather than their modules:
# from .datapoint import c_datapoint 
# from .rigidbody import c_rigidbody
from .rotmat import *
from .general import * 
# from .arrays import c_array
# from .cnvrt import *

from . import params 
from . import tools

#
# modules 
## 
# import sys, os
# sys.path.append(os.getcwd() + '/../body')
# sys.path.append(os.getcwd() + '/../filters')
# sys.path.append(os.getcwd() + '/../seekers')
# sys.path.append(os.getcwd() + '/../seekers')


from .body.datapoint import datapoint 
from .body.rigidbody import rigidbody 
# from .body.sixdof import sixdof

# from .filters import *
from . import seekers
from . import path_planning 

# from . import linalg
# __all__.extend(['linalg', 'fft', 'random', 'ctypeslib', 'ma'])
from . import filters
# __all__.extend(['filters'])


