# -*- coding: utf-8 -*-

import platform
import os
from include import *
from exception_messages import *

def is_platform_supported():
    return platform.system() in supported_platforms
    
def check_root():
    if os.geteuid() != 0:
        throw Exception(NEED_TO_BE_SUPERUSER)

def calcSize( self, size ):
    ''' Takes number of kB and returns a string
                of proper size. Like if > 1024, return a megabyte '''
    if size > 1024:
        size = size // 1024
        
        if size > 1024:
            size = size // 1024
            return ( "%d GiB" % ( size ) )
        
        return ( "%d MiB" % ( size ) )
        
    return ( "%d KiB" % ( size ) )