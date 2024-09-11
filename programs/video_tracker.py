from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist 
from scipy.linalg import expm 

from matplotlib import pyplot as plt 
plt.style.use('dark_background')  

import os, sys
sys.path.append('')
import c4dynamics as c4d
# import c4dynamics 

from c4dynamics.utils.plottracks import plottracks
 
# from enum import Enum
import numpy as np
import argparse
import pickle 
# import copy 
import cv2

from _mtracks import mTracks, Trkstate

'''
multi object tracking evaluation and benchmarks 
  https://github.com/JonathonLuiten/TrackEval
  https://www.youtube.com/watch?v=ymiVEcDzWj8
  https://www.cvlibs.net/datasets/kitti/raw_data.php
  https://motchallenge.net/data/MOT17/



'''


# HIGHLIGHTS:
# BUG:    Highlights the presence of a bug or an issue.
# FIXME:  Indicates that there is a problem or bug that needs to be fixed.
# HACK:   Suggests that a workaround or temporary solution has been implemented and should be revisited.
# NOTE:   Provides additional information or context about the code.
# XXX:    Used to highlight something that is problematic, needs attention, or should be addressed later.


class videofile():

  def __init__(self, vidpath, outfol, t0 = 0): 

    self.path = vidpath
    self.t0 = t0 
    self.open()
  

    self.N = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) # total frames count 
    self.fps = self.cap.get(cv2.CAP_PROP_FPS)
    self.dt = 1 / self.fps # 1 / frame per second = the length of a single frame
    
    self.tf = self.N * self.dt 

    self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    videoout = os.path.join(outfol, 'vidprocessed.mp4')
    self.writer = cv2.VideoWriter(videoout, cv2.VideoWriter_fourcc(*'mp4v')
                            , int(self.cap.get(cv2.CAP_PROP_FPS))
                                , [self.width, self.height])
    
  
  def open(self):
    self.cap = cv2.VideoCapture(self.path)
    # self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.t0 // self.dt)


def detections(video, tf, datafol, showon = False, delpkl = False):
  ''' 
    takes an opened video object, 
    if detctions already exist for the video, load them, 
    if not, runs detecting function.
  '''


  if 'pklpts' in locals():
    # delete stored pickled 
    del(pklpts)

  ptspath = os.path.join(datafol, 'detections.pkl')

  if os.path.exists(ptspath):
    ''' pickle from storage '''
    if not delpkl: # TODO change delpkl to ignoropkl  
    #   os.remove(ptspath)
    # else: 
      with open(ptspath, 'rb') as file:
        pklpts = pickle.load(file)
        c4d.cprint('points imported', 'm')


  f_frames = int(tf / video.dt)


  if 'pklpts' not in locals(): 
    ''' run detector and pickle to storage '''

    c4d.cprint('running detector', 'm')

    yolo3 = c4d.detectors.yolov3()
    yolo3.nms_th = .45
    pklpts = {}
    for idx in range(f_frames + 1):

      c4d.cprint(str(idx) + ' / ' + str(f_frames), 'c')

      ret, frame = video.cap.read()
      if not ret: break
      # pool.apply_async(process_frame, (idx, frame, output_queue))
      pklpts[idx] = yolo3.detect(frame)
      print(f'frame {idx}', end = ': ')
      for p in pklpts[idx]:
        cv2.rectangle(frame, p.box[0], p.box[1], [205, 109, 33], 2)
        print(p.class_id, end = '  ')
      print()
      if showon: 
        cv2.imshow(str(idx), frame)
        cv2.waitKey(10)

    video.open()
        

    with open(os.path.join(datafol, 'detections.pkl'), 'wb') as file:
      pickle.dump(pklpts, file)


  print(f'{f_frames} frames, {len([p for pts in pklpts.values() for p in pts])} detected objects')
  return pklpts


def systemmodel(vidname, sampletime):
  '''
  https://chatgpt.com/share/cf10f21a-de39-46dc-9c76-58e583a95d10
  Sure, here are some sources that provide information and insights 
    into the different dynamic models used with Kalman filters for object tracking in 2D scenes:

  1. **Constant Velocity Model (CV)**:
    - "An Introduction to the Kalman Filter" by Greg Welch and Gary Bishop: 
        This classic paper provides a foundational understanding of the Kalman filter, 
        including the CV model.
    - "Understanding Kalman Filters with Python" by Shane Lynn: This online tutorial 
        covers the implementation of Kalman filters, including the CV model, using Python.

  2. **Constant Acceleration Model (CA)**:
    - "Optimal State Estimation: Kalman, H Infinity, and Nonlinear Approaches" by 
        Dan Simon: This book discusses various dynamic models for Kalman filters, 
        including the CA model.
    - "Kalman Filter with Constant Acceleration Model" by Atsushi Sakai: This GitHub 
        repository includes code examples and explanations for implementing the CA 
        model with a Kalman filter.

  3. **Constant Turn Model (CT)**:
    - "Introduction to Autonomous Robots" by Nikolaus Correll and others: This 
        textbook covers robotic perception and localization, including the CT model 
        and its application in robot navigation.
    - "Object Tracking using Kalman Filters: A Review" by Vivekanand Mishra and others: 
        This research paper discusses different dynamic models, including the CT model, 
        for object tracking.

  4. **Constant Jerk Model (CJ)**:
    - "Kalman Filter with Constant Jerk Model" by Atsushi Sakai: Similar to the CA model 
        example, this GitHub repository provides code and explanations for implementing 
        the CJ model with a Kalman filter.
    - "A New Approach to Linear Filtering and Prediction Problems" by Rudolf E. 
        Kalman: Kalman's original paper is a foundational resource for understanding 
        Kalman filters and their extensions, including models like CJ.

  5. **Constant Heading Model (CH)**:
    - "Mobile Robot Localization and Map Building: A Multisensor Fusion Approach" 
        by Diofantos G. Hadjimitsis: This book discusses Kalman filters and their 
        applications in mobile robot localization, including the CH model.
    - "Introduction to Autonomous Mobile Robots" by Roland Siegwart and Illah 
        Nourbakhsh: This book covers various aspects of mobile robotics, including 
        motion models like CH for Kalman filtering.

  These sources provide a mix of theoretical explanations, practical implementations, 
    and application-specific insights into using Kalman filters with different dynamic 
    models for object tracking in 2D scenes.

  '''
  

  if vidname == '3 planes':
    modeltype = 'LINEAR_VELOCITY_BAD_MEASURES'
  elif vidname == 'cars2_short':
    modeltype = 'LINEAR_ACCELERATION' 
    modeltype = 'LINEAR_ACCELERATION_SIZE'
    modeltype = 'LINEAR_VELOCITY_SIZE' 
    modeltype = 'LINEAR_VELOCITY' 
    modeltype = 'LINEAR_ACCELERATION_SIZE2'
  else:
    modeltype = 'LINEAR_VELOCITY'

  c4d.cprint('kalman model: ' + modeltype, 'g')



  sys = {}

  if modeltype == 'LINEAR_VELOCITY': 


    '''
    X = [x, y, w, h, vx, vy]
    #    0  1  2  3  4   5  

    x'  = vx
    y'  = vy
    w'  = 0
    h'  = 0
    vx' = 0
    vy' = 0

    H = [1 0 0 0 0 0
        0 1 0 0 0 0
        0 0 1 0 0 0
        0 0 0 1 0 0]
    '''


    ''' system matrices '''
    sys['A'] = np.zeros((6, 6))
    sys['A'][0, 4] = sys['A'][1, 5] = 1
    sys['F'] = expm(sys['A'] * sampletime)
    sys['H'] = np.zeros((4, 6))
    sys['H'][0, 0] = sys['H'][1, 1] = sys['H'][2, 2] = sys['H'][3, 3] = 1
    sys['dt'] = sampletime

    ''' covariance matrices '''
    measure_err = .01 
    velocity_err = .707
    sys['P'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2, velocity_err**2, velocity_err**2])
    sys['Qk'] = np.diag([0.5, 0.5, 0.5, 0.5, 1, 1]) * measure_err**2
    sys['Rk'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2])



  if modeltype == 'LINEAR_VELOCITY_SIZE': 


    '''
    X = [x, y, w, h, vx, vy, vw, vh]
    #    0  1  2  3  4   5   6   7 

    x'  = vx  (0, 4)
    y'  = vy  (1, 5)
    w'  = vx  (2, 6)
    h'  = vy  (3, 7)
    vx' = 0
    vy' = 0
    vw' = 0
    vh' = 0

    H = [1 0 0 0 0 0
        0 1 0 0 0 0
        0 0 1 0 0 0
        0 0 0 1 0 0]
    '''


    ''' system matrices '''
    sys['A'] = np.zeros((8, 8))
    sys['A'][0, 4] = sys['A'][1, 5] = sys['A'][2, 6] = sys['A'][3, 7] = 1
    sys['F'] = expm(sys['A'] * sampletime)
    sys['H'] = np.zeros((4, 8))
    sys['H'][0, 0] = sys['H'][1, 1] = sys['H'][2, 2] = sys['H'][3, 3] = 1
    sys['dt'] = sampletime

    ''' covariance matrices '''
    measure_err = .01 
    velocity_err = .707
    sys['P'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2, velocity_err**2, velocity_err**2, velocity_err**2, velocity_err**2])
    sys['Qk'] = np.diag([0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1]) * measure_err**2
    sys['Rk'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2])




  elif modeltype == 'LINEAR_VELOCITY_BAD_MEASURES': 

    ''' system matrices '''
    sys['A'] = np.zeros((6, 6))
    sys['A'][0, 4] = sys['A'][1, 5] = 1
    sys['F'] = expm(sys['A'] * sampletime)
    sys['H'] = np.zeros((4, 6))
    sys['H'][0, 0] = sys['H'][1, 1] = sys['H'][2, 2] = sys['H'][3, 3] = 1
    sys['dt'] = sampletime

    ''' covariance matrices '''
    measure_err = .01 
    velocity_err = .707
    sys['P'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2, velocity_err**2, velocity_err**2])
    sys['Qk'] = np.diag([0, 0, 0, 0, measure_err**2, measure_err**2])
    sys['Rk'] = 4 * np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2])




  elif modeltype == 'LINEAR_ACCELERATION':

    '''
    X = [x, y, w, h, vx, vy, ax, ay]
    #    0  1  2  3  4   5   6   7

    x'  = vx  (0, 4)
    y'  = vy  (1, 5) 
    w'  = 0
    h'  = 0
    vx' = ax  (4, 6)
    vy' = ay  (5, 7)
    ax' = 0
    ay' = 0

    H = [1 0 0 0 0 0 0 0
        0 1 0 0 0 0 0 0
        0 0 1 0 0 0 0 0 
        0 0 0 1 0 0 0 0]

    '''


    ''' system matrices '''
    sys['A'] = np.zeros((8, 8))
    sys['A'][0, 4] = sys['A'][1, 5] = sys['A'][4, 6] = sys['A'][5, 7] = 1
    sys['F'] = expm(sys['A'] * sampletime)
    sys['H'] = np.zeros((4, 8))
    sys['H'][0, 0] = sys['H'][1, 1] = sys['H'][2, 2] = sys['H'][3, 3] = 1
    sys['dt'] = sampletime

    ''' covariance matrices '''
    measure_err = .01 
    velocity_err = .707
    acceleration_err = .707

    sys['P'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2, velocity_err**2, velocity_err**2, acceleration_err**2, acceleration_err**2])
    sys['Qk'] = np.diag([0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1]) * measure_err**2
    sys['Rk'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2])


  elif modeltype == 'LINEAR_ACCELERATION_SIZE':

    '''
    X = [x, y, w, h, vx, vy, ax, ay]
    #    0  1  2  3  4   5   6   7

    x'  = vx  (0, 4)
    y'  = vy  (1, 5) 
    w'  = vx  (2, 4)
    h'  = vy  (3, 5)
    vx' = ax  (4, 6)
    vy' = ay  (5, 7)
    ax' = 0
    ay' = 0
    

    H = [1 0 0 0 0 0 0 0
        0 1 0 0 0 0 0 0
        0 0 1 0 0 0 0 0 
        0 0 0 1 0 0 0 0]
    for k, v in sys.items(): print(k), print(v)
    '''


    ''' system matrices '''
    sys['A'] = np.zeros((8, 8))
    sys['A'][0, 4] = sys['A'][1, 5] = sys['A'][4, 6] = sys['A'][5, 7] = sys['A'][2, 4] = sys['A'][3, 5] = 1
    sys['F'] = expm(sys['A'] * sampletime)
    sys['H'] = np.zeros((4, 8))
    sys['H'][0, 0] = sys['H'][1, 1] = sys['H'][2, 2] = sys['H'][3, 3] = 1
    sys['dt'] = sampletime

    ''' covariance matrices '''
    measure_err = .01 
    velocity_err = .4
    acceleration_err = .707

    sys['P'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2, velocity_err**2, velocity_err**2, acceleration_err**2, acceleration_err**2])
    sys['Qk'] = np.diag([0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1]) * measure_err**2
    sys['Rk'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2])


  elif modeltype == 'LINEAR_ACCELERATION_SIZE2':

    '''
    X = [x, y, w, h, vx, vy, ax, ay, vw, vh]
    #    0  1  2  3  4   5   6   7   8   9

    x'  = vx  (0, 4)
    y'  = vy  (1, 5) 
    w'  = vw  (2, 8)
    h'  = vh  (3, 9)
    vx' = ax  (4, 6)
    vy' = ay  (5, 7)
    ax' = 0   
    ay' = 0
    vw' = 0
    vh' = 0
    

    H = [1 0 0 0 0 0 0 0 0 0
        0 1 0 0 0 0 0 0 0 0 
        0 0 1 0 0 0 0 0 0 0 
        0 0 0 1 0 0 0 0 0 0]
    for k, v in sys.items(): print(k), print(v)
    '''


    ''' system matrices '''
    sys['A'] = np.zeros((10, 10))
    sys['A'][0, 4] = sys['A'][1, 5] = sys['A'][4, 6] = sys['A'][5, 7] = sys['A'][2, 8] = sys['A'][3, 9] = 1
    sys['F'] = expm(sys['A'] * sampletime)
    sys['H'] = np.zeros((4, 10))
    sys['H'][0, 0] = sys['H'][1, 1] = sys['H'][2, 2] = sys['H'][3, 3] = 1
    sys['dt'] = sampletime

    ''' covariance matrices '''
    measure_err = .01 
    velocity_err = .707
    acceleration_err = .707

    sys['P'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2, velocity_err**2, velocity_err**2, acceleration_err**2, acceleration_err**2, velocity_err**2, velocity_err**2])
    sys['Qk'] = np.diag([0.5, 0.5, .5, .5, 1, 1, 1, 1, 1, 1]) * measure_err**2
    sys['Rk'] = np.diag([measure_err**2, measure_err**2, measure_err**2, measure_err**2])

  return sys 


# class plotbackend(Enum):
#   SHOW  = 1
#   SAVE  = 2  
#   SHOWSAVE = 3

def cv2_rectangle_dash(frame, box, ldash, lcolor, lwidth):
  # ldash 0: no line.     # continuous.
  # ldash 1: continuous.  # dash
  # ldash 2: dash         # double dash 
  x1 = box[0][0]
  y1 = box[0][1]
  x2 = box[1][0]
  y2 = box[1][1]

  dash_length = 10

  if ldash == 1: dash_spacing = 0 
  elif ldash == 2: dash_spacing = 10 # 5
  else: dash_spacing = -20
  # dash_spacing = 5 * (ldash - 1) # <-10: no line, 0: continuous, 5: dash
  
  # Draw the dashed rectangle
  for i in range(x1, x2, dash_length + dash_spacing):
      cv2.line(frame, (i, y1), (min(i + dash_length, x2), y1), lcolor, thickness = lwidth)
      cv2.line(frame, (i, y2), (min(i + dash_length, x2), y2), lcolor, thickness = lwidth)

  for j in range(y1, y2, dash_length + dash_spacing):
      cv2.line(frame, (x1, j), (x1, min(j + dash_length, y2)), lcolor, thickness = lwidth)
      cv2.line(frame, (x2, j), (x2, min(j + dash_length, y2)), lcolor, thickness = lwidth)

  # cv2.imshow('image', frame)
  # cv2.waitKey(10)



def runtracker(vidpath, tf = None
                  , showon = True, save_frames = False, delpkl = False
                      # , save_png = plotbackend.SHOWSAVE
                          , classlist = None, blanktrk = None, subfol = ''):
  ''' 
    takes a video path, 
    runs kalman filter, 
    returns path to processed video and a dictonary of tracks
  '''

  vidname = os.path.basename(vidpath)[:-4]
  outfol = os.path.join('examples', '_out', vidname) # video, detections. 
  subfol = os.path.join('examples', '_out', vidname, subfol) # mtracks, stills, processed vid. 

  if not os.path.exists(subfol): os.makedirs(subfol) 
  
  video = videofile(vidpath, subfol)
  if tf is None: tf = video.tf

  #
  # timings
  ##

  t = 0
  frmidx = 0
  predict_rate = 1 # 2 # twice frames rate 
  dt = video.dt / predict_rate

  #
  # detections, kalman
  ##
  pklpts  = detections(video, tf, outfol, delpkl = delpkl)
  kfmodel = systemmodel(vidname, dt)
  mtracks = mTracks(kfmodel, subfol, video.dt)  
  

  debugassignment = False 






  while True:

    tlist = {} # []
    tclosed = []

    # predict existing tracks. 
    for key, trk in mtracks.trackers.items():

      trk.store(t)
      if hasattr(trk, 'vw') and hasattr(trk, 'ax'):
        trk.px, trk.py, trk.pw, trk.ph, trk.pvx, trk.pvy, trk.pax, trk.pay, trk.pvw, trk.pvh = trk.P.diagonal() #   
        trk.storeparams(['state', 'px', 'py', 'pw', 'ph', 'pvx', 'pvy', 'pax', 'pay', 'pvw', 'pvh'], t) #  
      elif hasattr(trk, 'vw'):
        trk.px, trk.py, trk.pw, trk.ph, trk.pvx, trk.pvy, trk.pvw, trk.pvh = trk.P.diagonal() #   
        trk.storeparams(['state', 'px', 'py', 'pw', 'ph', 'pvx', 'pvy', 'pvw', 'pvh'], t) #  
      elif hasattr(trk, 'ax'):
        trk.px, trk.py, trk.pw, trk.ph, trk.pvx, trk.pvy, trk.pax, trk.pay = trk.P.diagonal() #   
        trk.storeparams(['state', 'px', 'py', 'pw', 'ph', 'pvx', 'pvy', 'pax', 'pay'], t) #  
      else:
        trk.px, trk.py, trk.pw, trk.ph, trk.pvx, trk.pvy = trk.P.diagonal()   
        trk.storeparams(['state', 'px', 'py', 'pw', 'ph', 'pvx', 'pvy'], t) 


      # def isold(trk):
      # a track is languished in one of cases:
      # 1 if is just opened and didnt have sequential update (1 time of measure time)
      # 2 or if it's in predict state, its predictions say it's inside the frame,
      #    but 10 times of measure time elapsed without an update.
      # 3 or when it's outside the frame and 5 times of measure time elapsed without an update.

      trk.cnt_predict += 1
      if trk.state == Trkstate.OPENED: 
        # i want to add these only once 
        # tlist.append([trk.x, trk.y])
        nescape = 1 
        # continue
      elif trk.x < 0 or trk.x > 1 or trk.y < 0 or trk.y > 1:
        nescape = 5 
      else:
        nescape = 100000 # 20 # 

      if trk.cnt_predict > predict_rate * nescape:       
        trk.state = Trkstate.CLOSED
        tclosed.append(key) 
        continue

      #
      # predict 
      ## 
      # the condition here is necessary for a few reasons:
      # 1 opened trackes already had predict in the opening (NOTE but in the second time not. so if it hadnt update it may go astray. but there isnt second time.)
      # 2 opened trackes must be appended to the following list because otherwise they werent associated or that 
      #   the associated objects had wrong indices. 

      # opened0: dont predict, dont update

      # skip tracks for debugging puposes. 
      skiptrk = True if blanktrk and key == blanktrk['trk'] and t > blanktrk['t1'] and t < blanktrk['t2'] and not blanktrk['predict'] else False   
      
      if trk.state != Trkstate.OPENED and not skiptrk:
        # dont update opened trackes up until a new update. 
        trk.predict()
        trk.state = Trkstate.PREDICTED
      else: 
        c4d.cprint(f'trk {key} is skipped')




      tlist[key] = [trk.x, trk.y] # tlist.append([trk.x, trk.y])

    # remove closed trks
    for key in tclosed: # an exclimation mark must be put here because popping 
      # items from unsorted list may remove undesired indices after the list changes with
      # the first pop. 
      # no. trackers is a dict and not a list. 
      mtracks.trackers_hist[key] = mtracks.trackers.pop(key)

    if round(video.fps * t, 1) % 1 < 1e-10:   # a camera cycle 
      # camera cycle: 
      ret, frame = video.cap.read()
      if not ret: break
      pts = pklpts[frmidx] # dict((k, v) for k, v in enumerate(pklpts[frmidx]))
      frmidx += 1


      plist = []
      ipts = len(pts)
      for p in reversed(pts): 
        # iterate over the list in a reverse order to pop out undesired (classified) items 
        # without harming the list indices. 
        ipts -= 1
        if classlist is not None and not any(c == p.class_id for c in classlist):
          pts.pop(ipts) # pts[:] really doesnt change but pts does and when i pop item 6th, the list is shorten to 8. now no longer 9th item. 
          continue 

        #
        # remove plots according to user input in blanktrk.
        # blanktrk structure:
        # type: dict
        # key 'trk': trk number to remove the associated plots.
        # key 't1': time to start removing plots
        # key 't2': time to stop removing plots
        ##  
        if blanktrk is not None:
          skipplot = False 
          for itrk, vtrk in mtracks.trackers.items():
            if itrk != blanktrk['trk']: continue 
            # print(f'{t = :.3f}')
            if vtrk.P(p) < mtracks.dist_th:
              if t > blanktrk['t1'] and t < blanktrk['t2']:
                pts.pop(ipts) # pts[:] really doesnt change but pts does and when i pop item 6th, the list is shorten to 8. now no longer 9th item. 
                skipplot = True  
                # print(f'dropped')
          if skipplot: continue

        plist.append([p.x, p.y])
      
      # return plist to original order:
      plist.reverse()


      # prepare existing tracks to association 

      # find matching 
      trkassignment = {} # trk_key: obvservation 
      if tlist and plist:
        # the d matrix is assignment of tracks (rows) and observations (columns)
        d = cdist(np.array(list(tlist.values())), plist)
        # may 14th after the linear_sum_assignment was confused to a track that obviusley 
        # didnt have a corresponding plot i'm giving a try to drop far tracks in advance.
        # namely drop tracks that their distance from any other plot is bigger than 2*dist_th. 
        d_th = np.all(d > 2 * mtracks.dist_th, axis = 1)
        d = d[~d_th, :]
        rm_keys = c4d.idx2keys(tlist, np.where(d_th)[0])
        for k in rm_keys:
          tlist.pop(k)

        # linear_sum_assignment() returns optimal indices in terms of assigning trk to point
        r_idx, cidx = linear_sum_assignment(d) 
        for r, c in zip(r_idx, cidx): 
          if d[r, c] < mtracks.dist_th:
            # trkkeys[idx] = plist_idx:
            trkassignment[list(tlist.keys())[r]] = c # convert the trk index to a key and assign it with the detection (plist) index.  

          
          



      idx_unassc = np.arange(len(plist))[np.setdiff1d(np.arange(len(plist)), list(trkassignment.values()))]
      

      ''' test assignment '''

      if debugassignment and frmidx >= 45: 
        _, axdebug = plt.subplots(1, 1)
        # detection o
        # trk x
        # color pairs
        # legend numbers. 
        # first failing attempt to do all vectorized (the failure is in generating vecotrized labels)
        # ncolors = np.random.rand(len(trkassignment), 3)
        # plots   = np.array(plist)[list(trkassignment.values()), :]
        # tracks  = np.array([mtracks.trackers[trki].X[:2] for trki in trkassignment.keys()])
        # keynames = [str(trki) for trki in trkassignment.keys()]
        # axdebug.plot(np.atleast_2d(plots[:, 0]), np.atleast_2d(-plots[:, 1]), marker = 'o', markerfacecolor = 'none', linewidth = 0, color = ncolors)              
        # axdebug.plot(plots[:, 0], -plots[:, 1], linewidth = 0, marker = 'o', color = ncolors), facecolors = 'none')
        # axdebug.plot(tracks[:, 0], -tracks[:, 1], linewidth = 0, color = ncolors, marker = 'x', label = keynames)
        # c4d.plotdefaults(axdebug, 'assignments', 'x', 'y')
        
        for idx, (itrk, iplot) in enumerate(trkassignment.items()): 
          plots = np.array(plist)[iplot, :]
          tracks = mtracks.trackers[itrk].X[:2]
          axdebug.scatter(*plots, marker = 'o', color =  np.array(mtracks.trackers[itrk].color)[np.r_[-1:2:2, 0]] / 255, facecolors = 'none') # rotates the colors to match the order of opencv channels. 
          axdebug.scatter(*tracks, marker = 'x', color = np.array(mtracks.trackers[itrk].color)[np.r_[-1:2:2, 0]] / 255, label = str(itrk))

        for idx in idx_unassc:
          plots = pts[idx].X[:2]
          axdebug.scatter(*plots, marker = 'o', color = np.ones(3), facecolors = 'none')
          
        for itrk, vtrk in mtracks.trackers.items():
          if any(itrk == it for it in trkassignment.keys()): continue
          axdebug.scatter(*vtrk.X[:2], marker = 'x', color = np.array(vtrk.color)[np.r_[-1:2:2, 0]] / 255, label = str(itrk))
          
        axdebug.invert_yaxis()
        axdebug.legend(title = 'trk', facecolor = None)
        c4d.plotdefaults(axdebug, 'Assignments | t = ' + str(round(t, ndigits = 3)) + ' | f ' + str(frmidx), 'x', 'y')
      
      ''' test assignment - end '''
        
      
      
      for i in idx_unassc: 
        # ADD TRACK, INITIAL KALMAN, 
        mtracks.add(pts[i])

      for key, c in trkassignment.items():
        trk = mtracks.trackers[key]
        trk.cnt_predict = 0
        
        trk.update(pts[c].X)
        trk.state = Trkstate.CORRECTED

        # store the raw plots
        # TODO make the constructor an option to take dp.X from other datapoint or simply take a datapoint and copy its state values.
        trk.M = c4d.state(x = pts[c].x, y = pts[c].y, w = pts[c].w, h = pts[c].h) 
        trk.storeparams(['M.x', 'M.y', 'M.w', 'M.h'])



      # draw existing tracks. 
      # topleft(x, y), (w, h)

      # display frame number 
      # display time 
      cv2.putText(frame, str(frmidx), (5, 20), cv2.FONT_HERSHEY_PLAIN, 1, [0, 0, 0], 2)

      ss = t % 60 
      tt = t / 60
      mm = tt % 60 // 1 
      tt = tt / 60
      hh = tt // 1 
      timestr = f'{int(hh):02d}:{int(mm):02d}:{ss:05.2f}'
      cv2.putText(frame, timestr, (55, 20), cv2.FONT_HERSHEY_PLAIN, 1, [0, 0, 0], 2)

      for key, trk in mtracks.trackers.items():
        if trk.state == Trkstate.OPENED: continue # 0 or trk.state == Trkstate.OPENED1: continue  
        # if trk.state == Trkstate.OPENED: 
        #   lwidth = 1
        #   ldash  = 0 

        # ldash: 
        #   0 no line
        #   1 continuous
        #   2 dash 
        ldash = 1 
        if trk.state == Trkstate.PREDICTED: 
          # if in last cycle there wasnt detection, mark in dash. 
          ldash = 0 if blanktrk and not blanktrk['predict'] else 2   
          ldash = 1
          ldash = 2 # 0 #        ''' 0 no line, 1 continuous, 2 dash''' 
          if key == 0 or key == 2: continue 

        # cv2.rectangle(frame, trk.box[0], trk.box[1], trk.color, 2)
        lwidth = 3
        if key == 10 or key == 27: 
          lwidth = 6
        # display bounding box 
        cv2_rectangle_dash(frame, trk.box, ldash, trk.color, lwidth)
        
        if ldash: 
          X = trk.Xpixels
          # display trk number 
          cv2.putText(frame, str(key), (X[0], X[1] - 10), cv2.FONT_HERSHEY_PLAIN, 1, trk.color, 2)
          fdiagonal = np.sqrt(trk._frameheight**2 + trk._framewidth**2)
          # display velocity arrow 
          cv2.arrowedLine(frame, (X[0], X[1]), (X[0] + int(np.min([fdiagonal, X[4]]) * .1)
                                              , X[1] + int(np.min([fdiagonal, X[5]]) * .1)), trk.color, 4)




      if showon:
        cv2.imshow('image', frame)
        cv2.waitKey(10)
          
      video.writer.write(frame)

      if save_frames == True:
        cv2.imwrite(os.path.join(subfol, str(frmidx) + '_t' + str(round(t, ndigits = 3)).replace('.', '_') + '.png'), frame)

    t += dt
    if t >= tf: break # time over 

  video.writer.release()
  cv2.destroyAllWindows()

  c4d.cprint(f'{len({**mtracks.trackers_hist, **mtracks.trackers})} trackes opened, {len({**mtracks.trackers_hist})} trackes closed', 'b')

  mtracks.store()
  # mtracks.plotresults(pklpts, video.dt, dt, save_png, filter_trkid = filter_trkid)
  plottracks(subfol, block = False)
  
  return mtracks






if __name__ == '__main__': 
  

  parser = argparse.ArgumentParser()

  # vidpath, tf = None, showon = True, save_frames = False, delpkl = False
  #           , classlist = None, blanktrk = None, subfol = ''
  parser.add_argument('--vidname', help = 'the video name in the resources folder to run') # None) , default = 'cars1'
  parser.add_argument('--subfol', default = '', help = 'subfolder name in the output folder to store the function products.')
  parser.add_argument('--tf', type = float) # , default = 100
  # store_true means if provided without following param then set it to true. 
  parser.add_argument('--debug', action = 'store_true', default = False, help = 'whether to run in debug mode')
  parser.add_argument('--delpkl', default = False, type = bool)
  parser.add_argument('--save_frames', default = False, type = bool) # , default = True
  parser.add_argument('--classlist', nargs = '+', type = str, help = 'objects class to filter')
  parser.add_argument('--blanktrk', nargs = '+', type = float, help = 'trk and times for which to filter plots')

  args = parser.parse_args()
  args_dict = vars(args)

  print(args)
  print(args_dict)

  if args.debug: 
    
    # import psutil
    # processes = psutil.process_iter(['pid', 'name'])
    # for process in processes:
    #   print(f"PID: {process.info['pid']} - Name: {process.info['name']}")
    # import pdb
    # pdb.Pdb().set_trace()
    # import pydevd
    # pydevd.settrace('localhost', port = 5678, stdoutToServer = True
    #                         , stderrToServer = True, suspend = False
    #                             , trace_only_current_thread = True)
    

    input(f'Run python debugger using process id.\n' \
          'Select the pyenv process.\n' \
            'Wait for red messages in the console\n' \
              'Press to continue')
    
  args_dict.pop('debug')

  
  videoname = args.vidname
  args_dict.pop('vidname')

  # print(args_dict)

  if args.blanktrk:
    btrk = int(args_dict['blanktrk'][0])
    bt1 = args_dict['blanktrk'][1]
    bt2 = args_dict['blanktrk'][2]
    if len(args_dict['blanktrk']) > 3:
      bpredict = True if args_dict['blanktrk'][3] else False 
    else: 
      bpredict = False 

    args_dict['blanktrk'] = {'trk': btrk, 't1': bt1, 't2': bt2, 'predict': bpredict}


# args_dict['delpkl'] = True


  # if debug: 
  #   input(f'run python debugger using process id. \nselect the pyenv process. \npress to continue and wait')



''' main '''
resourcedir = os.path.join('examples', 'resources')
vidtracks = {}
print()
for f in os.listdir(resourcedir):
  if f.lower().endswith('.mp4'):
    if videoname is not None and videoname != f.lower()[:-4]: continue
    # if f.lower()[:-4] != 'cars1': continue  # '3 planes': continue # 'aerobatics': continue  # 
    
    c4d.cprint(f'{f[:-4]} is running', 'y')

    vidtracks[f[:-4]] = runtracker(os.path.join(resourcedir, f)
                              # , tf = tf
                                  # , save_frames = True
                                    # , save_png = plotbackend.SHOWSAVE
                                      # , classlist = ['car'] # None # , 'person', 'truck', 'bus'
                                        , **args_dict
                              )





# (.venv12) PS D:\Dropbox\c4dynamics> python .\examples\video_tracker.py --save_frames 1 --tf 5 --classlist 
# car truck --blanktrk 10 1.4 1.7 --subfol noline --vidname cars2_short

