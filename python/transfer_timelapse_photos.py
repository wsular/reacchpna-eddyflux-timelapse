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

from glob import glob

from definitions.sites import site_list
from definitions.paths import SD_DRIVE, TIMELAPSE_PHOTO_DIR
from definitions.version import __version__

RC_NOSRCDIR = 1
RC_NOFILES = 2
RC_NOANTEXE= 3
RC_NOBATCH = 4
RC_ANTERR = 5
RC_CPYERR = 6
RC_ENVERR = 7

splashscreen = """\
=========================================================
=        Timelapse camera photo transfer utility        =
=                                                       =
=  Regional Approaches to Climate Change | Objective 2  =
=               Washington State University             =
=========================================================
"""
srcloc = os.path.join(SD_DRIVE, 'DCIM', '100_WSCT')
dstloc = TIMELAPSE_PHOTO_DIR
antexe = r'"C:\Program Files (x86)\Ant Renamer\Renamer.exe"'
if not os.path.isfile(antexe.strip('"')):
    antexe = antexe.replace(' (x86)','') # try x86 XP-style
    if not os.path.isfile(antexe.strip('"')):
        antexe = antexe.replace(' Files','s') # try Win7 style
        if not os.path.isfile(antexe.strip('"')):
            print 'Could not locate Ant Renamer in default locations'
            print antexe
            raw_input('Press <enter> to exit...')
            sys.exit(RC_NOANTEXE)
antarg = ' -b "{arb}" -afr "{src}" -g -x' #batch file name, source dir
cpyexe = r'xcopy "{src}" "{dst}\" /C /K /V /Q /X /Y' #src, dest
    # XCOPY source <destination>
    #   /C      continue, even on error
    #   /K      copies attributes (default is reset)
    #   /V      verify each new file
    #   /Q      do not display file names while copying
    #   /X      copies file audit settings (incl ownership/ACL)
    #   /Y      suppresses prompt to overwrite existing file
ejtcmd = r'"usb_disk_eject.exe" /REMOVELETTER %s' # srcloc drive letter

_codelist = dict((str(i+1),s.code) for (i,s) in enumerate(site_list))

_arbtemplate = """\
<?xml version="1.0" encoding="UTF-8"?>
<AntRenamer Version="2.10.0" Date="2013-02-04">
 <Batch>
  <Exif Mask="{site}_%datetimeoriginal%%ext%"/>
  <StrRepl Search="-00." Repl="." AllOccurences="-1" CaseSensitive="0" IncludeExt="-1" OnlyExt="0"/>
  <StrRepl Search="-" Repl="" AllOccurences="-1" CaseSensitive="0" IncludeExt="0" OnlyExt="0"/>
  <StrRepl Search=" " Repl="." AllOccurences="-1" CaseSensitive="0" IncludeExt="0" OnlyExt="0"/>
  <ChangeCase Option="3" AfterChars="- .+(" UseLocale="0" IncludeExt="0" OnlyExt="-1"/>
 </Batch>
</AntRenamer>
"""

if __name__ == '__main__':
    if 'nt' not in os.name:
        print 'This application requires a Windows environment.'
        raw_input('Press <enter> to exit...')
        sys.exit(RC_ENVERR)
    if len(sys.argv) > 1:
        srcloc = sys.argv[1]

    print splashscreen
    print 'Source directory: %s \nCounting files...' % srcloc,
    try:
        filelist = os.listdir(srcloc)
    except WindowsError as err:
        print 'Warning: no disk found in %s' % os.path.splitdrive(srcloc)[0]
        raw_input('Press <enter> to exit...')
        sys.exit(RC_NOSRCDIR)
    print "%d files found" % len(filelist)
    if len(filelist) == 0:
        print 'Warning: no files were found in %s' % srcloc
        raw_input('Press <enter> to exit...')
        sys.exit(RC_NOFILES)
    print """\nWhere are these files from?"""
    for (i,s) in enumerate(site_list):
        print '  (%d) %s  %s' % (i+1, s.code, s.name)

    choice = ''
    while choice not in _codelist.keys()+['q', 'Q']:
        choice = raw_input("Choose #, <o> to open 1st file, <q> to quit: ")
        if choice.lower() == 'o':
            smpfile = os.path.join(srcloc, filelist[0])
            subprocess.call(smpfile, shell=True)
    if choice.lower() == 'q':
        import sys; sys.exit()

    cpydst = dstloc % {'code' : _codelist[choice]}
    print 'Using target directory: ', cpydst
    confirm = raw_input('Press <enter> to continue or Ctrl+C to abort.')

    try:
        os.makedirs(cpydst)
    except OSError:
        if not os.path.isdir(cpydst):
            raise

    tmpdir = os.path.join(cpydst, 'imgs_to_rename')
    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)

    tmparb = os.path.join(tmpdir, 'renameactions.tmp~')
    #temp file name must not be modified by ant renamer (no dot, dash...)
    with open(tmparb, mode='w') as arbfile:
        arbfile.write(_arbtemplate.format(site=_codelist[choice]))

    print ' * Copying files to temporary destination... ',
    cmd = cpyexe.format(src=srcloc, dst=tmpdir)
    rc = subprocess.check_call(cmd, shell=True)
    if rc:
        print ' Error: Unable to copy files to destination'
        raw_input('Press <enter> to exit...')
        sys.exit(RC_CPYERR)
    # xcopy prints equivalent 'done.' statement to stdout

    #if successful, results of copy cmd ends in "\n " so no preceding space
    print '* Renaming image files...',
    cmd = antexe + antarg.format(arb=os.path.normpath(tmparb), src=tmpdir)
    rc = subprocess.check_call(cmd, shell=True)
    if rc:
        print ' Error: Ant Renamer exited with code %s' % rc
        raw_input('Press <enter> to exit...')
        sys.exit(RC_ANTERR)
    else:
        print 'done.'
    os.remove(tmparb) #delete renamer batch file

    # TODO check if files of same name exist in destination folder b4 copying
    overwrite = False
    confirm = '' #reset to known state
    firstrenamefound = False
    print ' * Moving files to final destination... ',
    for tmppath in glob(os.path.join(tmpdir, '*.*')):
        fname = os.path.basename(tmppath)
        newpath = os.path.normpath(os.path.join(tmpdir, os.path.pardir, fname))
        if os.path.isfile(newpath):
            if not firstrenamefound:
                print '\n' #extra white space to draw attention to prompt
                firstrenamefound = True
            if not overwrite:
                msg = ('File exists at destination ({fname}). Overwrite? '
                       '[Y]es, Yes to [a]ll, else no: ')
                confirm = raw_input(msg.format(fname=fname))

            if overwrite or confirm.lower() in ['y', 'a']:
                os.remove(newpath)
                if confirm.lower() == 'a': overwrite = True
            else:
                continue
        try:
            os.rename(tmppath, newpath)
        except:
            print ' ! Could not move: {name}'.format(name=tmppath)
    if not os.listdir(tmpdir):
        try:
            os.rmdir(tmpdir)
        except OSError:
            print '\n ! Temporary directory emptied but could not be removed'
    else:
        print '\n ! Some files remain in the temporary directory ({dir})'.format(
            dir=os.path.normpath(tmpdir))

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
    sys.exit()
