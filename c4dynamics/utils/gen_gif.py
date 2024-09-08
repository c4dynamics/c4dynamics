import os
import imageio
import natsort

def gif(dirname, gif_name, duration = None):
    '''

    Gif creator.

    `gif` creates a Gif from a directory containing image files.

    Parameters
    ----------

    dirname : str
        The path to the directory containing image files.

    gif_name : str
        The desired name of the output GIF file.

    duration : float, optional
        The duration (in seconds) for each frame of the GIF. 
        If None, default duration is used.

        
    Example
    -------
    .. code::

      >>> from IPython.display import Image
      >>> f16 = c4d.rigidbody()
      >>> dt = .01
      >>> for t in np.arange(0, 9, dt): 
      ...     # in 3 seconds make 180 deg: 
      ...     if t < 3: 
      ...         f16.psi += dt * 180 * c4d.d2r / 3
      ...     elif t < 6: 
      ...         f16.theta += dt * 180 * c4d.d2r / 3
      ...     else:
      ...         f16.phi -= dt * 180 * c4d.d2r / 3 
      ...     f16.store(t)
      >>> x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r] 
      >>> modelpath = os.path.join(os.getcwd(), 'examples\\resources\\f16')
      >>> outfol = os.path.join(os.getcwd(), 'examples\\out\\f16_monochrome_gif')
      >>> f16.animate(modelpath, savedir = outfol, angle0 = x0, modelcolor = [0, 0, 0], cbackground = [230 / 255, 230 / 255, 255 / 255])
      >>> gifname = 'f16_monochrome_gif.gif'
      >>> c4d.gif(outfol, gifname, duration = 1)
      >>> Image(filename = os.path.join(outfol, gifpath)) 

    .. figure:: /_static/gifs/f16_monochrome_gif.gif
    
    '''
    dirfiles = natsort.natsorted(os.listdir(dirname)) 
    imgfiles = [f for f in dirfiles if f.lower().endswith(('.png', '.jpg', '.jpeg', 'bmp', '.tiff'))] 

    # dirfiles.sort(key = lambda f: int(''.join(filter(str.isdigit, f))))
    # dirfiles = [f for f in listdir(dirname) if isfile(join(dirname, f))]

    # x = (frame_rate � duratio) / total number of images

    fps = 60 # 60hz (60frames per second) -> 16.6msec
    if duration is None: 
        interval = 1
    else: 
        interval = int(len(imgfiles) / (duration * fps))

    images = []

    for i in range(0, len(imgfiles), interval):
        images.append(imageio.imread(os.path.join(dirname, imgfiles[i])))

    gif_name = gif_name if gif_name.endswith('.gif') else gif_name + '.gif'
    imageio.mimsave(os.path.join(dirname, gif_name)
                        , images, loop = 0, duration = int(1000 * 1 / fps))


