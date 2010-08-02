# -*- coding: utf-8 -*-

# Import all the Exception messages
from exception_messages import *

def create_signature(filename, is_update, is_upgrade, \
        upgrade_type, install_packages_list, install_src_packages_list, \
                                                target_release, src_build_dep):
    """
    Create a signature for the apt system from the options provided
    
    
    filename is the name of the file where the the signatre will be stored
    The options are:
    * Update
    * Upgrade
     * Upgrade Type
    * Intall Packages
    * Install Source Packages
     * Source build dependency
    
    Optionally target_release can be over-ridden from default
    """
    
    # If the user doesn't specify anything, then by default 
    # it means that he/she wants to run update and upgrade
    if is_update is False and is_upgrade is False \
        and install_packages_list is None and install_src_packages_list is None:
        is_update = True
        is_upgrade = True
    
    # Check if the file already exists, then try to delete it
    if os.path.isfile(filename):
        if os.access( filename, os.W_OK )  is False:
            throw Exception(SIGNATURE_FILE_NOT_WRITABLE)
        else:
            os.unlink(filename)
    
    