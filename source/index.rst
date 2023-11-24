.. C4dynamics documentation master file, created by
   sphinx-quickstart on Thu Nov 23 16:12:22 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. _c4dynamics_docs_mainpage:

========================
C4dynamics Documentation
========================

.. toctree::
   :maxdepth: 1
   :hidden:

   User Guide <user/index>
   API reference <reference/index>
   Development <dev/index>
   release


**Version**: |version|

 
**Useful links**:
`Source Repository <https://github.com/C4dynamics/C4dynamics>`_ |

C4Dynamics (read Tsipor (bird) Dynamics) is the open-source framework of algorithms development for objects in space and time.  
It is a Python library that provides entities for developing and analyzing algorithms of physical systems, that is, system with dynamics, with one or more of the internal systems and algorithms of C4dynamics:  
ODE Solver (4th order Runge-Kutta)  
Kalman Filters  
Asymptotic Observer  
Radar Model  
IMU Model  
GPS Model  
Line Of Sight Seeker  
Or with one of the 3rd party libraries integrated with C4dynamics:  
OpenCV
YOLO  

.. grid:: 2

    .. grid-item-card::
        :img-top: docs/_images/getting_started.svg

        Getting started
        ^^^^^^^^^^^^^^^

        New to C4dynamics? Check out the Absolute Beginner's Guide. It contains an
        introduction to C4dynamics's main concepts and links to additional tutorials.

        +++

        .. button-ref:: user/absolute_beginners
            :expand:
            :color: secondary
            :click-parent:

            To the absolute beginner's guide

    .. grid-item-card::
        :img-top: docs/_images/user_guide.svg

        User guide
        ^^^^^^^^^^

        The user guide provides in-depth information on the
        key concepts of C4dynamics with useful background information and explanation.

        +++

        .. button-ref:: user
            :expand:
            :color: secondary
            :click-parent:

            To the user guide



.. This is not really the index page, that is found in
   _templates/indexcontent.html The toctree content here will be added to the
   top of the template header
