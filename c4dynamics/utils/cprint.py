import sys 
sys.path.append('.')

TXTCOLORS =     { 'k': '30', 'black':   '30'
                , 'r': '31', 'red':     '31'
                , 'g': '32', 'green':   '32'
                , 'y': '33', 'yellow':  '33'
                , 'b': '34', 'blue':    '34'
                , 'm': '35', 'magenta': '35'
                , 'c': '36', 'cyan':    '36'
                , 'w': '37', 'white':   '37'
                    }

def cprint(txt = '', color = 'white', end = '\n'):
  '''
    Printing colored text in the console.

    Parameters
    ----------

    txt : str
        The text to be printed.
    
    color : str, optional
        The color of the text. Default is 'white'.
    
    Example
    -------

    .. code:: 
    
      >>> import c4dynamics as c4d
      >>> carr = ['y', 'w', 'r', 'm', 'c', 'g', 'k', 'b']
      >>> for c in carr:
      ...   c4d.cprint('C4DYNAMICS', c) # doctest: +IGNORE_OUTPUT

    .. raw:: html

      <span style="color:yellow">C4DYNAMICS</span><br>
      <span style="color:white">C4DYNAMICS</span><br>
      <span style="color:red">C4DYNAMICS</span><br>
      <span style="color:magenta">C4DYNAMICS</span><br>
      <span style="color:cyan">C4DYNAMICS</span><br>
      <span style="color:green">C4DYNAMICS</span><br>
      <span style="color:black">C4DYNAMICS</span><br>
      <span style="color:blue">C4DYNAMICS</span><br>
 
  '''
  settxt = '\033['


  settxt += TXTCOLORS[color] 
      
  print(settxt + 'm' + str(txt) + '\033[0m', end = end)


if __name__ == "__main__":

  from c4dynamics import rundoctests
  rundoctests(sys.modules[__name__])



