import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import UnivariateSpline

def fit_curve(x,y,k=3,steps = 10):
    """
    This function is used to fit a curve to a set of input data points.
    
    Parameters:
        x (list or numpy array): The x-coordinates of the data points.
        y (list or numpy array): The y-coordinates of the data points.
        k (int, optional): The degree of the smoothing spline. Default is 3.
        steps (int, optional): The number of points on the x-axis that the output curve should be evaluated at. Default is 10.
    
    Returns:
        tuple: A tuple of two numpy arrays, representing the x and y coordinates of the fitted curve.
    
    Example (plot included):
      np.random.seed(0)
      x = np.linspace(0, 1, num=11, endpoint=True)
      y = np.sin(-x**2/9.0)
      plt.scatter(x, y, s=100, label='Random data')
      xs,ys= fit_curve(x,y,k=3,steps = 10)
      plt.plot(xs,ys, 'm', label='UnivariateSpline')

      plt.legend()
      plt.show()
    """
    xs = np.linspace(0, x[-1], steps)
    s = UnivariateSpline(x, y,k=k)
    ys = s(xs)
    return xs,ys

