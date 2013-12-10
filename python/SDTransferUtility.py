# -*- coding: utf-8 -*-
"""
Created on Mon Dec 09 14:57:26 2013

@author: pokeeffe
"""

import logging
import os
import os.path as osp

from glob import glob

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

_default_search_string = r'DCIM\*_WSCT\*.jpg'


class SDTransferUtility(Frame):
    """GUI program for transferring timelapse images from SD cards"""

    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(padx=5, pady=5, expand=YES, fill=BOTH)

        self.__srch_dir = StringVar(value=SD_DRIVE) # XXX
        self.__srch_str = StringVar(value=_default_search_string) # XXX
        self.__set_output_RO = IntVar(value=1)
        self.__set_output_A = IntVar(value=1)

        self.__setup_gui()


    def __setup_gui(self):
        """Build up GUI from widgets"""
        topfrm = Frame(self)
        topfrm.pack(expand=NO, fill=X, side=TOP)
        Label(topfrm, text=_prog_title_).pack(side=TOP)

        sfrm = LabelFrame(topfrm, padx=5, pady=5, relief=RIDGE,
                            text='Source File Search')
        srch_lbl = Label(sfrm, text='Root search dir.:')
        srch_fld = Entry(sfrm, textvariable=self.__srch_dir)
        find_lbl = Label(sfrm, text='Match string:')
        find_fld = Entry(sfrm, textvariable=self.__srch_str)
        rfsh_btn = Button(sfrm, text='Refresh', command=self.__search)
        brws_btn = Button(sfrm, text='Browse', command=self.__set_srch_dir)

        sfrm.pack(expand=YES, fill=X, side=TOP)
        srch_lbl.pack(side=LEFT)
        srch_fld.pack(side=LEFT, expand=YES, fill=X, padx=5)
        brws_btn.pack(side=LEFT, padx=3)
        find_lbl.pack(side=LEFT)
        find_fld.pack(side=LEFT, expand=YES, fill=X, padx=5)
        rfsh_btn.pack(side=RIGHT, padx=3)




    def __set_srch_dir(self):
        """Browse to source directory"""
        choice = askdirectory(title='Select source directory',
                              mustexist=True)
        if choice and osp.isdir(choice):
            self.__srch_dir.set(choice.replace('/','\\'))
#            refresh = askyesno(title='Refresh source directory',
#                           message='Source directory has changed. Refresh?')
#            if refresh:
#                self.__refresh()


    def __search(self):
        """Search for files in source directory"""
        globstr = osp.join(self.__srch_dir.get(), self.__srch_str.get())
        found = glob(globstr)
        for fname in found:
            print fname


#    def __view_srcdir(self):
#        """Open source directory in file explorer"""
#        source = self.__srcdir.get()
#        if not source:
#            return False
#        if not osp.isdir(source):
#            showerror(title='View error',
#                  message=('Error occurred, could not open specified '
#                           'directory: %s') % source)
#        else:
#            os.startfile(osp.abspath(source))

    #def _


if __name__=='__main__':
    root = Tk()
    root.title(_prog_title_)
    SDTransferUtility().mainloop()

