# -*- coding: utf-8 -*-

import platform
import os
import string
import hashlib

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
