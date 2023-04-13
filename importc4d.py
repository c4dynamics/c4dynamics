
import sys, os, importlib
sys.path.append(os.path.join(os.getcwd(), '..'))

# 
# load C4dynamics
## 
import C4dynamics as c4d
importlib.reload(c4d)
from C4dynamics.params import * 