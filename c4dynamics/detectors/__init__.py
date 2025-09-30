''' 

`c4dynamics` provides an API to third party object detection models.


.. list-table:: 
  :header-rows: 0

  * - :class:`YOLOv3 <c4dynamics.detectors.yolo3_opencv.yolov3>`
    - Realtime object detection model based on YOLO (You Only Look Once) approach with 80 pre-trained COCO classes

   
'''

import os, sys 
sys.path.append('.')

from c4dynamics.detectors.yolo3_opencv import yolov3

if __name__ == "__main__":

  # import doctest, contextlib
  # from c4dynamics import IgnoreOutputChecker, cprint
  
  # # Register the custom OutputChecker
  # doctest.OutputChecker = IgnoreOutputChecker

  # tofile = False 
  # optionflags = doctest.FAIL_FAST

  # if tofile: 
  #   with open(os.path.join('tests', '_out', 'output.txt'), 'w') as f:
  #     with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
  #       result = doctest.testmod(optionflags = optionflags) 
  # else: 
  #   result = doctest.testmod(optionflags = optionflags)

  # if result.failed == 0:
  #   cprint(os.path.basename(__file__) + ": all tests passed!", 'g')
  # else:
  #   print(f"{result.failed}")
  from c4dynamics import rundoctests
  rundoctests(sys.modules[__name__])



