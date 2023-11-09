from matplotlib import pyplot as plt

plt.rcParams["font.family"] = "Corbel Bold"# "Modern Love"# "Britannic Bold" # "Times New Roman"
plt.rcParams["font.size"] = 16

exec(open('importc4d.py').read())

h0 = 1000
dt = .001
t  = 0
g = -9.8

ball = c4d.datapoint(z = h0)

while ball.z >= 0:
    ball.run(dt, np.array([0, 0, g] * ball.m))
    ball.store(t)
    t += dt

plt.style.use('dark_background')
ball.draw('z')

plt.title('Free-Falling Ball vs. Time')
plt.xlabel('TIME (S)')
plt.ylabel('HEIGHT (M)')

ln = plt.gca().lines
ln[0].set_color('tab:purple')

#
# for developers:
#   1) try to change the initial altitude, h0, and re-run the program. 
#   2) draw also the trajectory in x axis: ball.draw('x')
#       what do you see? why there is no motion in x?
#   3) now, set initial velocity in x, change line 7 to: ball = c4d.datapoint(vx = 100, z = -h0)
#       run again and draw the x trajectory. 
#       what do you see now?
#       what does it do to the motion in z axis? why? 
#   4) import c4dynamics as c4d in your project and use the object c4d.datapoint to model your physics. 
#   FAQ? contact zivmeri @ linkedin \ gmail, or C4dynamics at github. 
## 







