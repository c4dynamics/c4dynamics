import time
_tic = 0.0

def tic():
    '''
    Starts stopwatch timer.

    Inspired by `MATLAB's` tic toc, `tic()` records the current time to start measuring elapsed time.
    When used in conjunction with `toc()` serves as a stopwatch 
    timer to measure the time interval between two events. 

    Returns
    -------
    out : float
        The recorded start time. 

    Examples 
    --------

    .. code:: 
        
      >>> N = 10000
      >>> tic()
      >>> a = np.ones((1, 3))
      >>> for i in range(N - 1):
      ...     a = np.concatenate((a, np.ones((1, 3))))
      >>> t1 = toc()
      >>> c4d.cprint('numpy concat: ' + str(1000 * t1) + ' ms', 'r')
        numpy concat: 1101.062536239624 ms

    .. code:: 

      >>> tic()
      >>> a = np.zeros((N, 3))
      >>> for i in range(N):
      ...     a[i, :] = np.ones((1, 3))
      >>> t2 = toc()
      >>> c4d.cprint('numpy predefined: ' + str(1000 * t2) + ' ms', 'g')
        numpy predefined: 294.16894912719727 ms

    .. code:: 

      >>> tic()
      >>> a = []
      >>> for i in range(N):
      ...     a.append([1, 1, 1])
      >>> a = np.array(a)
      >>> t3 = toc()
      >>> c4d.cprint('list to numpy: ' + str(1000 * t3) + ' ms', 'y')
        list to numpy: 86.08531951904297 ms
    
    '''

    global _tic
    _tic = time.time()
    return _tic

def toc():
    '''
 
    Stops the stopwatch timer and reads the elapsed time.

    Measures the elapsed time since the last call to `tic()` and prints the result in seconds.


    Returns
    -------
    out : float
        Elapsed time in seconds.

    Examples 
    --------

    .. code:: 
        
      >>> N = 10000
      >>> tic()
      >>> a = np.ones((1, 3))
      >>> for i in range(N - 1):
      ...     a = np.concatenate((a, np.ones((1, 3))))
      >>> t1 = toc()
      >>> c4d.cprint('numpy concat: ' + str(1000 * t1) + ' ms', 'r')
        numpy concat: 1101.062536239624 ms

    .. code:: 

      >>> tic()
      >>> a = np.zeros((N, 3))
      >>> for i in range(N):
      ...     a[i, :] = np.ones((1, 3))
      >>> t2 = toc()
      >>> c4d.cprint('numpy predefined: ' + str(1000 * t2) + ' ms', 'g')
        numpy predefined: 294.16894912719727 ms

    .. code:: 

      >>> tic()
      >>> a = []
      >>> for i in range(N):
      ...     a.append([1, 1, 1])
      >>> a = np.array(a)
      >>> t3 = toc()
      >>> c4d.cprint('list to numpy: ' + str(1000 * t3) + ' ms', 'y')
        list to numpy: 86.08531951904297 ms
    '''

    global _tic
    dt = time.time() - _tic
    print(dt)
    return dt



# tic():

#     Records the current time to start measuring elapsed time.
    
#     Returns:
#     float: The recorded start time.

# toc():

#     Measures the elapsed time since the last call to `tic()` and prints the result in seconds.

#     Returns:
#     float: The elapsed time in seconds.
