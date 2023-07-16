# import tensorflow as tf
import numpy as np
import cv2
from tensorflow import image
from tensorflow.image import combined_non_max_suppression
from tensorflow import split, reshape, shape, concat

def _non_max_suppression(inputs, model_size, max_output_size,
                        max_output_size_per_class, iou_threshold,
                        confidence_threshold):
    
    bbox, confs, class_probs = split(inputs, [4, 1, -1], axis=-1)
    bbox = bbox/model_size[0]
    scores = confs * class_probs
    boxes, scores, classes, valid_detections = \
                        combined_non_max_suppression(boxes = reshape(bbox, (shape(bbox)[0], -1, 1, 4)) 
                        , scores = reshape(scores, (shape(scores)[0], -1, shape(scores)[-1]))
                        , max_output_size_per_class = max_output_size_per_class
                        , max_total_size = max_output_size
                        , iou_threshold = iou_threshold
                        , score_threshold = confidence_threshold
    )
    return boxes, scores, classes, valid_detections


def resize_image(inputs, modelsize):
    '''
    Reshapes "inputs" to have "modelsize" dimensions.
    Parameters
    ----------
    inputs : numpy list
        Image input.
    modelsize : numpy list
        Reshaped dimensions.

    Returns
    -------
    TYPE
        DESCRIPTION.

    '''
    return image.resize(inputs, modelsize)

def load_class_names(file_name):
    with open(file_name, 'r') as f:
        class_names = f.read().splitlines()
    return class_names

def output_boxes(inputs,model_size, max_output_size, max_output_size_per_class,
                 iou_threshold, confidence_threshold):
    center_x, center_y, width, height, confidence, classes = \
        split(inputs, [1, 1, 1, 1, 1, -1], axis=-1)
    
    top_left_x = center_x - width / 2.0
    top_left_y = center_y - height / 2.0
    bottom_right_x = center_x + width / 2.0
    bottom_right_y = center_y + height / 2.0
    inputs = concat([top_left_x, top_left_y, bottom_right_x,
                        bottom_right_y, confidence, classes], axis=-1)
    
    boxes_dicts = _non_max_suppression(inputs, model_size, max_output_size,
                                      max_output_size_per_class, iou_threshold, confidence_threshold)
    
    return boxes_dicts

def draw_outputs(img, boxes, objectness, classes, nums, class_names):
    boxes, objectness, classes, nums = boxes[0], objectness[0], classes[0], nums[0]
    boxes=np.array(boxes)
    for i in range(nums):
        
        left_coordinates = tuple((boxes[i,0:2] * [img.shape[1],img.shape[0]]).astype(np.int32))
        right_coordinates = tuple((boxes[i,2:4] * [img.shape[1],img.shape[0]]).astype(np.int32))
        img = cv2.rectangle(img, (left_coordinates), (right_coordinates), (255,0,0), 2)
        img = cv2.putText(img, '{} {:.4f}'.format(
            class_names[int(classes[i])], objectness[i]),
                          (left_coordinates), cv2.FONT_HERSHEY_PLAIN,
                          1, (0, 0, 255), 2)
    return img
