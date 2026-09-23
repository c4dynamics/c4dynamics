# yolov3

YOLO: Real-Time Object Detection

`yolov3` is a YOLOv3 (You Only Look Once) object detection model.
Though it is no longer the most accurate object detection algorithm,
YOLOv3 is still a very good choice when you need real-time detection
while maintaining excellent accuracy.

YOLOv3 processes an entire image in a single forward pass,
making it efficient for dynamic scenes.
Its key strength lies the ability to simultaneously
predict bounding box coordinates and class probabilities
for multiple objects within an image.

Parameters
==========
weights_path : str, optional
    Path to the YOLOv3 weights file. Defaults None.

See Also
========
.filters
.pixelpoint

**Classes**

Using YOLOv3 means
object detection capability with the 80 pre-trained
classes that come with the COCO dataset.

The following 80 classes are available using COCO's pre-trained weights:

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

*Figure 1*:
Object Detection with YOLO using COCO pre-trained classes 'dog', 'bicycle', 'truck'.
Read more at: `darknet-yolo <https://pjreddie.com/darknet/yolo/>`_.

**Implementation (c4dynamics)**

The `yolov3` class abstracts the complexities of model initialization,
input preprocessing, and output parsing.
The `detect` method returns a
`pixelpoint`
for each detected object.
The `pixelpoint` is a `predefined state class`
representing a data point in a video frame with an associated bounding box.
Its methods and properties enhance the YOLOv3 output structure,
providing a convenient data structure for handling tracking missions.

**Installation**

C4dynamics downloads
the YOLOv3' weights file
once at first call to `yolov3` and saves it to the cache.
For further details see `datasets`.
Alternatively, the user can provide a path to his
own weights file using the parameter `weights_path`.

**Construction**

A YOLOv3 detector instance is created by making a direct call
to the `yolov3` constructor:

```python
>>> from c4dynamics.detectors import yolov3
>>> yolo3 = yolov3()
Fetched successfully
```
Initialization of the instance does not require any mandatory parameters.

Example
=======

The following snippet initializes the YOLOv3 model and
runs the `detect()` method on an image containing four airplanes.
The example uses the `datasets` module from `c4dynamics` to fetch an image.
For further details, see `c4dynamics.datasets`.

Import required packages:

```python
>>> import cv2
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
```
Load YOLOv3 detector:

```python
>>> yolo3 = c4d.detectors.yolov3()
Fetched successfully
```
Fetch and read the image:

```python
>>> imagepath = c4d.datasets.image('planes')
Fetched successfully
>>> img = cv2.imread(imagepath)
```
Run YOLOv3 detector on an image:

```python
>>> pts = yolo3.detect(img)
```
Now `pts` consists of
`pixelpoint`
instances for each object detected in the frame.
Let's use the properties and methods of the `pixelpoint` class to
view the attributes of the detected objects:

```python
>>> def ptup(n): return '(' + str(n[0]) + ', ' + str(n[1]) + ')'
>>> print('{:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}'.format('center x', 'center y', 'box top-left', 'box bottom-right', 'class', 'frame size')) # doctest: +IGNORE_OUTPUT
>>> for p in pts:
...   print('{:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}'.format(p.x, p.y, ptup(p.box[0]), ptup(p.box[1]), p.class_id, ptup(p.fsize)))     # doctest: +IGNORE_OUTPUT
...   cv2.rectangle(img, p.box[0], p.box[1], [0, 0, 0], 2)      # +IGNORE_OUTPUT
...   point = (int((p.box[0][0] + p.box[1][0]) / 2 - 75), p.box[1][1] + 22)     # doctest: +IGNORE_OUTPUT
...   cv2.putText(img, p.class_id, point, cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 0, 0], 2)     # doctest: +IGNORE_OUTPUT
center x  |  center y  |   box top-left   | box bottom-right |   class    |   frame size
  615     |    295     |    (562, 259)    |    (668, 331)    | aeroplane  |  (1280, 720)
  779     |    233     |    (720, 199)    |    (838, 267)    | aeroplane  |  (1280, 720)
  635     |    189     |    (578, 153)    |    (692, 225)    | aeroplane  |  (1280, 720)
  793     |    575     |    (742, 540)    |    (844, 610)    | aeroplane  |  (1280, 720)
```

```python
>>> plt.figure() # doctest: +IGNORE_OUTPUT
>>> plt.axis(False) # doctest: +IGNORE_OUTPUT
>>> plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) # doctest: +IGNORE_OUTPUT
```

### `confidence_th`

```python
confidence_th(self) -> float
```

Gets and sets the confidence threshold used in the object detection.

Detected objects with confidence scores below this threshold are filtered out.

### Parameters
confidence_th : float
    The new confidence threshold for object detection.
    Defaults: `confidence_th = 0.5`.

### Returns
confidence_th : float
    The confidence threshold for object detection.
    Detected objects with confidence scores below this threshold are filtered out.

### Example
Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import cv2
```
Fetch 'planes.png' using the c4dynamics' datasets module (see `c4dynamics.datasets`):

```python
>>> impath = c4d.datasets.image('planes')
Fetched successfully
```
Load YOLOv3 detector and set 3 confidence threshold values to compare:

```python
>>> yolo3 = c4d.detectors.yolov3()
Fetched successfully
>>> confidence_thresholds = [0.9, 0.95, 0.99]
```
Run the detector on each threshold:

```python
>>> _, axs = plt.subplots(1, 3)
>>> for i, confidence_threshold in enumerate(confidence_thresholds):
...   yolo3.confidence_th = confidence_threshold
...   img = cv2.imread(impath)
...   pts = yolo3.detect(img)
...   for p in pts:
...     cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2) # doctest: +IGNORE_OUTPUT
...   axs[i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # doctest: +IGNORE_OUTPUT
...   axs[i].set_title(f"Confidence Threshold: {confidence_threshold}", fontsize = 6)
...   axs[i].axis('off') # doctest: +IGNORE_OUTPUT
```

A single object being missed, particularly when setting the confidence threshold to 0.99,
suggests that the model is highly confident in its predictions.
This level of performance is typically achievable when the model
has been trained on a diverse and representative dataset,
encompassing a wide variety of object instances, backgrounds,
and conditions.

### `detect`

```python
detect(self, frame: numpy.ndarray) -> list[c4dynamics.states.lib.pixelpoint.pixelpoint]
```

Detects objects in a frame using the YOLOv3 model.

At each call, the detector performs the following steps:

1. Preprocesses the frame by creating a blob, normalizing pixel values, and swapping Red
   and Blue channels.
2. Sets input to the YOLOv3 model and performs a forward pass to obtain detections.
3. Extracts detected objects based on a confidence threshold, calculates bounding box
   coordinates, and filters results using Non-Maximum Suppression (NMS).

### Parameters
frame : numpy.array
    An input frame for object detection.

### Returns
out : list[pixelpoint]
    A list of `pixelpoint` objects
    representing detected objects,
    each containing bounding box coordinates and class label.

### Examples
**Setup**

Import required packages:

```python
>>> import cv2  # opencv-python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
```
Fetch 'planes.png' and 'aerobatics.mp4' using the c4dynamics' datasets
module (see `c4dynamics.datasets`):

```python
>>> impath = c4d.datasets.image('planes')
Fetched successfully
>>> vidpath = c4d.datasets.video('aerobatics')
Fetched successfully
```
Load YOLOv3 detector:

```python
>>> yolo3 = c4d.detectors.yolov3()
Fetched successfully
```
Let the auxiliary function:

```python
>>> def ptup(n): return '(' + str(n[0]) + ', ' + str(n[1]) + ')'
```
**Object detection in a single frame**

```python
>>> img = cv2.imread(impath)
>>> pts = yolo3.detect(img)
>>> for p in pts:
...   cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2) # doctest: +IGNORE_OUTPUT
```

```python
>>> plt.figure() # doctest: +IGNORE_OUTPUT
>>> plt.axis(False) # doctest: +IGNORE_OUTPUT
>>> plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) # doctest: +IGNORE_OUTPUT
```

**Object detection in a video**

```python
>>> video_cap = cv2.VideoCapture(vidpath)
>>> while video_cap.isOpened():
...   ret, frame = video_cap.read()
...   if not ret: break
...   pts = yolo3.detect(frame)
...   for p in pts:
...     cv2.rectangle(frame, p.box[0], p.box[1], [0, 255, 0], 2) # doctest: +IGNORE_OUTPUT
...     cv2.imshow('YOLOv3', frame)  # doctest: +IGNORE_OUTPUT
...   cv2.waitKey(10) # doctest: +IGNORE_OUTPUT
```

**The output structure**

The output of the detect() function is a list of `pixelpoint` object.
The `pixelpoint` has unique attributes to manipulate the detected object class and
bounding box.

```python
>>> print('{:^10} | {:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}' # doctest: +IGNORE_OUTPUT
...             .format('# object', 'center x', 'center y', 'box top-left', 'box bottom-right', 'class', 'frame size'))
>>> # main loop:
>>> for i, p in enumerate(pts):
...   print('{:^10d} | {:^10.3f} | {:^10.3f} | {:^16} | {:^16} | {:^10} | {:^14}'
...         .format(i, p.x, p.y, ptup(p.box[0]), ptup(p.box[1]), p.class_id, ptup(p.fsize)))
...   cv2.rectangle(img, p.box[0], p.box[1], [0, 0, 0], 2)      # doctest: +IGNORE_OUTPUT
...   point = (int((p.box[0][0] + p.box[1][0]) / 2 - 75), p.box[1][1] + 22)
...   cv2.putText(img, p.class_id, point, cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 0, 0], 2)  # doctest: +IGNORE_OUTPUT
# object  |  center x  |  center y  |   box top-left   | box bottom-right |   class    |  frame size
   0      |   0.584    |   0.376    |    (691, 234)    |    (802, 306)    | aeroplane  |  (1280, 720)
   1      |   0.457    |   0.473    |    (528, 305)    |    (642, 376)    | aeroplane  |  (1280, 720)
   2      |   0.471    |   0.322    |    (542, 196)    |    (661, 267)    | aeroplane  |  (1280, 720)
   3      |   0.546    |   0.873    |    (645, 588)    |    (752, 668)    | aeroplane  |  (1280, 720)
```

```python
>>> plt.figure()  # doctest: +IGNORE_OUTPUT
>>> plt.axis(False) # doctest: +IGNORE_OUTPUT
>>> plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))  # doctest: +IGNORE_OUTPUT
```

### `nms_th`

```python
nms_th(self) -> float
```

Gets and sets the Non-Maximum Suppression (NMS) threshold.

Objects with confidence scores below this threshold are suppressed.

### Parameters
nms_th : float
    The new threshold value for NMS during object detection.
    Defaults: `nms_th = 0.5`.

### Returns
nms_th : float
    The threshold value used for NMS during object detection.
    Objects with confidence scores below this threshold are suppressed.

### Example
Import required packages:

```python
>>> import c4dynamics as c4d
>>> from matplotlib import pyplot as plt
>>> import cv2
```
Fetch 'planes.png' using the c4dynamics' datasets module (see `c4dynamics.datasets`):

```python
>>> impath = c4d.datasets.image('planes')
Fetched successfully
```
Load YOLOv3 detector and set 3 NMS threshold values to compare:

```python
>>> yolo3 = c4d.detectors.yolov3()
Fetched successfully
>>> nms_thresholds = [0.1, 0.5, 0.9]
```
Run the detector on each threshold:

```python
>>> _, axs = plt.subplots(1, 3)
>>> for i, nms_threshold in enumerate(nms_thresholds):
...   yolo3.nms_th = nms_threshold
...   img = cv2.imread(impath)
...   pts = yolo3.detect(img)
...   for p in pts:
...     cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2) # doctest: +IGNORE_OUTPUT
...   axs[i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)) # doctest: +IGNORE_OUTPUT
...   axs[i].set_title(f"NMS Threshold: {nms_threshold}", fontsize = 6)
...   axs[i].axis('off') # doctest: +IGNORE_OUTPUT
```

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

