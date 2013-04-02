# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 08:09:41 2012

@author: pokeeffe
"""

__version_info__ = (0, 1, '20130401')
__version__ = '.'.join(str(x) for x in __version_info__)

from copy import copy


paths = {
    # these paths are generally only good for the workstation in Dana lab
    # housing the share server; they are for the scripts' benefit anyway
    'home' : r'C:\SHARES\proj\2011_REACCH',
    'downloads' : r'C:\Campbellsci\Loggernet',
    'cf_card' : r'D:', 
    'sd_card' : r'F:', 
    'scriptlogs' : r'C:\SHARES\proj\2011_REACCH\scripts\logs',
    # network services (http, ftp, sftp, ...) 
    'nethome' : r'/proj/2011_REACCH/'}
# be sure to substitute the 4-char site code for %s
paths['telemetry'] = paths['home'] + r'tower_%s\L0_telemetry'
paths['rawbinary'] = paths['home'] + r'tower_%s\L0_raw_binary'
paths['rawascii'] = paths['home'] + r'tower_%s\L0_raw_ascii'
paths['stddaily'] = paths['home'] + r'tower_%s\L0_std_daily'


class Site(object):
    """Represent an objective 2 monitoring site"""
    
    def __init__(self, name, code, serial_num, local_IP=None, remote_IP=None):
        """Return new instance of the Site class
        
        Args:
            name: str
                full name of the field site as a string                
            code: str
                four-character unique designation for the site
            serial_num: int
                serial number of the datalogger at the site as integer
            
        Keyword args:
            local_IP: str
                IP address of the datalogger's ethernet adapater 
            remote_IP: str
                IP address of the broadband modem at the site
            
        Returns: new instance of the FieldSite class
        """
        self.name = name
        self.code = str(code).upper()
        self.serial_num = int(serial_num)
        self.local_IP = local_IP
        self.remote_IP = remote_IP
        self.SN = self.serial_num

"""Premade site objects available upon import"""        
cfnt = Site('Cook Farm no-till',
            'CFNT',
            6034,
            '192.168.174.30',
            '123.456.789.012')
lind = Site('Lind Dryland Research Station',
            'LIND',
            6035,'192.168.174.31',
            '123.456.789.012')
cfct = Site('Cook Farm conventional till',
            'CFCT',
            6503,
            '192.168.174.32',
            '123.456.789.012')
mmtn = Site('Moscow Mountain',
            'MMTN',
            6504,
            '192.168.174.33',
            '123.456.789.012')

site_list = [cfnt, lind, cfct, mmtn]
"""List of Site objects to iterate through"""

site_codes = [x.code for x in site_list]
"""List of four-character site codes"""

site_SNs = [x.SN for x in site_list]
"""List of serial numbers at the sites"""

code2sn = dict([[x.code,x.SN] for x in site_list])
"""Dictionary to look up serial number from site code"""

sn2code = dict([[x.SN,x.code] for x in site_list])
"""Dictionary to look up site code from serial number"""

code2site = {s.code : s for s in site_list}
"""Dictionary to get Site objects based on string site code"""


    
                    








