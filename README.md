<div align="center">
  <img src="https://github.com/C4dynamics/C4dynamics/blob/main/docs/source/_icon/c4dlogotext.svg">
</div>



# Tsipor Dynamics

## Algorithms Engineering and Development



Tsipor (bird) Dynamics (c4dynamics) is the open-source framework of algorithms development for objects in space and time.




![Static Badge](https://img.shields.io/badge/python-%20?style=for-the-badge&logo=python&color=white)
![PyPI - Version](https://img.shields.io/pypi/v/c4dynamics?style=for-the-badge&color=orange&link=https%3A%2F%2Fpypi.org%2Fproject%2Fc4dynamics%2F)
![GitHub deployments](https://img.shields.io/github/deployments/C4dynamics/C4dynamics/github-pages%20?style=for-the-badge&label=docs)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/c4dynamics/c4dynamics/run-tests.yml?style=for-the-badge&label=tests&link=https%3A%2F%2Fgithub.com%2FC4dynamics%2FC4dynamics%2Fblob%2Fmain%2F.github%2Fworkflows%2Frun-tests.yml)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/C4dynamics/C4dynamics/paper.yml?style=for-the-badge&label=Paper)
![Pepy Total Downloads](https://img.shields.io/pepy/dt/c4dynamics?style=for-the-badge&color=blue%20&link=https%3A%2F%2Fpepy.tech%2Fprojects%2Fc4dynamics%3FtimeRange%3DthreeMonths%26category%3Dversion%26includeCIDownloads%3Dtrue%26granularity%3Ddaily%26viewType%3Dline%26versions%3D2.0.3%252C2.0.1%252C2.0.0)




[Documentation](https://c4dynamics.github.io/C4dynamics/)


## Why c4dynamics?

✅ State objects for easy modeling

✅ Built-in functions for Kalman filters

✅ Optimization for Monte Carlo simulations

✅ Seamless integration with OpenCV & Open3D 



**c4dynamics** is designed to 
simplify the development of algorithms for dynamic systems, 
using state space representations. 
It offers engineers and researchers a systematic approach to model, 
simulate, and control systems in fields like 
``robotics, aerospace,`` and ``navigation``.

The framework introduces ``state objects,`` which are foundational 
data structures that encapsulate state vectors and provide 
the tools for managing data, simulating system behavior, 
and analyzing results. 

With integrated modules for sensors, 
detectors, and filters, 
c4dynamics accelerates algorithm development 
while maintaining flexibility and scalability.



## Requirements 
- 3.8 <= Python <= 3.12
- Required packages are listed in [requirements.txt](requirements.txt)



## Installation 


* [PIP](https://pypi.org/project/c4dynamics/)

```
>>> pip install c4dynamics
```



* [GitHub](https://github.com/C4dynamics/C4dynamics)  

To run the latest GitHub version, download the repo and install required packages:

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

## Support 
If you encounter problems, have questions, or would like to suggest improvements, 
please open an Issue in this repository.


## New in Block 2

Enhancements and modules in latest release:

- Complete state space objects mechanism
- Seeker and radar measurements
- Kalman filter and Extended Kalman filter
- YOLOv3 object detection API 
- Datasets fetching to run examples
- Documentation

