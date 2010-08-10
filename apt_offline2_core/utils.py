# -*- coding: utf-8 -*-

import platform
import os
import string
import hashlib
import threading
import urllib2
import socket
from decimal import *

from include import *
from exception_messages import *
from exceptions import *

def check_apt_get_availablity():
    """ Check if apt-get is present on the system or not """
    
    if os.system( '/usr/bin/apt-get' ) != 0:
        raise AptGetUnavailableError(APT_GET_MISSING)

def check_platform_supported():
    """ Checks if the host platform is supported or not """
    
    if platform.system() in supported_platforms is False:
        raise PlatformNotSupportedError(PLATFORM_NOT_SUPPORTED)
    
def check_root():
    """ Check if the current user has super-administrative priviliges or not """
    
    if os.geteuid() != 0:
        raise NotSuperuserError(NEED_TO_BE_SUPERUSER)

def humanize_file_size( size ):
    ''' Takes number of kB and returns a string
                of proper size. Like if > 1024, return a megabyte '''
    getcontext().prec = 3
    size = Decimal(size)
    if size > 1024:
        size = size / Decimal(1024)
        
        if size > 1024:
            size = size / Decimal(1024)
            return ( "%s GiB" % ( size.__str__() ) )
        
        return ( "%s MiB" % ( size.__str__() ) )
        
    return ( "%s KiB" % ( size.__str__() ) )

def check_valid_upgrade_type(upgrade_type):
    """ Checks if the upgrade_type is valid or not """
    
    if upgrade_type is None:
        raise UpgradeTypeInvalidError(UPGRADE_TYPE_MISSING)
    
    if upgrade_type not in upgrade_types:
        raise UpgradeTypeInvalidError(UPGRADE_TYPE_INVALID)

def files(root): 
        for path, folders, files in os.walk(root): 
            for file in files:
                yield path, file

def find_first_match(cache_dir=None, filename=None):
    '''Return the full path of the filename if a match is found
    Else Return False'''
        
    # Do the sanity check first
    #if cache_dir is None or filename is None or os.path.isdir(cache_dir) is False:
    if cache_dir is None:
        return False
    elif filename is None:
        return False
    elif os.path.isdir(cache_dir) is False:
        return False
    else:
        for path, file in files(cache_dir): 
            if file == filename:
                return os.path.join(path, file)
        return False


def stripper(item):
    '''Strips extra characters from "item".
    Breaks "item" into:
    url - The URL
    file - The actual package file
    size - The file size
    checksum - The checksum string
    and returns them.'''

    item = item.split(' ')
    url = string.rstrip(string.lstrip(''.join(item[0]), chars="'"), chars="'")
    file = string.rstrip(string.lstrip(''.join(item[1]), chars="'"), chars="'")
    size = int(string.rstrip(string.lstrip(''.join(item[2]), chars = "'"), chars="'"))
    #INFO: md5 ends up having '\n' with it.
    # That needs to be stripped too.
    checksum = string.rstrip(string.lstrip(''.join(item[3]), chars = "'"), chars = "'")
    checksum = string.rstrip(checksum, chars = "\n")

    return url, file, size, checksum

def sha256(data):
    """ Get the data and compute a sha256 hash digest """

    hash = hashlib.sha256()
    hash.update(data.read())
    return hash.hexdigest()

def md5(data):
    """ Get the data and compute a md5 hash digest """

    hash = hashlib.md5.new()
    hash.update(data.read())
    return hash.hexdigest()

def HashMessageDigestAlgorithms(checksum, hash_type, file):
    """ Get the file, the hash type and the checksum and check if it is valid """

    data = open(file, "rb")
    if hash_type == "sha256":
        hash = sha256(data)
    elif hash_type == "md5":
        hash = md5(data)
    else:
        hash = None

    if hash == checksum:
        return True

    return False

def CheckHashDigest(file, checksum):
    """ Take a file and the checksum type and compute whether the checksum is correct or not """

    type = checksum.split(":")[0]
    type=type.lower()
    checksum=checksum.split(":")[1]
    return HashMessageDigestAlgorithms(checksum, type, file)


def download_from_web(url, file, download_dir, notification):
    '''url = url to fetch
    file = file to save to
    donwload_dir = download path'''
    
    socket.setdefaulttimeout(30)
    
    try:
        thread_name = threading.currentThread().getName()
        block_size = 4096
        i = 0
        counter = 0
        size_done = 0
        
        os.chdir(download_dir)
        temp = urllib2.urlopen(url)
        headers = temp.info()
        size = int(headers['Content-Length'])
        data = open(file,'wb')

        socket_counter = 0
        while i < size:
            socket_timeout = None
            try:
                data.write (temp.read(block_size))
            except socket.timeout, timeout:
                socket_timeout = True
                socket_counter += 1
            except socket.error, error:
                socket_timeout = True
                socket_counter += 1
            if socket_counter == SOCKET_TIMEOUT_RETRY:
                #errfunc(101010, "Max timeout retry count reached. Discontinuing download.\n", url)
                
                # Clean the half downloaded file.
                os.unlink(file)
                return False
            
            if socket_timeout is True:
                #errfunc(10054, "Socket Timeout. Retry - %d\n" % (socket_counter) , url)
                continue

            size_done += min(block_size, size - i)
            size_done = min(size_done, size)
            increment = min(block_size, size - i)
            i += block_size
            counter += 1
            notification.current_file_progress(thread_name, file, size, size_done)
        
        data.close()
        temp.close()
        return True
    #FIXME: Find out optimal fix for this exception handling
    except OSError, (errno, strerror):
        errfunc(errno, strerror, download_dir)
    except urllib2.HTTPError, errstring:
        errfunc(errstring.code, errstring.msg, url)
    except urllib2.URLError, errstring:
        #INFO: Weird. But in urllib2.URLError, I noticed that for
        # error type "timeouts", no errno was defined.
        # errstring.errno was listed as None 
        # In my tests, wget categorized this behavior as:
        # 504: gateway timeout
        # So I am doing the same here.
        #if errstring.errno is None:
        #    errfunc(504, errstring.reason, url)
        #else:
        #    errfunc(errstring.errno, errstring.reason, url)
        pass
    except IOError, e:
        if hasattr(e, 'reason'):
            log.err("%s\n" % (e.reason))
        if hasattr(e, 'code') and hasattr(e, 'reason'):
            #errfunc(e.code, e.reason, file)
            pass
    except socket.timeout:
        #errfunc(10054, "Socket timeout.\n", url)
        pass