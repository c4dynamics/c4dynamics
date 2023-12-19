# from IPython.display import display_html
# display_html("<script>Jupyter.notebook.kernel.restart()</script>", raw = True)

import re
import os, sys
# import importlib


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project   = 'C4dynamics'
copyright = '2023, C4dynamics'
author    = 'C4dynamics'
# release   = '0.0.40'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.graphviz',
    'sphinx.ext.ifconfig',
    'matplotlib.sphinxext.plot_directive',
    'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive',
    'sphinx.ext.mathjax',
    'sphinx_design',]

templates_path = ['_templates']
exclude_patterns = []






# # Check if the module is loaded
# if 'c4dynamics' in sys.modules:
#     print('\033[91m' + 'reimport c4dynamics' + '\033[0m')
#     del sys.modules['c4dynamics']
sys.path.append(os.path.join('..', '..'))
# sys.path.append('./c4dynamics')
# sys.path.append(os.path.join(os.getcwd(), 'c4dynamics'))
# print('\033[91m' + os.getcwd() + '\033[0m')

import c4dynamics
# Reload the module
# importlib.reload(importlib.import_module(project.lower()))

# The short X.Y version (including .devXXXX, rcX, b1 suffixes if present)
version = re.sub(r'(\d+\.\d+)\.\d+(.*)', r'\1\2', c4dynamics.__version__)
version = re.sub(r'(\.dev\d+).*?$', r'\1', version)
# The full version, including alpha/beta/rc tags.
release = c4dynamics.__version__
print("%s %s" % (version, release))

# -----------------------------------------------------------------------------
# HTML output
# -----------------------------------------------------------------------------

html_theme = 'pydata_sphinx_theme'

html_favicon = '_static/favicon/favicon.ico'

# Set up the version switcher.  The versions.json is stored in the doc repo.
if os.environ.get('CIRCLE_JOB', False) and \
        os.environ.get('CIRCLE_BRANCH', '') != 'main':
    # For PR, name is set to its ref
    switcher_version = os.environ['CIRCLE_BRANCH']
elif ".dev" in version:
    switcher_version = "devdocs"
else:
    switcher_version = f"{version}"

# html_theme_options = {
#   "logo": {
#       "image_light": "c4dlogo.svg",
#       "image_dark": "c4dlogo.svg",
#   },
#   "github_url": "https://github.com/C4dynamics/C4dynamics",
#   "collapse_navigation": True,
#   "external_links": [
#       {"name": "Learn", "url": "https://c4dynamics.github.io/C4dynamics/user/"},
#       {"name": "NEPs", "url": "https://github.com/C4dynamics/C4dynamics/wiki/Architecture-&-Roadmap"}
#       ],
#   "header_links_before_dropdown": 6,
#   # Add light/dark mode and documentation version switcher:
#   "navbar_end": ["theme-switcher", "version-switcher", "navbar-icon-links"],
#   "switcher": {
#       "version_match": switcher_version,
#       "json_url": "",
#   },
# }

html_title = "%s v%s Manual" % (project, version)
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'
html_css_files = ["c4dynamics.css"]
html_context = {"default_mode": "dark"}
html_use_modindex = True
html_copy_source = False
html_domain_indices = False
html_file_suffix = '.html'

htmlhelp_basename = 'c4dynamics'

if 'sphinx.ext.pngmath' in extensions:
    pngmath_use_preview = True
    pngmath_dvipng_args = ['-gamma', '1.5', '-D', '96', '-bg', 'Transparent']

# mathjax_path = "scipy-mathjax/MathJax.js?config=scipy-mathjax"

plot_html_show_formats = False
plot_html_show_source_link = False

