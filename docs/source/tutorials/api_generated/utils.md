# utils

## `cprint`

```python
cprint(txt='', color='white', end='\n')
```

Printing colored text in the console.

### Parameters
txt : str
    The text to be printed.

color : str, optional
    The color of the text. Default is 'white'.

### Example
```python
>>> import c4dynamics as c4d
>>> carr = ['y', 'w', 'r', 'm', 'c', 'g', 'k', 'b']
>>> for c in carr:
...   c4d.cprint('C4DYNAMICS', c) # doctest: +IGNORE_OUTPUT
```

  <span style="color:yellow">C4DYNAMICS</span><br>
  <span style="color:white">C4DYNAMICS</span><br>
  <span style="color:red">C4DYNAMICS</span><br>
  <span style="color:magenta">C4DYNAMICS</span><br>
  <span style="color:cyan">C4DYNAMICS</span><br>
  <span style="color:green">C4DYNAMICS</span><br>
  <span style="color:black">C4DYNAMICS</span><br>
  <span style="color:blue">C4DYNAMICS</span><br>

## `tic`

```python
tic()
```

Starts stopwatch timer.

Inspired by `MATLAB's` tic toc, `tic()` records the current time to start
measuring elapsed time.
When used in conjunction with `toc()` serves as a stopwatch
timer to measure the time interval between two events.

### Returns
out : float
    The recorded start time.

### Examples
```python
>>> import c4dynamics as c4d
>>> import numpy as np
```

```python
>>> N = 10000
>>> tic()   # doctest: +IGNORE_OUTPUT
>>> a = np.ones((1, 3))
>>> for i in range(N - 1):
...     a = np.concatenate((a, np.ones((1, 3))))
>>> t1 = toc() # doctest: +IGNORE_OUTPUT
>>> c4d.cprint('numpy concat: ' + str(1000 * t1) + ' ms', 'r') # doctest: +IGNORE_OUTPUT
numpy concat: 40.0 ms
```

```python
>>> tic() # doctest: +IGNORE_OUTPUT
>>> a = np.zeros((N, 3))
>>> for i in range(N):
...     a[i, :] = np.ones((1, 3))
>>> t2 = toc() # doctest: +IGNORE_OUTPUT
>>> c4d.cprint('numpy predefined: ' + str(1000 * t2) + ' ms', 'g') # doctest: +IGNORE_OUTPUT
numpy predefined: 3.0 ms
```

```python
>>> tic()# doctest: +IGNORE_OUTPUT
>>> a = []
>>> for i in range(N):
...     a.append([1, 1, 1])
>>> a = np.array(a)
>>> t3 = toc()# doctest: +IGNORE_OUTPUT
>>> c4d.cprint('list to numpy: ' + str(1000 * t3) + ' ms', 'y') # doctest: +IGNORE_OUTPUT
```
  list to numpy: 0.0 ms

## `toc`

```python
toc(show=True, minutes=False)
```

Stops the stopwatch timer and reads the elapsed time.

Measures the elapsed time since the last call to `tic()` and prints the result in seconds.

### Returns
out : float
    Elapsed time in seconds.

### Examples
```python
>>> import c4dynamics as c4d
>>> import numpy as np
```

```python
>>> N = 10000
>>> tic() # doctest: +IGNORE_OUTPUT
>>> a = np.ones((1, 3))
>>> for i in range(N - 1):
...     a = np.concatenate((a, np.ones((1, 3))))
>>> t1 = toc() # doctest: +IGNORE_OUTPUT
>>> c4d.cprint('numpy concat: ' + str(1000 * t1) + ' ms', 'r') # doctest: +IGNORE_OUTPUT
numpy concat: 31.0 ms
```

```python
>>> tic() # doctest: +IGNORE_OUTPUT
>>> a = np.zeros((N, 3))
>>> for i in range(N):
...     a[i, :] = np.ones((1, 3))
>>> t2 = toc() # doctest: +IGNORE_OUTPUT
>>> c4d.cprint('numpy predefined: ' + str(1000 * t2) + ' ms', 'g') # doctest: +IGNORE_OUTPUT
numpy predefined: 15.0 ms
```

```python
>>> tic() # doctest: +IGNORE_OUTPUT
>>> a = []
>>> for i in range(N):
...     a.append([1, 1, 1])
>>> a = np.array(a)
>>> t3 = toc() # doctest: +IGNORE_OUTPUT
>>> c4d.cprint('list to numpy: ' + str(1000 * t3) + ' ms', 'y') # doctest: +IGNORE_OUTPUT
```
  list to numpy: 0.0 ms

## `plotdefaults`

```python
plotdefaults(ax, title, xlabel='', ylabel='', fontsize=8, ilines=None)
```

Setting default properties on a matplotlib axis.

### Parameters
ax : matplotlib.axes.Axes
    The matplotlib axis on which to set the properties.

title : str
    Plot title.

xlabel : str
    The label for the x-axis.

ylabel : str
    The label for the y-axis.

fontsize : int, optional
    The font size for the title, x-axis label, y-axis label, and tick labels. Default is 8.

### Example
```python
>>> import c4dynamics as c4d
>>> f16 = c4d.rigidbody()
>>> dt = .01
>>> for t in np.arange(0, 9, dt):
...   if t < 3:
...     f16.phi += dt * 180 / 9 * c4d.d2r
...   elif t < 6:
...     f16.phi += dt * 180 / 6 * c4d.d2r
...   else:
...     f16.phi += dt * 180 / 3  * c4d.d2r
...   f16.store(t)
>>> ax = plt.subplot()
>>> ax.plot(*f16.data('phi', c4d.r2d), 'm', linewidth = 2) # doctest: +IGNORE_OUTPUT
>>> c4d.plotdefaults(ax, '$\varphi$', 'Time', 'deg', fontsize = 18)
```

## `gif`

```python
gif(dirname, gif_name, duration=None)
```

Gif creator.

`gif` creates a Gif from a directory containing image files.

### Parameters
dirname : str
    The path to the directory containing image files.

gif_name : str
    The desired name of the output GIF file.

duration : float, optional
    The duration (in seconds) for each frame of the GIF.
    If None, default duration is used.

### Example
Let's generate images of an F16 aircraft in different orientations and create a gif from them.

1. Prepare trajectory to animate.

Import required packages:

```python
>>> import c4dynamics as c4d
>>> from IPython.display import Image
>>> import numpy as np
>>> import os
```
Settings and initial conditions:

```python
>>> f16 = c4d.rigidbody()
>>> dt = 0.01
```
Main loop:

```python
>>> for t in np.arange(0, 9, dt):
...  # in 3 seconds make 180 deg:
...  if t < 3:
...    f16.psi += dt * 180 * c4d.d2r / 3
...  elif t < 6:
...    f16.theta += dt * 180 * c4d.d2r / 3
...  else:
...    f16.phi -= dt * 180 * c4d.d2r / 3
...  f16.store(t)
```
2. Animate and save image files.

(Use c4dynamics' `datasets` to fetch F16 3D model.)

```python
>>> f16path = c4d.datasets.d3_model('f16')
Fetched successfully
>>> x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r]
>>> outfol = os.path.join('tests', '_out', 'f16b')
>>> f16.animate(f16path, savedir = outfol, angle0 = x0, modelcolor = [0, 0, 0],
...       cbackground = [230 / 255, 230 / 255, 255 / 255])
```
3. Export images as gif.

```python
>>> gifname = 'f16_monochrome_gif.gif'
>>> c4d.gif(outfol, gifname, duration = 1)
>>> Image(filename = os.path.join(outfol, gifname))  # doctest: +IGNORE_OUTPUT
```

