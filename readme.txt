===============================================================
Data management scripts for REACCH Objective 2 monitoring sites
===============================================================

This folder contains the data management scripts used with REACCH Objective 2 
monitoring sites. Some run automatically so be mindful when editing. 

Folders
-------
/scripts
+--/igorpro    Procedures written for Igor Pro 
+--/logs       Log files made by scripts
+--/python     Scripts written in Python


Release Notes
=============

Version 0.4.1
-------------
- Apply hotfix to `process_new_telemetry_data.py` which fixes script's ability
  to locate correct destination directory

Version 0.4.0
-------------
- Script launching batch files replaced with shortcuts; solves issue with
  command reverting to Windows directory because of starting with UNC path
  as CWD and thus failing to find targets
- New graphical program for transferring timelapse image photos released:
  `SDTransferUtility.pyw` replaces `transfer_timelapse_photos.py`
    * Finds images using file name mask (e.g. searches multiple directories)
    * Automatic preview of selected image file
    * Process images from multiple locations (handled per directory)
    * No external dependency on Ant Renamer
    * Still only Windows-only
- Overhaul of CompactFlash memory card transfer program
    * More informative file characterization
    * Automatic exclusion of non-REACCH/invalid data files
    * Begin processing with single button press
    * Input file names are no longer permanently modified
    * Enhanced options availability: 
        . Set parameters for identifying & splitting large files
        . Specify target folder for standardized output
    * Process files from multiple sites simulataneously
    * Threading speeds up some processing steps
    * Still requires monitoring to acknowledge CardConvert dialogs
- Updated path definitions are cleaner to use

Version 0.3.1
-------------
- Hot-fix correction of directory path handling in relation to timelapse
  camera image transfer script

Version 0.3
-------------
- Release of script for processing newly downloaded telemetry data into 
  standard format and appending to existing data files
- Definitions now contained in groups across multiple files:
    * fileio : functions to open files, sniff properties, etc
    * paths  : locations of directories and files
    * sites  : objects containing monitoring site attributes
    * tables : functions and dictionaries representing data file structure 

Version 0.2.3
-----------
- Support added for new monitoring site 'MSLK'
- Changes to CompactFlash Transfer Utility
    * Applies standard formatting to plain-text files created by Card Convert
    * Improved support for ejecting card
- Changes to timelapse photo transfer script
    * Site options now pulled from definitions, not hard-coded

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


