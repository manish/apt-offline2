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

class UpgradeSuccess(unittest.TestCase):

    def setUp(self):
        self.log = Log(True,True)

    def test_upgrade_success(self):
        """ Run upgrade successfully """

        self.assertTrue(upgrade_upgrade("/tmp/upgrade", self.log))

    def test_dist_upgrade_success(self):
        """ Run dist-upgrade successfully """

        self.assertTrue(upgrade_dist_upgrade("/tmp/dist_upgrade", self.log))

    def test_dselect_upgrade_success(self):
        """ Run dselect-upgrade successfully """

        self.assertTrue(upgrade_dselect_upgrade("/tmp/dselect_upgrade", self.log))
        
    def test_upgrade(self):
        """ Call the main upgrade method """
        
        self.assertTrue(upgrade("/tmp/main_upgrade", "upgrade", self.log))

    def test_upgrade_invalid_type(self):
        """ Provide an invalid upgrade type """
        
        self.assertRaises(UpgradeTypeInvalidError, upgrade, "/tmp/foo", "blah", self.log)

if __name__ == '__main__':
    if os.geteuid() != 0:
        print("This test is supposed to be run with superuser priviliges")
    else:
        unittest.main()
