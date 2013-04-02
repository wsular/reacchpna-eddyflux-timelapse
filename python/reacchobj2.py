# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 08:09:41 2012

@author: pokeeffe
"""

__version_info__ = (0, 1, '20120917')
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

class FieldSite(object):
    """Represent an objective 2 field site
    
    Class represents an Objective 2 (GHG monitoring) field site of the 
    Regional Approaches to Climate Change project. Defines commonly-used data 
    about each site and define common methods for manipulating that data.
    """
    
    def __init__(self, name, code, serno, local_IP=None, remote_IP=None):
        """Return new instance of the FieldSite class
        
        Args:
            name: full name of the field site as a string
            code: four-character unique designation for the site
            serno: serial number of the datalogger at the site as integer
            
        Keyword args:
            local_IP: IP address of the datalogger's ethernet adapater 
            remote_IP: IP address of the broadband modem at the site
            
        Returns: new instance of the FieldSite class
        
        """
        self._name = name
        self._code = str(code)
        self._sta_serialno = int(serno)
        self._local_IP = local_IP
        self._remote_IP = remote_IP
        
    @property
    def name(self):
        """full name of site"""
        return self._name
        
    @property
    def code(self):
        """four-character unique site designation"""
        return self._code
        
    @property
    def SN(self):
        """serial number of datalogger at site"""
        return self._sta_serialno

    @property
    def local_IP(self):
        """IP address of the datalogger's ethernet adapter"""
        return self._local_IP
        
    @property
    def remote_IP(self):
        """IP address of the broadband modem at the site"""
        return self._remote_IP
    
    @property
    def raw_downloads_dir(self):
        """full path to raw downloads directory"""
        import os
        return os.path.join(home_dir,
                            self.code.upper(),
                            'L0_raw_downloads')

        
cfnt = FieldSite('Cook Farm no-till','CFNT',6034)
lind = FieldSite('Lind Dryland Research Station','LIND',6035)
cfct = FieldSite('Cook Farm conventional till','CFCT',6503)
mmtn = FieldSite('Moscow Mountain','MMTN',6504)

site_list = [cfnt, lind, cfct, mmtn]

site_codes = [x.code for x in site_list]
site_sernos = [x.SN for x in site_list]

code2sn = dict([[x.code,x.SN] for x in site_list])
sn2code = dict([[x.SN,x.code] for x in site_list])

    
                    








