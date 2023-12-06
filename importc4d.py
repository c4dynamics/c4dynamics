import sys, os # , importlib
sys.path.append(os.path.join(os.getcwd(), '..'))

# 
# load c4dynamics
## 
import c4dynamics as c4d

prefix = 'c4dynamics'
matching_modules = [module_name for module_name in sys.modules if module_name.startswith(prefix)]
for module_name in matching_modules:
    # print(module_name)
    del sys.modules[module_name]

# importlib.reload(c4d)
import c4dynamics as c4d

from c4dynamics.utils.params import * 
from c4dynamics.utils.tictoc import * 


