Reinforcement Learning Environment
==================================

`c4dynamics` provides an interface for defining and running Reinforcement Learning 
Enviroenments. 


*******************
Background Material
*******************

Reinforcement Learning formalizes decision-making in dynamical systems 
using the **Markov Decision Process (MDP)** framework. 
An MDP is defined by the tuple:

.. math::

   (S, A, P, R, \gamma)

where:

- :math:`S` is the set of states representing all possible configurations of the system.
- :math:`A` is the set of actions available to the agent.
- :math:`P(s'|s,a)` is the state transition probability, describing the likelihood of moving from state :math:`s` to state :math:`s'` after taking action :math:`a`.
- :math:`R(s,a,s')` is the reward function, quantifying the immediate benefit of transitioning from :math:`s` to :math:`s'` via :math:`a`.
- :math:`\gamma \in [0,1]` is the discount factor, determining the importance of future rewards.

The agent interacts with the environment through a **policy** :math:`\pi(a|s)`, 
which maps states to probabilities over actions. 
The **goal** of reinforcement learning is to find an optimal policy :math:`\pi^*` 
that maximizes the expected cumulative reward:

.. math::

   G_t = \sum_{k=0}^{\infty} \gamma^k R_{t+k+1}

Many RL algorithms, including Q-learning, policy gradients, and actor-critic methods, 
rely on **iteratively estimating the value of states or state-action pairs** 
and updating the policy to improve long-term performance. 
This mathematical foundation underpins virtually all RL environments, 
regardless of the underlying system being modeled.




****************************
Implementing RL Environments 
****************************

The Reinforcement Learning (RL) Environment module in c4dynamics provides a flexible and structured 
framework to simulate interactive systems for RL agents. 
It is designed to standardize how agents perceive states, take actions, and receive feedback, 
making it easy to implement custom environments and test learning algorithms.

At the core of every RL environment is the State class. 
This class serves as a parent for all environment-specific state objects 
and is designed to simplify both mathematical and data operations on the system's state variables. 
By encapsulating the state in a structured object, the framework allows you to:

- Perform vectorized operations and transformations on state variables.
- Access and modify individual or grouped state components conveniently.
- Integrate easily with the step and reset methods of any environment, providing consistent and reusable state updates.

Each environment in this module extends the base State class and implements:

- step(action) - Computes the next state, reward, and termination signal given an agent's action.
- reset() - Resets the environment to an initial state, ensuring reproducibility for training episodes.

This design allows seamless integration with various RL algorithms while maintaining 
a clear separation between the dynamics of the system, the state representation, and the agent's interaction logic.

By leveraging the State class as a foundation, c4dynamics makes it straightforward to create, 
manipulate, and reason about complex environments, whether for robotics, guidance systems, or other dynamic simulations.






