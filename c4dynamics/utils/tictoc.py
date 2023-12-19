import time
_tic = 0.0

def tic():
    global _tic
    _tic = time.time()
    return _tic

def toc():
    global _tic
    dt = time.time() - _tic
    print(dt)
    return dt

