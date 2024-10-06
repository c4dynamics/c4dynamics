import sys 
sys.path.append('.')
# utils 
## cprint

import c4dynamics as c4d 



# print(c4d.utils.const.__doc__)
# print(c4d.utils.math.__doc__)



carr = ['k', 'r', 'g', 'y', 'b', 'm', 'c', 'w']

for c in carr:
  c4d.cprint('C4DYNAMICS', c)

import c4dynamics as c4d 
from c4dynamics.utils.tictoc import * 
import numpy as np

N = 10000

tic()

a = np.ones((1, 3))
for i in range(N - 1):
  a = np.concatenate((a, np.ones((1, 3))))

print(a.shape)
print(a)
t1 = toc()
c4d.cprint('numpy concat: ' + str(1000 * t1) + ' ms', 'r')


###
tic()

a = np.zeros((N, 3))
for i in range(N):
  a[i, :] = np.ones((1, 3))

print(a.shape)
print(a)
t2 = toc()
c4d.cprint('numpy predefined: ' + str(1000 * t2) + ' ms', 'g')

### 
tic()

a = []
for i in range(N):
  a.append([1, 1, 1])

a = np.array(a)
print(a.shape)
print(a)
t3 = toc()
c4d.cprint('list to numpy: ' + str(1000 * t3) + ' ms', 'y')

## gif
import socket
import sys, os

if socket.gethostname() != 'ZivMeri-PC':
    print('chaning dir')
    os.chdir('\\\\192.168.1.244\\d\\Dropbox\\c4dynamics')


    from IPython.display import Image


    # sys.path.append(os.path.join(os.getcwd(), '..'))
    import numpy as np 
    from matplotlib import pyplot as plt 
    plt.rcParams["font.size"] = 14
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams["font.family"] = "Times New Roman"   # "Britannic Bold" # "Modern Love"#  "Corbel Bold"# 
    plt.style.use('dark_background')  # 'default' # 'seaborn' # 'fivethirtyeight' # 'classic' # 'bmh'

    import c4dynamics as c4d 
    import numpy as np 





    f16forgif = c4d.rigidbody()


    dt = .01
    for t in np.arange(0, 9, dt): 
        # in 3 seconds make 180 deg: 
        if t < 3: 
            f16forgif.psi += dt * 180 * c4d.d2r / 3
        elif t < 6: 
            f16forgif.theta += dt * 180 * c4d.d2r / 3
        else:
            f16forgif.phi -= dt * 180 * c4d.d2r / 3 
        f16forgif.store(t)


    
    # then it has theta(screen) = 180, phi (screen) = 90
    x0 = [90 * c4d.d2r, 0, 180 * c4d.d2r] 


    modelpath = os.path.join(os.getcwd(), 'examples\\resources\\f16')
    outfol = os.path.join(os.getcwd(), 'examples\\out\\f16_monochrome_gif')


    f16forgif.animate(modelpath, savedir = outfol, angle0 = x0, modelcolor = [0, 0, 0], cbackground = [230 / 255, 230 / 255, 255 / 255])



    from IPython.display import Image

    gifname = 'f16_monochrome_gif.gif'
    c4d.gif(outfol, gifname, duration = 1)

    gifpath = os.path.join(os.getcwd(), 'docs/source/_static/gifs/', gifname)
    os.replace(os.path.join(outfol, gifname), gifpath)
    Image(filename = gifpath) 

## plotdefautls

import socket

if socket.gethostname() != 'ZivMeri-PC':
  print('chaning dir')
  os.chdir('\\\\192.168.1.244\\d\\Dropbox\\c4dynamics')


import sys, os

# sys.path.append(os.path.join(os.getcwd(), '..'))
import numpy as np 
from matplotlib import pyplot as plt 
plt.rcParams["font.size"] = 14
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams["font.family"] = "Times New Roman"   # "Britannic Bold" # "Modern Love"#  "Corbel Bold"# 
plt.style.use('dark_background')  # 'default' # 'seaborn' # 'fivethirtyeight' # 'classic' # 'bmh'

import c4dynamics as c4d 
import numpy as np 

# generate a rigidbody 
f16 = c4d.rigidbody()

dt = .01

for t in np.arange(0, 9, dt): 
    # in 3 seconds make 180 deg: 
    if t < 3: 
        f16.phi += dt * 180 / 9 * c4d.d2r
    elif t < 6: 
        f16.phi += dt * 180 / 6 * c4d.d2r
    else:
        f16.phi += dt * 180 / 3 * c4d.d2r
    f16.store(t)

# plt.figure(figsize = (15, 5))
ax = plt.subplot()
ax.plot(*f16.data('phi', c4d.r2d), 'm', linewidth = 2)

c4d.plotdefaults(ax, '$\\varphi$', 'Time', 'deg', fontsize = 18)


plt.tight_layout()
plt.savefig(os.path.join(os.getcwd()
              , 'docs/source/_static/images/plotdefaults.png')
                , dpi = 600, bbox_inches = 'tight', pad_inches = 0)














