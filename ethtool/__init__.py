#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   __init__.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import platform

os = platform.system().lower()


if os == 'linux':
    from .linux import Ethtool
else:
    Ethtool = None
