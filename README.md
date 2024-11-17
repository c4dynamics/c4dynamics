<div align="center">
  <img src="https://github.com/C4dynamics/C4dynamics/blob/main/docs/source/icon/c4dlogotext.svg">
</div>



# Tsipor Dynamics

## Algorithms Engineering and Development



Tsipor (bird) Dynamics (c4dynamics) is the open-source framework of algorithms development for objects in space and time.

[![My Skills](https://skillicons.dev/icons?i=python)](https://skillicons.dev)  


Documentation: https://c4dynamics.github.io/C4dynamics/


## Motivation

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




## Installation 


* PIP  

```
>>> pip install c4dynamics
```
Visit PyPi: 
https://pypi.org/project/c4dynamics/


* GitHub  

To run the latest GitHub version, download c4dynamics: 

https://github.com/C4dynamics/C4dynamics

Install required packages:

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


## Features 



## Architecture

## Roadmap 



### 1. **GitHub Page (Repository README)**  
**Purpose**: To introduce your project to developers and contributors.  

**Focus**: Provide a concise overview of the project, its purpose, and how to get started.  

**What to include**:  

   - **Project Name** and **Brief Description**: 
   Explain the problem your project solves or the features it offers.

   - **Key Features**: 
   Highlight what makes your project unique or useful.

   - **Installation Instructions**: 
   How someone can clone the repository and run the project locally.
   - **Usage**: Basic examples of how to use the project or API.
   
   - **Contributing Guidelines**: Link to guidelines for developers who want to contribute.
   - **Links to Documentation**: Provide a link to the full documentation page.
   - **License**: The open-source license under which your project is distributed.




