***********************************
6 DOF - Missile Guidance Simulation  
***********************************


Six degrees of freedom (6DOF) simulation of a missile employing 
proportional navigation guidance to pursue a target.
Conducting 

.. .. figure:: figures/threefundamental.png

..    **Figure**
..    Conceptual diagram showing the relationship between the three
..    fundamental objects used to describe the data in an array: 1) the
..    ndarray itself, 2) the data-type object that describes the layout
..    of a single fixed-size element of the array, 3) the array-scalar
..    Python object that is returned when a single element of the array
..    is accessed.


Jupyter Notebook
================

`The example's notebook can be downloaded 
from the examples folder in C4dynamics' 
GitHub <https://github.com/C4dynamics/C4dynamics/tree/main/examples>`_ 

.. `Source Repository <https://github.com/C4dynamics/C4dynamics>`_ |



Missile and Target
==================

The target is a datapoint object which means 
it has all the attributes of a mass in space:

.. code:: 

    target = c4d.datapoint(x = 4000, y = 1000, z = -3000
                            , vx = -250, vy = 0, vz = 0)


Additional variables are: mass (default 1, if not initialized), 
and three accelerations: ax, ay, az (default 0, if not initialized). 


The missile is a rigid-body object, 
which means that it has all the attributes of a datapoint,
and additional attributes of angular motion:


.. code::

    missile = c4d.rigidbody(m = 85, iyy = 61, izz = 61, xcm = 1.55)

More angular variables of a rigidbody object are 
three Euler angles, three body rates, and three angular rates.


As the dynamics in this example involves a 
combustion of fuel of the rocket engine the 
missile’s mass attributes varying as function of time. 
To recalculate the mass during the run time it's a 
good advice to save these initial conditions:

.. code::    

    m0      = missile.mass
    xcm0    = missile.xcm



Subsystems
==========

For the purpose of the presenentation in this example, three 
modules were created - control system, engine, and aerodynamics. 
A seeker object is part of the C4dynamics library: 

.. code:: 

    seeker  = c4d.sensors.lineofsight(dt, tau1 = 0.01, tau2 = 0.01)
    ctrl    = mcontrol_system.control_system(dt)
    eng     = mengine.engine()
    aero    = maerodynamics.aerodynamics()


Main loop
=========

The main loop includes the following steps: 

1) Estimation of missile-target line-of-sight angular rate 
2) Production of missile's wings-deflection commands 
3) Calculation of missile's forces and moments 
4) Integration of equations of motion 

The simulation runs until one of the following conditions:
1) The missile hits the ground
2) The simulation time is over 



Line of Sight Rate Estimation 
-----------------------------

The seeker accepts the relative 
position and velocity and produces filtered line of sight measure: 

.. code:: 

    vTM = target.vel - missile.vel  # missile-target relative velocity 
    rTM = target.pos - missile.pos  # relative position 
    rTMnorm = np.linalg.norm(rTM)   # range to target 
    uR      = rTM / rTMnorm         # unit range vector 
    vc      = -uR * vTM             # closing velocity 
    wf = seeker.measure(rTM, vTM)   # filtered los vector 


Wings Deflection Commands 
-------------------------

After some inteval of time from missile launch, 
the control system gets into action.
The control command implements proportional navigation command, 
i.e. a gain times the line of sight rate.   

.. code::

    if t >= 0.5:
        Gs       = 4 * missile.V()
        acmd     = Gs * np.cross(wf, ucl)
        ab_cmd   = missile.BI @ acmd 
        afp, afy = ctrl.update(ab_cmd, Q)
        d_pitch  = afp - alpha 
        d_yaw    = afy - beta  


Forces and Moments 
------------------

The forces and moments are rooted from three sources: aerodyanmics, propulsion system, and gravity.

.. code::

    # aerodynamics 
    cL, cD = aero.f_coef(mach, alpha_total)
    L = Q * aero.s * cL
    D = Q * aero.s * cD
    A = D * np.cos(alpha_total) - L * np.sin(alpha_total) # aero axial force 
    N = D * np.sin(alpha_total) + L * np.cos(alpha_total) # aero normal force 
    cM, cN = aero.m_coef(mach, alpha, beta, d_pitch, d_yaw 
                        , missile.xcm, Q, missile.V(), fAb[1], fAb[2]
                            , missile.q, missile.r)
    mA = np.array([0                                # aerodynamic moemnt in roll
                    , Q * cM * aero.s * aero.d          # aerodynamic moment in pitch
                        , Q * cN * aero.s * aero.d])        # aerodynamic moment in yaw 
            
    # propulsion 
    thrust, thref = eng.update(t, pressure)

    # gravity
    fGe = np.array([0, 0, missile.mass * c4d.g_ms2])


Rotation Matrix
---------------

The forces are calculated in body frame, which is rotated with the missile motion.
To integrate these forces with the equations of motion, they must be transformed to 
an inertial frame. 

The properties BI and IB of rigidbody objects use to proved the 
Body from Inertial (BI) DCM (Direction Cosine Matrix)
and Inertial from Body (IB) DCM. 
By default, the DCM order is built by 3-2-1 Euler rotation. 
The inertial frame is determined by the frame that the initial Euler angles refer to.

.. code::

    # aerodynamics
    fAb = np.array([ -A
                        , N * (-v / np.sqrt(v**2 + w**2))
                            , N * (-w / np.sqrt(v**2 + w**2))])
    fAe = missile.IB @ fAb

    # propulsion    
    fPb = np.array([thrust, 0, 0])# 
    fPe = missile.IB @ fPb

    # total forces
    forces = np.array([fAe[0] + fPe[0] + fGe[0]
                        , fAe[1] + fPe[1] + fGe[1]
                            , fAe[2] + fPe[2] + fGe[2]])


Equations of Motion and Integration  
-----------------------------------

After deriving the forces and moment vectors, 
the equations of motion can be integrated. 
inteqm() is C4dynamics' routine that runs 
Runge-Kutta integration of 4th order 
on 6DOF motion for rigidbody objects (missile)
and 3DOF motion for datapoint objects (target):

.. code:: 

    # missile motion integration
    missile.inteqm(forces, mA, dt)

    # target motion integration  
    target.inteqm(np.array([0, 0, 0]), dt)

    # update and store data 
    t += dt
    missile.store(t)
    target.store(t)


The update of the target and missile poisitons 
marks the end of a simulation cycle. 
Then the conditions to end the simulation are recalculated 
and the transition to next cycle or to post simulation calculation 
is determined. 


Results Analysis
================

.. code:: 

    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.tight_layout()

    textcolor = 'white'

    ax1.plot(missile.get_data('x') / 1000, -missile.get_data('z') / 1000, 'b', linewidth = 2, label = 'missile')
    ax1.plot(target.get_data('x') / 1000, -target.get_data('z') / 1000, 'r', linewidth = 2, label = 'target')
    ax1.set_title('Side View', color = textcolor)
    ax1.set(xlabel = 'Downrange (km)', ylabel = 'Altitude (km)')
    ax1.xaxis.label.set_color(textcolor)
    ax1.yaxis.label.set_color(textcolor)
    ax1.set_xlim(0, 5)
    ax1.set_ylim(0, 3.5)
    ax1.grid(alpha = .5,  which = 'both', color = textcolor)
    ax1.tick_params(axis = 'x', colors = textcolor)  # Change X-axis tick color to purple
    ax1.tick_params(axis = 'y', colors = textcolor)  # Change X-axis tick color to purple
    ax1.legend(fontsize = 14) # title = '#trk', loc = 'center left', bbox_to_anchor = (1, 0.5))

    ax2.plot(missile.get_data('x') / 1000, missile.get_data('y') / 1000, 'b', linewidth = 2, label = 'missile')
    ax2.plot(target.get_data('x') / 1000, target.get_data('y') / 1000, 'r', linewidth = 2, label = 'target')
    ax2.set_title('Top View', color = textcolor)
    ax2.set(xlabel = 'Downrange (km)', ylabel = 'Crossrange (km)')
    ax2.xaxis.label.set_color(textcolor)
    ax2.yaxis.label.set_color(textcolor)
    ax2.set_xlim(0, 5)
    ax2.set_ylim(0, 1.5)
    ax2.grid(alpha = .5, which = 'both', color = textcolor)
    ax2.tick_params(axis = 'x', colors = textcolor)  # Change X-axis tick color to purple
    ax2.tick_params(axis = 'y', colors = textcolor)  # Change X-axis tick color to purple
    ax2.legend(fontsize = 14) 
    plt.subplots_adjust(hspace = 1)

.. figure:: /../../examples/out/dof6sim_topside.png

.. code:: 
    
    fig = plt.figure(figsize = (wfig, hfig))
    ax = fig.add_subplot(111, projection = '3d')
    wfig = 12
    hfig = 7
    dfig = 3
    ax.plot(missile.get_data('x'), missile.get_data('y'), missile.get_data('z') * 0.3048, 'b', linewidth = 2, label = 'missile') # , color = '#2ECC71') # '#001F3F') # )
    ax.plot(target.get_data('x'), target.get_data('y'), target.get_data('z') * 0.3048, 'r', linewidth = 2, label = 'target') # , color = '#E74C3C') # '#FF5733') # )
    ax.set_title('Trajectories')
    ax.set(xlabel = 'X (m)', ylabel = 'Y (m)', zlabel = 'Z (ft)')
    ax.set_xlim(0, 7000)
    ax.set_ylim(0, 1100)
    ax.invert_zaxis()
    ax.set_box_aspect([wfig, hfig, dfig])
    ax.legend(fontsize = 14) # title = '#trk', loc = 'center left', bbox_to_anchor = (1, 0.5))
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis._axinfo["grid"]['linestyle'] = ":"
    ax.yaxis._axinfo["grid"]['linestyle'] = ":"
    ax.zaxis._axinfo["grid"]['linestyle'] = ":"
    plt.show()

.. figure:: /../../examples/out/dof6sim_trajectories_.png


