# type: ignore

# from matplotlib import pyplot as plt 
import sys, os
sys.path.append('.')
import c4dynamics as c4d 
import cv2 
import numpy as np
import pooch 
# import shutil 
from c4dynamics.datasets._manager import imagesmap, videosmap, nnsmap, d3smap 
from c4dynamics.datasets._registry import CACHE_DIR
import matplotlib.image as mpimg
from matplotlib import pyplot as plt 



# CACHE_DIR     = os.path.join(pooch.os_cache(''), 'c4data')
aeropath      = c4d.j(CACHE_DIR, videosmap['aerobatics'])
trianglepath  = c4d.j(CACHE_DIR, imagesmap['triangle'])
planespath    = c4d.j(CACHE_DIR, imagesmap['planes'])
bunnymeshpath = c4d.j(CACHE_DIR, d3smap['bunny_mesh'])
yolov3path    = c4d.j(CACHE_DIR, nnsmap['yolov3'])
bunnypath     = c4d.j(CACHE_DIR, d3smap['bunny'])
f16path       = c4d.j(CACHE_DIR, d3smap['f16'])



def downloadall():

  c4d.cprint('9. download all ', 'y')

  print(os.path.exists(planespath))
  print(os.path.exists(trianglepath))
  print(os.path.exists(aeropath))
  print(os.path.exists(yolov3path))
  print(os.path.exists(bunnypath))
  print(os.path.exists(bunnymeshpath))
  print(os.path.exists(f16path))

  # download and check if exists 
  c4d.datasets.download_all()
  print(os.path.exists(planespath))
  print(os.path.exists(trianglepath))
  print(os.path.exists(aeropath))
  print(os.path.exists(yolov3path))
  print(os.path.exists(bunnypath))
  print(os.path.exists(bunnymeshpath))
  print(os.path.exists(f16path))


def clearcache(): 

  c4d.cprint('8. clear cache', 'y')

  c4d.cprint('clear all', 'g')
  c4d.cprint(c4d.datasets.image('planes'), 'y')
  c4d.cprint(c4d.datasets.image('triangle'), 'y')
  c4d.cprint(c4d.datasets.video('aerobatics'), 'y')
  if False:
    c4d.cprint(c4d.datasets.nn_model('yolov3'), 'y')
  c4d.cprint(c4d.datasets.d3_model('bunny'), 'y')
  c4d.cprint(c4d.datasets.d3_model('bunnymesh'), 'y')
  c4d.cprint(c4d.datasets.d3_model('f16'), 'y')
  c4d.datasets.clear_cache()


  cache_root = list(os.walk(CACHE_DIR))
  root, dirs, files = cache_root[0][0], cache_root[0][1], cache_root[0][2]
  print(len(os.path.join(root, dirs)))
  print(len(os.path.join(root, files)))



  # check if planes is currently existing 
  c4d.cprint('clear planes', 'g')
  impath = c4d.datasets.image('planes')
  print(os.path.exists(impath))
  c4d.datasets.clear_cache('planes')
  print(os.path.exists(impath))

  c4d.cprint('clear triangle', 'g')
  impath = c4d.datasets.image('triangle')
  print(os.path.exists(impath))
  c4d.datasets.clear_cache('triangle')
  print(os.path.exists(impath))
    
  c4d.cprint('clear aerobatics', 'g')
  path = c4d.datasets.video('aerobatics')
  print(os.path.exists(path))
  c4d.datasets.clear_cache('aerobatics')
  print(os.path.exists(path))

  c4d.cprint('clear yolo', 'g')
  path = c4d.datasets.nn_model('yolov3')
  print(os.path.exists(path))
  c4d.datasets.clear_cache('yolov3')
  print(os.path.exists(path))

  c4d.cprint('clear bunny', 'g')
  path = c4d.datasets.d3_model('bunny')
  print(os.path.exists(path))
  c4d.datasets.clear_cache('bunny')
  print(os.path.exists(path))

  c4d.cprint('clear bunny mesh', 'g')
  path = c4d.datasets.d3_model('bunny_mesh')
  print(os.path.exists(path))
  c4d.datasets.clear_cache('bunny_mesh')
  print(os.path.exists(path))

  c4d.cprint('clear f16', 'g')
  path = c4d.datasets.d3_model('f16')
  print(os.path.exists(path))
  c4d.datasets.clear_cache('f16')
  print(os.path.exists(path))
 

def f16(): 

  c4d.cprint('7. F16', 'y')

  import open3d as o3d 

  f16path = c4d.datasets.d3_model('f16')
  model = []
  for f in sorted(os.listdir(f16path)):
    model.append(o3d.io.read_triangle_mesh(os.path.join(f16path, f)).compute_vertex_normals())
    

  o3d.visualization.draw_geometries(model)


def mesh(): 
  c4d.cprint('6. mesh stanford bunny', 'y')
  import open3d as o3d 

  mbunnypath = c4d.datasets.d3_model('bunny_mesh')
  ply = o3d.io.read_triangle_mesh(mbunnypath)
  ply.compute_vertex_normals()
  print(ply)
  o3d.visualization.draw_geometries([ply])


def bunny(): 

  c4d.cprint('5. stanford bunny', 'y')
  import open3d as o3d 

  bunnypath = c4d.datasets.d3_model('bunny')
  pcd = o3d.io.read_point_cloud(bunnypath)
  print(pcd)
  o3d.visualization.draw_geometries([pcd])


def yolov3(): 
  c4d.cprint('4. yolo v3', 'y')
  # Z:\Dropbox\c4dynamics\c4dynamics\detectors
  # print(os.getcwd())

  impath = c4d.datasets.nn_model('yolov3')
  net = cv2.dnn.readNet(impath, 'c4dynamics/detectors/yolov3.cfg')
  # print("Layers:", layer_names)
  # Optionally, inspect the weights of specific layers
  for i, layer in enumerate(net.getLayerNames()):
    print(f"Layer {i}:\t{layer}")
    if i > 4: break 


def videos(): 
  c4d.cprint('3. videos', 'y')

  vidpath = c4d.datasets.video('aerobatics')
  cap = cv2.VideoCapture(vidpath)
  while cap.isOpened():
    ret, frame = cap.read() 
    if not ret: break
    cv2.imshow('aerobatics', frame)  
    # Wait for 25ms and check if 'q' is pressed to exit
    if cv2.waitKey(33) & 0xFF == ord('q'):
        break

  # Release the video capture object and close any OpenCV windows
  cap.release()
  cv2.destroyAllWindows()


def planes(): 
  c4d.cprint('2. planes', 'y')

  impath = c4d.datasets.image('planes')
  # cv2.imshow('planes', cv2.imread(impath))
  # cv2.waitKey(0)
  img = mpimg.imread(impath)
  
  plt.figure() 
  plt.imshow(img)
  plt.axis('off')
  

def triangle(): 
  c4d.cprint('1. triangle', 'y')

  impath = c4d.datasets.image('triangle')
  # cv2.imshow('triangle', cv2.imread(impath))
  # cv2.waitKey(0)
  plt.figure() 

  img = mpimg.imread(impath)
  plt.imshow(img)
  plt.axis('off')


if __name__ == '__main__':

  # downloadall()
  # clearcache() 
  # f16() 
  # mesh() 
  # bunny() 
  yolov3() 
  # videos() 
  # planes() 
  # triangle() 

  # plt.show() 


