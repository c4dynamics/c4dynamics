import os, sys 
import subprocess

sys.path.append('..')
import c4dynamics as c4d 


testfol = 'tests'


'''
missing:
animate
rotmat
radar 
seeker
state
dp
rb
pp
const, cprint, gen_gif, math, plottools, tictoc

'''
for file_name in os.listdir(testfol):

  if file_name == 'run_unittests.py': continue
  if file_name == 'run_doctests.py': continue
  if not file_name.endswith(".py"): continue

  testfile = os.path.join(testfol, file_name)
  c4d.cprint(testfile, 'g')

  subprocess.run([sys.executable, testfile])




