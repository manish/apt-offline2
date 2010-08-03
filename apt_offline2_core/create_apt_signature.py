# -*- coding: utf-8 -*-

import os
import os.path

# Import all the Exception messages
from exception_messages import *

# Import all Exceptions
from exceptions import *

# Include Utility functions
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
            raise SignatureFileError(SIGNATURE_FILE_NOT_WRITABLE)
        else:
            os.unlink(filename)
    
    
    # If the user wants to update
    if is_update:
        update(filename, logger)
    
    # If the user wants to perform an upgrade
    if is_upgrade:
        upgrade(filename, upgrade_type, logger)
    
    # If the user wants to install packages
    if install_packages_list != None and install_packages_list  != []:
        install_packages(filename, install_packages_list, target_release, logger)

    # If the user wants to install source packages
    if install_src_packages_list != None and install_src_packages_list  != []:
        install_source_packages(filename, install_src_packages_list, target_release, src_build_dep, logger)


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
    
    if upgrade_type == "upgrade":
        res = upgrade_upgrade(filename ,log)
    elif upgrade_type == "dist-upgrade":
        res = upgrade_dist_upgrade(filename ,log)
    elif upgrade_type == "dselect-upgrade":
        res = upgrade_dist_upgrade(filename ,log)
        
    return res


def upgrade_upgrade(filename ,log):
    """ Invoked if the user wanted upgrade """

    try:
        # import apt
        import apton
        try:
            install_file = open( filename, 'a' )
        except IOError:
            log.err( "Cannot create file %s.\n" % (filename))
            raise SignatureFileError(OPEN_CREATION_SIGNATURE_FILE_FAILED)

        # Get the list of all packages which are fit to be upgraded
        log.verbose("Using the python-apt library to generate the database.\n")
        upgradable = filter( lambda p: p.isUpgradable, apt.Cache())
        log.msg( "\nGenerating database of files that are needed for an upgrade.\n" )
        
        #dup_records = []
        #for pkg in upgradable:
            #pkg._lookupRecord( True )
            #dpkg_params = apt_pkg.ParseSection(pkg._records.Record)
            #arch = dpkg_params['Architecture']
            #path = dpkg_params['Filename']
            #checksum = dpkg_params['SHA256'] #FIXME: There can be multiple checksum types
            #size = dpkg_params['Size']
            #cand = pkg._depcache.GetCandidateVer( pkg._pkg )
            #for ( packagefile, i ) in cand.FileList:
                #indexfile = PythonAptQuery.cache._list.FindIndex( packagefile )
                #if indexfile:
                    #uri = indexfile.ArchiveURI( path )
                    #file = uri.split( '/' )[ - 1]
                    #if checksum.__str__() in dup_records:
                            #continue
                    #install_file.write( uri + ' ' + file + ' ' + size + ' ' + checksum + "\n" )
                    #dup_records.append( checksum.__str__() )
    except ImportError:
        log.msg( "\nGenerating database of files that are needed for an upgrade.\n" )
        os.environ['__apt_set_upgrade'] = filename
        
        if os.system( '/usr/bin/apt-get -qq --print-uris upgrade >> $__apt_set_upgrade' ) != 0:
            raise AptSystemBrokenError(APT_SYSTEM_BROKEN)
        
    return True


def upgrade_dist_upgrade(filename ,log):
    """ Invoked if the user wanted a dist-upgrade """
    
    log.msg( "\nGenerating database of files that are needed for a dist-upgrade.\n" )
    os.environ['__apt_set_upgrade'] = filename
    if os.system( '/usr/bin/apt-get -qq --print-uris dist-upgrade >> $__apt_set_upgrade' ) != 0:
        raise AptSystemBrokenError(APT_SYSTEM_BROKEN)
    
    return True


def upgrade_dselect_upgrade(filename ,log):
    """ Invoked if the user wanted a dselect-upgrade """
    
    log.msg( "\nGenerating database of files that are needed for a dselect-upgrade.\n" )
    os.environ['__apt_set_upgrade'] = filename
    if os.system( '/usr/bin/apt-get -qq --print-uris dselect-upgrade >> $__apt_set_upgrade' ) != 0:
        raise AptSystemBrokenError(APT_SYSTEM_BROKEN)
    
    return True


def install_packages(filename, install_packages_list, target_release, log):
    """ Invoked if the user wants to install packages """
    
    # Check if the platform is supported
    utils.check_platform_supported()
    
    # Check if the user is running with super-user priviliges
    utils.check_root()
    
    comma_sep_package_list = ", ".join(install_packages_list)
    log.msg( "\nGenerating database of package %s and its dependencies.\n" % (comma_sep_package_list) )
    
    package_list = " ".join(install_packages_list)
    os.environ['__apt_set_install_packages'] = package_list
    
    os.environ['__apt_set_install'] = filename
    
    # If the target release is specified, include it as -t switch
    if target_release:
        os.environ['__apt_set_install_release'] = target_release
        if os.system( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release install $__apt_set_install_packages >> $__apt_set_install' ) != 0:
            raise AptSystemBrokenError(APT_SYSTEM_BROKEN)
    else:
        #FIXME: Find a more Pythonic implementation
        if os.system( '/usr/bin/apt-get -qq --print-uris install $__apt_set_install_packages >> $__apt_set_install' ) != 0:
            raise AptSystemBrokenError(APT_SYSTEM_BROKEN)

    return True


def install_source_packages(filename, install_source_packages_list, target_release, src_build_dep, log):
    """ Invoked if the user wants to install packages """
    
    # Check if the platform is supported
    utils.check_platform_supported()
    
    # Check if the user is running with super-user priviliges
    utils.check_root()
    
    comma_sep_source_package_list = ", ".join(install_source_packages_list)
    log.msg( "\nGenerating database of package %s and its dependencies.\n" % (comma_sep_source_package_list) )
    
    source_package_list = " ".join(install_source_packages_list)
    os.environ['__apt_set_install_packages'] = source_package_list
    
    os.environ['__apt_set_install'] = filename
    
    # If the target release is specified, include it as -t switch
    if target_release:
        os.environ['__apt_set_install_release'] = target_release
        if os.system( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release source $__apt_set_install_src_packages >> $__apt_set_install' ) != 0:
            raise AptSystemBrokenError(APT_SYSTEM_BROKEN)
    else:
        #FIXME: Find a more Pythonic implementation
        if os.system( '/usr/bin/apt-get -qq --print-uris source $__apt_set_install_src_packages >> $__apt_set_install' ) != 0:
            raise AptSystemBrokenError(APT_SYSTEM_BROKEN)

    if src_build_dep:
        log.msg("Generating Build-Dependency for source packages %s.\n" % (comma_sep_source_package_list) )
        if target_release:
            os.environ['__apt_set_install_release'] = target_release
            if os.system( '/usr/bin/apt-get -qq --print-uris -t $__apt_set_install_release build-dep $__apt_set_install_src_packages >> $__apt_set_install' ) != 0:
                raise AptSystemBrokenError(APT_SYSTEM_BROKEN)
        else:
            #FIXME: Find a more Pythonic implementation
            if os.system( '/usr/bin/apt-get -qq --print-uris build-dep $__apt_set_install_src_packages >> $__apt_set_install' ) != 0:
                raise AptSystemBrokenError(APT_SYSTEM_BROKEN)