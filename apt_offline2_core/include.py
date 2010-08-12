# -*- coding: utf-8 -*-

supported_platforms = ["Linux", "GNU/kFreeBSD", "GNU"]

upgrade_types = [ "upgrade", "dist-upgrade", "dselect-upgrade"]

apt_update_target_path = '/var/lib/apt/lists/partial'
apt_update_final_path = '/var/lib/apt/lists/'
apt_package_target_path = '/var/cache/apt/archives/'

import os
import threading
import zipfile
import bz2
import gzip

Python_2_5 = True
try:
        import hashlib
except ImportError:
        Python_2_5 = False

SOCKET_TIMEOUT_RETRY = 5

class INotify:
    """
    Creates a generic class interface. The methods needs to be
    overloaded so that it can be used
    """
    
    def current_file_progress(self, thread_name, filename, total_size, size_downloaded):
        """
        Gives the progress of the current file
        
        This method gives the name of the currently downloaed file, the
        total size of the file and the size of file downloaded
        """
        pass


    def set_total_items(self, items_count):
        """
        Sets the total number of items to be downloaded
        """
        pass


    def increment_download(self, file_name):
        """
        Adds one to the total number of downloaded items
        """
        pass
    
    
    def set_total_download_size(self, total_size):
        """
        Tells us the total size which is to be downloaded
        """
        pass
    
    
    def add_downloaded_size(self, size_downloaded):
        """
        Tells us the size downloaded which needs to be incremented
        """
        pass
    
    def failed_packages(self, package_name, package_verion):
        """
        Tells us the package name and the version of the packages which failed_packages
        """
        pass



class Archiver:
    def __init__( self, lock=None ):
        if lock is None or lock != 1:
            self.ZipLock = False
            self.lock = False
        else:
            self.ZipLock = threading.Lock()
            self.lock = True
    
    def TarGzipBZ2_Uncompress( self, SourceFileHandle, TargetFileHandle ):
        try:
            TargetFileHandle.write( SourceFileHandle.read() )
        except EOFError:
            pass
        except IOError:
            #TODO: What constitutes an "IOError: invalid data stream" ???
            # Couldn't find much from the docs. Needs to be investigated.
            
            # Answer:
            # A BZ2 file corruption is seen during file creation only.
            # Perhaps it has to do with the bad netowrk, loss of packets et cetera
            # The safest bet at the moment is to simply discard such files, which were
            # downloaded in damaged form.
            return False
        return True
    
    def compress_the_file( self, zip_file_name, files_to_compress ):
        '''Condenses all the files into one single file for easy transfer'''

        try:
            if self.lock:
                self.ZipLock.aqcuire( True )
            filename = zipfile.ZipFile( zip_file_name, "a" )
        except IOError:
           #INFO: By design zipfile throws an IOError exception when you open
           # in "append" mode and the file is not present.
           filename = zipfile.ZipFile( zip_file_name, "w" )
        finally: #Supported from Python 2.5 ??
            filename.write( files_to_compress, os.path.basename( files_to_compress ), zipfile.ZIP_DEFLATED )
            filename.close()
            try:
                if self.lock:
                    self.ZipLock.release()
            except:
               pass

            return True

    def decompress_the_file( self, archive_file, target_file, archive_type ):
        '''Extracts all the files from a single condensed archive file'''
        if archive_type == "bzip2" or archive_type == "gzip":
            if archive_type == "bzip2":
                try:
                    read_from = bz2.BZ2File( archive_file, 'r' )
                except IOError:
                    return False
            elif archive_type == "gzip":
                try:
                    read_from = gzip.GzipFile( archive_file, 'r' )
                except IOError:
                    return False
            else:
                return False
                    
            try:
                write_to = open ( target_file, 'wb' )
            except IOError:
                return False
            
            if self.TarGzipBZ2_Uncompress( read_from, write_to ) != True:
                #INFO: Return False for the stream that failed.
                return False
            write_to.close()
            read_from.close()
            return True
        elif archive_type == "zip":
            #INFO: We will never reach here.
            # Package data from Debian is usually served only in bz2 or gzip format
            # Plain zip is something we might never see.
            # Leaving it here just like that. Maybe we will use it in the future

            # FIXME: This looks odd. Where are we writing to a file ???
            try:
                zip_file = zipfile.ZipFile( archive_file, 'r' )
            except IOError:
                return False
            #FIXME:
            for filename in zip_file.namelist():
                try:
                    write_to = open ( filename, 'wb' )
                except IOError:
                    return False
                write_to.write(zip_file.read(filename) )
                write_to.flush()
                write_to.close()
            zip_file.close()
            return True
        else:
            return False