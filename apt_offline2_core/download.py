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

def download(filename, download_dir, cache_dir, disable_md5check, \
                        num_of_threads, bundle_file, socket_timeout, deb_bugs):
    """
    Downloads all the required files which are specified in the file provided
    
    filename - the path of the signature file
    download_dir - the directory path where the files will be stored
    cache_dir - the directory where the downloaded files will be cached
    disable_md5check - boolean (True/False) specifying whether to check for md5 checksum
    num_of_threads - Specifying the number of threads
    bundle_file - TODO
    socket_timeout - The time after which the connection timeouts
    deb_bugs - TODO
    """
    
    # Check whether socket timeout is provided  or not
    # If provided, check if it an integer or not. If yes, then set the socket timeout
    if socket_timeout:
        try:
            socket_timeout.__int__()
            socket.setdefaulttimeout( socket_timeout )
            log.verbose( "Default timeout now is: %d.\n" % ( socket.getdefaulttimeout() ) )
    except AttributeError:
            log.err( "Incorrect value set for socket timeout.\n" )
            raise WrongDataTypeError(SOCKET_TIMEOUT_SHOULD_BE_INTEGER)

    #INFO: Python 2.5 has hashlib which supports sha256
    # If we don't have Python 2.5, disable MD5/SHA256 checksum
    if AptOfflineLib.Python_2_5 is False:
        disable_md5check = True
        log.verbose( "\nMD5/SHA256 Checksum is being disabled. You need atleast Python 2.5 to do checksum verification.\n" )

    # If the filename is not provided then there is nothing to download
    if filename is None:
        raise SignatureFileError(SIGNATURE_FILE_NOT_PROVIDED)
    
    # If the file is not present or not accessible to the current user
    if os.access( filename, os.F_OK):
        log.msg( "\nFetching APT Data\n\n" )
    else:
        log.err( "\nFile not present. Check path.\n" )
        raise SignatureFileError(SIGNATURE_FILE_MISSING_INACCESSIBLE)

    # If the cache directory is specified, then check if it exists
    # If it does not exist, then warn the user
    if cache_dir is not None:
        if os.path.isdir(cache_dir) is False:
            log.verbose( "WARNING: cache dir %s is incorrect. Did you give the full path ?\n" % (cache_dir) )
            raise IOError(CACHE_DIR_ERROR)

    #INFO: Thread Support
    if num_of_threads > 2:
        log.msg("WARNING: If you are on a slow connection, it is good to\n")
        log.msg("WARNING: limit the number of threads to a low number like 2.\n")
        log.msg("WARNING: Else higher number of threads executed could cause\n")
        log.msg("WARNING: network congestion and timeouts.\n\n")

    if deb_bugs:
        # TODO
        pass

    items_for_download = []
    
    #INFO: We don't distinguish in between what to fetch
    # We just rely on what a signature file lists us to get
    # It can be just debs or just package updates or both
    if filename is not None:
        try:
            raw_data_list = open( filename, 'r' ).readlines()
        except IOError, ( errno, strerror ):
            log.err( "%s %s\n" % ( errno, strerror ) )
            #errfunc( errno, '' )

        for item in raw_data_list:
            items_for_download.append( item )

        del raw_data_list

    # INFO: Let's get the total number of items. This will get the
    # correct total count in the progress bar.
    total_items = len(items_for_download)
    
    # total_download_size will store the total size to be downloaded
    # It is initialized to 0
    total_download_size = 0
    
    for item in items_for_download:
        try:
            (url, file, download_size, checksum) = stripper(item)
            size = int(download_size)
            
            # If the download size is 0, then make a HTTP HEAD request to
            # to know the actual size
            if size == 0:
                log.msg("MSG_START")
                temp = urllib2.urlopen(url)
                headers = temp.info()
                size = int(headers['Content-Length'])
            total_download_size += size
        except:
            ''' some int parsing problem '''
            pass
        
    log.msg("MSG_END")
    
    # Queue up the requests.
    for item in items_for_download:
        requestQueue.put(item)
    
    # Shut down the threads after all requests end.
    # (Put one None "sentinel" for each thread.)
    for t in thread_pool: requestQueue.put(None)