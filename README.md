<div align="center">
  <img src="https://github.com/C4dynamics/C4dynamics/raw/main/utils/C4dynamics.png">
</div>

# Tsipor Dynamics
## Algorithms Engineering and Development
****


C4Dynamics (read Tsipor (bird) Dynamics) is the open-source framework of algorithms development for objects in space and time.

[![My Skills](https://skillicons.dev/icons?i=python)](https://skillicons.dev)  


## Table of contents
- [Motivation](https://github.com/C4dynamics/C4dynamics/tree/main/#motivation)
- [Installation](https://github.com/C4dynamics/C4dynamics/tree/main/#installation)
- [Quickstart](https://github.com/C4dynamics/C4dynamics/tree/main/#quickstart)
- [Architecture](https://github.com/C4dynamics/C4dynamics/tree/main/#architecture)
- [Contributors ✨](https://github.com/C4dynamics/C4dynamics/tree/main/#contributors-✨)
- [Quickstart for Contributors](https://github.com/C4dynamics/C4dynamics/tree/main/#quickstart-for-contributors)
- [Getting Started](https://github.com/C4dynamics/C4dynamics/tree/main/#getting-started)
- [Example 1: Objects Detection and Tracking](https://github.com/C4dynamics/C4dynamics/tree/main/#example-1---objects-detection-and-tracking)
- [Example 2: Missile Guidance Example](https://github.com/C4dynamics/C4dynamics/tree/main/#example-2---six-degrees-of-freedom-simulation)


## Motivation
C4dynamics provides two basic entities for developing and analyzing algorithms of objects in space and time:
* datapoint: a class defining a point in space: position, velocity, acceleration, and mass. 
* rigidbody: a class defining a rigid body in space, i.e. an object with length and angular position. 

You can develop and analyze algorithms by operating on these objects with one of the internal systems or algorithms of C4dynamics:  
* ODE Solver (4th order Runge-Kutta)  
* Kalman Filter  
* Extended Kalman Filter  
* Luenberger Observer  
* Radar System  
* Altitude Radar  
* IMU Model  
* GPS Model  
* Line Of Sight Seeker  
  
Or one of the 3rd party libraries integrated with C4dynamics:   
* NumPy  
* Matplotlib  
* OpenCV  
* YOLO  
  
Whether you're a seasoned algorithm engineer or just getting started, this framework has something to offer. Its modular design allows you to easily pick and choose the components you need, and its active community of contributors is always working to improve and expand its capabilities.
  
So why wait? Start using C4dynamics today and take your algorithms engineering to the next level!
  



## Installation 
* PIP  
```
pip install c4dynamics
```

* GitHub  
To run the latest GitHub version, download c4dynamics: 
https://github.com/C4dynamics/C4dynamics  
Install the required packages:
```
pip install -r requirements.txt
```

* Conda   
Alternatively, run the preinstalled conda environment (see conda_installation.md):
```
conda env create -f c4dynamics_env.yaml
```
 
 
 
 

## Quickstart
Import the framework:
```
import c4dynamics as c4d
```

Define a point in space with some initial conditions: 
```
pt = c4d.datapoint(x = 1000, vx = 100)
```

Define a body in space with some initial conditions: 
```
body = c4d.rigidbody(theta = 15 * 3.14 / 180)
```

Load an object detection module (YOLO):
```
yolodet = c4d.detectors.yolo(height = height, width = width)
```

Define a linear Kalman Filter, perform a prediction and an update: 
```
pt.filter = c4d.filters.kalman(np.hstack((z, np.zeros(2))), P, A, H, Q, R)
pt.filter.predict()
pt.filter.correct(measure)
```

Store the current state of the datapoint (at time t):
```
pt.store(t)
```

Store other variables added to the datapoint object:
```
pt.storevar('kalman_state', t)
```

Define errors to a general-purpose seeker with C4dynamics: 
```
rdr = c4d.seekers.radar(sf = 0.9, bias = 0, noisestd = 1)
```





## Architecture
For Architecture & Roadmap, see the Wiki page.  




## Contributors ✨

[//]: contributor-faces
<a href="https://www.linkedin.com/in/ziv-meri/">                      <img src="https://github.com/C4dynamics/C4dynamics/raw/main/utils/ziv_noa2.png"        title="Ziv Meri" width="80" height="80"></a> 	<a href="https://www.linkedin.com/in/aviva-shneor-simhon-17b733b/">   <img src="https://github.com/C4dynamics/C4dynamics/raw/main/utils/aviva2.png"          title="Aviva Shneor Simhon" width="80" height="80"></a> 	<a href="https://www.linkedin.com/in/amit-elbaz-54301382/">           <img src="https://github.com/C4dynamics/C4dynamics/raw/main/utils/amit2.png"           title="Amit Elbaz" width="80" height="80"></a> 	<a href="https://www.linkedin.com/in/avraham-ohana-computer-vision/"> <img src="https://github.com/C4dynamics/C4dynamics/raw/main/utils/avraham2.png"        title="Avraham Ohana" width="80" height="80"></a> 	<a href="https://chat.openai.com/chat">                               <img src="https://github.com/C4dynamics/C4dynamics/raw/main/utils/openai-featured.png" title="Chat GPT" width="80" height="80"></a>

[//]: contributor-faces

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!




## Quickstart for Contributors
* See the page contributing.md
* In any case, it's a good advise to start with the example dof6sim.ipynb and change the missile-target conditions to gain some experience with the framework. This example appears also down here in the README




# Getting Started  
See all the examples at: https://github.com/C4dynamics/C4dynamics/tree/main/examples 
Complete explanation at the README in the examples folder. 


## Example 1 - Objects Detection and Tracking 
1. https://github.com/C4dynamics/C4dynamics/blob/main/examples/detect_track.ipynb
2. Detecting objects using the YOLOv3 model, updating and predicting their trajectories with the Kalman filter employing linear dynamics. Association between tracks is performed using scikit-learn's k-neighbors.
3. Each track is represented as a C4dynamics-datapoint, and the update and prediction are executed with the internal C4dynamics-Kalman-filter.
<div align="center">
  <img src="https://github.com/C4dynamics/C4dynamics/raw/main/examples/out/detection-tracking-tank-truck.gif">
</div>


## Example 2 - Six Degrees of Freedom Simulation 
1. https://github.com/C4dynamics/C4dynamics/blob/main/examples/dof6sim.ipynb
2. 6 DOF simulation of a missile employing proportional navigation guidance to pursue a target Conducting a 6-degree-of-freedom (6 DOF) simulation of a missile utilizing proportional navigation guidance to pursue a target.
3. The target is represented by a C4Dynamics-datapoint, i.e. object with translational motion. The missile is modeled as a C4Dynamics-rigidbody object, with variables representing both translational and rotational motion
For this example, additional systems and sensors (not part of C4dynamics but available for download from the examples folder) were developed:  
Control system  
Engine  
Aerodynamics  
<div align="center">
  <img src="https://github.com/C4dynamics/C4dynamics/raw/main/examples/out/dof6sim_trajectories.png">
</div>










