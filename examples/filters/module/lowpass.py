import numpy as np 
from matplotlib import pyplot as plt 
plt.style.use('dark_background')  

import os, sys
sys.path.append('')
import c4dynamics as c4d 




# Define the simulation parameters
fs = 100000  # Sampling frequency
t = np.linspace(0, 0.01, int(0.01 * fs))  # Time vector (0 to 10ms)


# Define the RC filter components
R = 1000  # 1 kOhm
C = 0.1e-6  # 0.1 uF
fc = 1 / (2 * np.pi * R * C)  # Cutoff frequency
# Define the input signal: a sum of two sinusoids, one below and one above the cutoff frequency
f1 = 500  # Frequency below cutoff (500 Hz)
f2 = 5000  # Frequency above cutoff (5000 Hz)

audio_in = np.sin(2 * np.pi * f1 * t) + np.sin(2 * np.pi * f2 * t)


dt = 1 / fs
lpf = c4d.filters.lowpass(alpha = dt / (R * C + dt))
audio_out = c4d.state(x = 0) 
audio_out.store(0)


for n in range(1, len(audio_in)):

  audio_out.x = lpf.sample(audio_in[n]) 
  audio_out.store(t[n])





from matplotlib.ticker import ScalarFormatter
# plotcov = False 
textsize = 10
# covlabel = ''
# pad_left = 0.1
# pad_others = 0.2

fig, ax = plt.subplots(1, 1, dpi = 200, figsize = (9, 3) # figsize = (8, 2) # 
              , gridspec_kw = {'left': .1, 'right': .95
                                , 'top': .9 , 'bottom': .1
                                  , 'hspace': 0.5, 'wspace': 0.4}) 


ax.plot(t * 1000, audio_in, 'c', linewidth = 1.5, label = 'X in') 
ax.plot(audio_out.data('x')[0] * 1000, audio_out.data('x')[1], 'm', linewidth = 1.5, label = 'X out')

c4d.plotdefaults(ax, '2 Sinusoids Lowpass Filtered', 'Time [msec]', 'Amplitude', textsize)
ax.legend(fontsize = 'xx-small', facecolor = None, framealpha = .5)  #, edgecolor = None Set font size and legend box properties
# xx-small, x-small, small, medium, large, x-large, xx-large, larger, smaller, None

ax.yaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.get_major_formatter().set_useOffset(False)
ax.yaxis.get_major_formatter().set_scientific(False)






for ext in ['.png', '.svg']:
  plt.savefig(os.path.join(os.getcwd(), 'docs', 'source', '_static', 'figures'
                        , 'filters_' + os.path.basename(__file__)[:-3] + ext)
              , dpi = 1200
                  , bbox_inches = 'tight', pad_inches = .3)
                  # , bbox_inches = bbox)





plt.show(block = True)


