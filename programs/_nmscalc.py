import matplotlib.pyplot as plt
plt.style.use('dark_background')  
import numpy as np


def nms_boxes(boxes, scores, threshold = 0.5, overlap_threshold = 0.5):
    # Sort boxes based on their scores (highest to lowest)
    sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    boxes = [boxes[i] for i in sorted_indices]
    scores = [scores[i] for i in sorted_indices]

    # Initialize list to store indices of selected boxes
    selected_indices = []

    while len(boxes) > 0:
        # Pick the box with the highest score (top box)
        top_box = boxes[0]
        selected_indices.append(sorted_indices[0])

        # Calculate IoU between top box and remaining boxes
        ious = [calculate_iou(top_box, box) for box in boxes[1:]]
        
        # Filter boxes based on overlap threshold
        filtered_indices = [i for i, iou in enumerate(ious) if iou < overlap_threshold]
        
        # Update boxes and scores
        # filtered_indices is not including the top_box then all its index is 
        #   in 1 step after boxes. 
        boxes = [boxes[i + 1] for i in filtered_indices]
        scores = [scores[i + 1] for i in filtered_indices]
        sorted_indices = [sorted_indices[i + 1] for i in filtered_indices]

    return selected_indices


def calculate_iou(box1in, box2in):
    # Calculate intersection coordinates

    # box1in, box2in: xmin, ymin, width, heigh
    # box1, box2: xmin, ymin, xmax, ymax

    box1 = [box1in[0], box1in[1], box1in[0] + box1in[2], box1in[1] + box1in[3]]
    box2 = [box2in[0], box2in[1], box2in[0] + box2in[2], box2in[1] + box2in[3]]

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    # Calculate intersection area
    intersection_area = max(0, x2 - x1 + 1) * max(0, y2 - y1 + 1)

    # Calculate union area
    box1_area = (box1[2] - box1[0] + 1) * (box1[3] - box1[1] + 1)
    box2_area = (box2[2] - box2[0] + 1) * (box2[3] - box2[1] + 1)
    union_area = box1_area + box2_area - intersection_area

    # Calculate IoU
    iou = intersection_area / union_area

    return iou


def draw_boxes(boxes, image_width, image_height, idx):
    # Create a figure with specified image dimensions
    fig, ax = plt.subplots(figsize=(image_width / 100, image_height / 100))  # Convert to inches

    # Plot the image frame (optional)
    ax.set_xlim(0, image_width)
    ax.set_ylim(image_height, 0)  # Inverted y-axis for images

    # Plot each bounding box
    for i, box in enumerate(boxes):
        lwidth = 3 if len([j for j in idx if i == j]) else 1
        x_min, y_min, width, height = box
        rect = plt.Rectangle((x_min, y_min), width, height, fill = False, edgecolor = np.random.rand(3), linewidth = lwidth)
        ax.add_patch(rect)

    # Show the plot
    plt.show()



#        top left x, top left y, width, height
boxes = [[779.6349906921387, 415.12992292642593, 773.5513687133789, 137.67999351024628]
            , [853.2427024841309, 415.86905390024185, 678.654899597168, 137.33212172985077]
            , [513.876371383667, 518.1469541788101, 489.034481048584, 235.73955416679382]
            , [472.5542163848877, 618.9133197069168, 511.5743064880371, 178.33568930625916]
            , [481.8397521972656, 601.2791848182678, 551.5726089477539, 198.20683479309082]
            , [550.2194881439209, 522.8721387684345, 422.5604438781738, 113.7124952673912]
            , [514.421796798706, 531.2718115746975, 495.76818466186523, 111.07096463441849]]

# scores = [0.9, 0.75, 0.8, 0.85]
scores = [0.9941151738166809, 0.9889332056045532, 0.51142418384552, 0.7718912959098816, 0.9523084163665771, 0.551020085811615, 0.9651079773902893]

# Threshold for confidence score (e.g., 0.8)
confidence_threshold = 0.5
# Overlap threshold for NMS (e.g., 0.5)
overlap_threshold = 0.5

# Apply Non-Maximum Suppression using custom nms_boxes function
indices = nms_boxes(boxes, scores, confidence_threshold, overlap_threshold)

# Display the indices of selected boxes after NMS
print("Indices of selected boxes after NMS:", indices)

image_width = 1920
image_height = 1080

draw_boxes(boxes, image_width, image_height, indices)









