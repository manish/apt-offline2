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

class UpgradeFailure(unittest.TestCase):

    def setUp(self):
        self.log = Log(True,True)

    def test_upgrade_not_root(self):
        """ Fail since the user is not root """
        
        self.assertRaises(NotSuperuserError, upgrade, "/non_root", "upgrade", self.log)


if __name__ == '__main__':
    if os.geteuid() == 0:
        print("This test is supposed to be run without superuser priviliges")
    else:
        unittest.main()
