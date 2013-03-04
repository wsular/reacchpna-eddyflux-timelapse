# -*- coding: utf-8 -*-
"""Rename photos from timelapse cameras

@author Patrick O'Keeffe <pokeeffe@wsu.edu>
"""

import os
import subprocess

splashscreen = """\
=========================================================
=        Timelapse camera photo transfer utility        =
=                                                       =
=  Regional Approaches to Climate Change | Objective 2  =
=               Washington State University             =
=========================================================
"""
srcloc = r'F:\DCIM\100_WSCT'
antexe = r'C:\Program Files (x86)\Ant Renamer\renamer.exe'
antarg = '-b "%s" -afr "%s" -g -x' #batch file name, source dir
arbloc = r'..\Ant Renamer batch files\%s timelapse rename batch process.arb'
dstloc = r'C:\SHARES\2011_REACCH\tower_%s\photos_timelapsecam'

_codelist = {'1' : 'CFNT',
             '2' : 'LIND',
             '3' : 'CFCT',
             '4' : 'MMTN' }

def check_for_ant_renamer():
    if not os.path.isfile(antexe):
        print 'Error: could not locate Ant Renamer installation directory'
        raw_input('Press any key to continue...')

def find_batch_file(codestr):
    arbpath = arbloc % codestr
    if not os.path.isfile(arbpath):
        print 'Error: could not locate appropriate Ant Renamer batch file'
        raw_input('Press any key to continue...')
    return arbpath

def main():
    print splashscreen 
    print 'Source directory: %s \nCounting files...' % srcloc, 
    filelist = os.listdir(srcloc)
    print "%d files found" % len(filelist)
    if len(filelist) == 0:
        print 'Warning: no files were found in %s' % srcloc
        raw_input('Press any key to exit...')
        import sys; sys.exit(0)
    print """
Where are these files from?
  (1) CFNT  Cook Agronomy Farm, no-till
  (2) LIND  Lind Dryland Research Station
  (3) CFCT  Cook Agronomy Farm, conventional till
  (4) MMTN  Moscow Mountain area site \n"""

    choice = ''
    while choice not in ['1', '2', '3', '4', 'q', 'Q']:
        choice = raw_input("Choose 1-4, <o> to open 1st file, <q> to quit: ")
        if choice.lower() == 'o':
            smpfile = os.path.join(srcloc, filelist[0])
            subprocess.call(smpfile, shell=True)
    if choice.lower() == 'q':
        import sys; sys.exit(0)
    
    arb = find_batch_file(_codelist[choice])
    print 'using batch file: ', arb

    print 'put files in: ', dstloc % _codelist[choice]

    raw_input('Press any key to exit...')

if __name__ == '__main__':
    main()
