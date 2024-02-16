.. currentmodule:: c4dynamics 

.. _bodyobjects.fdatapoint:

********************************
Fdatapoint (:class:`fdatapoint`)
********************************

The :class:`fdatapoint` extends the :class:`datapoint`
to form a datapoint in an image.  




Parameters 
==========

The following parameters and attributes extend
the super class, the datapoint. 


bbox : tuple
  Bounding box coordinates in normalized format (xc, yc, w, h).

  xc : float; The x-coordinate of the center of the bounding box.

  yc : float; The y-coordinate of the center of the bounding box.

  w  : float; The width of the bounding box.

  h  : float; The height of the bounding box.

iclass : string 
  Class label or identifier associated with the data point.

framesize : tuple
  Size of the frame in pixels (width, height).

  width : int; The width of the image. 
  
  height : int; The height of the image. 

.. autosummary:: 
  :toctree: generated/

  fdatapoint.iclass 



Note
----

The normalized coordinates are expressed with respect to the 
dimensions of the image, ranging from 0 to 1, where 0 represents 
the left or the upper edge, and 1 represents the right or the bottom edge. 





Attributes
==========

.. autosummary:: 
  :toctree: generated/

  fdatapoint.box
  fdatapoint.set_box_size
  fdatapoint.fsize
  fdatapoint.Xpixels 

  




