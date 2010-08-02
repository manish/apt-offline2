# -*- coding: utf-8 -*-

supported_platforms = ["Linux", "GNU/kFreeBSD", "GNU"]

upgrade_types = [ "upgrade", "dist-upgrade", "dselect-upgrade"]

apt_update_target_path = '/var/lib/apt/lists/partial'
apt_update_final_path = '/var/lib/apt/lists/'
apt_package_target_path = '/var/cache/apt/archives/'