# -*- coding: utf-8 -*-
"""
Created on Mon Dec 09 14:57:26 2013

@author: pokeeffe
"""

import logging
import os
import os.path as osp

from Tkinter import *
from tkMessageBox import askyesno, showerror
from tkFileDialog import askdirectory

from definitions.fileio import (set_readonly_attr,
                                set_archive_attr)
from definitions.paths import SD_DRIVE, TIMELAPSE_PHOTO_DIR
from definitions.version import __version__


try:
    import exifread
except ImportError:
    raise
    #### try to install exifread here or try an ant renamer alternative?


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


_prog_title_ = 'Timelapse Image Transfer Utility'


class SDTransferUtility(Frame):
    """GUI program for transferring timelapse images from SD cards"""

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(padx=5, pady=5, expand=YES, fill=BOTH)

        self.__srcdir = StringVar()
        self.__set_output_RO = IntVar(value=1)
        self.__set_output_A = IntVar(value=1)

        self.__setup_gui()


    def __setup_gui(self):
        """Build up GUI from widgets"""
        topfrm = Frame(self)
        topfrm.pack(expand=NO, fill=X, side=TOP)
        Label(topfrm, text=_prog_title_).pack(side=TOP)

        srcfrm = LabelFrame(topfrm, padx=5, pady=5, relief=RIDGE,
                            text='Source File Search')
        srcfld = Entry(srcfrm, textvariable=self.__srch_dir)
        vwsbtn = Button(srcfrm, text='View', command=self.__view_srch_dir)
        refbtn = Button(srcfrm, text='Refresh', command=self.__refresh_src)
        srcbtn = Button(srcfrm, text='Browse', command=self.__set_srcdir)

        srcfrm.pack(expand=YES, fill=X, side=TOP)
        srcfld.pack(side=LEFT, expand=YES, fill=X, padx=5)
        vwsbtn.pack(side=RIGHT, padx=3)
        refbtn.pack(side=RIGHT, padx=3)
        srcbtn.pack(side=RIGHT, padx=3)


    def __set_srcdir(self):
        """Browse to source directory"""
        choice = askdirectory(title='Select source directory',
                              mustexist=True)
        if choice and osp.isdir(choice):
            self.__srcdir.set(choice.replace('/','\\'))
            refresh = askyesno(title='Refresh source directory',
                           message='Source directory has changed. Refresh?')
            if refresh:
                self.__refresh_src()


    def __refresh_src(self):
        """Search for files in source directory"""

        print 'refreshing'


    def __view_srcdir(self):
        """Open source directory in file explorer"""
        source = self.__srcdir.get()
        if not source:
            return False
        if not osp.isdir(source):
            showerror(title='View error',
                  message=('Error occurred, could not open specified '
                           'directory: %s') % source)
        else:
            os.startfile(osp.abspath(source))

    #def _


if __name__=='__main__':
    root = Tk()
    root.title(_prog_title_)
    SDTransferUtility().mainloop()

