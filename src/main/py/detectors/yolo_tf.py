from tensorflow.keras.models import load_model
from tensorflow import image, expand_dims,  split, reshape, shape, concat
from tensorflow.image import combined_non_max_suppression

# https://saturncloud.io/blog/how-to-resolve-python-kernel-dies-on-jupyter-notebook-with-tensorflow-2/
# from .detector_utils import * 
import numpy as np
import os


MODEL_SIZE                = (416, 416, 3)
NUM_OF_CLASSES            = 80
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

    2. measure(self, frame): 
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
    
    
    def __init__(self, model, height = 0, width = 0):
        # modelpath = os.path.join(os.getcwd(), 'src', 'main', 'resources', 'detectors', 'yolo_darknet')
        self.model = model # load_model(modelpath, compile = False)

        with open(os.path.join(os.getcwd(), 'src', 'main', 'resources', 'detectors', 'yolo', 'v3', 'coco.names'), 'r') as f:
            self.class_names = f.read().splitlines()

        self.width = width
        self.height = height




        
    def detect(self, frame, t, outfile):
        # frame (1080, 1920, 3), resized_frame tf([1, 416, 416, 3])
        resized_frame = expand_dims(frame, 0)
        resized_frame = image.resize(resized_frame, (MODEL_SIZE[0], MODEL_SIZE[1]))
        
        detections = self.model.predict(resized_frame, verbose = 0).squeeze()
        # detections shape: (1, 10647, 85)
        

        xcenter = detections[:, 0].copy()
        # top_left_x = center_x - width / 2.0
        detections[:, 0] = xcenter - detections[:, 2] / 2.0  # top_left_x        
        # bottom_right_x = center_x + width / 2.0
        detections[:, 2] = xcenter + detections[:, 2] / 2.0  # bottom_right_x
        ycenter = detections[:, 1].copy()
        # top_left_y = center_y - height / 2.0
        detections[:, 1] = ycenter - detections[:, 3] / 2.0  # top_left_y
        # bottom_right_y = center_y + height / 2.0
        detections[:, 3] = ycenter + detections[:, 3] / 2.0  # bottom_right_y


        bbox, confs, class_probs = split(detections, [4, 1, -1], axis = -1)
        bbox = bbox / MODEL_SIZE[0]
        scores = confs * class_probs


        boxes, _, _, Nvalid = combined_non_max_suppression(
                            boxes = reshape(bbox, (1, -1, 1, 4)) # reshapedbox 
                                , scores = expand_dims(scores, axis = 0)  # reshape(scores, (1, -1, 1, 4)) # reshape(scores, (shape(scores)[0], -1, shape(scores)[-1]))
                                    , max_output_size_per_class = MAX_OUTPUT_SIZE_PER_CLASS
                                        , max_total_size = MAX_OUTPUT_SIZE
                                            , iou_threshold = IOU_THRESHOLD
                                                , score_threshold = CONFIDENCE_THRESHOLD)

        # Extract class indices with highest confidence
        class_indices = np.argmax(class_probs, axis = -1)

        # Extract class labels using the class_indices and class_names
        class_labels = [self.class_names[i] for i in class_indices]


        N = Nvalid[0].numpy()
        boxout = boxes[0][:N].numpy()
        
        # 
        # translate the normalized diagnonal of the bounding box to the size of the recorded frame:
        ## 
        boxout[:, [0, 2]] *= self.width # x1
        # boxout[:, 2] = boxout[:, 2] * self.width # x2
        
        boxout[:, [1, 3]] *= self.height # y1 
        # boxout[:, 3] = boxout[:, 3] * self.height # y2 
        # log
        # normalized box out coordinates 
        
        # Return both bounding boxes and object classifications
        return boxout, class_labels[:N]
        
