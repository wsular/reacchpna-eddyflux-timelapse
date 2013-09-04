===============================================================
Data management scripts for REACCH Objective 2 monitoring sites
===============================================================

:Contact: pokeeffe@wsu.edu
:Version: 0.2
:Date: 2013-06-04

Overview
========
This folder contains the data management scripts used with REACCH Objective 2 
monitoring sites. Please ensure the production scripts located on the share
server [#]_ under ``/proj/2011_REACCH/scripts/`` are not modified. Some 
scripts run at a scheduled time and may fail if improperly edited. 

.. [#] The share server is available online to users logged on to WSU networks 
   at ``ftp://`` and ``http://lar-d216-share.cee.wsu.edu``. Alternatively, the
   REACCH share folder can be added as a network drive; map a new drive to
   ``\\lar-d216-share.cee.wsu.edu\reacch`` or 
   ``\\lar-d216-share.cee.wsu.edu\proj\2011_REACCH``.

Contributing
------------
These files are tracked with the distributed version control system Git_. 
Users are welcomed and encouraged to clone the repository and make their own
contributions. Alternatively, users can add scripts to this folder and make 
periodic requests to have their work checked in. 

Issues, support and enhancement requests are being being handled with Redmine_ 
project management software. This application also hosts files, tracks 
releases (versions) and lets users browse the repository. 

    ================    =================
    Repository path     repo_
    ----------------    -----------------
    Contact email       pokeeffe@wsu.edu
    ----------------    -----------------
    Redmine             rm_
    ================    =================

.. _Git: http://www.git-scm.org
.. _Redmine: http://www.redmine.org
.. _repo: http://lar-d216-share.cee.wsu.edu/scm/git/reacch-obj2/ectower_data_scripts
.. _rm: https://lar-d216-share.cee.wsu.edu/redmine


Contents
========
What is in the ``/scripts`` folder?

Batch file (*.bat) shortcuts
----------------------------
There are batch files (*.bat) in the root folder to provide a simplified way 
of interacting with the various scripts. In general, the shortcuts are 
designed to be used on the share workstation in Dana 216; some users may need 
to create a copy of the batch files and modify the specified drive letter for 
use on their own workstation.

.. table:: Subfolders

    =========       ========
    Folder          Contents
    ---------       --------
    /bin            Binary executables including third-party programs
    /doc            Documentation for users and researchers
    /igorpro        Procedure files written for use with Igor Pro
    /logs           Log files from scripts *[not in DVCS]*
    /python         Scripts written in python and related auxilary files
    =========       ========

/bin
----
The programs in here are used by a variety of scripts. Users are free to use 
them too so long as the program (name included) is not modified at all.

/doc
----
Documentation for users is in here. 

/igorpro
--------
Procedures written for Igor Pro should be saved as independent text files
(*.ipf) and stored in this folder. This is not a place for experiments to be 
saved; one exception might be where a set of rigorous tests for some procedure 
are saved along with data and plots. 

/logs
-----
This folder contains log files from various scripts. For clarity, name the log
file so it's easily associated with the script generating it. 

**The files in this folder are not checked in to version control.**

/python
-------
Scripts written in Python are located here. File names should start with a 
verb and have a sufficiently descriptive noun such that the script's goals 
are immediately apparent. For scripts that have ancillary files, create a 
subfolder to hold each script's files. 


Release Notes
=============

Version 0.2
-----------
- Changes to CompactFlash Transfer Utility
    * Now depends upon ``definitions.py`` for paths & site code definitions
    * Breaks large files (>200MB) into smaller ones (~100MB)
    * Sets read-only+archive attributes on generated ASCII files too now
    * FIX: path choices are no longer cleared if dialog is cancelled
    * Prompts to confirm exit if source directory still contains files 
- Changes to timelapse photo transfer script:
    * No longer requires separate renaming batch script (but does still depend 
      on objects in ``definitions.py``)
    * Renames files on hard disk -- massive speed improvement
    * Supports overwriting if files already exist in destination

Version 0.1
-----------
- Not really an initial release but first official release
- Can transfer binary data from CompactFlash cards, generate ASCII files, then 
  empty and eject CF card. [``python/CFTransferUtility.pyw``]
- Can transfer photos taken by timelapse cameras, rename then empty and eject
  SD card. [``python/transfer_timelapse_photos.py``]


