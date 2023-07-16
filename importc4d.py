
import sys, os, importlib
sys.path.append(os.path.join(os.getcwd(), '..'))

# 
# load C4dynamics
## 
import C4dynamics as c4d

prefix = 'C4dynamics'
matching_modules = [module_name for module_name in sys.modules if module_name.startswith(prefix)]
for module_name in matching_modules:
    # print(module_name)
    del sys.modules[module_name]

# importlib.reload(c4d)
import C4dynamics as c4d

from C4dynamics.params import * 


