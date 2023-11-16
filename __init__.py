#
# c4dynamics __init__
##

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

# from . import utils
from .utils import params 
from .utils.rotmat import *
from .utils.gen_gif import gen_gif
from .utils.cprint import print

#
# modules 
## 
from .src.main.py.body.datapoint import datapoint 
from .src.main.py.body.rigidbody import rigidbody 

from .src.main.py import seekers
# from .src.main.py import path_planning 
from .src.main.py import filters
from .src.main.py import detectors


