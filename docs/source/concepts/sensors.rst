Sensors
=======

The ``sensors`` module in c4dynamics provides
physical and vision-based sensor models for simulating real-world measurements.

It encompasses a variety of sensing modalities, from physical measurements to computer vision. 
This gives simulated agents the “eyes and ears” they need to perceive and interpret the environment.


This module is designed to be flexible and extensible, 
allowing you to integrate multiple sensor types into your 
simulations while maintaining consistent interfaces for data acquisition and processing.


This section includes three main components:


YOLOv3 Class
------------
A real-time object detection interface based on the YOLOv3 architecture. 
It provides bounding boxes, class predictions, and confidence scores, 
enabling simulated agents to perceive and classify visual elements in their environment.

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



.. figure:: /_architecture/yolo-object-detection.jpg

*Figure 1*:
Object Detection with YOLO using COCO pre-trained classes 'dog', 'bicycle', 'truck'.
Read more at: `darknet-yolo <https://pjreddie.com/darknet/yolo/>`_.




Seeker Class
------------
Models a generic seeker sensor used in guidance and tracking simulations. 
It measures the azimuth and elevation angles through an error model, 
simulating how onboard seekers detect and track targets.

**Functionality**

At each time step, the seeker returns measurements based on the true geometry relative to the target.

Let the relative coordinates in an arbitrary frame of reference: 

.. math::

  dx = target.x - seeker.x

  dy = target.y - seeker.y

  dz = target.z - seeker.z


The relative coordinates in the seeker body frame are given by: 

.. math::

  x_b = [BR] \cdot [dx, dy, dz]^T 

where :math:`[BR]` is a 
Body from Reference DCM (Direction Cosine Matrix)
formed by the seeker three Euler angles. See the `rigidbody` section below. 

The azimuth and elevation measures are then the spatial angles: 

.. math:: 

  az = tan^{-1}{x_b[1] \over x_b[0]}

  el = tan^{-1}{x_b[2] \over \sqrt{x_b[0]^2 + x_b[1]^2}}



Where:

- :math:`az` is the azimuth angle
- :math:`el` is the elevation angle
- :math:`x_b` is the target-radar position vector in radar body frame

.. figure:: /_architecture/skr_definitions.svg
  
  Fig-1: Azimuth and elevation angles definition   




Radar Class
----------- 
Simulates a configurable radar sensor, producing measurements such as range, azimuth, and elevation. 
As a subclass of `Seeker`, radar measurements are passed through an error model to simulate real-world sensor imperfections.

**Radar vs Seeker**
    

The following table
lists the main differences between 
:class:`seeker <c4dynamics.sensors.seeker.seeker>` and :class:`radar <c4dynamics.sensors.radar.radar>` 
in terms of measurements and 
default error parameters:
    
  

.. list-table:: 
  :widths: 22 13 13 13 13 13 13  
  :header-rows: 1

  * - 
    - Angles
    - Range
    - :math:`σ_{Bias}`
    - :math:`σ_{Scale Factor}`
    - :math:`σ_{Angular Noise}`
    - :math:`σ_{Range Noise}`

  * - Seeker 
    - ✔️
    - ❌
    - :math:`0.1°`
    - :math:`5%`
    - :math:`0.4°`
    - :math:`--`

  * - Radar 
    - ✔️
    - ✔️
    - :math:`0.3°`
    - :math:`7%`
    - :math:`0.8°`
    - :math:`1m`

    

Whether you are simulating an autonomous vehicle, a missile guidance loop, or a robotic system, 
the Sensors module gives your models the “eyes and ears” they need to interact with the dynamic world.


See Also 
--------

.. list-table:: 
  :header-rows: 0

  * - :class:`YOLOv3 <c4dynamics.detectors.yolo3_opencv.yolov3>`
    - Realtime object detection model based on YOLO (You Only Look Once) approach  
      with 80 pre-trained COCO classes. 
  * - :class:`seeker <c4dynamics.sensors.seeker.seeker>`
    - Direction detector.
  * - :class:`radar <c4dynamics.sensors.radar.radar>`
    - Range-direction detector.



