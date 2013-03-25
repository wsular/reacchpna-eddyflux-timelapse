# -*- coding: utf-8 -*-
"""Rename photos from timelapse cameras

Exit codes
    0   No errors
    1   No source directory found
    2   No files found in source directory
    3   Ant Renamer executable not found
    4   Ant Renamer batch file not found
    5   An error occurred running Ant Renamer
    6   An error occurred running xcopy
    7   Run outside Windows environment

@author Patrick O'Keeffe <pokeeffe@wsu.edu>
"""

import os
import subprocess
import sys

splashscreen = """\
=========================================================
=        Timelapse camera photo transfer utility        =
=                                                       =
=  Regional Approaches to Climate Change | Objective 2  =
=               Washington State University             =
=========================================================
"""
srcloc = r'F:\DCIM\100_WSCT'
dstloc = r'C:\SHARES\proj\2011_REACCH\tower_%s\photos_timelapsecam'
antexe = r'"C:\Program Files (x86)\Ant Renamer\renamer.exe"'
antarg = ' -b "%s" -afr "%s" -g -x' #batch file name, source dir
arbloc = r'%s timelapse file namer.arb'
cpyexe = r'xcopy "%s" "%s\" /C /K /V /Q /X /Y' #src, dest
    # XCOPY source <destination>
    #   /C      continue, even on error
    #   /K      copies attributes (default is reset)
    #   /V      verify each new file
    #   /Q      do not display file names while copying
    #   /X      copies file audit settings (incl ownership/ACL)
    #   /Y      suppresses prompt to overwrite existing file
ejtcmd = r'"..\bin\usb_disk_eject.exe" /REMOVELETTER %s' # srcloc drive letter

_codelist = {'1' : 'CFNT',
             '2' : 'LIND',
             '3' : 'CFCT',
             '4' : 'MMTN' }

RC_NOERRS = 0
RC_NOSRCDIR = 1
RC_NOFILES = 2
RC_NOANTEXE= 3
RC_NOBATCH = 4
RC_ANTERR = 5
RC_CPYERR = 6
RC_ENVERR = 7

def check_for_ant_renamer():
    if not os.path.isfile(antexe):
        print 'Error: could not locate Ant Renamer installation directory'
        raw_input('Press any key to exit...')
        sys.exit(RC_NOANTEXE)

def find_batch_file(codestr):
    arbpath = arbloc % codestr
    if not os.path.isfile(arbpath):
        print 'Error: could not locate appropriate Ant Renamer batch file'
        raw_input('Press any key to exit...')
        sys.exit(RC_NOBATCH)
    return arbpath


if __name__ == '__main__':
    if 'nt' not in os.name:
        print 'This application requires a Windows environment.'
        raw_input('Press any key to quit...')
        sys.exit(RC_ENVERR)
    if len(sys.argv) > 1:
        srcloc = sys.argv[1]

    print splashscreen
    print 'Source directory: %s \nCounting files...' % srcloc,
    filelist = os.listdir(srcloc)
    print "%d files found" % len(filelist)
    if len(filelist) == 0:
        print 'Warning: no files were found in %s' % srcloc
        raw_input('Press any key to exit...')
        sys.exit(RC_NOFILES)
    print """
Where are these files from?
  (1) CFNT  Cook Agronomy Farm, no-till
  (2) LIND  Lind Dryland Research Station
  (3) CFCT  Cook Agronomy Farm, conventional till
  (4) MMTN  Moscow Mountain area site"""

    choice = ''
    while choice not in ['1', '2', '3', '4', 'q', 'Q']:
        choice = raw_input("Choose 1-4, <o> to open 1st file, <q> to quit: ")
        if choice.lower() == 'o':
            smpfile = os.path.join(srcloc, filelist[0])
            subprocess.call(smpfile, shell=True)
    if choice.lower() == 'q':
        import sys; sys.exit(RC_NOERRS)

    arbfile = find_batch_file(_codelist[choice])
    print '\nUsing batch file: ', arbfile
    cpydst = dstloc % _codelist[choice]
    print 'Target directory: ', cpydst

    confirm = raw_input('Are these settings OK? C=continue, else quit: ')
    if not confirm.strip().lower() == 'c':
        raw_input('Press any key to exit...')
        sys.exit(RC_NOERRS)
    print

    print ' * Renaming image files...',
    cmd = antexe + antarg % (arbfile, srcloc)
    rc = subprocess.check_call(cmd, shell=True)
    if rc:
        print ' Error: Ant Renamer exited with code %s' % rc
        raw_input('Press any key to exit...')
        sys.exit(RC_ANTERR)
    else:
        print 'done.'

    print ' * Copying files to destination... ',
    cmd = cpyexe % (srcloc, cpydst)
    rc = subprocess.check_call(cmd, shell=True)
    if rc:
        print ' Error: Unable to copy files to destination'
        raw_input('Press any key to exit...')
        sys.exit(RC_CPYERR)
    # xcopy prints equivalent 'done.' statement to stdout
    print ' * Finished transferring files.'

    ask = raw_input('\nDelete all files in source directory? Y=yes, else no: ')
    print
    if ask.strip().lower() == 'y':
        filelist = os.listdir(srcloc)
        print ' * Emptying source directory...',
        for file in filelist:
            try:
                os.remove(os.path.join(srcloc, file))
            except WindowsError as err:
                print ' Error: unable to remove %s (%s) ' % (file, err)
        print 'done.'
    else:
        print ' * Source files NOT deleted from card'

    ask = raw_input('\nAttempt to eject source directory? Y=yes, else no: ')
    if ask.strip().lower() == 'y':
        try:
            drive = os.path.splitdrive(srcloc)[0].strip(':')
            subprocess.check_call(ejtcmd % drive, shell=True)
        except subprocess.CalledProcessError as err:
            print 'Unable to eject source drive: %s' % err

    raw_input('Press <enter> to exit...')
