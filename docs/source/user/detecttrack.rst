*******************************
Objects Detection and Tracking
*******************************

Detecting objects using the YOLOv3 model, updating and predicting their trajectories 
with the Kalman filter employing linear dynamics. Association between tracks is performed 
using scikit-learn's k-neighbors.
Each track is represented as a C4dynamics-datapoint, and the update and prediction are executed with the internal C4dynamics-Kalman-filter.




.. table of content 
.. intro
.. car detection with YOLO
.. car tracking with kalman filter 
.. main loop exerts. 


.. 3 levels of header

.. ******************************************
.. The N-dimensional array (:class:`ndarray`)
.. ******************************************

.. Constructing arrays
.. ===================

.. Memory layout
.. -------------

.. example box and code box:
.. .. admonition:: Example

..    A 2-dimensional array of size 2 x 3, composed of 4-byte integer
..    elements:

..    >>> x = np.array([[1, 2, 3], [4, 5, 6]], np.int32)



Jupyter Notebook
================
`The example's notebook can be downloaded from the examples folder in C4dynamics' GitHub <https://github.com/C4dynamics/C4dynamics/tree/main/examples>`_ 

.. `Source Repository <https://github.com/C4dynamics/C4dynamics>`_ |

Video Processing 
================
The video capture, reading of the frames, applying annotations, and other image operations 
are produced with OpenCV library. 
The main loop is performed while the video is still open, where each iteration reads a new frame 
that uses for the next operations.  


.. admonition:: OpenCV 

   Initialization: 

   .. code:: 

      cvideo = cv2.VideoCapture(videoin)


   Main loop: 

   
   .. code:: 

      while cvideo.isOpened():
         ret, frame = cvideo.read()
         ...


Detection 
=========

Every frame is transmitted into an object detection model which provides a list of boxes 
encompassing the detected objects. 

.. admonition:: YOLO 
   
   Initialization:

   .. code:: 

      yolodet = c4d.detectors.yolo()

   Main Loop:

   .. code:: 

      zList = yolodet.detect(frame, t) 



Tracks Management 
=================

Every detected object generates a **tracker** object.
A **tracker** object inherits from the **C4dynamics.datapoint** class and extends it.
The **datapoint** grants the tracker position and velocity attributes. The **tracker** also 
associates the object a **Kalman filter**. 

.. admonition:: Tracker 
   
   Creation:

   .. code:: 

      self.trackers[key] = tracker(z)


**self.trackers** is a dictionary of trackers, where a key is a unique track ID, and 
the value is a tracker object.  

When an object is detected, a **NearestNeighbors** algorithm is running to 
decide whether to associate it with an existing track, or to create a new track.
Associating a detection with an existing track includes the update of its position 
and voclity, and storing the state in the current time stamp:


.. admonition:: Tracker 
   
   Update:

   .. code:: 

            self.trackers[key].x = center[0]
            self.trackers[key].y = center[1]
            self.trackers[key].vx = vel[0]
            self.trackers[key].vy = vel[1]
            
            self.trackers[key].store(t)
            self.trackers[key].storevar('state', t)



State Estimation 
================

To provide smooth and continuous estimation of the objects in the video frames, 
the tracks that detected should be enhanced with a **Kalman Filter**.
The **Kalman Filter** manages two tasks:


1. Update the track state (position and velocity) according to the weight that 
given to the sensor.

2. Predict the track state according to the model of the dynamics that associated 
with the object (linear motion, in this example).

**Prediction** is performed in every iteration of the main loop. 
**Update** is preformed when a valid detection is introduced. 


.. admonition:: Kalman Filter  
   
   Initialization (At the tracker constructor, as the **Kalman filter** is part 
   of the **Tracker** class)

   .. code:: 
   
      self.filter = c4d.filters.kalman(np.hstack((z, np.zeros(2))), P, A, H, Q, R)

   Where z is the first detection, and P, A, H, Q, R are the Kalman matrices represent
   the covariance, the state transition, the observation, the process noise, and the measurement noise, respectively. 

   Prediction:

   .. code:: 

            self.trackers[key].filter.predict()

   Update:

   .. code:: 

            self.trackers[key].filter.correct(measurement)

   Where measurement is the object coordinates as given by the detector.  


.. ### Car Tracking with Kalman Filter

.. After detecting the cars in the images, we will track them over time using a Kalman filter. 
.. The Kalman filter is a recursive algorithm that estimates the state of a dynamic 
.. system given noisy measurements. By integrating the Kalman filter with our car detection 
.. results, we can track the movement of cars and predict their future positions.

.. In this section, we will:

.. 1. Initialize the Kalman filter.
.. 2. Extract the detected car positions.
.. 3. Update the Kalman filter with the detected car positions.
.. 4. Predict and visualize the tracked car positions.

.. ### Summary

.. By combining car detection using YOLO and car tracking with the Kalman filter,
 we can achieve robust and accurate tracking of cars in surveillance videos.  
.. The C4dynamics algorithms engineering framework provides an efficient environment 
.. for implementing and evaluating such computer vision algorithms. In this example, leveraging *Amit Elbaz* masters' project to detect and track vehicles with Yolo and Kalman Filter. 

.. Let's start!









.. figure:: /../../examples/out/detection-tracking-tank-truck.gif

   **Figure**
   Ouput video including bounding boxes encompassing the tracked vehicles.
