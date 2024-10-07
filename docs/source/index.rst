.. C4dynamics documentation master file, created by
   sphinx-quickstart on Thu Nov 23 16:12:22 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
.. title:: C4DYNAMICS

.. raw:: html

   <div class = "text-center">
   <img  src = "_static/c4dlogo.svg" 
         class = "mx-auto my-4 dark-light" 
         style = "width: 200%; max-width: 200px;">
   <h1 class="display-1">C4DYNAMICS</h1>
   <p class="fs-4"><strong>(Tsipor Dynamics)</strong></p>
   <p class="fs-4"><strong>Elevate your algorithms</strong></p>
   </div>


`c4dynamics` is a framework for algorithms development.


**what are state objects?**
Navigation, Control, ... are all characetarized by a basic 
entity which is a state vector for math operations.. 

A state object represents a state vector and other attributes 
that form an entity of a physical (dynamic) system.    
  
Don't ever get messy with ton of objects and variables. 

With `c4dynamics` your object includes everything you need for your state:

\\ plane, resistor-capacitor, x signal, 
\\ x-y image pixels. 

.. code::
   
   >>> plane = c4d.state(z = 1000, gamma = 10)
   >>> print(plane)
   [z  γ] 

.. code::

   >>> plane.X 
   [1000    10]




   
**Version**: |version|

 
`Source Repository <https://github.com/C4dynamics/C4dynamics>`_


`c4dynamics` is the open-source framework of algorithms development 
for objects in space and time.  

It is a Python library that provides entities for developing and analyzing algorithms of physical systems, that is, system with dynamics, with one or more of the internal systems and algorithms of C4dynamics:  

- Sensors 
- Detectors 
- Filters 
- Math Operators 

Or with one of the 3rd party libraries integrated with C4dynamics:

- OpenCV
- YOLO
- Open3D
- NumPy
- Matplotlib 


.. grid:: 1

   .. grid-item-card::


      API Reference
      ^^^^^^^^^^^^^

      Detailed description of the objects, modules, and functions
      included in c4dynamics. 
      
      +++

      .. button-ref:: api
         :expand:
         :color: secondary
         :click-parent:

         To the reference guide





.. toctree::
   :maxdepth: 1
   :hidden:

   API Reference <api/index>

.. 
   Installation 
   Quickstart 
   Use Cases \ programs \ examples \ 
