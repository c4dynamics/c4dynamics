from setuptools import setup, find_packages
import codecs
import os # , sys
import re 

package = 'c4dynamics'
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.md'), encoding = 'utf-8') as fh:
    long_description = '\n' + fh.read()


import c4dynamics

VERSION = c4dynamics.__version__
print(VERSION)
print('did u remember to upgrade the version number??') 

DESCRIPTION = 'The framework for algorithms engineering with Python.'
LONG_DESCRIPTION = 'Tsipor (bird) Dynamics (c4dynamics) is the open-source framework of algorithms development for objects in space and time.'

required_packages = []

with open(os.path.join(here, 'requirements.txt'), 'r') as file:
    for line in file:
        line = line.strip()  # Remove leading and trailing whitespaces
        if not line.startswith('#'):
            required_packages.append(line)


# Now, lines_to_append contains all lines from the file that don't start with a hash
print(required_packages)


# Setting up
# sys.argv.append('sdist')
# sys.argv.append('bdist_wheel')

setup(
      name                          =  package
    , version                       =  VERSION
    , author                        = 'c4dynamics'
    , author_email                  = 'zivmeri@gmail.com'
    , description                   =  DESCRIPTION
    , long_description_content_type = 'text/markdown'
    , long_description              = long_description  # LONG_DESCRIPTION   # 
    , packages                      = find_packages()
    , include_package_data          = True
    # , package_data                  = {package: ['resources/detectors/yolo/v3/*.*']}  
    # Include all files in the 'resource' folder.
    # , exclude_package_data          = {package: ['resources/detectors/yolo/v3/*.*']}
    # , exclude_package_data          = {package: ['src/main/resources/*.*']}
    , install_requires              = required_packages
    , python_requires = ">=3.8,<3.13" # update also in run-tests.yml, readme.md, pyproject.yaml, setup_guide.ipynb 
    , keywords = ['python', 'dynamics', 'physics'
                    , 'algorithms', 'computer vision'
                        , 'navigation', 'guidance', 'slam' 
                            , 'vslam', 'image processing', 'signal processing', 'control']
    , classifiers = ['Development Status :: 5 - Production/Stable'
                        , 'Intended Audience :: Developers'
                            , 'Programming Language :: Python :: 3'
                                , 'Operating System :: Unix'
                                    , 'Operating System :: MacOS :: MacOS X'
                                        , 'Operating System :: Microsoft :: Windows']
        )


print('always make a tag version with a pip upload!')

