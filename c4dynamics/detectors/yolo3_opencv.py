import os
import cv2
import numpy as np
from c4dynamics import fdatapoint 


MODEL_SIZE = (416, 416, 3)


class yolov3:
    
    _nms_th = 0.5 
    _confidence_th = 0.5 
 
    def __init__(self): # , **kwargs): 

        v3path = os.path.join('c4dynamics', 'resources', 'detectors', 'yolo', 'v3')

        weights_path = os.path.join(v3path, 'yolov3.weights')
        cfg_path     = os.path.join(v3path, 'yolov3.cfg')
        coconames    = os.path.join(v3path, 'coco.names')

        self.net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        ln = self.net.getLayerNames()
        self.ln = [ln[i - 1] for i in self.net.getUnconnectedOutLayers()]

        with open(coconames, 'r') as f:
            self.class_names = f.read().strip().split('\n')
        
        # self.__dict__.update(kwargs)
        


    @property 
    def nms_th(self):
        '''
        Non-Maximum Suppression (NMS) threshold.

        Gets or sets for the Non-Maximum Suppression (NMS) threshold. Default: `nms_th = 0.5`. 

        
        Parameters (Setter)
        -------------------
        val : float
            The new threshold value for NMS during object detection.

        Returns (Getter)
        ----------------

        out : float
            The threshold value used for NMS during object detection.
            Objects with confidence scores below this threshold are suppressed. 

            
        Example
        -------
        
        .. code:: 
            
            >>> imagename = 'planes.jpg'
            >>> imgpath = os.path.join(os.getcwd(), 'examples', 'resources', imagename)
            >>> yolo3 = c4d.detectors.yolov3()
            >>> nms_thresholds = [0.1, 0.5, 0.9]
            >>> for i, nms_threshold in enumerate(nms_thresholds, 1)
            ...   yolo3.nms_th = nms_threshold
            ...   img = cv2.imread(imgpath)
            ...   pts = yolo3.detect(img)
            ...   for p in pts:
            ...     cv2.rectangle(img, p.box[0], p.box[1], [0, 0, 0], 2)
            ...   plt.subplot(1, 3, i)
            ...   plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ...   plt.title(f"NMS Threshold: {nms_threshold}")
            ...   plt.axis('off')

        .. figure:: /_static/images/yolo3_nms_th.png                  


        A high value (0.9) for the Non-Maximum Suppression (NMS) threshold here  
        leads to an increased number of bounding boxes around a single object.
        When the NMS threshold is high, it means that a significant overlap is 
        required for two bounding boxes to be considered redundant, 
        and one of them will be suppressed.
        To address this issue, it's essential to choose an appropriate 
        NMS threshold based on the characteristics of your dataset and the 
        level of overlap between objects. 
        A lower NMS threshold (e.g., 0.4 or 0.5) 
        is commonly used to suppress redundant boxes effectively 
        while retaining accurate detections. 
        Experimenting with different 
        threshold values and observing their impact on the results is crucial 
        for optimizing the performance of object detection models.



        '''
        return self._nms_th 

    @nms_th.setter
    def nms_th(self, val):
        self._nms_th = val
        
    @property 
    def confidence_th(self):
        '''
        Confidence threshold used in the object detection.

        Gets or sets for the confidence threshold. Default: `confidence_th = 0.5`. 


        Parameters (Setter)
        -------------------
        val : float
            The new confidence threshold for object detection.

        Returns (Getter)
        ----------------
        out : float
            The confidence threshold for object detection.
            Detected objects with confidence scores below this threshold are filtered out.


        Example
        -------

        .. code:: 

            >>> imagename = 'planes.jpg'
            >>> imgpath = os.path.join(os.getcwd(), 'examples', 'resources', imagename)
            >>> yolo3 = c4d.detectors.yolov3()
            >>> confidence_thresholds = [0.9, 0.95, 0.99]
            ... for i, confidence_threshold in enumerate(confidence_thresholds, 1):  
            ...   yolo3.confidence_th = confidence_threshold
            ...   img = cv2.imread(imgpath)
            ...   pts = yolo3.detect(img)
            ...   for p in pts:
            ...     cv2.rectangle(img, p.box[0], p.box[1], [0, 0, 0], 2)
            ...   plt.subplot(1, 3, i)
            ...   plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            ...   plt.title(f"Confidence Threshold: {confidence_threshold}")
            ...   plt.axis('off')


        .. figure:: /_static/images/yolo3_confidence_th.png


        A single object being missed, particularly when setting the confidence threshold to 0.99, 
        suggests that the model is highly confident in its predictions. 
        This level of performance is typically achievable when the model 
        has been trained on a diverse and representative dataset, 
        encompassing a wide variety of object instances, backgrounds, 
        and conditions. 


        '''

        return self._confidence_th 

    @confidence_th.setter
    def confidence_th(self, val):
        self._confidence_th = val
        


    def detect(self, frame):
        '''
        Detects objects in a frame using the YOLOv3 model.

        At each sample, the detector performs the following steps:

        1. Preprocesses the frame by creating a blob, normalizing pixel values, and swapping Red and Blue channels.

        2. Sets input to the YOLOv3 model and performs a forward pass to obtain detections.

        3. Extracts detected objects based on a confidence threshold, calculates bounding box coordinates, and filters results using Non-Maximum Suppression (NMS).

        Parameters
        ----------
        frame : numpy.array or list
            An input frame for object detection.

        Returns
        -------
        out : list[fdatapoint]
            A list of :class:`fdatapoint` objects representing detected objects, 
            each containing bounding box coordinates and class labels.

        Examples
        --------

        The datasets used in the examples are available in the 
        `Source Repository <https://github.com/C4dynamics/C4dynamics>`
        under example/resources. 


        Import required packages
        ^^^^^^^^^^^^^^^^^^^^^^^^
        
        .. code:: 
        
            >>> import os 
            >>> import cv2      # opencv-python 
            >>> import numpy as np 
            >>> import c4dynamics as c4d 
            >>> from matplotlib import pyplot as plt

            



        Object detecion in a single frame 
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        .. code:: 

            >>> imagename = 'planes.jpg'
            >>> img = cv2.imread(os.path.join(os.getcwd(), 'examples', 'resources', imagename))
            >>> yolo3 = c4d.detectors.yolov3()
            >>> pts = yolo3.detect(img)
            >>> for p in pts:
            ...   cv2.rectangle(img, p.box[0], p.box[1], np.random.randint(0, 255, 3).tolist(), 3)
            >>> fig, ax = plt.subplots()
            >>> ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        .. figure:: /_static/images/yolo3_image.png


        Object detecion in a video 
        ^^^^^^^^^^^^^^^^^^^^^^^^^^

        .. code::
        
            >>> videoname = 'aerobatics.mp4'
            >>> videoin   = os.path.join('examples', 'resources', videoname)
            >>> videoout  = os.path.join(os.getcwd(), videoname)
            >>> cvideo      = cv2.VideoCapture(videoin)
            >>> cvideo_out  = cv2.VideoWriter(videoout, cv2.VideoWriter_fourcc(*'mp4v')
            ...                 , int(cvideo.get(cv2.CAP_PROP_FPS))
            ...                     , [int(cvideo.get(cv2.CAP_PROP_FRAME_WIDTH))
            ...                        , int(cvideo.get(cv2.CAP_PROP_FRAME_HEIGHT))])
            >>> yolo3 = c4d.detectors.yolov3()
            >>> while cvideo.isOpened():
            ...     ret, frame = cvideo.read()
            ...     if not ret: break
            ...     pts = yolo3.detect(frame)
            ...     for p in pts:
            ...         cv2.rectangle(frame, p.box[0], p.box[1], [0, 0, 0], 2)# np.random.randint(0, 255, 3).tolist(), 2)    
            ...     cvideo_out.write(frame)
            >>> cvideo_out.release()

        .. figure:: /_static/images/aerobatics.gif


        The output structure
        ^^^^^^^^^^^^^^^^^^^^

        The output of the detect() function is a list of :class:`fdatapoint` object.
        The :class:`fdatapoint` has unique attributes to manipulate the detected object class and  
        bounding box. 

        .. code::

            >>> print('{:^10} | {:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}'.format(
            ...     '# object', 'center x', 'center y', 'box top-left'
            ...         , 'box bottom-right', 'class', 'frame size'))
            >>> for i, p in enumerate(pts):
            ...     tlb = '(' + str(p.box[0][0]) + ', ' + str(p.box[0][1]) + ')'
            ...     brb = '(' + str(p.box[1][0]) + ', ' + str(p.box[1][1]) + ')'
            ...     fsize = '(' + str(p.fsize[0]) + ', ' + str(p.fsize[1]) + ')'
            ...     print('{:^10d} | {:^10.3f} | {:^10.3f} | {:^16} | {:^16} | {:^10} | {:^14}'.format(
            ...                 i, p.x, p.y, tlb, brb, p.iclass, fsize))
            ...     c = np.random.randint(0, 255, 3).tolist()
            ...     cv2.rectangle(img, p.box[0], p.box[1], c, 2)
            ...     point = (int((p.box[0][0] + p.box[1][0]) / 2 - 75), p.box[1][1] + 22)
            ...     cv2.putText(img, p.iclass, point, cv2.FONT_HERSHEY_SIMPLEX, 1, c, 2)
            >>> fig, ax = plt.subplots()
            >>> ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            >>> ax.set_axis_off()
             # object  |  center x  |  center y  |   box top-left   | box bottom-right |   class    |  frame size  
                0      |   0.584    |   0.376    |    (691, 234)    |    (802, 306)    | aeroplane  |  (1280, 720)  
                1      |   0.457    |   0.473    |    (528, 305)    |    (642, 376)    | aeroplane  |  (1280, 720)  
                2      |   0.471    |   0.322    |    (542, 196)    |    (661, 267)    | aeroplane  |  (1280, 720)  
                3      |   0.546    |   0.873    |    (645, 588)    |    (752, 668)    | aeroplane  |  (1280, 720) 

        .. figure:: /_static/images/yolo3_outformat.png


        '''
        #
        # Step 1: Preprocess the Frame
        #   - Create a blob (binary large object) from the input frame with the 
        #       specified dimensions
        #   - Normalize pixel values to a range of 0 to 1
        #   - Specify the dimensions of the input layer of the YOLOv3 model
        #   - Swap Red and Blue channels (BGR to RGB)
        #   - Set crop to False to preserve the original aspect ratio
        ##
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (MODEL_SIZE[0], MODEL_SIZE[1]), swapRB = True, crop = False)

        #
        # Step 2: Set Input to the YOLOv3 Model and Perform Forward Pass
        #   - Set the blob as the input to the YOLOv3 model
        #   - Get the names of the output layers of the model
        #   - Perform a forward pass through the model to obtain detections
        ##
        self.net.setInput(blob)
        detections = self.net.forward(self.ln)
        
        #
        # Step 3: Extract Detected Objects
        #   - Iterate through the detected objects in the forward pass results
        #   - Filter objects based on confidence threshold
        #   - Calculate bounding box coordinates and convert to integers
        #   - Append bounding box coordinates and class labels to respective lists
        ##
        raw = []
        boxes = []
        classIDs = []
        confidences = []
        h, w = frame.shape[:2]

        for detection in detections:
            for d in detection:
                
                scores = d[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                
                if scores[classID] > self._confidence_th:  # Adjust the confidence threshold as needed

                    box = d[:4] * [w, h, w, h] # relative (xc, yc, w, h) to pixels 
                    # (center_x, center_y, width, height) = box.astype('int')

                    x = box[0] - box[2] / 2 # top left x 
                    y = box[1] - box[3] / 2 # top left y 

                    boxes.append([x, y, box[2], box[3]]) # top left x, top left y, width, height
                    confidences.append(float(confidence))
                    classIDs.append(classID) 
                    raw.append(d[:4]) 


        indices = cv2.dnn.NMSBoxes(boxes, confidences, self._confidence_th, self._nms_th)
        
        box_out = []
        class_out = []
        points_out = []


        if len(indices) > 0:
            for i in indices.flatten():
                # (x, y) = (boxes[i][0], boxes[i][1])
                # (w, h) = (boxes[i][2], boxes[i][3])
                #               x top left, y top left,   x bottom right,           y bottom right 
                box_out.append([boxes[i][0], boxes[i][1], boxes[i][0] + boxes[i][2], boxes[i][1] + boxes[i][3]])
                
                class_out.append(self.class_names[classIDs[i]])

                points_out.append(fdatapoint(raw[i], self.class_names[classIDs[i]], (w, h)))

        box_out = np.array(box_out)
        
        return points_out # box_out, class_out,  



