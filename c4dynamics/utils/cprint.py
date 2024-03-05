TXTCOLORS =     { 'k': '30', 'black':   '30'
                , 'r': '31', 'red':     '31'
                , 'g': '32', 'green':   '32'
                , 'y': '33', 'yellow':  '33'
                , 'b': '34', 'blue':    '34'
                , 'm': '35', 'magenta': '35'
                , 'c': '36', 'cyan':    '36'
                , 'w': '37', 'white':   '37'
                    }

def cprint(txt, color = 'white', bold = False, italic = False):
    '''
    ******
    cprint
    ******

    Printing colored text in the console.

    Parameters
    ----------

    txt : str
        The text to be printed.
    
    color : str, optional
        The color of the text. Default is 'white'.
    
    bold : bool, optional
        If True, the text will be printed in bold. Default is False.
    
    italic : bool, optional
        If True, the text will be printed in italic. Default is False.

    Example
    -------

    .. code:: 
    
        >>> carr = ['k', 'r', 'g', 'y', 'b', 'm', 'c', 'w']
        >>> for c in carr:
        ...     c4d.cprint('C4DYNAMICS', c)
        
        
    .. figure:: /_static/images/cprint.png

    
        
    '''
    settxt = '\033['

    # if bold:
    #     settxt += '1;'
    # if italic:
    #     settxt += '3;'

    settxt += TXTCOLORS[color] 
        
    print(settxt + 'm' + str(txt) + '\033[0m')

