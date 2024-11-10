# type: ignore

import sys, os 
sys.path.append('.')
import c4dynamics as c4d
import cv2
from c4dynamics.utils.tictoc import * 
import numpy as np 

from matplotlib import pyplot as plt 
plt.rcParams["font.family"] = "Times New Roman"   
plt.style.use('dark_background')  

factorsize = 4
aspectratio = 1080 / 1920 

savedir = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'yolov3') 


impath = c4d.datasets.image('planes')
vidpath = c4d.datasets.video('aerobatics')



def ptup(n): return '(' + str(n[0]) + ', ' + str(n[1]) + ')'


def intro(): 

  c4d.cprint('intro', 'y')

  img = cv2.imread(impath)
  yolo3 = c4d.detectors.yolov3()
  tic()
  pts = yolo3.detect(img)
  toc()
  print('{:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}'.format('center x', 'center y', 'box top-left', 'box bottom-right', 'class', 'frame size'))
  
  for p in pts:

    print('{:^10d} | {:^10d} | {:^16} | {:^16} | {:^10} | {:^14}'.format(p.x, p.y, ptup(p.box[0]), ptup(p.box[1]), p.class_id, ptup(p.fsize)))
    cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2)

    point = (int((p.box[0][0] + p.box[1][0]) / 2 - 75), p.box[1][1] + 22)
    cv2.putText(img, p.class_id, point, cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 255, 0], 2)
  #  center x  |  center y  |   box top-left   | box bottom-right |   class    |   frame size
  #    615     |    295     |    (562, 259)    |    (668, 331)    | aeroplane  |  (1280, 720)
  #    779     |    233     |    (720, 199)    |    (838, 267)    | aeroplane  |  (1280, 720)
  #    635     |    189     |    (578, 153)    |    (692, 225)    | aeroplane  |  (1280, 720)
  #    793     |    575     |    (742, 540)    |    (844, 610)    | aeroplane  |  (1280, 720)


  # cv2.imwrite(os.path.join(savedir, 'intro.png'), img)
  # cv2.imshow('yolov3', img)
  # cv2.waitKey(0)
  plt.figure()
  plt.axis(False)
  plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
  plt.savefig(c4d.j(savedir, 'intro.png'), bbox_inches = 'tight', pad_inches = .05, dpi = 600)



def nms(): 

  c4d.cprint('nms threshold', 'y')

  yolo3 = c4d.detectors.yolov3()
  nms_thresholds = [0.1, 0.5, 0.9]

  _, axs = plt.subplots(1, 3, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.05, 'right': .95, 'hspace': 0.05, 'wspace': 0.05, 'top': .95, 'bottom': .05})

  for i, nms_threshold in enumerate(nms_thresholds):
    
    yolo3.nms_th = nms_threshold
    img = cv2.imread(impath)
    tic()
    pts = yolo3.detect(img)
    toc() 
    for p in pts:
      cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2)
      
    axs[i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axs[i].set_title(f"NMS Threshold: {nms_threshold}", fontsize = 6)
    axs[i].axis('off')

  plt.savefig(c4d.j(savedir, 'nms_th.png'), bbox_inches = 'tight', pad_inches = .05, dpi = 600)



def confidence_th():

  c4d.cprint('confidence threshold', 'y')

  yolo3 = c4d.detectors.yolov3()
  confidence_thresholds = [0.9, 0.95, 0.99]

  _, axs = plt.subplots(1, 3, dpi = 200, figsize = (factorsize, factorsize * aspectratio), gridspec_kw = {'left': 0.05, 'right': .95, 'hspace': 0.05, 'wspace': 0.05, 'top': .95, 'bottom': .05})

  for i, confidence_threshold in enumerate(confidence_thresholds):
    
    yolo3.confidence_th = confidence_threshold
    img = cv2.imread(impath) 
    tic()
    pts = yolo3.detect(img)
    toc()
    for p in pts:
      cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2)
    
    axs[i].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axs[i].set_title(f"Confidence Threshold: {confidence_threshold}", fontsize = 6)
    axs[i].axis('off')

  plt.savefig(c4d.j(savedir, 'confidence_th.png'), bbox_inches = 'tight', pad_inches = .05, dpi = 600)


def singleimage():

  c4d.cprint('detect(): single image', 'y')
  yolo3 = c4d.detectors.yolov3()

  img = cv2.imread(impath) 
  tic()
  pts = yolo3.detect(img)
  toc()
  for p in pts:
    cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2)

  plt.figure()
  plt.axis(False)
  plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
  plt.savefig(c4d.j(savedir, 'single_image.png'), bbox_inches = 'tight', pad_inches = .05, dpi = 600)


def outforamt(): 

  c4d.cprint('detect(): output structure', 'y')

  yolo3 = c4d.detectors.yolov3()

  img = cv2.imread(impath)
  tic()
  pts = yolo3.detect(img)
  toc()
  print('{:^10} | {:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}'
            .format('# object', 'center x', 'center y', 'box top-left', 'box bottom-right', 'class', 'frame size'))

  for i, p in enumerate(pts):
    print('{:^10d} | {:^10.3f} | {:^10.3f} | {:^16} | {:^16} | {:^10} | {:^14}'
          .format(i, p.x, p.y, ptup(p.box[0]), ptup(p.box[1]), p.class_id, ptup(p.fsize)))
    cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2)
    point = (int((p.box[0][0] + p.box[1][0]) / 2 - 75), p.box[1][1] + 22)
    cv2.putText(img, p.class_id, point, cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 255, 0], 2)

  plt.figure()
  plt.axis(False)
  plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
  plt.savefig(c4d.j(savedir, 'outformat.png'), bbox_inches = 'tight', pad_inches = .05, dpi = 600)


def invideo(): 

  c4d.cprint('detect(): a video', 'y')
  yolo3 = c4d.detectors.yolov3()

  video_cap = cv2.VideoCapture(vidpath)
  video_out = cv2.VideoWriter(c4d.j(savedir, 'on_video.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), int(video_cap.get(cv2.CAP_PROP_FPS)), [int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))])

  while video_cap.isOpened():
    ret, frame = video_cap.read()
    if not ret: break
    tic()
    pts = yolo3.detect(frame)
    toc()
    for p in pts:
      cv2.rectangle(frame, p.box[0], p.box[1], [0, 255, 0], 2) 
    video_out.write(frame)
    cv2.imshow('YOLOv3', frame)
    cv2.waitKey(10)

  video_out.release()



def custompath(weightspath = r'C:\c4dynamics\c4dynamics\resources\detectors\yolo\v3\yolov3.weights'): 
  c4d.cprint('custom weights path', 'y')
  yolo3 = c4d.detectors.yolov3(weights_path = weightspath)
  tic()
  pts = yolo3.detect(cv2.imread(impath))
  toc()
  for p in pts:
    print(p.class_id)


def coconames(coconamespath = r'C:\c4dynamics\c4dynamics\resources\detectors\yolo\v3\coco.names'): 
  c4d.cprint('verify coco names order', 'y')

  with open(coconamespath, 'r') as f:
    cname = f.read().strip()
  coconames = cname.split()

  for i in range(1, 81):
    print(f"'{coconames[i-1]}', ", end = '')
    if i % 5 == 0: 
      print(f'\n')


  for s1, s2 in zip(coconames, c4d.detectors.yolo3.class_names):
    if s1 != s2: 
      print(f'{s1} != {s2}')


if __name__ == '__main__': 

  intro()
  confidence_th()
  nms()
  outforamt()
  singleimage()
  invideo()

  
   
























