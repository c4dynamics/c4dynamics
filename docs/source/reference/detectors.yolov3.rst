.. currentmodule:: c4dynamics.detectors 

.. _detectors.yolov3:

************************
YOLOv3 (:class:`yolov3`)
************************

:class:`yolov3` is a YOLOv3 (You Only Look Once) object detection model. 


YOLO: Real-Time Object Detection
================================

Though it is no longer the most accurate object detection algorithm, 
YOLOv3 is still a very good choice when you need real-time detection 
while maintaining excellent accuracy.


The YOLOv3 detector architectures represent 
a groundbreaking approach to real-time object detection. 

YOLOv3 processes an entire image in a single forward pass, 
making it exceptionally efficient for dynamic scenes.

The key strength of YOLOv3 lies in its ability to simultaneously 
predict bounding box coordinates and class probabilities 
for multiple objects within an image. 





C4dynamics
==========

C4dynamics provides developers with a powerful and user-friendly interface 
for working with the YOLOv3 object detection model. 

With :class:`yolov3`, developers can seamlessly integrate real-time 
object detection capabilities into their computer vision algorithms. 

:class:`yolov3` abstracts the complexities of model initialization, 
input preprocessing, and output parsing, 
allowing developers to focus on algorithm development 
rather than implementation details. 

Additionally, C4dynamics introduces the :class:`fdatapoint`, 
enhancing the YOLOv3 output structure and providing a 
convenient data structure for handling bounding box 
information and frame sizes associated with detected objects. 

This abstraction streamlines the development process, 
enabling developers to work with object detection results efficiently. 

Overall, C4dynamics significantly contributes to a smoother and 
more intuitive experience for developers leveraging the YOLOv3 
model in their computer vision projects.



Classes 
=======

Using YOLOv3 means 
object detection capability with the 80 pre-trained 
classes that come with the COCO dataset. 

 
The following 80 classes are available using COCO's pre-trained weights: 

.. admonition:: COCO dataset

  person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, 
  traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, 
  dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, 
  umbrella, handbag, tie, suitcase, frisbee, skis,snowboard, sports ball, 
  kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, 
  bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, 
  sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, 
  couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, 
  keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, 
  clock, vase, scissors, teddy bear, hair drier, toothbrush



.. figure:: /_static/images/yolo-object-detection.jpg

  *Figure*
  Object Detection with YOLO using COCO pre-trained classes 'dog', 'bicycle', 'truck'.
  Read more at: `darknet-yolo <https://pjreddie.com/darknet/yolo/>`_ .


Installation 
============

C4dynamics stores the YOLOv3' weights file on a remote server using 
git-lfs due to its large size. 

In some cases, the archive does not include the git-lfs files. 
Therefore, it's a good advice to install git-lfs before
downloading any archive that includes large files. 

On Windows, download `git-lfs <https://git-lfs.com/>`_  and run: 

.. code:: 

  git lfs install

On Linux: 

.. code:: 

  sudo apt-get install git-lfs
  git lfs install


If you face issues while cloning C4dynamics or using the YOLO detector, 
it is likely that the yolov3.weights file has not been downloaded correctly. 
To resolve this, download and install git-lfs and then reinstall C4dynamics.




Construction
============

A YOLOv3 detector instance is created by making a direct call 
to the yolov3 constructor: 

`yolo3 = c4d.detectors.yolov3()`

Initialization of the instance does not require any 
mandatory parameters.



Attributes
==========

The detector attributes provide functionality to detect objects in 
a frame and to set ang get the sensitivity parameters, nonmaximum supression threshold 
and confidence threshold. 

.. autosummary:: 
  :toctree: generated/

   yolov3.detect 
   yolov3.nms_th
   yolov3.confidence_th 


