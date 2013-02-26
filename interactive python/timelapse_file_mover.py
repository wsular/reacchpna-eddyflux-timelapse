# -*- coding: utf-8 -*-
"""Rename photos from timelapse cameras

@author Patrick O'Keeffe <pokeeffe@wsu.edu>
"""

import os
import subprocess

antexe = r'C:\Program Files (x86)\Ant Renamer\renamer.exe'
antarg = '-b "%s" -afr "%s" -g -x' #batch file name, source dir

testloc = r'U:\ectower_data_scripts.git\CFNT timelapse rename batch process.arb'
srcloc = r'F:\DCIM\100_WSCT'


splashscreen = """\
=========================================================
=        Timelapse camera photo transfer utility        =
=                                                       =
=  Regional Approaches to Climate Change | Objective 2  =
=               Washington State University             =
=========================================================

Source directory: %s
Counting files..."""

filelist = os.listdir(srcloc)
print splashscreen % srcloc, "%d files found" % len(filelist)
print """
Where are these files from?
  (1) CFNT  Cook Agronomy Farm, no-till
  (2) LIND  Lind Dryland Research Station
  (3) CFNT  Cook Agronomy Farm, conventional till
  (4) MMTN  Moscow Mountain area site """

choice = ''
while not (choice.isdigit() or choice == 'q'):
    choice = raw_input("Choose 1-4 or q to quit: ")

print 'you choose %s' % choice

raw_input('Press any key to exit...')

