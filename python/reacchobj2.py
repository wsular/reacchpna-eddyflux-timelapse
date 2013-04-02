# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 08:09:41 2012

@author: pokeeffe
"""

__version_info__ = (0, 1, '20120917')
__version__ = '.'.join(str(x) for x in __version_info__)

home_dir = r'C:\DATA\REACCH'
download_dir = r'C:\Campbellsci\Loggernet'
card_dir = r'D:'

log_paths = {'pushed_dls' : r'C:\DATA\_admin\reacch_logs\downloads_sync_log.txt',
             'push_test'  : r'C:\DATA\_admin\reacch_logs\downloads_sync_test.txt'}


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

    
                    








