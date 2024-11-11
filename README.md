<div align="center">
  <img src="https://github.com/C4dynamics/C4dynamics/blob/main/docs/source/icon/c4dlogotext.svg">
</div>



# Tsipor Dynamics

## Algorithms Engineering and Development



Tsipor (bird) Dynamics (c4dynamics) is the open-source framework of algorithms development for objects in space and time.

[![My Skills](https://skillicons.dev/icons?i=python)](https://skillicons.dev)  


Complete Documentation: https://c4dynamics.github.io/C4dynamics/


## Motivation

**c4dynamics** is designed to 
simplify the development of algorithms for dynamic systems, 
using state space representations. 
It offers engineers and researchers a systematic approach to model, 
simulate, and control systems in fields like ``robotics``, 
``aerospace``, and ``navigation``.

The framework introduces ``state objects``, which are foundational 
data structures that encapsulate state vectors and provide 
the tools for managing data, simulating system behavior, 
and analyzing results. 

With integrated modules for sensors, 
detectors, and filters, 
c4dynamics accelerates algorithm development 
while maintaining flexibility and scalability.




## Installation 

* PIP  

```
>>> pip install c4dynamics
```

* GitHub  

To run the latest GitHub version, download c4dynamics: 
https://github.com/C4dynamics/C4dynamics



&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  



Install the required packages:
```
>>> pip install -r requirements.txt
```

 
 
 

## Quickstart

Import c4dynamics:
```
>>> import c4dynamics as c4d
```

Define state space object of two variables in the state space (y, vy) with initial conditions (change the state with your variables): 
```
>>> s = c4d.state(y = 1, vy = 0.5)
``` 

Multiply the state vector by a matrix and store:  
```
>>> F = [[1, 1],                      
         [0, 1]]              
>>> s.X += F @ s.X                     
>>> s.store(t = 1)                    
```

Print the state variables, the state vector, and the stored data:  
```
>>> print(s)  
[ y  vy ]
>>> s.X 
[2.5  1]
>>> s.data('y')                      
([0,  1], [1,  2.5])
```


Load an object detection module (YOLO):
```
>>> yolodet = c4d.detectors.yolo(height = height, width = width)
```

Define errors to a general-purpose seeker with C4dynamics: 
```
>>> rdr = c4d.seekers.radar(sf = 0.9, bias = 0, noisestd = 1)
```

Define a linear Kalman Filter, perform a prediction and an update: 
```
>>> pt.filter = c4d.filters.kalman(np.hstack((z, np.zeros(2))), P, A, H, Q, R)
>>> pt.filter.predict()
>>> pt.filter.correct(measure)
```



Define a point in space (pre-defined state) with some initial conditions: 
```
>>> pt = c4d.datapoint(x = 1000, vx = 100)
```

Define a body in space (pre-defined state) with some initial conditions: 
```
>>> body = c4d.rigidbody(theta = 15 * 3.14 / 180)
```





## Architecture
For Architecture & Roadmap, see the Wiki page.  









