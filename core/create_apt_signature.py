# -*- coding: utf-8 -*-

import os
import os.path

# Import all the Exception messages
from exception_messages import *
import utils
from include import *

def create_signature(filename, is_update, is_upgrade, \
        upgrade_type, install_packages_list, install_src_packages_list, \
                                        target_release, src_build_dep, logger):
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
    logger is an instance of logger.Log
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
            raise Exception(SIGNATURE_FILE_NOT_WRITABLE)
        else:
            os.unlink(filename)
    
    # If the user wants to update
    if is_update:
        update(filename, logger)
    
    # If the user wants to perform an upgrade
    if is_upgrade:
        upgrade(filename, upgrade_type, logger)

def update(filename, log):
    """ Invoked if the user has chosen to update his system """
    
    # Check if the platform is supported
    utils.check_platform_supported()
    
    # Check if the user is running with super-user priviliges
    utils.check_root()
    
    #FIXME: Unicode Fix
    # This is only a workaround.
    # When using locales, we get translation files. But apt doesn't extract the URI properly.
    # Once the extraction problem is root-caused, we can fix this easily.
    os.environ['__apt_set_update'] = filename
    try:
            old_environ = os.environ['LANG']
    except KeyError:
            old_environ = "C"
    os.environ['LANG'] = "C"
    log.verbose( "Set environment variable for LANG from %s to %s temporarily.\n" % ( old_environ, os.environ['LANG'] ) )
    if os.system( '/usr/bin/apt-get -qq --print-uris update >> $__apt_set_update' ) != 0:
            log.err( "FATAL: Something is wrong with the apt system.\n" )
            Bool_SetterErrors = True
    log.verbose( "Set environment variable for LANG back to its original from %s to %s.\n" % ( os.environ['LANG'], old_environ ) )
    os.environ['LANG'] = old_environ


def upgrade(filename, upgrade_type, log):
    """ Invoked if the user wants to perform an upgrade """
    
    # Check if the platform is supported
    utils.check_platform_supported()
    
    # Check if the user is running with super-user priviliges
    utils.check_root()
    
    # Check if the provided upgrade type is valid or not
    utils.check_valid_upgrade_type(upgrade_type)