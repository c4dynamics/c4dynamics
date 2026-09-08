[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/C4dynamics/c4dynamics/blob/main/docs/source/tutorials/setup_guide.ipynb) ← Click to open in Google Colab

# Setup Guide

Welcome! This notebook is a step-by-step guide to installing c4dynamics and import the package to use in your programs.

There are three main ways to install c4dynamics:

- From `PyPI` (pip)
- Directly from `GitHub`
- Using `pyproject.toml`

## Python Version

c4dynamics requires Python 3.8 or newer. 

## Virtual Environment  

If you want to install and run c4dynamics in a virtual environment, follow this guide before proceeding: [How to Install Multiple Python Versions on your Computer and use them with VSCode](https://k0nze.dev/posts/install-pyenv-venv-vscode/).

## Dependencies 

c4dynamics uses three dependency sets, reflecting different levels of user involvement:

### 1. Basic 

For users working at a foundational level: defining state objects, manipulating them, and using library modules that do not involve computer-vision.

Included packages

- `numpy`
- `scipy` 
- `matplotlib`
- `pooch` 

### 2. Vision

Required for users working with computer-vision and tracking modules, such as: 

- [pixelpoint](https://c4dynamics.github.io/c4dynamics/api/states.lib.pixelpoint.html) 
- [YOLOv3](https://c4dynamics.github.io/c4dynamics/api/detectors.yolov3.html)
- [gif](https://c4dynamics.github.io/c4dynamics/api/generated/utils/c4dynamics.utils.gen_gif.gif.html)

Includes all basic dependencies, plus:

- `opencv-python`
- `imageio`
- `natsort`

### 3. Dev

For contributors who modify source code, run tests, or build documentation.
Includes all vision dependencies, plus:

- `coverage` 
- `nbsphinx`
- `sphinx`
- `sphinx-book-theme`
- `sphinx_design`


The dependency set installed depends on the chosen installation method.
Each installation approach below explicitly references the relevant dependency set.

### Note (Open3D)
open3d is required for the animate function, but it is not included in any dependency set due to frequent installation issues reported by users.
As a result, using animate or [rigidbody.animate](https://c4dynamics.github.io/c4dynamics/api/generated/rb/c4dynamics.states.lib.rigidbody.rigidbody.animate.html#c4dynamics.states.lib.rigidbody.rigidbody.animate) requires a separate installation:
```bash
pip install open3d
```


## PyPI

c4dynamics is published to [PyPI](https://pypi.org/project/c4dynamics/), install it using pip:

```python


!pip install c4dynamics


```


This approach is the most direct and easy, and automatically installs the package dependencies. 

To install additional dependency sets: 

```python


!pip install "c4dynamics[vision]"


```


or: 

```python


!pip install "c4dynamics[dev]"


```


## GitHub 

If you want the newest features, install the [latest GitHub version](https://github.com/C4dynamics/C4dynamics.git) (unstable).

To download the latest GitHub version, you can use `git` or download the ZIP archive from the `GitHub` page:

1. Using `git`

```python


!git clone https://github.com/C4dynamics/C4dynamics.git


```


2. From the GitHub page 

If you don't have `git` installed, you can download the repo manually. Go to the [page of the repo](https://github.com/C4dynamics/C4dynamics), press the `Code` button and then select `Download ZIP`:   

![Download ZIP from the GitHub repo page](https://raw.githubusercontent.com/c4dynamics/c4dynamics/main/docs/source/tutorials/setup_guide_download_zip.png)

Whether you downloaded it using `git clone` or manually through the repo page, add the base directory (the folder where c4dynamics is stored) to the python path (replace `/path/to/your/directory` with the actual path, such as `/home/user/c4dynamics` on Linux or `C:\Users\User\c4dynamics` on Windows):

```python


import sys
sys.path.append('/path/to/your/directory')


```


Now, change the current directory and install the dependencies: 

```python


!cd /path/to/your/directory


```


As outlined in the dependencies section, there are three dependency levels.  
To install the basic level, run:

```python


!pip install -r requirements.txt


```


The 'vision' set: 

```python


!pip install -r requirements-vision.txt


```


The 'dev' set: 

```python


!pip install -r requirements-dev.txt


```


## pyproject.toml

The third option allows you to modify the source code and have the changes reflected immediately (editable install).

Download c4dynamics (see GitHub section).  
Change directory: 

```python


!cd /path/to/your/directory


```


Where `/path/to/your/directory` is the root directory of c4dynamics.  

Install:

```python


!pip install -e .


```


For other dependency sets: 

```python


!pip install "c4dynamics[vision]"


```


Or: 

```python


!pip install "c4dynamics[dev]"


```


## Verify Installation 

```python


import c4dynamics
print(c4dynamics.__version__)


```


Now you can import c4dynamics and use it in your programs:

```python


import c4dynamics as c4d  # noqa: E501


```


## Troubleshooting

If any of the installation steps fail or you encounter unexpected behavior, please open an issue on the [c4dynamics GitHub Issues page](https://github.com/C4dynamics/C4dynamics/issues).  
Include your Python version, operating system, and the full error message to help us resolve problems quickly and improve the framework for everyone.