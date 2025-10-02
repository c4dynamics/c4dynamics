# 
# utils __init__
##

# from . import plottools 
# from . import gen_gif

import sys
sys.path.append('.')
vi = sys.version_info

if vi.minor <= 7:
    from c4dynamics.utils.images_loader import * 

# from . import const
# from . import math



if __name__ == "__main__":

  from c4dynamics import rundoctests
  rundoctests(sys.modules[__name__])




