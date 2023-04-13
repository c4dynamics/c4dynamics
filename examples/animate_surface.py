






import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits import mplot3d
from matplotlib import cm 
from matplotlib import animation 

fig = plt.figure(facecolor = 'black')
ax = plt.axes(projection = '3d')
ax.axis('off')


# sphere 
u = np.linspace(0, np.pi, 100)
v = np.linspace(0, 2 * np.pi, 100)
[u, v] = np.meshgrid(u, v)

x = np.sin(u) * np.cos(v)
y = np.sin(u) * np.sin(v)
z = np.cos(u) 

# hyperboloid 
u1 = np.linspace(-2, 2, 100)
v1 = np.linspace(0, 2 * np.pi, 100)
[u1, v1] = np.meshgrid(u1, v1)

x1 = np.sinh(u1) * np.cos(v1)
y1 = np.sinh(u1) * np.sin(v1)
z1 = np.cosh(u1) 

# cylinder 
# n = 20;
# r = [1 1]';
# if nargs > 0, r = args{1}; end
# if nargs > 1, n = args{2}; end
# r = r(:); % Make sure r is a vector.
# m = length(r); if m==1, r = [r;r]; m = 2; end

# theta = (0:n)/n*2*pi;

# sintheta = sin(theta); sintheta(n+1) = 0;

# x = r * cos(theta);
# y = r * sintheta;

# z = (0:m-1)'/(m-1) * ones(1,n+1);

n = 20
r = np.array([1, 1])
m = len(r); 
    
theta = np.arange(n + 1) / n * 2 * np.pi
sintheta = np.sin(theta); 
# sintheta = sintheta[np.r_[:len(sintheta), 0]] 
sintheta[-1] = 0

x2 = np.outer(r, np.cos(theta))
y2 = np.outer(r, sintheta)
z2 = np.outer(np.arange(m) / (m - 1), np.ones(n + 1))


ax.set_facecolor('cyan')

def init():
    # ax.plot_surface(z1, y1, x1, cmap = cm.PuRd) 
    # ax.plot_surface(-z1, y1, x1, cmap = cm.PuRd)
    # ax.plot_surface(z, y, x, cmap = cm.RdPu)
    ax.plot_surface(z2, y2, x2, cmap = cm.RdPu)
    print('init')

def animate(i):
    print(i)
    ax.view_init(elev = 4 * i, azim = i * 4)

ani = animation.FuncAnimation(fig, animate, init_func = init, frames = 90, interval = 0, blit = False)
plt.show()






