"""
Ordinary Differential Equations (:mod:`c4dynamics.ode`)
=======================================================

.. currentmodule:: c4dynamics.ode


.. autosummary::
   :toctree: generated/

   eqm3      three equations of translational motion.
   eqm6      six equations of translational and rotational motion.


Examples
--------

For examples, see the various functions.

"""

# from . import _pocketfft, _helper
# # TODO: `numpy.fft.helper`` was deprecated in NumPy 2.0. It should
# # be deleted once downstream libraries move to `numpy.fft`.
# from . import helper
# from ._pocketfft import *
# from ._helper import *

# __all__ = _pocketfft.__all__.copy()
# __all__ += _helper.__all__

# from numpy._pytesttester import PytestTester
# test = PytestTester(__name__)
# del PytestTester

from . import eqm3, eqm6 

