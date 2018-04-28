#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   flags.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

from bitflags import (
    BitFlags,
)


class IFF(BitFlags):

    names = (
       'UP',
       'BROADCAST',
       'DEBUG',
       'LOOPBACK',
       'POINTOPOINT',
       'NOTRAILERS',
       'RUNNING',
       'NOARP',
       'PROMISC',
       'ALLMULTI',
       'MASTER',
       'SLAVE',
       'MULTICAST',
       'PORTSEL',
       'AUTOMEDIA',
       'DYNAMIC',
       'LOWER_UP',
       'DORMANT',
       'ECHO',
    )
