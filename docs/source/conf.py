# from IPython.display import display_html
# display_html("<script>Jupyter.notebook.kernel.restart()</script>", raw = True)

import re
import os, sys
# import importlib

'''

required packages:

pip install sphinx
pip install sphinx_design
pip install sphinx_book_theme

https://github.com/numpy/numpy/issues/22408
Too light color for the label of "dev" version selection button
The label of "dev" version selection button is colored light gray in the dark mode and the button itself is colored orange. The difference in brightness between those two colors is too small to read.
In the light mode, the label color is black and it looks clear.

ss 2022-10-08 15 55 00

This is because pydata-sphinx-theme defines color for #version_switcher_button, whose value is #c9d1d9 in the dark mode although it is #333333 in the light mode. numpy.css's definition only overwrites the background color for "dev".

H3-level section heading colors
I think H3-level section heading colors is a bit too dark, but this may be a matter of opinion:

ss 2022-10-08 15 54 25

The cause is the same as that of the issue with the body text color; the color of h3 is overwritten in numpy.css.

'''
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project   = 'c4dynamics'
copyright = '2023, C4dynamics'
author    = 'C4dynamics'
# release   = '0.0.40'
# # Check if the module is loaded
# if 'c4dynamics' in sys.modules:
#     print('\033[91m' + 'reimport c4dynamics' + '\033[0m')
#     del sys.modules['c4dynamics']

sys.path.append('.')
sys.path.append(os.path.join('..', '..'))
# sys.path.append('./c4dynamics')
# sys.path.append(os.path.join(os.getcwd(), 'c4dynamics'))
# print('\033[91m' + os.getcwd() + '\033[0m')

import c4dynamics as c4d
# import c4dynamics.states.state 
# from c4dynamics.states.state import state.X0
# import import__all__ext

c4d.cprint('successfully imported c4dynamics', 'y')
# c4d.cprint('successfully imported import__all__ext', 'y')


# Reload the module
# importlib.reload(importlib.import_module(project.lower()))

# The short X.Y version (including .devXXXX, rcX, b1 suffixes if present)
version = re.sub(r'(\d+\.\d+)\.\d+(.*)', r'\1\2', c4d.__version__)
version = re.sub(r'(\.dev\d+).*?$', r'\1', version)
# The full version, including alpha/beta/rc tags.
release = c4d.__version__
print("%s %s" % (version, release))


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
      'sphinx.ext.autodoc'
    , 'sphinx.ext.autosummary'
    , 'sphinx.ext.coverage'
    , 'sphinx.ext.mathjax'
    , 'sphinx.ext.doctest'
    , 'sphinx.ext.viewcode'
    , 'sphinx.ext.extlinks'
    , 'sphinx.ext.intersphinx'
    , 'sphinx.ext.napoleon'
    , 'sphinx_design'
    # , 'import__all__ext'
]


# verbose debug 
traceback_show = True
autodoc_default_flags = ['members']
autosummary_generate = True
# Otherwise, the Return parameter list looks different from the Parameters list
napoleon_use_rtype = False
# napoleon_google_docstring = True
# napoleon_numpy_docstring = False
napoleon_type_aliases = {'Args': 'Arguments', 'Parameters': 'Arguments'}

'''
  https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

  
  Docstring Sections
  All of the following section headers are supported:

    Args (alias of Parameters)
    Arguments (alias of Parameters)
    Attention
    Attributes
    Caution
    Danger
    Error
    Example
    Examples
    Hint
    Important
    Keyword Args (alias of Keyword Arguments)
    Keyword Arguments
    Methods
    Note
    Notes
    Other Parameters
    Parameters
    Return (alias of Returns)
    Returns
    Raise (alias of Raises)
    Raises
    References
    See Also
    Tip
    Todo
    Warning
    Warnings (alias of Warning)
    Warn (alias of Warns)
    Warns
    Yield (alias of Yields)
    Yields

  # Napoleon settings
    napoleon_google_docstring = True
    napoleon_numpy_docstring = True
    napoleon_include_init_with_doc = False
    napoleon_include_private_with_doc = False
    napoleon_include_special_with_doc = True
    napoleon_use_admonition_for_examples = False
    napoleon_use_admonition_for_notes = False
    napoleon_use_admonition_for_references = False
    napoleon_use_ivar = False
    napoleon_use_param = True
    napoleon_use_rtype = True
    napoleon_preprocess_types = False
    napoleon_type_aliases = None
    napoleon_attr_annotations = True
'''


 # maps functions with a class name that is indistinguishable when case is 
 # ignore to another filename 


autosummary_filename_map = { # not sure this is necessary anymore
'c4dynamics.datapoint.x': 'c4dynamics.datapoint.x_var', 
#  'c4dynamics.datapoint.X': 'datapoint.x_property', 
 } 

autodoc_default_options = {
'ignore-module-all': True
}


# Sphinx project configuration
templates_path = ["_templates"]
exclude_patterns = ["_build", "**.ipynb_checkpoints"]
source_suffix = ".rst"
# The encoding of source files.
source_encoding = "utf-8"
master_doc = "index"
pygments_style = "default"
add_function_parentheses = False









# -----------------------------------------------------------------------------
# HTML output
# -----------------------------------------------------------------------------



# HTML output configuration
# -----------------------------------------------------------------------------
html_title = f'{project} <span class="project-version">{version}</span>'
html_short_title = project
# Don't use the logo since it gets in the way of the project name and is
# repeated in the front page.
# html_logo = "_static/pooch-logo.png"
html_favicon = "_static/c4dlogo.svg"
html_last_updated_fmt = "%b %d, %Y"
# html_copy_source = True
html_static_path = ["_static"]
# CSS files are relative to the static path
html_css_files = ["style.css"]
html_extra_path = []
html_show_sourcelink = False
html_show_sphinx = True
html_show_copyright = True

html_theme = "sphinx_book_theme"
html_theme_options = {
      "repository_url": f"https://github.com/{author.lower()}/{project.lower()}"
    , "repository_branch": "main"
    , "path_to_docs": "docs"
    # "launch_buttons": {
    #   "binderhub_url": "https://mybinder.org",
    #   "notebook_interface": "jupyterlab",
    # } 
    # "use_edit_page_button": True,
    # "use_issues_button": True,
    # "use_repository_button": True,
    # "use_download_button": True
    , "home_page_in_toc": True
}


'''

XXX AIs for docstrings. 
1 edit the intro to the states and states lib. 
2 animate is not a rb method. 
3 rotmat is not a rb method. 
4 what if the user wnats to povide vars that are not part of the state? 
5 how the user passes args which are not part of the state 
6 in every class after one paragraph to the most there comes parameters list. 
7 complete example and docstring to kalamn, ekf, lpf.
8 complete docing all the new modules
9 complete docing the state object. 
10 add new intro to pixelpoint 
11 in all the examples include the moduels of c4d and all the imports in different section like this:

  .. code::   
  
    >>> from scipy import ndimage, datasets 
    >>> import matplotlib.pyplot as ply

  .. code::

    >>> fig = plt.figure()
    ...

  class
  -----
  state
  datapoint
  rigidbody
  pixelpoint
  seeker
  yolo
  kalman
  ekf
  lpf

  
7 all the classes should follow the structure:
  intro paragraph.
  parameters
  kwargs parameters 
  example
  functionality? 
  conntiunue. 
8 datapoint and rigidbody should not include attrs that already appear at state. 
11 figures in seeker are bad size. 
12 in seeker i commented some parts that included toctrees and description 
    of arguments in construction etc.
13 docstrings of methods migrated from dp to state must be updated with their examples.
14 new methods should get new docstrings.  
16 rb has properties at the bottom. dp not. 
17 add section explains how the user adds methods (not just params and vars. ) 
18 test the plot functions with different backends. 
19 protcet the _data array to prevent modification from outside. 
20 maybe add an option to introduce parameters as dict in the constructor. 
21 replace the example in the intro of pixelpoint with the final example of 
    yolov3 in similar to seeker that examples in the intro give fully fledge descrption of the funcitonallity. 
22 the class docstring should include examples for the different arguments while the
    properties should have exmaples in their own page. 

table example:

.. list-table:: 
   :widths: 10 70 20
   :header-rows: 0

   * - Control 
     - :code:`s = c4d.state(theta = 0, omega = 0)`
     - angle, angular velocity 
   * - Navigation
     - :code:`s = c4d.state(x = 0, y = 0, z = 0, vx = 0, vy = 0, vz = 0, q0 = 0, q1 = 0, q2 = 0, q3 = 0, bax = 0, bay = 0, baz = 0)`
     - position, velocity, quaternions, biases
   * - Objects Tracking 
     - :code:`s = c4d.state(x = 0, y = 0, w = 0, h = 0)`
     - center pixels, bounding box size 

     


matrix template 



.. math::

  M = \\begin{bmatrix}
        m11   &   m12     &   m13     \\\\
        m21   &   m22     &   m23     \\\\ 
        m31   &   m32     &   m33     
      \\end{bmatrix}  

      

datasets for download and running the examples:
1. f16 object model.
2. planes.jpg 



Omit Articles: In titles, headings, labels, lists, and brief technical descriptions.
Include Articles: In full sentences, abstracts, summaries, and more narrative forms of writing
https://chatgpt.com/share/799febb0-c875-41be-99f7-c5555741d387


'''

