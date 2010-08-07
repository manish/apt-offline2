# -*- coding: utf-8 -*-

supported_platforms = ["Linux", "GNU/kFreeBSD", "GNU"]

upgrade_types = [ "upgrade", "dist-upgrade", "dselect-upgrade"]

apt_update_target_path = '/var/lib/apt/lists/partial'
apt_update_final_path = '/var/lib/apt/lists/'
apt_package_target_path = '/var/cache/apt/archives/'


Python_2_5 = True
try:
        import hashlib
except ImportError:
        Python_2_5 = False


class IDownloader:
    """
    Creates a generic class interface. The methods needs to be
    overloaded so that it can be used
    """
    
    def current_file_progress(filename, total_size, size_downloaded):
        """
        Gives the progress of the current file
        
        This method gives the name of the currently downloaed file, the
        total size of the file and the size of file downloaded
        """
        
        pass
    
    def items_downloaded(total_items, downloaded_items):
        """
        Tells us the no of files downloaded out of the total
        """
        
        pass
    
    def size_download_progress(total_size, current_download_size):
        """
        Tells us the total size whicj is to be downloaded and the current 
        amount which has been downloaded
        """
        pass