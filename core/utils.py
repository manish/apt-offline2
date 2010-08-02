# -*- coding: utf-8 -*-

import platform
import os
from include import *
from exception_messages import *

def check_platform_supported():
    if platform.system() in supported_platforms is False:
        raise Exception(PLATFORM_NOT_SUPPORTED)
    
def check_root():
    if os.geteuid() != 0:
        raise Exception(NEED_TO_BE_SUPERUSER)

def humanize_file_size( self, size ):
    ''' Takes number of kB and returns a string
                of proper size. Like if > 1024, return a megabyte '''
    if size > 1024:
        size = size // 1024
        
        if size > 1024:
            size = size // 1024
            return ( "%d GiB" % ( size ) )
        
        return ( "%d MiB" % ( size ) )
        
    return ( "%d KiB" % ( size ) )
    

def check_valid_upgrade_type(upgrade_type):
    """ Checks if the upgrade_type is valid or not """
    
    if upgrade_type is None:
        raise Exception(UPGRADE_TYPE_MISSING)
    
    if upgrade_type not in upgrade_types:
        raise Exception(UPGRADE_TYPE_INVALID)