# -*- coding: utf-8 -*-

import os
import os.path
import sys
import tempfile
from decimal import Decimal

cwd = os.getcwd()
parent_path = os.path.dirname(cwd)
sys.path.append(parent_path)

from apt_offline2_core.download import download

from apt_offline2_core.include import *

from apt_offline2_core.logger import Log

import apt_offline2_core.utils as utils

log = Log(True,True)

class Notifier(INotify):
    def current_file_progress(self, thread_name, filename, total_size, size_downloaded):
        """
        Gives the progress of the current file
        
        This method gives the name of the currently downloaed file, the
        total size of the file and the size of file downloaded
        """
        #print("Threadname: %s | File: %s | Total: %s | Done: %s \n" %(thread_name, filename, total_size, size_downloaded))
        pass

    def set_total_items(self, items_count):
        """
        Sets the total number of items to be downloaded
        """
        self.total_count = items_count
        self.downloaded = 0
        print("Total count: %s\n" %(items_count))


    def increment_download(self, file_name):
        """
        Adds one to the total number of downloaded items
        """
        self.downloaded += 1
        print("One more downloaded: %s | Total adds to: %s/%s\n" %(file_name, self.downloaded, self.total_count))
        
    
    
    def set_total_download_size(self, total_size):
        """
        Tells us the total size which is to be downloaded
        """
        self.total_data_size = total_size
        self.total_downloaded = 0
        print("Total size to download: %s\n" %(utils.humanize_file_size(total_size/Decimal(1000))))
    
    
    def add_downloaded_size(self, size_downloaded):
        """
        Tells us the size downloaded which needs to be incremented
        """
        
        self.total_downloaded += int(size_downloaded)
        print("More downloaded: %s/%s \n" %( utils.humanize_file_size(self.total_downloaded/Decimal(1000)), utils.humanize_file_size(self.total_data_size/Decimal(1000)) ))
    
notify = Notifier()
cache_dir = os.path.join(tempfile.gettempdir(),"foo")

download(   "/tmp/install_packages_only_no_target", # The signature file \
            None,  # Can be None. If None, then tempdir is used \
            cache_dir , # cache_dir Has to be provided \
            True, # Yes, for timebeing disable md5 check \
            2, # No of threads - 2 \
            None, # Bundle file is none. Files wont be archived \
            1000, # Socket timeout - 1000 ms \
            None, # no bug management\
            notify, # The instance of the notification object \
            log # The instance of the logger \
            )
