import os, sys
sys.path.append('')
import numpy as np 
import c4dynamics as c4d 
from matplotlib import pyplot as plt 
plt.style.use('dark_background')  
plt.switch_backend('TkAgg')



# every example should be self contained. 
runerrors = False
saveimages = False   
viewimages = False 



c4d.cprint('P()', 'c')
s = c4d.state(theta = 3.14, x = 1, y = 1)
print(s.P())
# 1.414 


s2 = c4d.state(x = 1)
print(s.P(s2))
# 0


s2 = c4d.state(z = 1)
if runerrors: 
  print(s.P(s2))
# Exception has occurred: ValueError  
# At least one distance coordinate, x, y, or z, must be common to both instances.

camera = c4d.state(x = 0, y = 0)
car = c4d.datapoint(x = -100, vx = 40, vy = -7)
dist = []
time = np.linspace(0, 10, 1000)
for t in time:
  car.inteqm(np.zeros(3), time[1] - time[0])
  dist.append(camera.P(car))




factorsize = 4
aspectratio = 1080 / 1920 
_, ax = plt.subplots(1, 1, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.15, 'right': .9, 'top': .9, 'bottom': .2, 'hspace': .8})
# print(type(ax))
ax.plot(time, dist, 'm', linewidth = 2)
c4d.plotdefaults(ax, 'Distance', 'Time (s)', '(m)', 14)



# standard saving  \ bad margings. 
savedir = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'states') 
figname = c4d.j(savedir, 'state_P.png')


plt.savefig(figname, bbox_inches = 'tight', pad_inches = .05, dpi = 600)
# plt.show(block = True)





