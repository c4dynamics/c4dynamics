- [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/c4dynamics/c4dynamics/blob/main/docs/source/programs/car_tracker.ipynb) ← Click to open in Google Colab
- To download this notebook, click the download icon in the toolbar above and select the .ipynb format.  
- For any questions or comments, please open an issue on the [c4dynamics issues page](https://github.com/c4dynamics/c4dynamics/issues).  


# Car Tracker – YOLO Detector and Kalman Filter 

This notebook demonstrates how to enhance object tracking by integrating a Kalman filter with an object detection model. 

Object detection models are widely used in computer vision to identify and localize objects in images and videos. However, raw detections often suffer from inconsistencies—bounding boxes may jitter across frames, and objects may momentarily disappear due to occlusions or detection failures.

While this implementation demonstrates tracking with YOLOv3, it is designed to be compatible with various object detection models.

To enhance tracking, a Kalman filter is used to:

- Smooth detections, reducing noise in bounding box positions.
- Handle missing detections by predicting object locations.

This notebook provides two tracking modes:

- Steady-state tracking – Uses a precomputed, fixed Kalman gain for the entire runtime.
- Adaptive covariance tracking – Dynamically adjusts the measurement covariance to account for variations in object movement.


<div style='text-align: center;'>
  <img src='car_tracker.drawio.png' alt='alt text'>
  <figcaption>Figure 1: Program flowchart: 1. Read an image. 2. Run the detector. 3. Update the object state. 4. Draw a bounding box </figcaption>
</div>

 - Object tracking starts with a source of images, such as a video stream or an image loader. 
 - Each frame is sent to the object detection model, and the returned data is used to filter undesired objects and update the vehicle state. 
 - The state is managed by the Kalman filter which holds the equations that describe the vehicle motion and the measurement properties. 
 - The up-to-date position can now be drawn on the screen. This cycle repeats until the last frame in the images source.  

Let's now break it down step by step.  
First, import the necessary packages: 

```python


# Check if Google Colab is running:
import sys
IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
	!pip install c4dynamics
	from google.colab.patches import cv2_imshow


```


```python


import cv2
import numpy as np
from IPython.display import Video
from matplotlib import pyplot as plt
from c4dynamics import plotdefaults
plt.style.use('dark_background')


```


## Video Dataset

The program uses a video from a free stock website, [available here](https://www.pexels.com/video/a-car-drifting-on-a-racing-track-4568686/).  
You can use c4dynamics [datasets module](https://c4dynamics.github.io/c4dynamics/api/Datasets.html) to fetch this file directly:

```python


from c4dynamics import datasets
video = datasets.video('drifting_car')


```


`video` is now holding a path to the cached video file:

```python


Video(video, width = 640, height = 360, embed = True)


```


### Video Setup

Image processing operations are performed using `opencv`. Let's configure the video capture:

```python


video_cap = cv2.VideoCapture(video)
fps = video_cap.get(cv2.CAP_PROP_FPS)
dt = 1 / fps


```


Define a video writer to save the results:

```python


width, height = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
vidout = cv2.VideoWriter('car_detected.mp4', int(video_cap.get(cv2.CAP_PROP_FOURCC)), fps, (width, height))


```


## YOLOv3

### Real-Time Object Detection

YOLO (You Only Look Once) v3 is the third generation of the popular object detection model. 
Although no longer the most accurate object detection algorithm, YOLOv3 remains a strong choice for real-time detection with good accuracy.

This implementation demonstrates tracking with YOLOv3 because c4dynamics provides a streamlined API to manage interactions with it. However, it can be replaced with any object detection model that outputs bounding boxes and classification labels.


YOLOv3 processes an entire image in a single forward pass, making it efficient for dynamic scenes. Its key strength lies in its ability to simultaneously predict bounding box coordinates and class probabilities for multiple objects within an image.

### Classes

YOLOv3 provides object detection capabilities with 80 pre-trained classes from the COCO dataset.
The following 80 classes are available using COCO’s pre-trained weights:



`person`, `bicycle`, `car`, `motorcycle`, `airplane`, `bus`, `train`, `truck`, `boat`, `traffic light`, `fire hydrant`, `stop sign`, `parking meter`, `bench`, `bird`, `cat`, `dog`, `horse`, `sheep`, `cow`, `elephant`, `bear`, `zebra`, `giraffe`, `backpack`, `umbrella`, `handbag`, `tie`, `suitcase`, `frisbee`, `skis,snowboard`, `sports ball`, `kite`, `baseball bat`, `baseball glove`, `skateboard`, `surfboard`, `tennis` `racket`, `bottle`, `wine glass`, `cup`, `fork`, `knife`, `spoon`, `bowl`, `banana`, `apple`, `sandwich`, `orange`, `broccoli`, `carrot`, `hot dog`, `pizza`, `donut`, `cake`, `chair`, `couch`, `potted plant`, `bed`, `dining table`, `toilet`, `tv`, `laptop`, `mouse`, `remote`, `keyboard`, `cell phone`, `microwave`, `oven`, `toaster`, `sink`, `refrigerator`, `book`, `clock`, `vase`, `scissors`, `teddy bear`, `hair drier`, `toothbrush`

<div style='text-align: center;'>
  <img src='../../_architecture/yolo-object-detection.jpg' alt='alt text'>
  <figcaption>Figure 2: Object Detection with YOLO using COCO pre-trained classes 'dog', 'bicycle', 'truck'. </figcaption>
</div>

Read more at: [darknet-yolo](https://pjreddie.com/darknet/yolo). 

### API

C4dynamics provides a simple API to manage interactions with the `YOLOv3` model through OpenCV’s neural network interface. The [datasets module](https://c4dynamics.github.io/c4dynamics/api/Datasets.html) downloads the YOLOv3’ weights file and saves it in the cache. 
Calling [c4dynamics.detectors.yolov3](https://c4dynamics.github.io/c4dynamics/api/detectors.yolov3) creates an instance of the YOLOv3 detector:

```python


from c4dynamics.detectors import yolov3
yolo3 = yolov3();


```


The method [detect](https://c4dynamics.github.io/c4dynamics/api/generated/yolov3/c4dynamics.detectors.yolo3_opencv.yolov3.detect.html) returns a `pixelpoint` representing each detected object in the input image.  
[pixelpoint](https://c4dynamics.github.io/c4dynamics/api/states.lib.pixelpoint.html) is a predefined state class representing a data-point in an image frame with an associated bounding box. 

```python


from c4dynamics import pixelpoint
print(pixelpoint())


```


`x` and `y` represent the center pixel of the detected object while `w` and `h` define the width and height of its bounding box. `pixelpoint` includes also data attributes encapsulating the object `classification` and the `size` of the target image. 

Working with `pixelpoint` objects streamlines integration with the Kalman filter, where YOLOv3 detections serve as inputs to update the car’s state.

## Kalman Filter

The Kalman filter optimally and smoothly tracks the vehicle despite errors in detection measurements or even in the absence of valid detections. 
The Kalman state vector acts as a snapshot of the tracked vehicle at each moment in time. 
The state vector includes variables such as position, velocity, and bounding box size. 

When the filter is initialized, the vehicle state is defined for the first time. 
When prior knowledge is unavailable, the state is usually initialized with zeros or a reasonable estimate.  
Then, using the vehicle’s equations of motion, the next state is estimated in the `prediction` step. 
Finally, when a valid detection is available, the measured position and bounding box size are used to update the Kalman state. This step is called `update` or `correct`.

To define a Kalman filter we should first agree on the dynamic model that represents the process, i.e. the vehicle motion, then to describe the detection and the noise properties of its measures. 

### Equations of Motion

Let's assume the car moves with constant velocity.

The equations of motion represent the car dynamics by a set of first order difference equations:

$$
  {x_c}_{k+1} = {x_c}_k + {v_x}_k \cdot dt \\
  {y_c}_{k+1} = {y_c}_k + {v_y}_k \cdot dt \\
  w_{k+1} = w_k    \\
  h_{k+1} = h_k    \\
  {v_x}_{k+1} = {v_x}_k  \\
  {v_y}_{k+1} = {v_y}_k  \\
$$

Where: 
- $x_c, y_c$ are the coordinates of the center pixel
- $w, h$ are the bounding box width and height 
- $v_x, v_y$ are the velocities of the object in $pixel/second$
- $dt$ is the time between frames $dt = 1/fps$ ($fps$ = frame per second) 
- $k$ is a discrete time variable
    
These equations imply constant velocity motion and a fixed bounding box size.

In a state space form, these equations are given by: 

$$ x_{k+1} = F \cdot x_k + \eta_k $$

Where:
- $x$ is the system state vector: $x = [x_c, y_c, w, h, v_x, v_y]^T$
- $F$ is the state matrix:  

$$
F = \begin{bmatrix}
        1   &   0   &   0   &   0   &   dt   &   0   \\
        0   &   1   &   0   &   0   &   0   &   dt   \\
        0   &   0   &   1   &   0   &   0   &   0   \\
        0   &   0   &   0   &   1   &   0   &   0   \\
        0   &   0   &   0   &   0   &   1   &   0   \\
        0   &   0   &   0   &   0   &   0   &   1 
      \end{bmatrix}  
$$  

- $\eta$ is an uncertainty in the process equations. 
  

```python


# process dynamics
F = np.eye(6)
F[0, 4] = F[1, 5] = dt


```


$\eta$ is white noise with mean zero and covariance matrix $Q$. The diagonal of $Q$ represents the variances of each vairable in $x$. 
The weight of $Q$ is determined in comparison to the measuremnt covariance $R$, therefore its will be initialized in the next paragraph. 

### Measurement

Recall that yolov3 detection returns a `pixelpoint` object. The state of a pixelpoint consists of center pixel and bounding box size that use to correct the kalman estimations. It also consists of a classification label that can use to filter undesired objects, i.e. no cars, in our case.  

Since the objects detector provides measurements of the center pixel and the bounding box size ($[x_c, y_c, w, h]^T$), we can write the measurement equations as: 
$$
y_k = H \cdot x_k + \nu_k
$$
Where: 
- $y$ is the estimation of the measurement.
- $H$ is the matrix that relates the system state to the measurement: 

$$
  H = \begin{bmatrix}
        1 & 0 & 0 & 0 & 0 & 0 \\
        0 & 1 & 0 & 0 & 0 & 0 \\
        0 & 0 & 1 & 0 & 0 & 0 \\
        0 & 0 & 0 & 1 & 0 & 0 
      \end{bmatrix}  
$$

- $x$ is the system state as defined above. 
- $\nu$ represents the measurement noise with mean zero and covariance matrix $R$. 

```python


H = np.zeros((4, 6))
H[range(4), range(4)] = 1


```


The diagonal of $R$ represents the variance of each measured vairable.  
Determining the actual error of the detection model requires some experience. 
We set the noise at one sigma (standard deviation) to be a fraction of the image width: 

```python


measure_std = width / 10000
R = np.eye(4) * measure_std**2    # measurement covariance
Q = np.eye(6) * measure_std**2    # process covariance


```


This preset of $Q$ and $R$ means none of them has advantage over the other, i.e. estimates based on predictions and corrections based on input detection accept the same weight.  
Later we will experience with a number of different values for $R$ and view the effect of it on the estimation performances. 

### Observability

Having defined the dynamics and the measurement matrix we can now calculate the observability matrix. 
The rank number must equal the system order to guarentee successful state estimation.

$$
  \mathcal{O} = \begin{bmatrix}
        H           \\
        H \cdot F   \\
        H \cdot F^2 \\
          \vdots    \\
        H \cdot F^{n-1}
      \end{bmatrix}  
$$

Where $\mathcal{O}$ is the observability matrix, $H$ is the measurement matrix, $F$ is the dynamics matrix, and $n$ is the system order (here $n=6$). 

```python


O = H
n = len(F)
for i in range(1, n):
  O = np.vstack((O, H @ np.linalg.matrix_power(F, i)))
rank = np.linalg.matrix_rank(O)
print(f'The system is observable (rank = n = {n}).' if rank == n else 'The system is not observable (rank = {rank), n = {n}).')


```


### Kalman Methods

The [kalman](https://c4dynamics.github.io/c4dynamics/api/filters.kalman.html) class of c4dynamics implements the equations to run the filter seamlessly without unnecessary overhead.  

Initialization occurs when creating the Kalman filter.  
The state vector with its initial conditions have to be introduced, as well as the matrices representing the dynamics and the measurement.

`predict` solves the dynamic equations and `update` corrects the estimations for each new input measurement. 

## Algorithm

### 1) Steady State Mode 

The system so far defined is time invariant. 
This property enables running the filter in a steady-state mode. That is, the system covariance ($P$) and the Kalman gain ($K$) can be evaluated once and use for all the updates during the run-time. 

Let's plug in all the parameters we have defined to initalize a Kalman object in a steady-state mode:

```python


from c4dynamics.filters import kalman
# create a kalman filter
kf = kalman({'x': 0, 'y': 0, 'w': 0, 'h': 0, 'vx': 0, 'vy': 0}, F = F, H = H, Q = Q, R = R, steadystate = True)


```


The filter now holds the Kalman gain and will use it at runtime to correct the estimates:

```python


print(kf._Kinf)


```


To easily draw the bounding box on each frame, let's define two auxiliary functions to calculate the bounding box top-left and bottom-right corners from the state vector: 

```python


# top left
def tl(X): return int(X[0] - X[2] / 2), int(X[1] - X[3] / 2)
# bottom right
def br(X): return int(X[0] + X[2] / 2), int(X[1] + X[3] / 2)


```


Main loop:  
The prediction step occurs in every cycle, while the update (correction) step is performed when a car is detected.

```python


t = 0

while video_cap.isOpened():
  kf.store(t)
  # predict
  kf.predict()
  ret, frame = video_cap.read()
  if not ret: break

  dtcts = yolo3.detect(frame)

  # take only the first 'car' classified object:
  d = next(iter([di for di in dtcts if di.class_id == 'car']), None)
  if d:
    # correct
    kf.update(d.X)
    # store the raw measurement:
    kf.detect = d
    kf.storeparams('detect', t)

  _ = cv2.rectangle(frame, tl(kf.X), br(kf.X), [0, 255, 0], 2)

  if IN_COLAB:
      cv2_imshow(frame)
  else:
      cv2.imshow('', frame)
      cv2.waitKey(10)

  vidout.write(frame)
  t += dt

video_cap.release()
vidout.release()
cv2.destroyAllWindows()


```


```python


Video('car_detected.mp4', width = 640, height = 360, embed = True)


```


To analyze the results, let's define a plotting function.

### Results 

`plot_track` takes kalman object and plots the trajectory ($x,y$ coordinates) on the image plane.
Additional arguments are:
- title (`str`): text to add the title
- detections (`bool`): flag indicating whether to display raw detections
- printtime (`bool`): add timestamps at key coordinates
- axislim (`list`): Specifies the axis limits as $[xmin, xmax, ymin, ymax]$

```python


def plot_track(kf, title, detections = False, printtime = False, axislim = None):

  _, ax = plt.subplots(1, 1, dpi = 200, figsize = (4, 2.25), gridspec_kw = {'left': 0.15, 'right': .9, 'top': .9, 'bottom': .2})
  ax.plot(kf.data('x')[1], kf.data('y')[1], 'om', markersize = 1, label = 'estimation')

  if detections:
    dxdy = np.vectorize(lambda d: (d.x, d.y) if isinstance(d, pixelpoint) else np.nan)(kf.data('detect')[1])
    ax.plot(dxdy[0], dxdy[1], 'co', markersize = .5, label = 'detection')

  plotdefaults(ax, title, 'X', 'Y', 8)
  ax.legend(fontsize = 6, facecolor = None)
  ax.invert_yaxis()

  if printtime:
    time = kf.data('t')

    xgrid  = np.arange(0, width, 100)
    xdata  = kf.data('x')[1]
    txgrid = [time[np.argmin(np.abs(xdata - v))] for v in xgrid]
    yxgrid = [kf.timestate(txi)[1] for txi in txgrid]

    for pt in zip(txgrid, xgrid, yxgrid):
      ax.text(pt[1], pt[2], f'{pt[0]:.2f}', fontsize = 5, color = "white")

  if axislim:
    ax.axis(axislim)


```


<!-- The second function 
o generate this figure we used numpy's `vectorize()` to extract the 
`x, y` attributes from the detection data.   -->


Let's start with simple trajectory: 

```python


plot_track(kf, title = 'Steady State Mode')


```


It's clear that the car's motion is not linear.  
However, we can identify roughly three segments where the motion is approximately linear.  
This is why constant velocity dynamics is useful in this video.

We can add marks presenting the difference between the Kalman estimations and the raw detections: 

```python


plot_track(kf, title = 'Steady State Mode', detections = True)


```


As mentioned, the underlying model is constant velocity dynamics. If we focus on the joints that connect two linear parts, where the car changes its velocity direction, we see that discrepancies may occur, i.e. a difference between the detection and the filter estimations: 

```python


plot_track(kf, title = 'Steady State Mode', detections = True, axislim = [400, 600, 250, 400])
pt = [490, 315]
circle = plt.Circle(pt, 15, color = 'blue', fill = False, linewidth = 1)
plt.gca().add_patch(circle)
plt.gca().invert_yaxis()


```


In the suspicious region, the estimation magenta dots separate from the detections (little dots mark). 

This occurs because the process matrix $Q$ is comparable in strength to $R$, meaning the filter 'trusts' the model as much as the measurements and effectively averages between them. 
It can be fixed by diminishing the measurement covariance in the transition times and allow the measures more weight.  
But doing so is not possible in steady state mode. 

### 2) Varying Covariance 

The execution in steady-state mode means that the estimation error (the state covariance matrix $P$) 
is calculated once and remains constant during the entire runtime.  
This mode is enabled when the system is $LTI$ (linear time invariant) 
and the covariance matrices that represent the dynamics uncertainty ($Q$) and the measurement noise ($R$) are constant. 
However, when $R$ or $Q$ are varying with time, steady-state mode is not feasible. 

The previous issue can be addressed by reducing the measurement noise matrix $R$ around the points when the velocity changes direction. 
Let's plot the detections with timestamps to determine where transitions between linear segments occur:

```python


plot_track(kf, title = 'Steady State Mode', detections = True,  printtime = True)


```


So the transitions happen to be around $t = 4s, t = 7.5s$:

```python


t_transitions = [4, 7.5]


```


To address the gap between the estimation and the detections, 
let's make the measurement covariance $R$ more 
tight around $t = 4, 7.5$:

$$
  std_{measure} = 
  \begin{cases} 
      im_{width} / 100000         & t  \approx 4s, 7.5s              \\
      im_{width} / 10000          & \text{otherwise}
  \end{cases}
$$

Where: 
- $std_{measure}$ is the measurement standard deviation (square root of the variance) 
- $im_{width}$ is the image width 


Near `t = 4s, t = 7.5s`, the measurement error is low, so the filter should give less weight to the process model.

The main loop is only modified to include changes in $R$: 

```python


kf = kalman({'x': 0, 'y': 0, 'w': 0, 'h': 0, 'vx': 0, 'vy': 0}, P0 = Q, F = F, H = H, Q = Q, R = R)
video_cap = cv2.VideoCapture(video)
t = 0

# main loop
while video_cap.isOpened():
  kf.store(t)
  kf.predict()

  ret, frame = video_cap.read()
  if not ret: break

  dtcts = yolo3.detect(frame)

  # take only the first 'car' classified object:
  d = next(iter([di for di in dtcts if di.class_id == 'car']), None)
  if d:
    # adjust R:
    if np.isclose(t, t_transitions, atol = 0.2).any():
      measure_std = width / 100000
    else:
      measure_std = width / 10000
    R = np.eye(4) * measure_std**2
    kf.update(d.X, R = R)
    # store the raw measurement:
    kf.detect = d
    kf.storeparams('detect', t)

  cv2.rectangle(frame, tl(kf.X), br(kf.X), [0, 255, 0], 2)

  if IN_COLAB:
      cv2_imshow(frame)
  else:
      cv2.imshow('', frame)
      cv2.waitKey(10)

  t += dt

video_cap.release()
cv2.destroyAllWindows()


```


Let's now focus on the joint around $t=4$ (we saw the respective coordinate earlier at $x \approx 500$)

```python


plot_track(kf, title = 'Varying Covariance Mode', detections = True, axislim = [400, 600, 250, 400])
circle = plt.Circle(pt, 15, color = 'blue', fill = False, linewidth = 1)
plt.gca().add_patch(circle)
plt.gca().invert_yaxis()


```


During the turns, the estimates (magenta) closely follow the detections (cyan), showing improved accuracy.

And the entire trajectory:

```python


plot_track(kf, title = 'Varying Covariance Mode', detections = True)


```


## Summary 

This program implements a Kalman filter-based object tracking system for detecting and tracking a car in a video.

It uses YOLOv3 for object detection, providing the object's center pixel, bounding box, and classification label.
The center pixel and bounding box are used to update the Kalman filter.

The Kalman filter (`kf`) is initialized to track the car’s position ($x, y$), size ($w, h$), and velocity ($v_x, v_y$).

The Kalman filter is applied in two modes:
- Steady-state: The system is assumed to be (linear and) time-invariant, so the Kalman gain ($K$) is computed once and remains constant throughout the runtime.
- Adaptive covariance: To correct discrepancies between estimates and detections during turns, the measurement noise covariance matrix $R$ is adjusted dynamically to give more weight to measurements at key transition points.

This adaptive approach enhances tracking accuracy by responding to motion changes.
The final visualization highlights how the Kalman filter smooths the trajectory while correcting for measurement noise and motion transitions


## Recap 

Video trackers upgrade your skills.
 
Here's a walkthrough of our object tracker: 
 
- Plug in a video stream or load your images. 
- Invert the frame rate to get dt = 1 / fps.
- Employ a detector from YOLO family. 
- A detection provides the following: 
- The center coordinates, [xc, yc].
- The bounding box size, [w, h]. 
- It's 4 variables for detection.
- Actually, the measurement. 
- Classification is given too. 
- It uses for filtering rejects. 
- Let's talk about dynamics.
- Deep breath, it's technical. 
- x  =  [  xc, yc, w, h, vxc, vyc  ]. 
- 6 variables for state vector x. 
- vxc and vyc are the velocities.
- Initialize the state: x=zeros(6). 
- Assume constant speed model. 
- vxc and vyc derivatives are zeros. 
- Assume no change in the box size. 
- Build the state matrix F = zeros(6,6): 
- Main diagonal: ones; F[0,4]=F[1,5]=dt. 
- The measurement matrix H=zeros(4,6):
- First diagonal: ones. Against a detection. 
- The system is observable. Save test time.
- Noise matrices now; R, Q; Keep it simple: 
- R is 4×4. Diagonal = framewidth / 1000.
- Q is 6x6, with these place the diagonal: 
- Same as R for near-constant velocity.
- Lower as the velocity more consant. 
- Solve Riccati equation for matrix P.
- Solvers exist. So don’t be afraid. 
- Compute K, the Kalman gains. 
- Finally the main loop is here:

1 Read the next input image.

2 Run the objects detector.

3 Filter by the object class.

4 Update the system state:

- x  =  F * x + K * ( z - H * x );
- z is the detected [xc,yc,w,h].  
- That's all the Kalman actually.

5 Show the frame. Draw the box.

6 Arrow for direction is an option.  
 
This is your take-away tracker.
 
Powerful and condensed. 
