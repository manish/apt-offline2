# -*- coding: utf-8 -*-

import os
import os.path
import socket
import Queue
import threading
import tempfile

# Import all the Exception messages
from exception_messages import *

# Import all Exceptions
from exceptions import *

# Include Utility functions
import utils

from include import *

from logger import Log

def download(filename, download_dir, cache_dir, disable_md5check, num_of_threads, \
            bundle_file, socket_timeout, deb_bugs, notification_object, log):
    """
    Downloads all the required files which are specified in the file provided
    
    filename - the path of the signature file
    download_dir - the directory path where the files will be stored
    cache_dir - the directory where the downloaded files will be cached. OPTIONAL
    disable_md5check - boolean (True/False) specifying whether to check for md5 checksum
    num_of_threads - Specifying the number of threads
    bundle_file - TODO
    socket_timeout - The time after which the connection timeouts
    deb_bugs - TODO
    """
    
    # Check if the logger instance if actually an instance of logger.Log
    if isinstance(log, Log) is False:
        raise TypeError(LOGGER_TYPE_WRONG)
    
    # Check if the notification object is an instance of class which extends
    # INotify or not. If not, thrn throw TypeError
    if isinstance(notification_object, INotify) is False:
        raise TypeError(NOTIFICATION_TYPE_WRONG)
    
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
    if Python_2_5 is False:
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
        elif os.access(cache_dir, os.W_OK) is False:
            log.verbose("Cache directory is not writeable. Downloads won't be cached")


    # Check if the download directory is provided
    if download_dir is None:
        tempdir = tempfile.gettempdir()
        if os.access(tempdir, os.W_OK):
            pidname = os.getpid()
            tempdir = os.path.join(tempdir, "apt-offline-downloads-" + str(pidname))
            os.mkdir(tempdir)
            
            download_dir = os.path.abspath(tempdir)
        else:
            log.err("%s is not writable" %(tempdir))
            raise IOError(TEMP_DOWNLOAD_DIR_NOT_WRITABLE %(tempfile))
    else:
        if os.access(download_dir, os.W_OK):
            download_dir = os.path.abspath(download_dir)
        else:
            # If the path is provided but does not exist, then create it
            try:
                os.umask(0002)
                os.mkdir(download_dir)
                download_dir = os.path.abspath(download_dir)
            except:
                log.err("Could not create directory %s" %(download_dir))
                raise

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
   
    # Create two Queues for the requests and responses
    requestQueue = Queue.Queue()
    responseQueue = Queue.Queue()
  
    for item in items_for_download:
        try:
            (url, file, download_size, checksum) = utils.stripper(item)
            size = int(download_size)
            log.msg("File: %s | URI: %s | Size: %s\n" %(file, url, download_size))
            # If the download size is 0, then make a HTTP HEAD request to
            # to know the actual size
            if size == 0:
                log.msg("Trying to get the filesize of file %s" %(file))
                temp = urllib2.urlopen(url)
                headers = temp.info()
                size = int(headers['Content-Length'])
            total_download_size += size
            requestQueue.put((url, file, size, checksum))
        except Exception as e:
            ''' some int parsing problem '''
            pass
    
    # Send the total items to be downloaded and total download size as notification
    notification_object.set_total_items(total_items) 
    notification_object.set_total_download_size(total_download_size)

    log.msg("Total size to download: %s\n" %(utils.humanize_file_size(total_download_size/1000)))

    
        # Pool of NUMTHREADS Threads that run run().
    thread_pool =   [
                    threading.Thread(
                                    target = run,
                                    args =   (
                                            requestQueue, 
                                            responseQueue, 
                                            notification_object,
                                            disable_md5check,
                                            bundle_file,
                                            socket_timeout,
                                            download_dir,
                                            cache_dir,
                                            total_items,
                                            log
                                            )
                                    )
                    for i in range(num_of_threads)
                    ]
    
    # Start the threads.
    for t in thread_pool: t.start()
    
    # Don't end the program prematurely.
    # (Note that because Queue.get() is blocking by
    # defualt this isn't strictly necessary. But if
    # you were, say, handling responses in another
    # thread, you'd want something like this in your
    # main thread.)
    for t in thread_pool: t.join()



def run(request, response, notification_object, disable_md5check, bundle_file, socket_timeout, 
                    download_dir, cache_dir, total_items, log, func=utils.find_first_match):
    """ Get the packages """

    # The counter which actually keeps track of the total amoutn downloaded
    total_handled = 0

    # Create an infinite loop and break only when the queue is empty
    while True:

        # If there is no item in the request Queue 
        if request.empty():
            break

        # Get an item from the request queue
        url, file, size, checksum = request.get()
 
        # Get the name of the current thread
        thread_name = threading.currentThread().getName()

        if file.endswith(".deb"):
            # The file is a deb file which needs to be downloaded

            # Try getting the package name and version
            package_details = file.split("_")

            # Check if the filename has the package name or not
            if len(package_details) > 0:
                
                # Get the package name
                package_name = package_details[0]
                
                # Try getting the package version
                try:
                    package_version = package_details[1]
                except IndexError:
                    package_verion = "NA"
                    log.verbose("Package version not found. Is it really a .deb file?\n")

                # Check if the package is on the local cache or not
                response.put(func(cache_dir, file))

                # Find the full file path
                full_file_path = response.get()
                if full_file_path is not False:
                    log.msg("Package %s found in the cache\n" %(package_name))
                    # The file is downloaded and cached in the specified cache folder
                    handle_cached_deb_file  (
                                            file,
                                            url,
                                            disable_md5check,
                                            checksum,
                                            download_dir,
                                            cache_dir,
                                            package_name,
                                            bundle_file,
                                            package_version,
                                            log,
                                            notification_object
                                            )
                    # Add this package's size to total_download
                    total_handled += size

                    # Send a notificiation to the update the data download
                    notification_object.increment_download(file)
                    # Send a notification to increment download_size
                    notification_object.add_downloaded_size(size)

                else:
                    # The file needs to be downloaded
                    download_deb_file   (
                                        file,
                                        url,
                                        disable_md5check,
                                        checksum,
                                        download_dir,
                                        cache_dir,
                                        package_name,
                                        bundle_file,
                                        package_version,
                                        log,
                                        notification_object
                                        )
                    
                    # Add this package's size to the total_download
                    total_handled += size

                    # Send a notification to update the data downloaded
                    notification_object.increment_download(file)
                    # Send a notification to increment download_size
                    notification_object.add_downloaded_size(size)


            else:
                raise DownloadFileFormatError(DOWNLOAD_FILE_NAME_FORMAT_ERROR %(file))
        else:
            # The file is an update file
            pass

def handle_cached_deb_file( file, url, disable_md5check, checksum, download_dir, cache_dir, 
                        package_name, bundle_file, package_version, log, notification_object):
   
    """ If a file has been downloaded and is present in the download cache, then retrive the package from there """

    if disable_md5check is False:
        # The md5 check is requested
        if utils.CheckHashDigest(full_file_path, checksum):
            log.verbose("Checksum correct for package: %s\n" %(package_name))

            if bundle_file:
                # Copy the file to the archive
                # TODO : Implement the archiving the file
                pass

            # The user has not requested to archive the file, just copy it to download_dir
            else:
                # Copy the file from cache directory to download_dir
                try:
                    shutil.copy(full_file_path, download_dir)
                    log.success("%s copied from local cache directory: %s" %(full_file_path, download_dir))
                except shutil.Error:
                    log.verbose("%s is already present in %s. Skipping copying" %(full_file_path, download_dir))

        else:
            # Download the package again
            log.verbose("%s checksum mismatch.\n" %(full_file_path))
            log.msg("Downloading %s\n" %(package_name))
            # Download the file 
            download_deb_file   (
                                file, 
                                url, 
                                disable_md5check, 
                                checksum, 
                                download_dir, 
                                cache_dir, 
                                package_name, 
                                package_version, 
                                log, 
                                notification_object
                                )
            
def download_deb_file(file, url, disable_md5check, checksum, download_dir, cache_dir, 
                        package_name, bundle_file, package_version, log, notification_object):
    """ Download the deb file """
    log.msg("Inside the file %s\n" %(file))
    is_download_success = utils.download_from_web(url, file, download_dir, notification_object)
    if is_download_success:
        # The package has been downloaded successfully
        if disable_md5check is False:

            # Check if the checksum is valid
            is_valid_checksum = utils.CheckHashDigest(file, checksum)

            if is_valid_checksum:
                if cache_dir and os.access(cache_dir, os.W_OK):
                    try:
                        shutil.copy(file, cache_dir)
                    except shutil.Error:
                        log.msg("%s file is already present in cache dir %s" %(file, cache_dir))
            else:
                log.err("%s checksum mismatch" %(package_name))

        # TODO
        # Bundle the file into an archive
        if bundle_file:
            pass

    # Send the notification that this package failed to download
    else:
        notification_object.failed_packages(package_name, package_version)
