# from scipy.integrate import odeint 
# from scipy.linalg import solve_discrete_are
import numpy as np 
import cv2 
from matplotlib import pyplot as plt 


# not for demonstration: 
import os, sys
from enum import Enum  
import zlib 




plt.style.use('dark_background')  
plt.switch_backend('TkAgg')


def rootdir(dir):
  print(dir)
  if dir[-2:] == ':\\': return dir  
  return rootdir(os.path.dirname(dir))

def c4dir(dir, addpath = ''):
  # dirname and basename are supplamentary:
  # c:\dropbox\c4dynamics\text.txt
  # dirname: c:\dropbox\c4dynamics
  # basename: text.txt 
  


  inc4d = os.path.basename(dir) == 'c4dynamics'
  hasc4d = any(f == 'c4dynamics' for f in os.listdir(dir) 
                if os.path.isdir(os.path.join(dir, f)))


  if inc4d and hasc4d: 
    addpath += ''
    return addpath
  
  addpath += '..\\'
  return c4dir(os.path.dirname(dir), addpath)


# rootdir(os.getcwd()) 

print(os.getcwd())
c4path = c4dir(os.getcwd())
print(c4path)
sys.path.append(c4path)


import c4dynamics as c4d 
from c4dynamics.utils.tictoc import tic, toc 

savedir = os.path.join(c4path, 'docs', 'source', '_examples', 'kf') 




import pickle 

yolo3 = c4d.detectors.yolov3()  


# https://www.pexels.com/@abed-ismail/
dname = 'drifting_car.mp4'
vidpath = c4d.datasets.video('drifting_car')


rtdetect = False # True # 

if not rtdetect: 
  
  ptspath = os.path.join('examples', '_out')
  ptsfile = os.path.join(ptspath, os.path.basename(vidpath)[:-4] + '.pkl')
  
  if os.path.exists(ptsfile):
    with open(ptsfile, 'rb') as file:
      detections = pickle.load(file)
  else: 
    detections = c4d.pixelpoint.video_detections(vidpath, storepath = ptspath)

#
video_cap = cv2.VideoCapture(vidpath)
fps = video_cap.get(cv2.CAP_PROP_FPS)
dt_frame = 1 / fps # 1 / frame per second = the length of a single frame
N = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT)) # total frames count 
tf = N * dt_frame 
# 


samplefactor = 2 



A = np.zeros((6, 6))
A[0, 4] = A[1, 5] = 1

C = np.zeros((4, 6))
C[0, 0] = C[1, 1] = C[2, 2] = C[3, 3] = 1


# observability test 
obsv = C
n = len(A)
for i in range(1, n):
  obsv = np.vstack((obsv, C @ np.linalg.matrix_power(A, i)))
rank = np.linalg.matrix_rank(obsv)
c4d.cprint(f'The system is observable (rank = n = {n}).' if rank == n else f'The system is not observable (rank = {rank}, n = {n}).', 'y')

dt = dt_frame / samplefactor # .0333 / 2 = .0166s 


def steadystate():


  c4d.cprint('steadystate', 'y')

    
  dt = dt_frame / samplefactor
  kf = c4d.filters.kalman.velocitymodel(dt, 4, 4)
   
  
  
  video_cap = cv2.VideoCapture(vidpath)
  video_out = cv2.VideoWriter(c4d.j(savedir, dname)
                              , cv2.VideoWriter_fourcc(*'mp4v')
                                  , int(video_cap.get(cv2.CAP_PROP_FPS))
                                      , [int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                                         , int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))])
  # import imageio
  # images2gif = []


  t = 0
  while video_cap.isOpened():
    kf.store(t)
    t += dt
    # if t > 100: break 
  
    kf.predict()

    if round(t / dt_frame, 1) % 1 >= 1e-10: continue   
    
    # camera cycle:

    ret, frame = video_cap.read()
    if not ret: break
    if rtdetect: 
      d = yolo3.detect(frame)
    else: 
      crc32 = zlib.crc32(frame.tobytes())
      d = detections[crc32]
    for di in d: print(di.class_id)

    if d and (d[0].class_id == 'car'): # or d[0].class_id == 'truck'): 
      kf.update(d[0].X)
      # cv2.rectangle(frame, d[0].box[0], d[0].box[1], [255, 0, 0], 2) 
      kf.detect = d 
      kf.storeparams('detect', t)
  

  
    cv2.rectangle(frame, box(kf.X)[0], box(kf.X)[1], [0, 255, 0], 2) 
    cv2.imshow('', frame)
    cv2.waitKey(10)
    video_out.write(frame)
    # images2gif.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))



  cv2.destroyAllWindows()
  video_out.release()
  # imageio.mimsave(c4d.j(savedir, dname[:-4] + '.gif'), images2gif, loop = 0, duration = tf / 2)

  return kf, 'steadystate' 



def box(X):
  # top left
  xtl = int(X[0] - X[2] / 2)
  ytl = int(X[1] - X[3] / 2)

  # bottom right 
  xbr = int(X[0] + X[2] / 2)
  ybr = int(X[1] + X[3] / 2)

  return [(xtl, ytl), (xbr, ybr)]


def drawkf(kf, kf_label): 


  if kf_label == 'steadystate':
    #
    # figure 1 - just the state
    ##
    kf.plot('x', filename = c4d.j(savedir, kf_label + '_x.png'))


    #
    # figure 2 - state and detections 
    ##
    c4d._figdef()
    plt.plot(*kf.data('x'), 'om', markersize = 1, label = 'estimation')
    plt.gca().plot(kf.data('detect')[0], np.vectorize(lambda d: d.x if isinstance(d, c4d.pixelpoint) else np.nan)(kf.data('detect')[1]), 'co', markersize = 1, label = 'detection')
    c4d.plotdefaults(plt.gca(), 'x vs detections', 'Time', 'x', 8)
    plt.legend(fontsize = 4, facecolor = None) #, loc = 'upper left')
    plt.savefig(c4d.j(savedir, kf_label + '_detections.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)
    
    plt.gca().set_xlim(4.46, 4.699)
    plt.gca().set_ylim(515, 530)
    plt.savefig(c4d.j(savedir, kf_label + '_detections_zoom.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)


  #
  # figure 3 - state + detection + covariance - no zoom, not stored 
  ##
  c4d._figdef()
  plt.plot(*kf.data('x'), 'om', markersize = 1, label = 'estimation')
  plt.gca().plot(kf.data('detect')[0], np.vectorize(lambda d: d.x if isinstance(d, c4d.pixelpoint) else np.nan)(kf.data('detect')[1]), 'co', markersize = 1, label = 'detection')
  t_std, x_std = kf.data('P00')[0], np.sqrt(kf.data('P00')[1])
  plt.gca().plot(t_std, kf.data('x')[1] - x_std, 'w', linewidth = 1, label = 'std')
  plt.gca().plot(t_std, kf.data('x')[1] + x_std, 'w', linewidth = 1)
  # plt.gca().set_xlim(4.46, 4.699)
  # plt.gca().set_ylim(515, 530)
  plt.legend(fontsize = 4, facecolor = None)
  c4d.plotdefaults(plt.gca(), 'x vs detections vs std', 'Time', 'x', 8)
  plt.savefig(c4d.j(savedir, 'steadystate_std.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)



  #
  # figure 3 - state + detection + covariance: zoom, stored 
  ##
  c4d._figdef()
  plt.plot(*kf.data('x'), 'om', markersize = 1, label = 'estimation')
  plt.gca().plot(kf.data('detect')[0], np.vectorize(lambda d: d.x if isinstance(d, c4d.pixelpoint) else np.nan)(kf.data('detect')[1]), 'co', markersize = 1, label = 'detection')
  t_std, x_std = kf.data('P00')[0], np.sqrt(kf.data('P00')[1])
  plt.gca().plot(t_std, kf.data('x')[1] - x_std, 'w', linewidth = 1, label = 'std')
  plt.gca().plot(t_std, kf.data('x')[1] + x_std, 'w', linewidth = 1)
  plt.gca().set_xlim(3.8, 4.3)
  plt.gca().set_ylim(470, 520)
  plt.legend(fontsize = 4, facecolor = None)
  c4d.plotdefaults(plt.gca(), 'x vs detections vs std', 'Time', 'x', 8)
  plt.savefig(c4d.j(savedir, kf_label + '_std_zoom.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)



  
  if kf_label == 'steadystate':
    #
    # figure 4: top view trajectory
    ##
    c4d._figdef()  
    plt.gca().plot(kf.data('x')[1], -kf.data('y')[1], 'm')
    c4d.plotdefaults(plt.gca(), 'top view - steady-state mode', 'x', 'y', 8)
    plt.savefig(c4d.j(savedir, kf_label + '_top.png'), bbox_inches = 'tight', pad_inches = .2, dpi = 600)

  plt.show(block = True)


def data_cursor(): 

  import matplotlib.pyplot as plt
  import numpy as np
  from mpldatacursor import datacursor

  fig, axes = plt.subplots(ncols=2)

  left_artist = axes[0].plot(range(11))
  axes[0].set(title='No box, different position', aspect=1.0)

  right_artist = axes[1].imshow(np.arange(100).reshape(10,10))
  axes[1].set(title='Fancy white background')

  # Make the text pop up "underneath" the line and remove the box...
  dc1 = datacursor(left_artist, xytext=(15, -15), bbox=None)

  # Make the box have a white background with a fancier connecting arrow
  dc2 = datacursor(right_artist, bbox=dict(fc='white'),
                  arrowprops=dict(arrowstyle='simple', fc='white', alpha=0.5))
  
  plt.show(block = True)


def continuous():

  c4d.cprint('continuous', 'y')

  dt = dt_frame / samplefactor 

  from scipy.linalg import expm 

  A = np.zeros((6, 6))
  A[0, 4] = A[1, 5] = 1

  C = np.zeros((4, 6))
  C[0, 0] = C[1, 1] = C[2, 2] = C[3, 3] = 1

  noisefactor = .5 

  ''' covariance matrices '''
  qstd = 4 
  rstd = 4 
  Q = np.eye(6) * qstd**2 #* noisefactor / dt 
  R = np.eye(4) * rstd**2 #* noisefactor * dt 
  fix4s = False 
  kf = c4d.filters.kalman({'x': 0, 'y': 0, 'w': 0, 'h': 0, 'vx': 0, 'vy': 0}
                              , P0 = Q, A = A, C = C, Q = Q, R = R, dt = dt)
   
  
    
  import warnings
  # warnings.simplefilter('ignore', c4d.c4warn)
  video_cap = cv2.VideoCapture(vidpath)
  t = 0
  while video_cap.isOpened():
    kf.store(t)
    # print(t)
    t += dt

    # if t > 100: break 
  
    if fix4s and t > 3.9 and t < 4.15:
      Q = np.eye(6) * 8**2 * noisefactor / dt 
    else: 
      Q = np.eye(6) * 4**2 * noisefactor / dt 

    kf.predict(Q = Q, u = 1)

    if round(t / dt_frame, 1) % 1 >= 1e-10: continue   
    
    # camera cycle:

    ret, frame = video_cap.read()
    if not ret: break
    if rtdetect: 
      d = yolo3.detect(frame)
    else: 
      crc32 = zlib.crc32(frame.tobytes())
      d = detections[crc32]
    # for di in d: print(di.class_id)

    if d and (d[0].class_id == 'car'): # or d[0].class_id == 'truck'): 
      kf.update(d[0].X)
      # cv2.rectangle(frame, d[0].box[0], d[0].box[1], [255, 0, 0], 2) 
      kf.detect = d 
      kf.storeparams('detect', t)
  

  
  #   cv2.rectangle(frame, box(kf.X)[0], box(kf.X)[1], [0, 255, 0], 2) 
  #   cv2.imshow('', frame)
  #   cv2.waitKey(10)


  # cv2.destroyAllWindows()



  return kf, 'continuous' 


def discrete():

  c4d.cprint('discrete', 'y')

  dt = dt_frame / samplefactor 
    

  from scipy.linalg import expm 

  A = np.zeros((6, 6))
  A[0, 4] = A[1, 5] = 1
  F = expm(A * dt)
  H = np.zeros((4, 6))
  H[0, 0] = H[1, 1] = H[2, 2] = H[3, 3] = 1

  noisefactor = .5 # dt * 2 
  ''' 
  covariance matrices 
  Qk = I * 8, Rk = I * 8
  Q = I * 480, R = 
  '''
  Qk = np.eye(6) * 4**2 * noisefactor
  Rk = np.eye(4) * 4**2 * noisefactor

  kf = c4d.filters.kalman({'x': 0, 'y': 0, 'w': 0, 'h': 0, 'vx': 0, 'vy': 0}
                              , P0 = Qk, F = F, H = H, Qk = Qk, Rk = Rk)
   
  print(kf.A) 
  n = kf.F.shape[0]
  obsv = kf.H
  for i in range(1, n):
    obsv = np.vstack((obsv, kf.H @ np.linalg.matrix_power(kf.F, i)))
  rank = np.linalg.matrix_rank(obsv)
  c4d.cprint(f'The system is observable (rank = n = {n}).' if rank == n else 'The system is not observable (rank = {rank), n = {n}).', 'y')
  
  video_cap = cv2.VideoCapture(vidpath)
  t = 0


  while video_cap.isOpened():
    kf.store(t)
    t += dt
    # if t > 100: break 
  
    if t > 3.9 and t < 4.15:
      Qk = np.eye(6) * 8**2 * noisefactor
    else: 
      Qk = np.eye(6) * 4**2 * noisefactor

    kf.predict(Qk = Qk)

    if round(t / dt_frame, 1) % 1 >= 1e-10: continue   
    
    # camera cycle:

    ret, frame = video_cap.read()
    if not ret: break
    if rtdetect: 
      d = yolo3.detect(frame)
    else: 
      crc32 = zlib.crc32(frame.tobytes())
      d = detections[crc32]
    # for di in d: print(di.class_id)

    if d and (d[0].class_id == 'car'): # or d[0].class_id == 'truck'): 
      kf.update(d[0].X)
      # cv2.rectangle(frame, d[0].box[0], d[0].box[1], [255, 0, 0], 2) 
      kf.detect = d 
      kf.storeparams('detect', t)
  

  
  #   cv2.rectangle(frame, box(kf.X)[0], box(kf.X)[1], [0, 255, 0], 2) 
  #   cv2.imshow('', frame)
  #   cv2.waitKey(10)


  # cv2.destroyAllWindows()


  return kf, 'discrete' 


if __name__ == '__main__': 
 

  # data_cursor()

  kf, kf_label = steadystate() 
  drawkf(kf, kf_label)

  kf, kf_label = discrete() 
  drawkf(kf, kf_label)

  kf, kf_label = continuous() 
  drawkf(kf, kf_label)

