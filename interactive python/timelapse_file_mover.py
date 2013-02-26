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
        raise IOError, 'Could not locate Ant Renamer install path'

def find_batch_file(codestr):
    arbpath = arbloc % codestr
    if not os.path.isfile(arbpath):
        raise IOError, 'Could not locate Ant Renamer batch files'
    return arbpath

def main():
    print splashscreen 
    print 'Source directory: %s \nCounting files...' % srcloc, 
    filelist = os.listdir(srcloc)
    print "%d files found" % len(filelist)
    print """
Where are these files from?
  (1) CFNT  Cook Agronomy Farm, no-till
  (2) LIND  Lind Dryland Research Station
  (3) CFCT  Cook Agronomy Farm, conventional till
  (4) MMTN  Moscow Mountain area site """

    choice = ''
    while not (choice.isdigit() or choice == 'q'):
        choice = raw_input("Choose 1-4 or q to quit: ")
    if choice == 'q':
        import sys
        sys.exit(0)
    
    arb = find_batch_file(_codelist[choice])
    print 'using batch file: ', arb

    print 'put files in: ', dstloc % _codelist[choice]

    raw_input('Press any key to exit...')

if __name__ == '__main__':
    main()
