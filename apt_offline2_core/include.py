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