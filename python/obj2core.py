# -*- coding: utf-8 -*-
"""
Contains common directories, names, variables, etc. for REACCH-related
scripts.

@author: pokeeffe
@version: 0.20120914
"""

#import csifileio as csi


paths = {'homeDir'     : r'C:\DATA\REACCH',
         'downloadDir' : r'C:\Campbellsci\Loggernet',
         'cardDir'     : r'D:',
         'DL_sync_log' : r'C:\DATA\_admin\reacch_logs\downloads_sync_log.txt'}
           

class CFNT():
    siteName = 'Cook Farm no-till'
    siteCode = 'CFNT'
    stationID = 6034
    dirs = {'downloads' : paths['homeDir']+'\CFNT\L0_raw_downloads',
            'cardfiles' : paths['homeDir']+'\CFNT\L0_raw_binary' }
    
class LIND():
    siteName = 'Lind Dryland Research Station'
    siteCode = 'LIND'
    stationID = 6035
    dirs = {'downloads' : paths['homeDir']+'\LIND\L0_raw_downloads',
            'cardfiles' : paths['homeDir']+'\LIND\L0_raw_binary' }
    
class CFCT():
    siteName = 'Cook Farm conventional till'
    siteCode = 'CFCT'
    stationID = 6503
    dirs = {'downloads' : paths['homeDir']+'\CFCT\L0_raw_downloads',
            'cardfiles' : paths['homeDir']+'\CFCT\L0_raw_binary' }
    
class MMTN():
    siteName = 'Moscow Mountain Road'
    siteCode = 'MMTN'
    stationID = 6504
    dirs = {'downloads' : paths['homeDir']+'\MMTN\L0_raw_downloads',
            'cardfiles' : paths['homeDir']+'\MMTN\L0_raw_binary' }


siteList = [ CFNT(), LIND(), CFCT(), MMTN() ]
siteBySN = dict([[x.stationID,x] for x in siteList])
siteByCode = dict([[x.siteCode,x] for x in siteList])

siteCodes = [x.siteCode for x in siteList]
siteSNs = [x.stationID for x in siteList]

code2id = dict([[x.siteCode,x.stationID] for x in siteList])
id2code = dict([[x.stationID,x.siteCode] for x in siteList])

"""
def archivedCardFileName(csiTOB3obj):
    \""" return filename generated from header metadata\"""
    if not isinstance(csiTOB3obj, csi.TOB3):
        raise InvalidFileType('Not a Campbellsci TOB3 file')
    sn = csiTOB3obj.station['serialno']
    try:
        site = siteBySN[sn]
        path = site.dirs['cardfiles']
        ts = csiTOB3obj.program['createdat']
        fmtts = ts.isoformat(sep='.').replace(':','').replace('-','')[:-2]
        table = csiTOB3obj.table['name']
        prefix = id2code[sn]+'_'+fmtts+'_'
        return path+'\\'+prefix+table+'.dat'
    except KeyError:
        raise NotWithREACCH        
      """
  
class InvalidFileType(Exception):
    pass

class NotWithREACCH(Exception):
    pass