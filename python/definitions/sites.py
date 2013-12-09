# -*- coding: utf-8 -*-
"""Objects representing field sites

    Typically just import site_list to iterate over:

        from definitions.sites import site_list

@author: Patrick O'Keeffe <pokeeffe@wsu.edu>
"""

from definitions.version import __version__


class cfnt():
    name = 'Cook Agronomy Farm no-till'
    code = 'CFNT'
    serial_num = '6034'
    local_ip = ('192.168.174.33', '255.255.255.0')
    remote_ip = ('166.139.116.107', '255.255.255.0')

class lind():
    name = 'Lind Dryland Research Station'
    code = 'LIND'
    serial_num = '6035'
    local_ip = ('192.168.174.32', '255.255.255.0')
    remote_ip = ('166.140.215.10', '255.255.255.0')

class cfct():
    name = 'Cook Agronomy Farm conventional till'
    code = 'CFCT'
    serial_num = '6503'
    local_ip = ('192.168.174.34', '255.255.255.0')
    remote_ip = ('166.140.215.11', '255.255.255.0')

class mmtn():
    name = 'Moscow Mountain high rainfall'
    code = 'MMTN'
    serial_num = '6504'
    local_ip = ('192.168.174.35', '255.255.255.0')
    remote_ip = ('166.140.215.12', '255.255.255.0')

class mslk():
    name = 'Moses Lake irrigated'
    code = 'MSLK'
    serial_num = '6505'
    local_ip = ('192.168.174.36', '255.255.255.0')
    remote_ip = ('166.154.195.59', '255.255.255.0')


site_list = [cfnt, lind, cfct, mmtn, mslk]


sn2code = dict([[site.serial_num, site.code] for site in site_list])


