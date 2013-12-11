# -*- coding: utf-8 -*-
"""
Created on Mon Dec 09 14:57:26 2013

@author: pokeeffe
"""

import logging
import os
import os.path as osp

from datetime import datetime
from glob import glob

from Tkinter import *
from tkMessageBox import askyesno, showerror
from tkFileDialog import askdirectory
from ScrolledText import ScrolledText

from ttk import Treeview

from PIL import Image, ImageTk

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

        self._sources = {}
        self._log_to_file = False

        self.__srch_dir = StringVar(value=SD_DRIVE) # XXX
        self.__srch_str = StringVar(value=_default_search_string) # XXX
        self.__set_output_RO = IntVar(value=1)
        self.__set_output_A = IntVar(value=1)

        self.__gui_setup()


    def __gui_setup(self):
        """Build up GUI from widgets"""
        topfrm = Frame(self)
        topfrm.pack(expand=YES, fill=BOTH, side=TOP)
        Label(topfrm, text=_prog_title_).pack(side=TOP)

        opts = self.__gui_options(topfrm)
        opts.pack(expand=NO, fill=X)

        hpane = PanedWindow(topfrm, orient=VERTICAL, sashrelief=GROOVE)
        hpane.pack(fill=BOTH, expand=YES)

        console = self.__gui_preview(hpane)
        logpane = self.__gui_logger(hpane)

        hpane.add(logpane, minsize=40)
        hpane.add(console, before=logpane)
        hpane.paneconfigure(logpane, pady=5)
        hpane.paneconfigure(console, pady=5)


    def __gui_options(self, parent=None):
        """Upper pane for entry fields, buttons, so on """
        thispane = Frame(parent)

        sfrm = LabelFrame(thispane, padx=5, pady=5, relief=RIDGE,
                          text='Source Image Search')
        sfrm.pack(expand=NO, fill=X, side=TOP)
        srch_lbl = Label(sfrm, text='Root search dir.:')
        srch_fld = Entry(sfrm, textvariable=self.__srch_dir)
        find_lbl = Label(sfrm, text='Match string:')
        find_fld = Entry(sfrm, textvariable=self.__srch_str)
        rfsh_btn = Button(sfrm, text='Search', command=self.__search)
        brws_btn = Button(sfrm, text='Browse', command=self.__set_srch_dir)
        srch_lbl.pack(side=LEFT)
        srch_fld.pack(side=LEFT, expand=YES, fill=X, padx=5)
        brws_btn.pack(side=LEFT, padx=3)
        rfsh_btn.pack(side=RIGHT, padx=3)
        find_fld.pack(side=RIGHT, expand=YES, fill=X, padx=5)
        find_lbl.pack(side=RIGHT)

        btnfrm = Frame(thispane)
        btnfrm.pack(expand=NO, fill=X, pady=5, side=BOTTOM)
        go_btn = Button(btnfrm, text='Begin processing',
                        command=self.__transfer_images)
        eject_btn = Button(btnfrm, text='Eject source dir.',
                        command=self.__eject_srch_dir)
        quit_btn = Button(btnfrm, text='Exit program',
                        command=self.__quit)
        go_btn.pack(side=LEFT)
        quit_btn.pack(side=RIGHT)
        eject_btn.pack(side=RIGHT, padx=10)

        return thispane

    def __gui_preview(self, parent=None):
        """Middle pane interacting with user"""
        thispane = Frame(parent)

        vpane = PanedWindow(thispane, orient=HORIZONTAL, sashrelief=GROOVE)
        vpane.pack(fill=BOTH, expand=YES)

        self._sourcetree = Treeview(vpane,
                                    columns=('destname'),
                                    selectmode='browse')
        self._sourcetree.heading('destname', text='Destination', anchor=W)
        self._preview = Button(vpane)

        vpane.add(self._sourcetree)
        vpane.add(self._preview)
        vpane.paneconfigure(self._sourcetree, padx=5)
        vpane.paneconfigure(self._preview, padx=5)

        return thispane


    def __gui_logger(self, parent=None):
        """Lower pane with logging output"""
        thispane = Frame(parent)

        hfrm = Frame(thispane)
        cbLog = Checkbutton(hfrm, text='Log output to: ',
                            variable=self._log_to_file)

        self.logpane = ScrolledText(thispane, height=2)
        self.logpane.pack(expand=YES, fill=BOTH, side=BOTTOM)

        return thispane


    ##### GUI ^ / LOGIC v #####

    def __set_srch_dir(self):
        """Browse to source directory"""
        choice = askdirectory(title='Select source directory',
                              mustexist=True)
        if choice and osp.isdir(choice):
             self.__srch_dir.set(choice.replace('/','\\'))


    def __search(self):
        """Search for files in source directory"""
        globstr = osp.join(self.__srch_dir.get(), self.__srch_str.get())
        files_found = glob(globstr)
        for f in files_found:
            this_dir = self._sources.setdefault(osp.dirname(f), {})
            dest_dir = this_dir.setdefault('dest', None) # not used here
            site_code = this_dir.setdefault('site', None) # just to defaults
            flist = this_dir.setdefault('flist', [])
            flist.append(f)
        self.__refresh_treeview()


    def __refresh_treeview(self):
        """Construct tree view data model"""
        for node in self._sourcetree.get_children(''):
            self._sourcetree.delete(node)

        for srcdir in sorted(self._sources.keys()):
            destdir = self._sources[srcdir]['dest']
            deststr = destdir or '<not yet determined>'
            sitecode = self._sources[srcdir]['site']
            iid = self._sourcetree.insert('', END,
                                          text=srcdir,
                                          values=[deststr])
            flist = self._sources[srcdir]['flist']
            for fname in flist:
                destname = self.__dest_fname_mask(fname)
                if sitecode:
                    destname = destname % {'site' : sitecode}
                self._sourcetree.insert(iid, END,
                                        text=osp.basename(fname),
                                        values=[destname])
                self._sourcetree.bind('<<TreeviewSelect>>', self.__preview_img)


    def __preview_img(self, event):
        w = event.widget
        if w.focus():
            fname = w.item(w.focus(), option='text')
            if fname not in self._sources.keys():
                srcdir = w.item(w.parent(w.focus()), option='text')
                imgpath = osp.join(srcdir, fname)
                self._preview_img = ImageTk.PhotoImage(Image.open(imgpath))
                self._preview.configure(image=self._preview_img)


    def __eject_srch_dir(self):
        pass


    def __dest_fname_mask(self, fname):
        """Return image destination name file mask

        In form of `%(site)s_YYYYMMDD.hhmm` YYYYMMDD is year/month/day, hhmm
        is (24) hour/min, and %(site)s is for dict-style string substitution.
        """
        _, ext = osp.splitext(fname)
        tags = exifread.process_file(open(fname, mode='rb'),
                                     details=False,
                                     stop_tag='DateTimeOriginal')
        timestamp = str(tags['EXIF DateTimeOriginal'])
        dt = datetime.strptime(timestamp, '%Y:%m:%d %H:%M:%S')
        return dt.strftime('%%(site)s_%Y%m%d.%H%M'+ext)


    def __cprint(self, msg):
        """Print to console pane"""
        self.console.insert(END, str(msg))
        self.console.see(END)
        self.update()


    def __transfer_images(self):
        print 'Entered `__transfer_images`'


    def __quit(self):
        Frame.quit(self)


if __name__=='__main__':
    root = Tk()
    root.title(_prog_title_)
    root.update_idletasks()
    root.minsize(root.winfo_reqwidth(),root.winfo_reqheight())
    SDTransferUtility().mainloop()

