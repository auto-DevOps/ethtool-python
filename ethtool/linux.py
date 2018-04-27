#!/usr/bin/env python
# -*- encoding=utf8 -*-

'''
FileName:   linux.py
Author:     Fasion Chan
@contact:   fasionchan@gmail.com
@version:   $Id$

Description:

Changelog:

'''

import ctypes
import struct

from collections import (
    OrderedDict,
)
from fcntl import (
    ioctl,
)
from socket import (
    AF_INET,
    SOCK_DGRAM,
    IPPROTO_IP,
    socket,
)

PF_INET = AF_INET


class Ethtool(object):

    SIOCGIFHWADDR = 0x8927
    SIOCETHTOOL = 0x8946

    ETHTOOL_GSET = 0x00000001
    ETHTOOL_GDRVINFO = 0x00000003
    ETHTOOL_GLINK = 0x0000000a

    # Since 4.6
    ETHTOOL_GLINKSETTINGS = 0x0000004c
    ETHTOOL_SLINKSETTINGS = 0x0000004d

    # net/if.h
    IFNAMSIZ = 16

    ETHTOOL_CMD_STRUCT = struct.Struct('3IH6B2IH2BI8B')
    ETHTOOL_CMD_STRUCT_FIELDS = (
        'cmd',
        'supported',
        'advertising',
        'speed',
        'duplex',
        'port',
        'phy_address',
        'transceiver',
        'autoneg',
        'mdio_support',
        'maxtxpkt',
        'maxrxpkt',
        'speed_hi',
        'eth_tp_mdix',
        'eth_tp_mdix_ctrl',
        'ip_advertising',
        'reserved',
    )

    ETHTOOL_DRVINFO_STRUCT = struct.Struct('I32s32s32s32s32s12s5I')
    ETHTOOL_DRVINFO_STRUCT_FIELDS = (
        'cmd',
        'driver',
        'version',
        'fw_version',
        'bus_info',
        'erom_version',
        'reserved2',
        'n_priv_flags',
        'n_stats',
        'testinfo_len',
        'eedump_len',
        'regdump_len',
    )
    ETHTOOL_DRVINFO_STRUCT_STRING_FIELDS = (
        'driver',
        'version',
        'fw_version',
        'bus_info',
        'erom_version',
    )

    ETHTOOL_VALUE_STRUCT = struct.Struct('2I')
    ETHTOOL_VALUE_STRUCT_FIELDS = (
        'cmd',
        'data',
    )

    ETHTOOL_LINK_SETTINGS_STRUCT = struct.Struct('2I7B1b1B3s64s')
    ETHTOOL_LINK_SETTINGS_STRUCT_FIELDS = (
        'cmd',
        'speed',
        'duplex',
        'port',
        'phy_address',
        'autoneg',
        'mdio_support',
        'eth_tp_mdix',
        'eth_tp_mdix_ctrl',
        'link_mode_masks_nwords',
        'reserved',
        #'link_mode_masks',
    )

    ETHTOOL_CMD_ONLY_STRUCT = struct.Struct('I')

    IFREQ_STRUCT = struct.Struct('16s')
    IFREQ_SIOCETHTOOL_STRUCT = struct.Struct('16sP')

    def __init__(self):
        self.s = socket(PF_INET, SOCK_DGRAM, IPPROTO_IP)

    def execute_ethtool_cmd(self, iface_name, cmd):
        encode_handler = getattr(iface_name, 'encode', None)
        if encode_handler is not None:
            iface_name = encode_handler()

        if not isinstance(cmd, ctypes.Array):
            cmd = ctypes.create_string_buffer(cmd, size=len(cmd))
        cmdptr = ctypes.addressof(cmd)
        ifreq = self.IFREQ_SIOCETHTOOL_STRUCT.pack(iface_name, cmdptr)
        ioctl(self.s.fileno(), self.SIOCETHTOOL, ifreq)
        return cmd.raw

    def create_ethtool_cmd_buffer(self, cmd, size):
        return ctypes.create_string_buffer(
            self.ETHTOOL_CMD_ONLY_STRUCT.pack(cmd),
            size=size,
        )

    def fetch_ethtool_cmd_struct(self, iface_name, cmd, struct):
        cmd = self.create_ethtool_cmd_buffer(
            cmd=cmd,
            size=struct.size,
        )

        return self.execute_ethtool_cmd(iface_name=iface_name, cmd=cmd)

    def fetch_ethtool_cmd(self, iface_name, cmd, struct, fields):
        cmd = self.fetch_ethtool_cmd_struct(
            iface_name=iface_name,
            cmd=self.ETHTOOL_GSET,
            struct=self.ETHTOOL_CMD_STRUCT,
        )

        values = struct.unpack(cmd)

        return OrderedDict(zip(fields, values))

    def fetch_settings(self, iface_name):
        settings = self.fetch_ethtool_cmd(
            iface_name=iface_name,
            cmd=self.ETHTOOL_GSET,
            struct=self.ETHTOOL_CMD_STRUCT,
            fields=self.ETHTOOL_CMD_STRUCT_FIELDS,
        )

        speed_hi = settings.pop('speed_hi')
        if speed_hi is not None:
            settings['speed'] = settings['speed'] | (speed_hi << 16)

        return settings

    def fetch_link_settings(self, iface_name):
        cmd = self.create_ethtool_cmd_buffer(
            cmd=self.ETHTOOL_GLINKSETTINGS,
            size=self.ETHTOOL_LINK_SETTINGS_STRUCT.size,
        )

        cmd = self.execute_ethtool_cmd(iface_name=iface_name, cmd=cmd)

        values = self.ETHTOOL_LINK_SETTINGS_STRUCT.unpack(cmd)
        data = dict(zip(self.ETHTOOL_LINK_SETTINGS_STRUCT_FIELDS, values))
        link_mode_masks_nwords = data['link_mode_masks_nwords']
        print('link_mode_masks_nwords', link_mode_masks_nwords)

    def fetch_drvinfo(self, iface_name):
        cmd = self.create_ethtool_cmd_buffer(
            cmd=self.ETHTOOL_GDRVINFO,
            size=self.ETHTOOL_DRVINFO_STRUCT.size,
        )

        cmd = self.execute_ethtool_cmd(iface_name=iface_name, cmd=cmd)

        values = self.ETHTOOL_DRVINFO_STRUCT.unpack(cmd)

        drvinfo = OrderedDict(zip(self.ETHTOOL_DRVINFO_STRUCT_FIELDS, values))

        for field in self.ETHTOOL_DRVINFO_STRUCT_STRING_FIELDS:
            drvinfo[field] = drvinfo[field].rstrip(b'\0')

        return drvinfo

    def fetch_link_status(self, iface_name):
        cmd = self.ETHTOOL_VALUE_STRUCT.pack(self.ETHTOOL_GLINK, 0)
        cmd = self.execute_ethtool_cmd(iface_name=iface_name, cmd=cmd)
        _, data = self.ETHTOOL_VALUE_STRUCT.unpack(cmd)
        return data == 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.s.close()
        self.s = None
