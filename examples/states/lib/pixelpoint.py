# type: ignore

import sys, os 
sys.path.append('.')
import c4dynamics as c4d
import numpy as np 
import cv2

from matplotlib import pyplot as plt 
plt.rcParams["font.family"] = "Times New Roman"   
plt.style.use('dark_background') 


savedir = os.path.join(os.getcwd(), 'docs', 'source', '_examples', 'pixelpoint') 

tripath = c4d.datasets.image('triangle')
planespath = c4d.datasets.image('planes')


def intro():

  from c4dynamics import pixelpoint 
  import numpy as np 
  d = [50, 50, 15, 25, 0.8, 0.1, 0.0, 0.05, 0.89]
  f_width, f_height = 100, 100
  class_names = ['dog', 'cat', 'horse', 'fox']

  pp = pixelpoint(x = d[0], y = d[1], w = d[2], h = d[3])
  pp.fsize = (f_width, f_height)
  pp.class_id = class_names[np.argmax(d[5:])]
  print(f'{d = }')
  print(f'{pp.fsize = }')
  print(f'{pp.class_id = }')

        
  

def tridetect(img):
  _, thresh = cv2.threshold(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 50, 255, 0)
  contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  bbox = []
  for contour in contours:
    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)    
    if len(approx) == 3:
      bbox.append(cv2.boundingRect(contour))
  return bbox


def ptup(n): 
  return '(' + str(n[0]) + ', ' + str(n[1]) + ')'


def from_image(): 

  c4d.cprint('Construction from image', 'y')

  img = cv2.imread(tripath)
  pp = c4d.pixelpoint(x = int(img.shape[1] / 2), y = int(img.shape[0] / 2), w = 100, h = 100)

  pp.fsize = img.shape[:2]
  print(pp.fsize) 


def from_detector(): 

  c4d.cprint('Construction from detector', 'y')

  d = [0, 1, 2, 3, .1, .2]
  f_width, f_height = 100, 20
  class_names = ['cat', 'dog']
  pp = c4d.pixelpoint(x = d[0], y = d[1], w = d[2], h = d[3])
  pp.fsize = (f_width, f_height)
  pp.class_id = class_names[np.argmax(d[4:])]


def detect_triangle(): 

  c4d.cprint('Triangles detection', 'y')

  img = cv2.imread(tripath)
  triangles = tridetect(img)

  print('{:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}'.format('center x', 'center y', 'box top-left', 'box bottom-right', 'class', 'frame size'))

  for tri in triangles: 
    pp = c4d.pixelpoint(x = int(tri[0] + tri[2] / 2), y = int(tri[1] + tri[3] / 2), w = tri[2], h = tri[3])
    
    pp.fsize = img.shape[:2]
    pp.class_id = 'triangle'
    print('{:^10d} | {:^10d} | {:^16} | {:^16} | {:^10} | {:^14}'.format(pp.x, pp.y, ptup(pp.box[0]), ptup(pp.box[1]), pp.class_id, ptup(pp.fsize)))

    cv2.rectangle(img, pp.box[0], pp.box[1], [0, 255, 0], 2)
  #  center x  |  center y  |   box top-left   | box bottom-right |   class    |   frame size  
  #    399     |    274     |    (184, 117)    |    (614, 431)    |  triangle  |   (600, 800)


  plt.figure()
  plt.axis(False)
  plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
  plt.savefig(c4d.j(savedir, 'triangle.png'), bbox_inches = 'tight', pad_inches = .05, dpi = 600)


def yolo(): 

  c4d.cprint('C4dynamics YOLOv3 detector', 'y')

  img = cv2.imread(planespath)
  yolo3 = c4d.detectors.yolov3()
  pts = yolo3.detect(img)
  print('{:^10} | {:^10} | {:^16} | {:^16} | {:^10} | {:^14}'.format('center x', 'center y', 'box top-left', 'box bottom-right', 'class', 'frame size'))

  for p in pts:
    print('{:^10d} | {:^10d} | {:^16} | {:^16} | {:^10} | {:^14}'.format(
      p.x, p.y, ptup(p.box[0]), ptup(p.box[1]), p.class_id, ptup(p.fsize)))
    
    cv2.rectangle(img, p.box[0], p.box[1], [0, 255, 0], 2)
    point = (int((p.box[0][0] + p.box[1][0]) / 2 - 75), p.box[1][1] + 22)
    cv2.putText(img, p.class_id, point, cv2.FONT_HERSHEY_SIMPLEX, 1, [0, 255, 0], 2)
  #  center x  |  center y  |   box top-left   | box bottom-right |   class    |   frame size
  #    615     |    295     |    (562, 259)    |    (668, 331)    | aeroplane  |  (1280, 720)
  #    779     |    233     |    (720, 199)    |    (838, 267)    | aeroplane  |  (1280, 720)
  #    635     |    189     |    (578, 153)    |    (692, 225)    | aeroplane  |  (1280, 720)
  #    793     |    575     |    (742, 540)    |    (844, 610)    | aeroplane  |  (1280, 720)

  plt.figure()
  plt.axis(False)
  plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
  plt.savefig(c4d.j(savedir, 'yolov3.png'), bbox_inches = 'tight', pad_inches = .05, dpi = 600)




if __name__ == '__main__': 
  intro()
  # from_image()
  # from_detector()
  # detect_triangle()
  # yolo() 

  plt.show(block = True)





