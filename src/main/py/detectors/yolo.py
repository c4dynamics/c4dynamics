from tensorflow.keras.models import load_model
from tensorflow import image, expand_dims,  split, reshape, shape, concat
from tensorflow.image import combined_non_max_suppression

# https://saturncloud.io/blog/how-to-resolve-python-kernel-dies-on-jupyter-notebook-with-tensorflow-2/
# from .detector_utils import * 
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

        performs the actual object detection on the given frame. 
        It preprocesses the frame, resizes it to match the model's input size, 
        and passes it through the YOLO model to obtain the bounding box coordinates, 
        scores, class predictions, and the number of detected objects.




    The yolo_detector class encapsulates the functionality of object detection using the YOLO model, 
    providing methods to perform detection, extract measurements, 
    and visualize the results on the frame. The class works in conjunction 
    with the YOLO model, which is loaded externally and used for the actual detection process.


    '''
    
    
    def __init__(self, height = 0, width = 0):
        modelpath = os.path.join(os.getcwd(), 'src', 'main', 'resources', 'detectors', 'yolo_darknet')
        self.model = load_model(modelpath, compile = False)

        with open(CLASS_NAME, 'r') as f:
            self.class_names = f.read().splitlines()

        self.width = width
        self.height = height
        
    def getMeasurements(self, frame, t, outfile):
        
        resized_frame = expand_dims(frame, 0)
        resized_frame = image.resize(resized_frame, (MODEL_SIZE[0], MODEL_SIZE[1]))
        
        pred = self.model.predict(resized_frame, verbose = 0)
        
        center_x, center_y, width, height, confidence, classes = split(pred, [1, 1, 1, 1, 1, -1], axis = -1)
        
        top_left_x = center_x - width / 2.0
        top_left_y = center_y - height / 2.0
        bottom_right_x = center_x + width / 2.0
        bottom_right_y = center_y + height / 2.0

        pred = concat([top_left_x, top_left_y, bottom_right_x, bottom_right_y, confidence, classes], axis = -1)
        
        bbox, confs, class_probs = split(pred, [4, 1, -1], axis = -1)
        bbox = bbox / MODEL_SIZE[0]
        scores = confs * class_probs

        # 
        # 
        #   Non-maximum suppression (NMS) is a technique often used in computer vision 
        #       and object detection tasks. Its primary purpose is to reduce the number 
        #       of bounding boxes or regions that are output by an object detection algorithm, 
        #       ensuring that only the most relevant and highest-scoring boxes are kept 
        #       while eliminating redundant or overlapping ones.
        #
        #   combined_non_max_suppression()
        #       https://www.tensorflow.org/api_docs/python/tf/image/combined_non_max_suppression
        #       Greedily \\ agressively \\ selects a subset of bounding boxes in descending order of score.
        #       This operation performs non_max_suppression on the inputs per batch, 
        #       across all classes. 
        #       Prunes \\ cuts\\ away boxes that have high intersection-over-union (IOU) overlap 
        #       with previously selected boxes. 
        #       Bounding boxes are supplied as [y1, x1, y2, x2], where (y1, x1) and (y2, x2) are 
        #       the coordinates of any diagonal pair of box corners and the coordinates can be 
        #       provided as normalized (i.e., lying in the interval [0, 1]) or absolute. 
        #       Note that this algorithm is agnostic to where the origin is in the coordinate 
        #       system. 
        # 
        #       Also note that this algorithm is invariant to orthogonal transformations 
        #       and translations of the coordinate system; thus translating or reflections 
        #       of the coordinate system result in the same boxes being selected by the algorithm. 
        #       The output of this operation is the final boxes, scores and classes tensor 
        #       returned after performing non_max_suppression.
        ## 
        boxes, _, _, nums = combined_non_max_suppression(
                            boxes = reshape(bbox, (shape(bbox)[0], -1, 1, 4)) 
                                , scores = reshape(scores, (shape(scores)[0], -1, shape(scores)[-1]))
                                    , max_output_size_per_class = MAX_OUTPUT_SIZE_PER_CLASS
                                        , max_total_size = MAX_OUTPUT_SIZE
                                            , iou_threshold = IOU_THRESHOLD
                                                , score_threshold = CONFIDENCE_THRESHOLD)


        if outfile is not None: 
            with open(outfile, 'at') as file:
                # file.write(f't: {t}, box: {reshape(bbox, (shape(bbox)[0], -1, 1, 4))}, scores: {scores} \n')
                file.write(f't: {t} \nboxes: \n\t{boxes[:, :nums[0].numpy()]} \n')




        MeasurementsNumber = nums[0].numpy()
        numpyBox = boxes[0][:MeasurementsNumber].numpy()
        
        numpyBox[:, 0] = numpyBox[:, 0] * self.width
        numpyBox[:, 2] = numpyBox[:, 2] * self.width
        
        numpyBox[:, 1] = numpyBox[:, 1] * self.height
        numpyBox[:, 3] = numpyBox[:, 3] * self.height
        
        return numpyBox
        
