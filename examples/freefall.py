from matplotlib import pyplot as plt
exec(open('importc4d.py').read())

h0 = 1000
dt = .05
t  = 0
g = -9.8

ball = c4d.datapoint(z = h0)

while ball.z >= 0:
    ball.run(dt, np.array([0, 0, g] * ball.m))
    ball.store(t)
    t += dt

ball.draw('z')
# plt.gca().invert_yaxis()
plt.title('FREE FALLING BALL')
plt.xlabel('TIME (S)')
plt.ylabel('HEIGHT (M)')

#
# for developers:
#   1) try to change the initial altitude, h0, and re-run the program. 
#   2) draw also the trajectory in x axis: ball.draw('x')
#       what do you see? why there is no motion in x?
#   3) now, set initial velocity in x, change line 7 to: ball = c4d.datapoint(vx = 100, z = -h0)
#       run again and draw the x trajectory. 
#       what do you see now?
#       what does it do to the motion in z axis? why? 
#   4) import C4dynamics as c4d in your project and use the object c4d.datapoint to model your physics. 
#   FAQ? contact zivmeri @ linkedin \ gmail, or C4dynamics at github. 
## 
