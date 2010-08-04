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

class InstallSourcePackages(unittest.TestCase):

    def setUp(self):
        self.log = Log(True,True)
        self.target = "lucid"

    def test_install_source_packages_notarget_success(self):
        """ Install packages without Target set"""
        
        self.assertTrue(install_source_packages("/tmp/install_source_packages_no_target", ["wvdial"], None, False, self.log))

    def test_install_source_packages_target_success(self):
        """ Install packages with Target Set"""
        
        self.assertTrue(install_source_packages("/tmp/install_source_packages_target", ["wvdial"], self.target, False, self.log))

    def test_install_source_packages_notarget_srcbuilddep_success(self):
        """ Install src build deps without Target set"""
        
        self.assertTrue(install_source_packages("/tmp/src_build_dep_no_target", ["wvdial"], None, True, self.log))

    def test_install_source_packages_target_srcbuilddep_success(self):
        """ Install src build deps with Target Set"""
        
        self.assertTrue(install_source_packages("/tmp/src_build_dep_target", ["wvdial"], self.target, True, self.log))


if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This test is supposed to be run with superuser priviliges")
    else:
        unittest.main()