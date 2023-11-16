import os
import imageio
import natsort

def gen_gif(dirname, gif_name):
    images = []
    dirfiles = natsort.natsorted(os.listdir(dirname)) # 'frames/'
    # dirfiles.sort(key = lambda f: int(''.join(filter(str.isdigit, f))))
    # dirfiles = [f for f in listdir(dirname) if isfile(join(dirname, f))]
    for filename in dirfiles:
        # print(filename)
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            images.append(imageio.imread(dirname + '/' + filename))

    imageio.mimsave(os.path.join(dirname, gif_name), images)


