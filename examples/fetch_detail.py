#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   fetch_detail.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import sys

from ethtool.linux import (
    Ethtool,
)

if len(sys.argv) > 1:
    iface_name = sys.argv[1]
else:
    iface_name = 'eth0'

with Ethtool() as ethtool:
    print(ethtool.fetch_settings(iface_name=iface_name))
    print('')

    print(ethtool.fetch_drvinfo(iface_name=iface_name))
    print('')

    print(ethtool.fetch_link_status(iface_name=iface_name))
    print('')
