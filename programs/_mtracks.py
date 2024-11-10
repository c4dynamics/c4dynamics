# type: ignore 
import os, sys
sys.path.append('')
import c4dynamics as c4d 

from enum import Enum
import numpy as np
import pickle 
import copy 

from matplotlib import pyplot as plt 
import types

class Trkstate(Enum):
  OPENED     = 0
  # OPENED1     = 1
  PREDICTED   = 1 # 2
  CORRECTED   = 2 # 3
  CLOSED      = 3 # 4

class ppkalman(c4d.pixelpoint, c4d.filters.kalman):

  def __init__(self, pp, X, kf):
    # self.units  = pp.units 
    self.fsize  = pp.fsize
    self.class_id = pp.class_id 
    c4d.filters.kalman.__init__(self, X, P0 = kf['P']
                                  , F = kf['F'], H = kf['H']
                                    , Q = kf['Qk'], R = kf['Rk'])
  
  @property  
  def Xpixels(self):
    return np.array([self.x * self._framewidth        # x
                      , self.y * self._frameheight      # y
                        , self.w * self._framewidth       # w
                      , self.h * self._frameheight       # h   
                        , self.vx * self._framewidth       # vx
                          , self.vy * self._frameheight]      # vy   
                            , dtype = np.int32)




class mTracks:

  '''
  trackers manager:
  list of active trackers
  add or remove tracks methods    #
  this class shouldnt belong to this project notebook but to the body module of c4d.
  theres also should be a saperation between the objects detecton processing and the objects bank handling. 
  however this class cannot currently be introduced as is to c4dyanmics as it doesnt handle body objects but handles tracks
  which is another class of this nb. 
  # 
  '''
  def __init__(self, kfmodel, fol, dt_video):
          
    self.keycnt = -1
    self.trackers = {}
    self.trackers_hist = {}
    self.dist_th = 50 / 1280 # 100 / 1280
    self.kf = kfmodel
    self.outfol = fol
    self.dt_video = dt_video


  def add(self, pp):

    key = self.keygenerator()

    # self.trackers[key] = copy.deepcopy(pp)


    if len(self.kf['F']) == 6:
      X = {'x': pp.x, 'y': pp.y, 'w': pp.w, 'h': pp.h, 'vx': 0, 'vy': 0}
    else: 
      X = {'x': pp.x, 'y': pp.y, 'w': pp.w, 'h': pp.h, 'vx': 0, 'vy': 0, 'ax': 0 , 'ay': 0}


    self.trackers[key] = ppkalman(pp, X, self.kf)

    # def _Xpixels(self):
    #   # superx = super().X
    #   return np.array([self.x * self._framewidth        # x
    #                     , self.y * self._frameheight      # y
    #                       , self.w * self._framewidth       # w
    #                     , self.h * self._frameheight       # h   
    #                       , self.vx * self._framewidth       # vx
    #                         , self.vy * self._frameheight]      # vy   
    #                           , dtype = np.int32)
  
    # self.Xpixels = types.MethodType(_Xpixels, self)

    
    print(self.trackers[key])
    
    self.trackers[key].predict()

    self.trackers[key].state = Trkstate.OPENED
    self.trackers[key].color = np.random.randint(50, 255, size = 3).tolist()
    # if key == 10: 
    #   self.trackers[key].color = [0, 255, 0]
    # if key == 23: 
    #   self.trackers[key].color = [0, 0, 255]

    self.trackers[key].cnt_predict = 0
    self.trackers[key].P_data = []
        

  def keygenerator(self):
    self.keycnt += 1
    return self.keycnt 
  

  def store(self):
    
    with open(os.path.join(self.outfol, 'mtracks.pkl'), 'wb') as file:
      pickle.dump(self, file)



      


