# -*- coding: utf-8 -*-
# pragma: no cover
# type: ignore 
# # The following environment is selected: 
# \\192.168.1.244\d\gh_repo\c4dynamics\.venv\Scripts\python.exe  
#

'''
 working plan:
   after proving the algo on synthetis videos i made manually here:
   take 2 or 3 types of motion videos:
   linear, parabole, sinsuidal
   and show performances with c4dynamics.
   show improvemnet for better dynamics modelling. 
   
'''
import os, sys
import socket
import cv2
import numpy as np
from enum import Enum
print(os.getcwd())
# import c4dynamics as c4d 
# if socket.gethostname() != 'ZivMeri-PC':
#   os.chdir(os.path.join('\\\\192.168.1.244', 'd', 'gh_repo', 'c4dynamics'))
print(sys.executable)
# https://github.com/microsoft/debugpy/issues/1231

FRAMEWIDTH = 1280
FRAMEHEIGHT = 720



class Im_saveshow(Enum):
  SHOW      = 1
  SAVE      = 2
  SAVESHOW  = 3 

class Motion_Type(Enum):
  LINEAR    = 1
  PARABOLE  = 2
  SINE     = 3   

def rotateimage(image, angle0, angle1):
    # Define the angle of rotation (in degrees)
  # angle = -90  # Change this value as needed

  # dangle = pathangle - current_rotation 

  # # Get the dimensions of the image
  # height, width = image.shape[:2]

  # rotation_matrix = cv2.getRotationMatrix2D((image.shape[1] / 2, image.shape[0] / 2), angle, 1)
  # # Calculate the new dimensions of the rotated image to prevent trimming
  # cos_theta  = np.abs(rotation_matrix[0, 0])
  # sin_theta  = np.abs(rotation_matrix[0, 1])
  # new_width  = int((height * sin_theta) + (width * cos_theta))
  # new_height = int((height * cos_theta) + (width * sin_theta))

  # # Adjust the rotation matrix for translation to keep the entire image visible
  # rotation_matrix[0, 2] += (new_width / 2)  - (width / 2)
  # rotation_matrix[1, 2] += (new_height / 2) - (height / 2)
  # Calculate the rotation matrix

  dangle = angle0 - angle1 

  # Get the dimensions of the image
  height, width = image.shape[:2]

  delta_rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), dangle, 1)
  angle_rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), dangle, 1)
  # Calculate the new dimensions of the rotated image to prevent trimming
  cos_theta  = np.abs(angle_rotation_matrix[0, 0])
  sin_theta  = np.abs(angle_rotation_matrix[0, 1])
  new_width  = int((height * sin_theta) + (width * cos_theta))
  new_height = int((height * cos_theta) + (width * sin_theta))

  # Adjust the rotation matrix for translation to keep the entire image visible
  delta_rotation_matrix[0, 2] += (new_width / 2)  - (width / 2)
  delta_rotation_matrix[1, 2] += (new_height / 2) - (height / 2)


  # Perform the rotation using warpAffine
  return cv2.warpAffine(image, delta_rotation_matrix, (new_width, new_height))

  # # Display the original and rotated images (optional)
  # cv2.imshow('Original Image', image)
  # cv2.imshow('Rotated Image', rotated_image)
  # cv2.waitKey(0)
  # cv2.destroyAllWindows()

  # # Save the rotated image
  # cv2.imwrite('path_to_save_rotated_image.jpg', rotated_image)

  # return rotated_image



def animate(objpath, x0 = 0, y0 = 0
              , scaling = 1, rotate = False, pathangle = None   
                , motion = Motion_Type.LINEAR, saveshow = Im_saveshow.SAVESHOW.value):

  ''' make a linear moving object video '''

  # Define the dimensions of the video frame
  saveon = any(x for x in [Im_saveshow.SAVESHOW.value, Im_saveshow.SAVE.value] if x == saveshow)
  showon = any(x for x in [Im_saveshow.SAVESHOW.value, Im_saveshow.SHOW.value] if x == saveshow)

  out = cv2.VideoWriter(os.path.join(os.getcwd(), 'examples', 'resources'
                                          , motion.name + '_' + os.path.basename(objpath)[:-4] 
                                            + str(int(x0)) + str(int(y0)) + '.mp4')
                              , cv2.VideoWriter_fourcc(*'mp4v') 
                                , 30.0, (FRAMEWIDTH, FRAMEHEIGHT))

  # Load the im_object you want to move
  im_object = cv2.imread(objpath, cv2.IMREAD_UNCHANGED)

  video_duration = 1

  if pathangle is None: 
    if motion == Motion_Type.LINEAR:
      pathangle = 0
    elif motion == Motion_Type.PARABOLE:
      pathangle = 45
      video_duration = 1.5
    elif motion == Motion_Type.SINE:
      pathangle = 0 
      video_duration = 2
  
  num_frames = int(30 * video_duration)
  
  # im_object = rotateimage(im_object, -pathangle * rotate)
  im_object = cv2.resize(im_object, tuple(reversed(tuple(int(scaling * i) for i in im_object.shape[:2]))))
  im_object = rotateimage(im_object, 0, pathangle * rotate)

  im_object_height, im_object_width, _ = im_object.shape

  # Ensure the im_object has 3 channels (remove alpha channel)
  im_object = im_object[:, :, :3]

  # Define initial position and velocity of the im_object
  # change to center of image 
  x_pos = int(x0 - im_object_width / 2) 
  y_pos = int(y0 - im_object_height / 2)

  vtotal_diag = np.sqrt(FRAMEHEIGHT**2 + FRAMEHEIGHT**2) / 30 
  x_velocity = int(vtotal_diag * np.cos(pathangle * np.pi / 180)) # int(FRAMEWIDTH / 30)  # Adjust velocity based on frame width
  y_velocity = int(vtotal_diag * np.sin(pathangle * np.pi / 180)) #  int(FRAMEHEIGHT / 30)  # Adjust velocity based on frame width
  
  # Define the duration of the video in seconds
  
 
  # Generate the frames for the video
  for fi in range(num_frames):
      # Create a black background frame
      frame = np.zeros((FRAMEHEIGHT, FRAMEWIDTH, 3), dtype = np.uint8)


      # Calculate the region to overlay the im_object on the frame

      if x_pos >= 0 and x_pos + im_object_width < FRAMEWIDTH:
        ''' simplest. all in '''
        TO_start_col    = x_pos
        TO_end_col      = x_pos + im_object_width
        FROM_start_col  = 0
        FROM_end_col    = im_object_width

      elif x_pos < 0:
        ''' pixels covered from left '''
        TO_start_col    = 0
        TO_end_col      = x_pos + im_object_width
        FROM_start_col  = -x_pos
        FROM_end_col    = im_object_width

      elif x_pos + im_object_width >= FRAMEWIDTH:
        ''' pixels covered from right '''
        TO_start_col    = x_pos
        TO_end_col      = FRAMEWIDTH
        FROM_start_col  = 0
        FROM_end_col    = max(FRAMEWIDTH - x_pos, 0)


      if y_pos >= 0 and y_pos + im_object_height < FRAMEHEIGHT:
        ''' simplest. all in '''
        TO_start_row    = y_pos
        TO_end_row      = y_pos + im_object_height
        FROM_start_row  = 0
        FROM_end_row    = im_object_height

      elif y_pos < 0:
        ''' pixels covered from top '''
        TO_start_row    = 0
        TO_end_row      = max(y_pos + im_object_height, 0)
        FROM_start_row  = -y_pos
        FROM_end_row    = im_object_height

      elif y_pos + im_object_height >= FRAMEHEIGHT:
        ''' pixels covered from bottom '''
        TO_start_row    = y_pos
        TO_end_row      = FRAMEHEIGHT
        FROM_start_row  = 0
        FROM_end_row    = max(FRAMEHEIGHT - y_pos, 0)
     

      fromshape = im_object[FROM_start_row : FROM_end_row, FROM_start_col : FROM_end_col].shape
      toshape = frame[TO_start_row : TO_end_row, TO_start_col : TO_end_col].shape

      frame[TO_start_row : TO_end_row, TO_start_col : TO_end_col] = (
                   im_object[FROM_start_row : FROM_end_row, FROM_start_col : FROM_end_col]
                      ).astype(np.uint8)
      


      # current_rotation = 0

      if motion == Motion_Type.LINEAR: 
        pass

      elif motion == Motion_Type.PARABOLE: 
        # parabole 
        # f / num_frames # when this is 1/2 i want pathangle to be zero. 
                        # when 1 to be 45.
                        # nameyly in full circly to change by 90.
                        # xdegrees per f.
                        # -90deg in numframes.
                        # x = -90 / nframe
        pathangle -= 90 / num_frames
        x_velocity = int(vtotal_diag * np.cos(pathangle * np.pi / 180)) # int(FRAMEWIDTH / 30)  # Adjust velocity based on frame width
        y_velocity = int(vtotal_diag * np.sin(pathangle * np.pi / 180)) # int(FRAMEHEIGHT / 30)  # Adjust velocity based on frame width
     
      elif motion == Motion_Type.SINE:
        # sinusidly 
        # all frames: 2 * pi
        # fi numframes
        # path angle 0 to 360 at numframes.
        # one frame 360/nframe
        pathangle =  90 * np.cos(3 * fi / num_frames * 2 * np.pi)
        x_velocity = int(vtotal_diag * np.cos(pathangle * np.pi / 180)) # int(FRAMEWIDTH / 30)  # Adjust velocity based on frame width
        y_velocity = int(vtotal_diag * np.sin(pathangle * np.pi / 180)) #  int(FRAMEHEIGHT / 30)  # Adjust velocity based on frame width
      
      

      # im_object = rotateimage(im_object, current_rotation, pathangle)
      # print(f'{fi:5.0f}  {pathangle}  {x_velocity}  {y_velocity}')


      x_pos += x_velocity
      y_pos += y_velocity

      # Write the frame to the video file

      if saveon:   
        out.write(frame)
      if showon:   
        cv2.imshow('im_object', frame)
        cv2.waitKey(300)



  # Release the VideoWriter object and close all windows
  out.release()
  cv2.destroyAllWindows()



# class Im_saveshow(Enum):
#   SHOW      = 1
#   SAVE      = 2
#   SAVESHOW  = 3 

objpath = os.path.join(os.getcwd(), 'examples', 'resources', 'car.png')


for runcase in range(1, 6):

  if runcase == 1: 
    ''' linear 1: left to right '''
    animate(objpath = objpath, motion = Motion_Type.LINEAR
            , x0 = 0, y0 = FRAMEHEIGHT / 2, scaling = .5, rotate = True)

  elif runcase == 2: 
    ''' linear 2: top to bottom '''
    animate(objpath = objpath, motion = Motion_Type.LINEAR
            , x0 = FRAMEWIDTH / 2, y0 = 0, scaling = .5, rotate = True
              , pathangle = 90)

  elif runcase == 3: 
    ''' linear 3: top left to bottom right '''
    animate(objpath = objpath, motion = Motion_Type.LINEAR
            , x0 = 0, y0 = 0, scaling = .5, rotate = True
              , pathangle = np.arctan(FRAMEHEIGHT / FRAMEWIDTH) * 180 / np.pi)

  elif runcase == 4: 
    ''' parabole 1: top left to top right '''
    animate(objpath = objpath, motion = Motion_Type.PARABOLE, x0 = 0, y0 = 0, scaling = .5)

  elif runcase == 5: 
    ''' sinusoid 1: left to right '''
    animate(objpath = objpath, motion = Motion_Type.SINE, x0 = 0, y0 = FRAMEHEIGHT / 2, scaling = .5)

 

