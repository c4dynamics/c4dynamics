import os
import cv2
import numpy as np


MODEL_SIZE           = (416, 416, 3)
CONFIDENCE_THRESHOLD = 0.5
NMS_THRESHOLD        = 0.5 # .3

class yolo:
    

    def __init__(self):
        yolov3 = os.path.join('c4dynamics', 'src', 'main', 'resources', 'detectors', 'yolo', 'v3')
        weights_path = os.path.join(yolov3, 'yolov3.weights')
        cfg_path     = os.path.join(yolov3, 'yolov3.cfg')
        coconames    = os.path.join(yolov3, 'coco.names')

        self.net = cv2.dnn.readNetFromDarknet(cfg_path, weights_path)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

        ln = self.net.getLayerNames()
        self.ln = [ln[i - 1] for i in self.net.getUnconnectedOutLayers()]


        with open(coconames, 'r') as f:
            self.class_names = f.read().strip().split('\n')


    
    def detect(self, frame, t, outfile):

        #
        # Step 1: Preprocess the Frame
        #   - Create a blob (binary large object) from the input frame with the specified dimensions
        #   - Normalize pixel values to a range of 0 to 1
        #   - Specify the dimensions of the input layer of the YOLO model
        #   - Swap Red and Blue channels (BGR to RGB)
        #   - Set crop to False to preserve the original aspect ratio
        ##
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (MODEL_SIZE[0], MODEL_SIZE[1]), swapRB = True, crop = False)

        #
        # Step 2: Set Input to the YOLO Model and Perform Forward Pass
        #   - Set the blob as the input to the YOLO model
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
        boxes = []
        confidences = []
        classIDs = []
        h, w = frame.shape[:2]

        for detection in detections:
            for d in detection:
                
                scores = d[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                if scores[classID] > CONFIDENCE_THRESHOLD:  # Adjust the confidence threshold as needed

                    box = d[:4] * np.array([w, h, w, h])
                    (center_x, center_y, width, height) = box.astype('int')

                    x = int(center_x - (width / 2)) # left edge 
                    y = int(center_y - (height / 2)) # top edge 

                    boxes.append([x, y, int(width), int(height)]) # top left x, top left y, width, height
                    confidences.append(float(confidence))
                    classIDs.append(classID)        

        indices = cv2.dnn.NMSBoxes(boxes, confidences, CONFIDENCE_THRESHOLD, NMS_THRESHOLD)
        
        box_out = []
        class_out = []

        if len(indices) > 0:
            for i in indices.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])
                box_out.append([x, y, x + w, y + h])
                class_out.append(self.class_names[classIDs[i]])
        box_out = np.array(box_out)
        
        return box_out, class_out
