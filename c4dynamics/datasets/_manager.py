import hashlib
import shutil
# import pooch 
import os 

from ._registry import CACHE_DIR, image_register, video_register, nn_register, d3_register, d3_f16_register

imagesmap = {'planes': 'planes.png', 'planes.png': 'planes.png', 'triangle': 'triangle.png', 'triangle.png': 'triangle.png'}
videosmap = {'aerobatics': 'aerobatics.mp4', 'aerobatics.mp4': 'aerobatics.mp4'}
nnsmap    = {'yolov3': 'yolov3.weights', 'yolo_v3': 'yolov3.weights', 'yolov3.weights': 'yolov3.weights'}
d3smap    = {'f16': 'f16', 'f_16': 'f16', 'bunny': 'bunny.pcd', 'bunnymesh': 'bunny_mesh.ply', 'bunny_mesh': 'bunny_mesh.ply'
                , 'bunny.pcd': 'bunny.pcd', 'bunnymesh.ply': 'bunny_mesh.ply', 'bunny_mesh.ply': 'bunny_mesh.ply'}

def image(image_name):
  ''' 
    Gets a path to an image from the local cache.  
    
    `image` downloads and manages image files from `c4dynamics` datasets.  
        

    .. list-table:: 
      :widths: 20 80
      :header-rows: 1

      * - Image Name
        - Description

      * - planes 
        - A 1280x720 snapshot of aerobatic airplanes (planes.png, 300KB)

      * - triangle 
        - A 800x600 image of a triangle (triangle.png, 20KB) 
        


    The images can be found at 
    https://github.com/C4dynamics/C4dynamics/blob/main/datasets/images/

    
    Parameters
    ----------
    image_name : str
        The name of the image to download 

    Returns
    -------
    out : str
        A path to the image file in the local cache

       
    Examples
    --------

    **planes**

    .. code::

      >>> import cv2
      >>> import c4dynamics as c4d
      >>> impath = c4d.datasets.image('planes')
      fetched successfully
      >>> cv2.imshow('planes', cv2.imread(impath))
      >>> cv2.waitKey(0)  # Display window waits for a key press to close

    .. figure:: ../../../datasets/images/planes.png

    
    **triangle** 

    .. code::

      >>> import cv2
      >>> import c4dynamics as c4d
      >>> impath = c4d.datasets.image('triangle')
      fetched successfully
      >>> cv2.imshow('triangle', cv2.imread(impath))
      >>> cv2.waitKey(0)  # Display window waits for a key press to close

    .. figure:: ../../../datasets/images/triangle.png
    
  '''

  imagein = imagesmap.get(image_name.lower(), None)

  if imagein is None:
    raise KeyError(f"'{image_name}' is not an image in c4dynamics datasets. Available images are: 'planes', 'triangle'.")

  filename = image_register.fetch(imagein)
  print('Fetched successfully') 
  return filename 


def video(video_name):
  ''' 
    Gets a path to a video from the local cache.  
    
    `video` downloads and manages video files from `c4dynamics` datasets.  
        

    .. list-table:: 
      :widths: 20 80
      :header-rows: 1

      * - Video Name
        - Description

      * - planes 
        - 10 seconds video file of aerobatic airplanes (aerobatics.mp4, 7MB)

      

    The videos can be found at 
    https://github.com/C4dynamics/C4dynamics/blob/main/datasets/videos/

    
    Parameters
    ----------
    video_name : str
        The name of the video to download 

    Returns
    -------
    out : str
        A path to the video file in the local cache

       
    Examples
    --------

    .. code::

      >>> import cv2 
      >>> import c4dynamics as c4d
      >>> vidpath = c4d.datasets.video('aerobatics')
      >>> cap = cv2.VideoCapture(vidpath)
      >>> while cap.isOpened():
      ...   ret, frame = cap.read() 
      ...   if not ret: break
      ...   cv2.imshow('aerobatics', frame)  
      ...   cv2.waitKey(33)
      >>> cap.release()
      >>> cv2.destroyAllWindows()

    
    .. figure:: /_static/gifs/aerobatics.gif


    
  '''

  videoin = videosmap.get(video_name.lower(), None)

  if videoin is None:
    raise KeyError(f"'{video_name}' is not a video in c4dynamics datasets. An available video is: 'aerobatics'.")

  filename = video_register.fetch(videoin)
  print('Fetched successfully') 
  return filename


def nn_model(nn_name): 
  ''' 
    Gets a path to a neural network model from the local cache.  
    
    `nn_model` downloads and manages neural network files from `c4dynamics` datasets.  
        

    .. list-table:: 
      :widths: 20 80
      :header-rows: 1

      * - NN Name
        - Description

      * - YOLOv3 
        - Pre-trained weights file (237 MB)
        


    YOLOv3 weights file can be found at 
    https://pjreddie.com/media/files/yolov3.weights

    
    Parameters
    ----------
    nn_name : str
        The name of the neural network model to download 

    Returns
    -------
    out : str
        A path to the neural network in the local cache

       
    Examples
    --------

    
    Print first 5 layers of YOLOv3: 

    .. code::

      >>> import cv2 
      >>> import c4dynamics as c4d
      >>> impath = c4d.datasets.nn_model('yolov3')
      fetched successfully
      >>> net = cv2.dnn.readNet(impath, 'c4dynamics/detectors/yolov3.cfg')
      >>> for i, layer in enumerate(layer_names):
      ...   print(f"Layer {i}:\t{layer}")
      ...   if i > 4: break 
      Layer 0:        conv_0
      Layer 1:        bn_0
      Layer 2:        leaky_1
      Layer 3:        conv_1
      Layer 4:        bn_1
      Layer 5:        leaky_2

    
  '''

  nnin = nnsmap.get(nn_name.lower(), None)

  if nnin is None:
    raise KeyError(f"'{nn_name}' is not a neural network model in c4dynamics datasets. An available model is: 'yolov3'.")

  filename = nn_register.fetch(nnin) 
  print('Fetched successfully') 
  return filename


def d3_model(d3_name): 
  '''
    Gets a path to a 3D model from the local cache.  
    
    `d3_model` downloads and manages 3D model files from `c4dynamics` datasets.  
        

    .. list-table:: 
      :widths: 20 80
      :header-rows: 1

      * - Model Name
        - Description

      * - bunny 
        - Point cloud file of Stanford bunny (bunny.pcd, 0.4MB)
        
      * - bunny_mesh 
        - Triangle mesh file of Stanford bunny (bunny_mesh.ply, 3MB)

      * - F16 
        - 10 stl files representing the jet parts as fuselage, ailerons, 
          cockpit, rudder and stabilators (10 files, total 3MB).  
        

    The models can be found at 
    https://github.com/C4dynamics/C4dynamics/blob/main/datasets/d3_models/

    

    Parameters
    ----------
    d3_name : str
        The name of the 3D model to download 

    Returns
    -------
    out : str
        A path to the model in the local cache. 
        For the `f16` model, the function returns a path 
        to the folder including 10 files.  

       
    Examples
    --------

    
    **Stanford bunny (point cloud)** 

    .. code::

      >>> import open3d as o3d 
      >>> import c4dynamics as c4d
      >>> bunnypath = c4d.datasets.d3_model('bunny')
      fetched successfully
      >>> pcd = o3d.io.read_point_cloud(bunnypath)
      >>> print(pcd)
      PointCloud with 35947 points.
      >>> o3d.visualization.draw_geometries([pcd])

    .. figure:: /_static/images/datasets/bunny.png

    
    **Stanford bunny (triangle mesh)** 
    
    .. code::

      >>> import open3d as o3d 
      >>> import c4dynamics as c4d
      >>> mbunnypath = c4d.datasets.d3_model('bunny_mesh')
      fetched successfully
      >>> ply = o3d.io.read_triangle_mesh(mbunnypath)
      >>> ply.compute_vertex_normals()
      >>> print(ply)
      TriangleMesh with 35947 points and 69451 triangles.
      >>> o3d.visualization.draw_geometries([ply])

    .. figure:: /_static/images/datasets/bunny_mesh.png


    **F16 (10 stl files)** 
    
    .. code::

      >>> import open3d as o3d 
      >>> import c4dynamics as c4d
      >>> f16path = c4d.datasets.d3_model('f16')
      fetched successfully
      >>> model = []
      >>> for f in sorted(os.listdir(f16path)):
      ...   model.append(o3d.io.read_triangle_mesh(os.path.join(f16path, f)).compute_vertex_normals())
      >>> o3d.visualization.draw_geometries(model)

      
    .. figure:: /_static/images/datasets/f16.png    


  '''

  d3in = d3smap.get(d3_name.lower(), None) 

  if d3in is None: 
    raise KeyError(f"'{d3_name}' is not a 3D model in c4dynamics datasets. Available models are: 'bunny', 'bunny_mesh', 'f16'.")


  # returns path 
  if d3in == 'f16': 
    d3_f16_register.fetch('Aileron_A_F16.stl')
    d3_f16_register.fetch('Aileron_B_F16.stl')
    d3_f16_register.fetch('Body_F16.stl') 
    d3_f16_register.fetch('Cockpit_F16.stl') 
    d3_f16_register.fetch('LE_Slat_A_F16.stl') 
    d3_f16_register.fetch('LE_Slat_B_F16.stl') 
    d3_f16_register.fetch('Rudder_F16.stl') 
    d3_f16_register.fetch('Stabilator_A_F16.stl') 
    filename = os.path.dirname(d3_f16_register.fetch('Stabilator_B_F16.stl'))
    
  else:
    filename = d3_register.fetch(d3in) 


  print('Fetched successfully') 
  return filename


def download_all():
  image('planes')
  image('triangle')
  video('aerobatics')
  nn_model('yolov3')
  d3_model('bunny')
  d3_model('bunny_mesh')
  d3_model('f16')


def clearcache(dataset = None):
  '''     
    Deletes datasets from the local cache.  

    If a dataset name is provided, the function deletes this alone.
    Otherwise, clears all the cache. 
    

    Parameters
    ----------
    dataset : str, optional
        The name of the dataset to delete. 


       
    Examples
    --------

    
    **Given dataset** 

    .. code::

      >>> import c4dynamics as c4d 
      >>> # download and verify 
      >>> impath = c4d.datasets.image('planes')
      Fetched successfully
      >>> print(os.path.exists(impath))
      True
      >>> # clear and verify 
      >>> c4d.datasets.clearcache('planes')
      >>> print(os.path.exists(impath))
      False

    **Clear all**
    
    .. code::

      >>> import c4dynamics as c4d 
      >>> # download all 
      >>> c4d.datasets.download_all()
      >>> # clear all and verify 
      >>> c4d.datasets.clearcache()
      >>> for root, dirs, files in os.walk(CACHE_DIR):
      ...   for file in files:
      ...     print(os.path.join(root, file))
      ...   for dir in dirs:
      ...     print(os.path.join(root, dir))





 '''
  if dataset is None: 
    for root, dirs, files in os.walk(CACHE_DIR):
      for file in files:
        os.remove(os.path.join(root, file))
      for dir in dirs:
        shutil.rmtree(os.path.join(root, dir))
    return 


  allmaps = imagesmap | videosmap | nnsmap | d3smap 
  datain  = allmaps.get(dataset.lower(), None)

  if datain is None:
    raise KeyError(f"'{dataset}' is not a dataset in c4dynamics.")

  datafile = os.path.join(CACHE_DIR, datain)
  if datain == 'f16':
    shutil.rmtree(datafile)
  else: 
    if os.path.exists(datafile):
      os.remove(datafile)




def sha256(filename):
  # filehash = pooch.file_hash(r'C:\Users\odely\Downloads\yolov3 (1).weights')

  hash_sha256 = hashlib.sha256()
  with open(filename, 'rb') as f:
    for byte_block in iter(lambda: f.read(4096), b""):
      hash_sha256.update(byte_block)
  return hash_sha256.hexdigest()

