from tensorflow.keras.models import load_model
from tensorflow import expand_dims

from .detector_utils import * 
import numpy as np
import cv2
import os


MODEL_SIZE                = (416, 416, 3)
NUM_OF_CLASSES            = 80
CLASS_NAME                = os.path.join(os.getcwd(), 'src', 'main', 'resources', 'detectors', 'coco.names')
MAX_OUTPUT_SIZE           = 40
MAX_OUTPUT_SIZE_PER_CLASS = 20
IOU_THRESHOLD             = 0.5
CONFIDENCE_THRESHOLD      = 0.5


class yolo():
    
    '''
    The yolo_detector class is a wrapper for object detection using the YOLO 
    (You Only Look Once) model. 

    1. __init__(self, height=0, width=0): 
        The class constructor initializes the YOLO model by loading it 
        from the specified model path. 
        It also loads the class names for the detected objects. 
        The height and width parameters are used to set the dimensions of the video frame.

    2. getMeasurements(self, frame): 
        This method takes a frame as input and performs object detection 
        on it using the YOLO model. 
        It returns the bounding box coordinates of the detected objects 
        scaled according to the frame dimensions.

    3. insertDetectionInImg(self): 
        This method draws the detected objects on the frame and returns the modified image.

    4. _detect(self, frame): 
        This private method performs the actual object detection on the given frame. 
        It preprocesses the frame, resizes it to match the model's input size, 
        and passes it through the YOLO model to obtain the bounding box coordinates, 
        scores, class predictions, and the number of detected objects.

    5. drawDetection(self): 
        This method draws the bounding boxes of the detected objects 
        on the frame and returns the modified image.



    The yolo_detector class encapsulates the functionality of object detection using the YOLO model, 
    providing methods to perform detection, extract measurements, 
    and visualize the results on the frame. The class works in conjunction 
    with the YOLO model, which is loaded externally and used for the actual detection process.


    '''
    
    
    def __init__(self, height = 0, width = 0):
        modelpath = os.path.join(os.getcwd(), 'src', 'main', 'resources', 'detectors', 'yolo_darknet')
        # self.model = keras.models.load_model(modelpath, compile = False)
        self.model = load_model(modelpath, compile = False)
        
        self.class_names = load_class_names(CLASS_NAME)
        self.width = width
        self.height = height
        
    def getMeasurements(self, frame):
        
        self._detect(frame) # 5 sec, 20sec
        
        self.MeasurementsNumber = self.nums[0].numpy()
        # [x0 , y0 , x1 , y1]
        
        # assign a subset of bounding box coordinates to the numpyBox attribute of the 
        # yoloDetector instance:        
        self.numpyBox = self.boxes[0][:self.MeasurementsNumber].numpy()
        
        self.numpyBox[:, 0] = self.numpyBox[:, 0] * self.width
        self.numpyBox[:, 2] = self.numpyBox[:, 2] * self.width
        
        self.numpyBox[:, 1] = self.numpyBox[:, 1] * self.height
        self.numpyBox[:, 3] = self.numpyBox[:, 3] * self.height
        
        return self.numpyBox
        
    def insertDetectionInImg(self):
        img = draw_outputs(self.frame,
                           self.boxes,
                           self.scores,
                           self.classes,
                           self.nums,
                           self.class_names)
        return img
    
    def _detect(self, frame):
        self.frame = frame
        # resized_frame = expand_dims(frame, 0)
        resized_frame = expand_dims(frame, 0)
        resized_frame = resize_image(resized_frame, (MODEL_SIZE[0], MODEL_SIZE[1]))
         
        self.pred = self.model.predict(resized_frame, verbose = 0)
        
        self.boxes, self.scores, self.classes, self.nums = output_boxes( \
                                    self.pred, MODEL_SIZE,
                                    max_output_size = MAX_OUTPUT_SIZE,
                                    max_output_size_per_class = MAX_OUTPUT_SIZE_PER_CLASS,
                                    iou_threshold = IOU_THRESHOLD,
                                    confidence_threshold = CONFIDENCE_THRESHOLD)
    
    def drawDetection(self):
        
        num = self.numpyBox.shape[0]
        for i in range(num):
            left_coordinates = ((self.numpyBox[i,0:2]).astype(np.int32))
            right_coordinates = ((self.numpyBox[i,2:4]).astype(np.int32))
            self.frame = cv2.rectangle(self.frame, (left_coordinates), (right_coordinates), (255,0,0), 2)
        return self.frame

        
    
    