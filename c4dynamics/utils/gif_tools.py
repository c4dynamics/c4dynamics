import os
import imageio
import natsort
from matplotlib import pyplot as plt 

# complete gif toolbox
# a function to save frames of vectors in a given rate 
# a function to load images from a folder and generate a gif 
# a function for straight generation of a gif from vector without saving it locally. 
        
# matplotlib
#   3 ways to draw plot:
#       1 
#creating the arrays for testing
    import numpy as np
    x = np.arange(1, 100)
    y = np.sqrt(x)
    #1st way
    plt.plot(x, y)
    #2nd way
    ax = plt.subplot()
    ax.plot(x, y)
    #3rd way
    figure = plt.figure()
    new_plot = figure.add_subplot(111)
    new_plot.plot(x, y)

def make_plot(missile, target, savedir): 

    xM = missile._data[1:, 1]
    yM = missile._data[1:, 2]
    zM = missile._data[1:, 3] 
    xT = target._data[1:, 1]
    yT = target._data[1:, 2]
    zT = target._data[1:, 3]       
    

    # t = np.arange(0, obj.tmax + obj.dt, obj.dt)

    # Make an image every di time points, corresponding to a frame rate of fps
    # frames per second.
    # Frame rate, s-1
    fps = 10
    di = int(1 / fps / dt)
    fig = plt.figure(figsize = (8.3333, 6.25), dpi = 72)
    plt.ioff()
    ax = fig.add_subplot(111)
    ax.set_facecolor('indianred')
    ns = 20
    # Plot a trail of the m2 bob's position for the last trail_secs seconds.
    trail_secs = 1
    # This corresponds to max_trail time points.
    max_trail = int(trail_secs / obj.dt)

    for i in range(0, len(xM)): # , di):
        # print(i // di, '/', t.size // di)
        
        # Plot and save an image of the double pendulum configuration for time
        # point i.s
        # The pendulum rods.
        ax.plot(xM[i], yM[i], zM[i], lw = 2, c = 'k')
        ax.plot(xT[i], yT[i], zT[i], lw = 2, c = 'r')


        # for j in range(ns):
        #     imin = i - (ns-j) * s
        #     if imin < 0:
        #         continue
        #     imax = imin + s + 1
        #     # The fading looks better if we square the fractional length along the
        #     # trail.
        #     alpha = (j / ns)**2
        #     ax.plot(x2[imin : imax], y2[imin : imax], c = 'r', solid_capstyle = 'butt',
        #             lw = 2, alpha = alpha)

        # Centre the image on the fixed anchor point, and ensure the axes are equal
        
        ax.set_xlim(-obj.L1 - obj.L2 - obj.r, obj.L1 + obj.L2 + obj.r)
        ax.set_ylim(-obj.L1 - obj.L2 - obj.r, obj.L1 + obj.L2 + obj.r)
        ax.set_aspect('equal', adjustable = 'box')
        plt.axis('off')
        plt.savefig(savedir + '/_img{:04d}.png'.format(i//di), dpi = 72) # frames
        plt.cla()
        
    print('images saved in ' + savedir)
    plt.close(fig)



def gen_gif(dirname):
    images = []
    dirfiles = natsort.natsorted(os.listdir(dirname)) # 'frames/'
    # dirfiles.sort(key = lambda f: int(''.join(filter(str.isdigit, f))))
    # dirfiles = [f for f in listdir(dirname) if isfile(join(dirname, f))]
    for filename in dirfiles:
        # print(filename)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append(imageio.imread(dirname + '/' + filename))

    imageio.mimsave('_img_movie.gif', images)
    print('_img_movie.gif is saved in ' + os.getcwd())



