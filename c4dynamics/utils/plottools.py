import numpy as np 
from matplotlib import pyplot as plt 
from matplotlib.ticker import ScalarFormatter

def plotdefaults(ax, title, xlabel, ylabel, fontsize = 12, ilines = None):
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

      >>> f16 = c4d.rigidbody()
      >>> dt = .01
      >>> for t in np.arange(0, 9, dt): 
      ...     if t < 3: 
      ...         f16.phi += dt * 180 / 9 * c4d.d2r
      ...     elif t < 6: 
      ...         f16.phi += dt * 180 / 6 * c4d.d2r
      ...     else:
      ...         f16.phi += dt * 180 / 3  * c4d.d2r
      ...     f16.store(t)
      >>> ax = plt.subplot()
      >>> ax.plot(f16.data('t'), f16.data('phi') * c4d.r2d, 'm', linewidth = 2)
      >>> c4d.plotdefaults(ax, '$\\varphi$', 'Time', 'deg', fontsize = 18)

        
    .. figure:: /_static/images/plotdefaults.png

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

    


def figdefaults(fig, savefol = None, darkmode = True): 

    #
    # pyplot
    ##
    if darkmode:
        plt.style.use('dark_background')  

    #
    # figure
    ##
    fdpi = 1200

    # fig.set_dpi(fdpi)
    # plt.subplots_adjust(left = 0.086, right = 0.9, top = 0.9, bottom = 0.152
    #                         , hspace = 0.5, wspace = 0.3) 

    #
    # save
    ##
    if savefol is not None: 
        fig.savefig(savefol, dpi = fdpi, bbox_inches = 'tight', pad_inches = 0.1)






def shiftmargins(filename, width, height, axl, axr):
    
    
    import cv2  

    
    if False: 
        
        bbox = ax.get_position()
        fig_width, fig_height = fig.get_size_inches() * fig.dpi
        width = int(fig_width)

        height = int(fig_height)
        top_left_corner_pixels = (int(bbox.xmin * fig_width), int((1 - bbox.ymax) * fig_height))
        bottom_right_corner_pixels = (int(bbox.xmax * fig_width), int((1 - bbox.ymin) * fig_height))

        axis_left_edge = top_left_corner_pixels[0]
        axis_right_edge = bottom_right_corner_pixels[0]


        # Create a Matplotlib figure and axis
        # Render the figure to a canvas and get the NumPy array representation
        fig.canvas.draw()

        # Convert the canvas to a NumPy array
        # The shape of the array is (height, width, 4), where 4 represents RGBA channels
        image = np.frombuffer(fig.canvas.tostring_argb(), dtype = np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        # Convert the ARGB image to RGBA
        image = np.roll(image, 3, axis = 2)
        # Convert the RGBA image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)


    image_rgb = cv2.imread(filename) 

    # calculate the shift size to cetner image 
    equal_margin_shift = int((width - axr - axl) / 2)

    # Create a translation matrix to shift the image left
    M = np.float32([[1, 0, equal_margin_shift], [0, 1, 0]])
    # Apply the translation to shift the image
    image_rgb = cv2.warpAffine(image_rgb, M, (width, height))
    # image_rgb = image_rgb[10 : -5, :] # crop by taking from row 10 to row -5. 


    
    cv2.imwrite(filename, image_rgb)

 

