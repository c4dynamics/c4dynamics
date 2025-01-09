import numpy as np 
from matplotlib import pyplot as plt 
from matplotlib.ticker import ScalarFormatter
import sys 
sys.path.append('.')


def _figdef():
    factorsize = 4
    aspectratio = 1080 / 1920 
    return plt.subplots(1, 1, dpi = 200
                , figsize = (factorsize, factorsize * aspectratio) 
                        , gridspec_kw = {'left': 0.15, 'right': .9
                                            , 'top': .9, 'bottom': .2})


def _legdef(): 
    return {'fontsize': 4, 'facecolor': None}


def plotdefaults(ax, title, xlabel = '', ylabel = '', fontsize = 8, ilines = None):
    '''

    Setting default properties on a matplotlib axis.

    Parameters
    ----------

    ax : matplotlib.axes.Axes
        The matplotlib axis on which to set the properties.
    
    title : str
        Plot title.
        
    xlabel : str
        The label for the x-axis.
    
    ylabel : str
        The label for the y-axis.
    
    fontsize : int, optional
        The font size for the title, x-axis label, y-axis label, and tick labels. Default is 14.

        
    Example
    -------

    .. code::

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
      >>> c4d.plotdefaults(ax, '$\\varphi$', 'Time', 'deg', fontsize = 18)

        
    .. figure:: /_examples/utils/plotdefaults.png

    '''
    if False:
        #
        # line
        ## 
        lwidth = 2 
        # set colors suite to the lines: 
        scolors = {'cyan': np.array([0, 1, 1])
                    , 'magenta': np.array([1, 0, 1])
                    , 'gold': np.array([1, 0.84, 0])
                    , 'deepskyblue': np.array([0, 0.75, 1])
                        , 'limegreen': np.array([0.2, 0.8, 0.2])
                        , 'coral': np.array([1, 0.5, 0.31])
                        , 'orchid': np.array([0.85, 0.44, 0.84])
                            , 'tomato': np.array([1, 0.39, 0.28])
                            , 'dodgerblue': np.array([0.12, 0.56, 1])
                            , 'palevioletred': np.array([0.86, 0.44, 0.58])} 
        
        if ilines is None: 
            lcolors = lcolors 
        else: 
            lcolors = np.array(list(scolors.values()))[ilines, :]


        for line, color in zip(ax.get_lines(), lcolors):
            line.set_color(color) 
            line.set_linewidth(lwidth)
            lwidth = 1
            
        #
        # legend
        ##
        ax.legend(fontsize = 'small', facecolor = None) 

    #
    # axis 
    ##
    ax.set_title(title, fontsize = fontsize, fontname = 'Times New Roman')
    ax.set_xlabel(xlabel, fontsize = fontsize, fontname = 'Times New Roman')
    ax.set_ylabel(ylabel, fontsize = fontsize, fontname = 'Times New Roman')
    ax.grid(alpha = 0.5)
    ax.tick_params(axis = 'both', labelsize = fontsize, labelfontfamily = 'Times New Roman')

    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.get_major_formatter().set_useOffset(False)
    ax.yaxis.get_major_formatter().set_scientific(False)


if __name__ == "__main__":

  import doctest, contextlib, os
  from c4dynamics import IgnoreOutputChecker, cprint
  
  # Register the custom OutputChecker
  doctest.OutputChecker = IgnoreOutputChecker

  tofile = False 
  optionflags = doctest.FAIL_FAST

  if tofile: 
    with open(os.path.join('tests', '_out', 'output.txt'), 'w') as f:
      with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
        result = doctest.testmod(optionflags = optionflags) 
  else: 
    result = doctest.testmod(optionflags = optionflags)

  if result.failed == 0:
    cprint(os.path.basename(__file__) + ": all tests passed!", 'g')
  else:
    print(f"{result.failed}")



