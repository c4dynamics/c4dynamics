import time
import numpy as np
import sys, os, importlib
# from enum import Enum
from matplotlib import pyplot as plt
# plt.close('all')

sys.path.append(os.path.join(os.getcwd(), '..'))
import c4dynamics as c4d
importlib.reload(c4d)
from c4dynamics.utils.params import * 
import dof6sim as s6d

# it's probably useless because it can print to file when range > 1 and always print the last sim. 
# class printres(Enum):
#     none = 0
#     dynamics = 1
#     statistics = 2

# 
# user input
##
outfol = 'aviva'
# print2file = printres.dynamics

cfile = os.path.join(os.getcwd(), 'examples', 'out', outfol, 's6dout.txt')

if not os.path.exists(os.path.dirname(cfile)):
    os.makedirs(os.path.dirname(cfile))
else:
    if os.path.isfile(cfile):
        os.remove(cfile)

with open(cfile, 'at') as f:
    f.write('%-15s %-15s %-15s %-15s %-15s %-15s %-15s %-15s \n' 
        % ('tau seeker (s)', 'tau ctrl (s)', 'time (s)', 'position (m)', 'velocity (m/s)', 'acc (m/s^2)', 'miss distance (m)', 'flight time (s)'))

tauseeker0 = 2.0 # 0.01
tauctrl0 = 2.0 # 0.04

for tau in range(1000): 
    tauseeker = np.max((tauseeker0 + np.random.randn(), 0.01))
    tauctrl = np.max((tauctrl0 + np.random.randn(), 0.01))
    
    # print('taus ', tauseeker, ', tauc', tauctrl)
    tic = time.time()

    missile, target, md, tfinal, data_arrays = s6d.dof6sim(tauseeker = tauseeker, tauctrl = tauctrl)
    
    # print('miss: %.2f, flight time: %.1f' % (md, tfinal))
    print('tauseeker: %.3f, tauctrl: %.3f, miss: %.5f, flight time: %.1f' % (tauseeker, tauctrl, md, tfinal))
    # print('total running time: ', time.time() - tic)

    delta_data  = data_arrays[0]
    omegaf_data = data_arrays[1]
    acc_data    = data_arrays[2]
    aoa_data    = data_arrays[3]
    moments_data = data_arrays[4]

    # if print2file: # print to file 
    with open(cfile, 'at') as f:

        pos_rel = np.linalg.norm(np.array([target.get_data('x') - missile.get_data('x')
                    , target.get_data('y') - missile.get_data('y')
                        , target.get_data('z') - missile.get_data('z')]).T
                            , ord = 2, axis = 1)
        vel_rel = np.linalg.norm(np.array([target.get_data('vx') - missile.get_data('vx')
                    , target.get_data('vy') - missile.get_data('vy')
                        , target.get_data('vz') - missile.get_data('vz')]).T
                            , ord = 2, axis = 1)
        acc_rel = np.linalg.norm(np.array([target.get_data('ax') - missile.get_data('ax')
                    , target.get_data('ay') - missile.get_data('ay')
                        , target.get_data('az') - missile.get_data('az')]).T
                            , ord = 2, axis = 1)
        
        tgtrng = np.sqrt(target.x0**2 + target.y0**2 + target.z0**2) * np.ones(pos_rel.shape).astype(int)

        md_vec = md * np.ones(pos_rel.shape)
        tf_vec = tfinal * np.ones(pos_rel.shape)


        np.savetxt(f, (np.array([tauseeker * np.ones(pos_rel.shape), tauctrl * np.ones(pos_rel.shape)
                        , missile.get_data('t'), pos_rel, vel_rel, acc_rel, md_vec, tf_vec]).T) 
                            , '%-15.3f %-15.3f %-15.4f %-15.0f %-15.0f %-15.0f %-15.6f %-15.3f')


#
# figures
##

plt.rcParams["font.family"] = "Times New Roman" # "Britannic Bold" # "Modern Love"#  "Corbel Bold"# 
plt.rcParams["font.size"] = 24
plt.style.use('dark_background')  # 'default' # 'seaborn' # 'fivethirtyeight' # 'classic' # 'bmh'# plt.style.use('ggplot') # 
plt.rcParams['figure.figsize'] = (6.0, 4.0) # set default size of plots
plt.rcParams['image.interpolation'] = 'nearest'
# plt.rcParams['image.cmap'] = 'gray'
# plt.rcParams['text.usetex'] = True

plt.ion()
plt.close('all')

# Some more magic so that the notebook will reload external python modules;
# see http://stackoverflow.com/questions/1907993/autoreload-of-modules-in-ipython
# %load_ext autoreload
# %autoreload 2

# 
# plt.show() plots all the figures present in the state machine. Calling it only at the end of 
#       the script, ensures that all previously created figures are plotted.
# Now you need to make sure that each plot indeed is created in a different figure. That can be 
#       achieved using plt.figure(fignumber) where fignumber is a number starting at index 1.
#



fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

textcolor = 'white'

ax1.plot(missile.get_data('x'), -missile.get_data('z') * 0.3048, 'b', linewidth = 4, label = 'missile')
ax1.plot(target.get_data('x'), -target.get_data('z') * 0.3048, 'r', linewidth = 4, label = 'target')
ax1.set_title('Side View', color = textcolor)
ax1.set(xlabel = 'Downrange (m)', ylabel = 'Altitude (ft)')
ax1.xaxis.label.set_color(textcolor)
ax1.yaxis.label.set_color(textcolor)
ax1.set_xlim(0, 4000)
ax1.set_ylim(0, 1100)
ax1.grid(alpha = .5,  which = 'both', color = textcolor)
ax1.tick_params(axis = 'x', colors = textcolor)  # Change X-axis tick color to purple
ax1.tick_params(axis = 'y', colors = textcolor)  # Change X-axis tick color to purple
ax1.legend(fontsize = 14) # title = '#trk', loc = 'center left', bbox_to_anchor = (1, 0.5))

ax2.plot(missile.get_data('x'), missile.get_data('y'), 'b', linewidth = 4, label = 'missile')
ax2.plot(target.get_data('x'), target.get_data('y'), 'r', linewidth = 4, label = 'target')
ax2.set_title('Top View', color = textcolor)
ax2.set(xlabel = 'Downrange (m)', ylabel = 'Crossrange (m)')
ax2.xaxis.label.set_color(textcolor)
ax2.yaxis.label.set_color(textcolor)
ax2.set_xlim(0, 4000)
ax2.set_ylim(0, 1100)
ax2.grid(alpha = .5, which = 'both', color = textcolor)
ax2.tick_params(axis = 'x', colors = textcolor)  # Change X-axis tick color to purple
ax2.tick_params(axis = 'y', colors = textcolor)  # Change X-axis tick color to purple
ax2.legend(fontsize = 14) # title = '#trk', loc = 'center left', bbox_to_anchor=(1, 0.5))
# ax2.invert_yaxis()

plt.savefig('examples\\trajectories.png', format = 'png', transparent = True)


from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure()
ax = fig.add_subplot(111, projection = '3d')

# Plot the trajectory
ax.plot(missile.get_data('x'), missile.get_data('y'), missile.get_data('z') * 0.3048, 'b', linewidth = 4, label = 'missile')
ax.plot(target.get_data('x'), target.get_data('y'), target.get_data('z') * 0.3048, 'r', linewidth = 4, label = 'target')
ax.set_title('Trajectories')
ax.set(xlabel = 'X (m)', ylabel = 'Y (m)', zlabel = 'Z (ft)')
ax.set_xlim(0, 4000)
ax.set_ylim(0, 1100)
ax.grid(alpha = .5)
ax.invert_zaxis()

ax.legend(fontsize = 14) # title = '#trk', loc = 'center left', bbox_to_anchor = (1, 0.5))

# Show the plot
plt.show()


# fig.tight_layout()
# plt.show()

# missile.draw('theta')

# target.draw('vx')
# target.draw('vy')

#
# total velocity 
##
plt.figure()
plt.plot(missile.get_data('t'), np.sqrt(missile.get_data('vx')**2 + missile.get_data('vy')**2 + missile.get_data('vz')**2))
plt.title('Vm')
plt.xlabel('t')
plt.ylabel('m/s')
plt.grid()
plt.legend()

# 
# omega los 
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_data('t'), omegaf_data[:, 0] * c4d.r2d, 'k', linewidth = 2)
ax1.set_title('$omega_p$')
ax1.grid()
ax1.set_xlim(0, 10)
ax1.set_ylim(-10, 10)
ax1.set(xlabel = 'time', ylabel = '')

ax2.plot(missile.get_data('t'), omegaf_data[:, 1] * c4d.r2d, 'k', linewidth = 2)
ax2.set_title('$omega_y$')
ax2.grid()
ax2.set_xlim(0, 10)
ax2.set_ylim(-10, 10)
ax2.set(xlabel = 'time', ylabel = '')

plt.subplots_adjust(hspace = 0.5)

# 
# wing deflctions
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_data('t'), delta_data[:, 0] * c4d.r2d, 'k', linewidth = 2)
ax1.set_title('\delta p')
ax1.grid()
ax2.plot(missile.get_data('t'), delta_data[:, 1] * c4d.r2d, 'k', linewidth = 2)
ax2.set_title('\delta y')
ax2.grid()

# 
# body-frame acceleration cmds
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_data('t'), acc_data[:, 2] / c4d.g, 'k', linewidth = 2)
ax1.set_title('aczb')
ax1.grid()
ax2.plot(missile.get_data('t'), acc_data[:, 1] / c4d.g, 'k', linewidth = 2)
ax2.set_title('acyb')
ax2.grid()

# 
# angles of attack
##
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
fig.tight_layout()

ax1.plot(missile.get_data('t'), aoa_data[:, 0] * c4d.r2d, 'k', linewidth = 2)
ax1.set_title('alpha')
ax1.grid()
ax2.plot(missile.get_data('t'), aoa_data[:, 1] * c4d.r2d, 'k', linewidth = 2)
ax2.set_title('beta')
ax2.grid()
ax3.plot(missile.get_data('t'), aoa_data[:, 2] * c4d.r2d, 'k', linewidth = 2)
ax3.set_title('total')
ax3.grid()

# 
# body-frame acceleration cmds
##
fig, (ax1, ax2) = plt.subplots(2, 1)
fig.tight_layout()

ax1.plot(missile.get_data('t'), moments_data[:, 1], 'k', linewidth = 2)
ax1.set_title('pitch moment')
ax1.grid()
ax2.plot(missile.get_data('t'), moments_data[:, 2], 'k', linewidth = 2)
ax2.set_title('yaw moment')
ax2.grid()

# 
# euler angles
##
missile.draw('psi')
missile.draw('theta')
missile.draw('phi')

# 
# body rates 
##
missile.draw('r')
missile.draw('q')
missile.draw('p')


# # 
# # 3d plot
# ##

# fig = plt.figure()
# ax = plt.subplot(projection = '3d')
# # ax.invert_zaxis()

# plt.plot(missile._data[1:, 1], missile._data[1:, 2], missile._data[1:, 3] 
#         , 'k', linewidth = 2, label = 'missile')
# plt.plot(target._data[1:, 1], target._data[1:, 2], target._data[1:, 3]
#         , 'r', linewidth = 2, label = 'target')
    
    
    
   
print(time.time() - tic)

plt.show(block = True)
# plt.close('all')
    

    
    
    
    
    