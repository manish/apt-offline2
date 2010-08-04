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

class CreateSignature(unittest.TestCase):
    
    def setUp(self):
        self.log = Log(True,True)

    def test_update_only_success(self):
        """ Only upgrade the system"""
        
        self.assertTrue(create_signature("/tmp/update_only_success", True, False, None, None, None, None, False, self.log))


    def test_upgrade_only_correct_type(self):
        """ Only update the system with type update"""
        
        self.assertTrue(create_signature("/tmp/upgrade_only_correct_type", False, True, "upgrade" , None, None, None, False, self.log))


    def test_upgrade_only_wrong_type(self):
        """ Try updating the system with wrong update type """
        
        self.assertRaises(UpgradeTypeInvalidError, create_signature,"/tmp/upgrade_only_wrong_type", False, True, "blah" , None, None, None, False, self.log)


    def test_install_packages_only_no_target(self):
        """ Install Package without setting the target """
        
        self.assertTrue(create_signature("/tmp/install_packages_only_no_target", False, False, None , ["wvdial", "alien"], None, None, False, self.log))


    def test_install_packages_only_target(self):
        """ Install Package with setting the target """
        
        self.assertTrue(create_signature("/tmp/install_packages_only_target", False, False, None , ["wvdial", "alien"], None, "lucid", False, self.log))
        
        
    def test_install_src_packages_only_no_target_nobuildeps(self):
        """ Install Source Package without setting the target without specifying build-deps"""
        
        self.assertTrue(create_signature("/tmp/install_src_packages_only_no_target_nobuildeps", False, False, None , None, ["wvdial", "alien"], None, False, self.log))


    def test_install_src_packages_only_target_nobuildeps(self):
        """ Install Source Package with setting the target without specifying build-deps"""
        
        self.assertTrue(create_signature("/tmp/install_src_packages_only_target_nobuildeps", False, False, None , None, ["wvdial", "alien"], "lucid", False, self.log))


    def test_install_src_packages_only_no_target_buildeps(self):
        """ Install Source Package without setting the target with specifying build-deps"""
        
        self.assertTrue(create_signature("/tmp/install_src_packages_only_no_target_buildeps", False, False, None , None, ["wvdial", "alien"], None, True, self.log))


    def test_install_src_packages_only_target_buildeps(self):
        """ Install Source Package with setting the target with specifying build-deps"""
        
        self.assertTrue(create_signature("/tmp/install_src_packages_only_target_buildeps", False, False, None , None, ["wvdial", "alien"], "lucid", True, self.log))
        

    def test_update_and_upgrade_valid_type(self):
        """ Do both an update and upgrade with valid upgrade type """
        
        self.assertTrue(create_signature("/tmp/update_and_upgrade_valid_type", True, True, "dist-upgrade", None, None, None, False, self.log))

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This test is supposed to be run with superuser priviliges")
    else:
        unittest.main()