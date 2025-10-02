import numpy as np

__doc__ = '''
Globals and conversion constants. 


C4dynamics includes several constants as global quantities 
and conversion units:


Global Constants
----------------

.. data:: pi 

  The ratio of a circle's circumference to its diameter.
  C4dynamics' pi is a simple assignment of numpy.pi: 

  ``pi = 3.1415926535897932384626433...``

  .. rubric:: Reference

  https://en.wikipedia.org/wiki/Pi


.. data:: g_ms2

  Gravity of earth in meter per square second. 

  ``g = 9.80665``

  .. rubric:: Reference

  https://en.wikipedia.org/wiki/Gravity_of_Earth


.. data:: g_fts2

  Gravity of earth in foot per square second. 

  ``g = 32.1740``

  .. rubric:: Reference

  https://en.wikipedia.org/wiki/Gravity_of_Earth



Conversion Constants
--------------------

.. data:: ft2m

  foot to meter.

  ``ft2m = 0.3048``


.. data:: lbft2tokgm2

  pound square foot to kilogram square meter.

  ``lbft2tokgm2 = 4.88243``


.. data:: r2d

  radians to degrees.

  ``r2d = 57.2958``


.. data:: d2r

  degrees to radians.

  ``d2r = 0.0174533``

.. data:: k2ms

  knots to meters per second

  ``k2ms = 0.514444``


'''

import sys 
sys.path.append('.')


#  global quantities 
pi       = np.pi
g_ms2    = 9.80665  # m/s^2 
g_fts2   = 32.1740  # ft/s^2

#  conversion variables 
ft2m        = 0.3048        # 1             # 
lbft2tokgm2 = 4.88243       # 47.8803 to include gravity        # 1      
r2d         = 180 / np.pi 
d2r         = np.pi / 180 
kmh2ms      = 1000 / 3600 
k2ms        = 1852 / 3600   # knots to meter per second



if __name__ == "__main__":

  from c4dynamics import rundoctests
  rundoctests(sys.modules[__name__])



