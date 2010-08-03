# -*- coding: utf-8 -*-
import unittest

import os
import os.path
import sys

cwd = os.getcwd()
parent_path = os.path.dirname(cwd)
sys.path.append(parent_path)

from apt_offline2_core.create_apt_signature import *
from apt_offline2_core.logger import Log
from apt_offline2_core.exceptions import *

class InstallPackages(unittest.TestCase):

    def setUp(self):
        self.log = Log(True,True)

    def test_install_packages_notarget_success(self):
        """ Install packages without Target set"""
        
        self.assertTrue(install_packages("/tmp/install_packages_no_target", ["wvdial"], None, self.log))

    def test_install_packages_target_success(self):
        """ Install packages with Target Set"""
        
        self.assertTrue(install_packages("/tmp/install_packages_target", ["wvdial"], "maverick", self.log))

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This test is supposed to be run with superuser priviliges")
    else:
        unittest.main()