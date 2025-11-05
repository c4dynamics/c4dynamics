---
title: 'C4DYNAMICS: The Python framework for state-space modeling and algorithm development'
tags:
  - Python
  - dynamics
  - state space
  - sensors
  - filters
  - detectors
authors:
  - name: Ziv Meri
    orcid: 0000-0002-7932-0562
    affiliation: 1
affiliations:
  - name: Independent Researcher, Israel
    index: 1
date: "2024-12-17"
bibliography: paper.bib
---

# Summary
Dynamic systems are critical across robotics, aerospace, and guidance, navigation, and control (GNC). The state-space representation is the most widely used modeling approach for dynamic systems in the time domain [@Kalman1104873; @Luenberger3830260412]. While Python provides robust numerical tools, it lacks a framework specifically for state-space modeling. **C4DYNAMICS** bridges this gap by introducing a Python-based platform designed for state-space modeling and analysis. 
The framework's modular architecture, with "state objects" at its core, simplifies the development of algorithms for sensors, filters, and detectors. This allows researchers, engineers, and students to effectively design, simulate, and analyze dynamic systems. By integrating state objects with a scientific library, *c4dynamics* offers a scalable and efficient solution for dynamic systems modeling.

# Statement of Need
Modeling and simulation of dynamical systems are essential across robotics, aerospace, and control engineering. 
In these fields, engineers design state-space–level algorithms - algorithms that operate directly on the mathematical representation of system states (e.g., position, velocity, or attitude).
While Python provides powerful numerical libraries (e.g., NumPy [@numpy2020], SciPy [@SciPy2020]) and several domain-specific frameworks (for example, robot simulators and control toolboxes), none directly support low-level algorithm development, where the state vector is explicitly modeled and manipulated.

*c4dynamics* is designed for engineers who prefer code-based modeling and want to explicitly define the variables encapsulated in the system’s state vector. It streamlines mathematical operations (e.g. scalar multiplication, dot products), and data operations (state storage, history retrieval, plotting).

For example, in a guidance or control system, engineers can directly model the position and velocity of a vehicle, apply Kalman filters to estimate its motion, and visualize results. All within a unified, Python-native workflow.


# Comparison with Existing Software
Existing tools generally fall into two categories: 

  1) Block-diagram frameworks (e.g., SimuPy [@Margolis2017simupy], BdSim [@NEVAY2020107200]) mimic Simulink and simplify model building through graphical interfaces, but they abstract away the state vector and limit direct mathematical manipulation.
  2) High-level simulators (e.g., [IR-Sim](https://ir-sim.readthedocs.io/en/stable/), RobotDART [@Chatzilygeroudis2024]) allow algorithm testing in predefined environments but lack flexibility for low-level system modeling and algorithm design.

Both operate at higher abstraction levels, concealing the underlying state-space formulation.
In block-diagram frameworks, users connect functional blocks, while individual state variables remain implicit.
In high-level simulators, states are often predefined by the environment (e.g., robot position, velocity) rather than exposed to the user.

In contrast, c4dynamics brings the state-space representation back into focus, allowing engineers to define, manipulate, and analyze the system’s state vector directly — bridging the gap between physical modeling and algorithm design.

For illustration, consider the modeling and simulation of a pendulum:
- In a block-diagram framework, the user connects integrators and functional blocks, focusing on signal flow rather than the physical meaning of the state variables.
- High-level simulators abstract the system even further: users define parameters in configuration files and observe the resulting motion at the behavioral level, rather than interacting with the underlying mathematical or algorithmic model.
- In a stateful approach, the user explicitly defines the state variables and their initial conditions, and performs algorithmic operations — both mathematical and data-related — within the main loop. 

*c4dynamics* adopts this stateful approach and extends it into a modular, Python-native framework for state-space modeling of dynamical systems.
Built around explicit state representations and complemented by a scientific library of filters and sensor models, it enables reproducible modeling, testing, and optimization of dynamic systems within the scientific Python ecosystem.


# Example 
The following example demonstrates how to model a simple pendulum using *c4dynamics*.
The state of the pendulum consists of two variables:
`X = [θ, q]`, where `θ` is the angular displacement (rod angle), and `q` is the angular rate.  

Initial conditions: `X0 = [50, 0]` (degrees, degrees per second, respectively). 

Additional parameters: 
- Rod length: `1[m]` (rigid, massless)
- Gravity: `9.8[m/s²]` 
- Integration function: `solve_ivp` (SciPy)
- Time step: `0.01[s]`
- Simulation duration: `5[s]`

Import required packages:
```
from scipy.integrate import solve_ivp
from matplotlib import pyplot as plt 
import c4dynamics as c4d
import numpy as np 
```

Define the state object and initial conditions:
```
pend  = c4d.state(theta = 50 * c4d.d2r, q = 0)
```

Run the simulation loop and store the state at each step:
```
dt = 0.01 
for ti in np.arange(0, 5, dt): 
  pend.store(ti)
  pend.X = solve_ivp(lambda t, y: [y[1], -9.8 * c4d.sin(y[0])], [ti, ti + dt], pend.X).y[:, -1]
```

Plot the angle history:
```
pend.plot('theta', scale = c4d.r2d, darkmode = False)
plt.show()
```

![](pendulum.png)





# References
