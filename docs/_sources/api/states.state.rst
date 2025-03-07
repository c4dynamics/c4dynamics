The state object 
================
.. currentmodule:: c4dynamics.states.state


.. autoclass:: state 


  **Operations** 
  

  The following properties and methods are categorized into two main types: 
  mathematical operations and data management operations. 

  .. raw:: html

    <b><u>Mathematical operations</u></b>

   
  Operations that involve direct manipulation of the state vector 
  using mathematical methods. These operations include normalization, norm calculation, and 
  other operations assume cartesian coordinates.  



  **Properties**

  .. autosummary:: 
    :toctree: generated/state

    state.X 
    state.X0 
    state.norm 
    state.normalize 
    state.position 
    state.velocity 


  **Methods** 

  .. autosummary:: 
    :toctree: generated/state

    state.addvars 
    state.P 
    state.V
    
  .. raw:: html

    <b><u>Data management operations</u></b>


  
  Operations that involve managing the state vector data, 
  such as storing and retrieving states at different times or handling time series data. 


  **Methods** 

  .. autosummary:: 
    :toctree: generated/state

    state.store
    state.storeparams
    state.data
    state.timestate
    state.plot 





