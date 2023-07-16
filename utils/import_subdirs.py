# import the python files in subdirectories 
# for example
#   filters 
#       |--lowpass
#       |--ex_kalman
#       |--luenberger 
# 

from os.path import dirname, basename, isfile, join
import glob

# idirs = ['D:\\gh_repo\\filters'
#             , 'D:\\gh_repo\\filters\\lowpass'
#             , 'D:\\gh_repo\\filters\\ex_kalman'
#             , 'D:\\gh_repo\\filters\\luenberger']

def importsubdir(idirs):
    modules = ''
    for d in idirs:
        modules += ',' + ','.join(glob.glob(join(d, "*.py")))
        # __all__: A list of strings that define what variables have to be imported to 
        #       another file. 
        #       The variables which are declared in that list can only be used in another 
        #       file after importing this file, the rest variables if called will throw an error.
        # __init__: The Default constructor in C++ and Java. Constructors are used to initializing
        #       the object’s state. The task of constructors is to initialize(assign values) to 
        #       the data members of the class when an object of the class is created. 
        #       Like methods, a constructor also contains a collection of statements
        #       (i.e. instructions) that are executed at the time of Object creation. 
        #       It is run as soon as an object of a class is instantiated. 
        #       The method is useful to do any initialization you want to do with your object.

    __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')] # exclude folders and the init file 

# for f in modules.split(','):
#     if isfile(f) and not f.endswith('__init__.py'):
#         print(f)


# for f in modules.split(','):
#     print(f)









