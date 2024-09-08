'''

Usage of Datasets
=================

C4dynamics dataset functions can be simply called as follows: 
:code:`c4dynamics.datasets.module(file)`, where the existing 
modules and files are detailed in the corresponding pages. 
This downloads the dataset file over the network once and saves the cache 
before returning a path to the file.




Dataset retrieval and storage
=============================

The YOLOv3 weights file can be found at the YOLO official 
site `Joseph Redmon <https://pjreddie.com/darknet/yolo/>`_, 
other dataset files are stored within 
C4dynamics GitHub repository under 
`datasets <https://github.com/C4dynamics/C4dynamics/blob/main/datasets/d3_models/>`_

`C4dynamics.datasets` uses 
`Pooch <https://www.fatiando.org/pooch/latest/>`_, 
a Python package built to simplify fetching data files. 
Pooch uses these repos to
retrieve the respective dataset 
files when calling the dataset function.

A registry of all the datasets, 
essentially a mapping of filenames with their
SHA256 hash and repo urls, are maintained, 
which Pooch uses to handle and verify
the downloads on function call. 
After downloading the dataset once, the files
are saved in the system cache directory under ``'scipy-data'``.

Dataset cache locations may vary on different platforms.

For Windows::

    'C:\\Users\\<user>\\AppData\\Local\\c4data'

For macOS::

    '~/Library/Caches/c4data'

For Linux and other Unix-like platforms::

    '~/.cache/c4data'  # or the value of the XDG_CACHE_HOME env var, if defined


In environments with constrained network connectivity for various security
reasons or on systems without continuous internet connections, 
one may manually
load the cache of the datasets by placing the contents of the dataset repo in
the above mentioned cache directory to avoid fetching dataset errors without
the internet connectivity.

'''


from ._manager import sha256, image, video, nn_model, d3_model, download_all, clearcache  



