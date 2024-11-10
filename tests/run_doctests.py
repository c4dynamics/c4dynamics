# type: ignore

import os, sys 
import subprocess

sys.path.append('.')
import c4dynamics as c4d 

print(sys.executable) 

packagefol = 'c4dynamics'

for dirpath, _, filenames in os.walk(packagefol):
  if '__pycache__' in dirpath: continue
  c4d.cprint(f'dir: {dirpath}', 'c')
  
  for file_name in filenames:
    if file_name == 'registery.py':     continue
    if file_name == 'kalman_v0.py':     continue 
    if file_name == 'kalman_v1.py':     continue 
    if file_name == 'yolo3_tf.py':      continue 
    if file_name == 'a.py':             continue 
    if file_name == 'luenberger.py':    continue 
    if file_name == 'lineofsight.py':   continue 
    if file_name == 'vidgen.py':        continue
    if file_name == 'video_gen.py':     continue
    if file_name == '_struct.py':       continue
    if file_name == 'images_loader.py': continue
    if file_name == 'slides_gen.py':    continue
    if file_name == 'plottracks.py':    continue
    if file_name == 'printpts.py':      continue
    
    if not file_name.endswith(".py"):   continue

    # if file_name == 'yolo3_opencv.py' or file_name == '_manager.py' or file_name == 'animate.py':     
    #   c4d.cprint('warning: yolo3, datasets, animate, are skipped!', 'r')
    #   continue

    testfile = os.path.join(dirpath, file_name)
    
    if dirpath == 'c4dynamics' and file_name == '__init__.py': 
      subprocess.run([sys.executable, '-m', 'c4dynamics'])
    else:       
      subprocess.run([sys.executable, testfile])




