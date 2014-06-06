===============================================================
Data management scripts for REACCH Objective 2 monitoring sites
===============================================================

This folder contains the data management scripts used with REACCH Objective 2 
monitoring sites. Several of these are scheduled to run automatically and 
should not be edited directly. 

Source repository (Git):
  https://lar-d216-share.cee.wsu.edu/repos/git/reacch-obj2/ectower_data_scripts

Project page:
  https://lar-d216-share.cee.wsu.edu/redmine/projects/id24

The security certificate is self-signed. Non-SSL (http://) is available while
using the WSU CEE network. For access from outside the WSU CEE network use:
  https://lar-d216-share.cee.wsu.edu:8080/ ...


Overview
========

In the 'igorpro' folder
-----------------------

<...>

In the 'python' folder
----------------------

Some of the scripts are meant to be run as programs:

CFTransferUtility.pyw
  A graphical program for transferring data collected from monitoring tower
  dataloggers (via CompactFlash card). It offers a quick, reliable process:
    * Automatically detects which site data is from
    * Copies and verifies binary data files (TOB3)
    * Converts binary data files to plain-text (TOA5)
    * Optionally splits large plain-text files to manageable chunks
    * Applies the standardizing script to plain-text files in preparation for
      processing with EddyPro
  This program is linked to by a shortcut on the share host computer desktop
  and start menu. 

SDTransferUtility.pyw
  A graphical program for transferring images captured by timelapse cameras at
  monitoring tower sites (via SD card). It provides a simple interface to:
    * Identify which site the images were taken at
    * Review and update the destination directory
    * Copy images to the destination directory under new timestamped names
  This program is linked to by a shortcut on the share host computer desktop
  and start menu.

Others run automatically as scheduled tasks:

process_new_telemetry_data.py
  When this script runs each morning, it calls `email_telemetry_plots.py` first
  and then uses `standardize_toa5.py` to append new data collected from the 
  monitoring sites to the appropriate files under the "L0_telemetry" folder on
  the network share. Telemetry data files are deleted after being successfully
  processed.

Still other scripts can be run as programs but since they are incorporated
into scheduled tasks or solve one-time maintenance issues, it is rarely
necessary to run them:

email_telemetry_plots.py
  Plots any telemetry data collected since `process_new_telemetry_data.py` last
  ran, exports it to a PDF file, then emails the file to a preset list. This
  script can be run alone but is normally called when the scheduled task
  `process_new_telemetry-data.py` runs.

rebuild_telemetry_files.py
  This command-line program will use the `standardize_toa5.py` module to 
  reconstruct all available plain-text raw data files ("L0_raw_ascii") into
  corresponding cumulative raw telemetry data files ("L0_telemetry"). 
    The impetus for this module was to, in effect, patch data missing from the 
  telemetry files with data from the raw plain-text files.

split_toa5.py
  Simple module to re-write monstrous text files (>1GB) produced by converting
  binary data file to plain-text into manageable chunks (~100MB by default).
  
standardize_toa5.py
  Accepts a plain-text raw (TOA5) data file from any program version operated 
  by a REACCH EC monitoring tower datalogger and generates a CSV file 
  conforming to a standard format which:
    * Has explicit 10hz time-series index padded with NAN rows where needed
    * Has no quotes on non-text fields (e.g. NAN not "NAN")
    * Has consistent table-dependent time length:
        - Daily: 10hz time-series data table
        - Monthly: 5/30min statistics data tables
        - Cumulative: incidental data tables
    * Translates table/column name to current table/column definition

Finally, other supporting files include:

definitions/fileio.py
  Functions to facilitate easy & consistent access to data files

definitions/paths.py
  String constants defining local file paths and project directory structure

definitions/sites.py
  Classes describing monitoring sites and their associated datalogger 

definitions/tables.py
  Data table definitions for current and previous datalogger programs. Has 
  function to translate data files of previous formats to the current format.

telemetry_plot_template.vsz
  This Veusz document acts as the template for telemetry data plots exported by
  `email_telemetry_plots.py`. Updates to this template document are reflected 
  when the script next runs.

usb_disk_eject.exe
  Both `CFTransferUtility.pyw` and `SDTransferUtility.pyw` use this executable
  to eject removable media (CF & SD cards).


Release Notes
=============

Version 0.4.4
-------------
- Hotfix applied to telemetry processing script so only REACCH-related files
  are processed and deleted (!). Applied fix is still imperfect: it would
  affect future additions if they follow the same naming convention for the
  station in Loggernet (e.g. "REMOTE_<something>")

Version 0.4.3
-------------
- Minor tweaks to axis settings in telemetry plots:
    * Clarify labels on logger panel temp. and friction velocity plots
    * Set static bounds (+/-1000m) on Obukhov length plot axis
- Reorder sites in telemetry plot summary to group by locality
- Shortcuts are removed in favor of those on the share host's desktop and
  start menu
- Add Overview section to readme explaining each script

Version 0.4.2
-------------
- New script `email_telemetry_plots.py` generates plots of data collected by 
  telemetry from all five tower monitoring sites over the last 24 hours, 
  exports the plots to a PDF file and emails the PDF to a list of individuals. 
    * Runs automatically as part of the daily telemetry data processing task
    * Can be run independently if necessary
- New script `rebuild_telemetry_files.py` reconstructs monitoring tower 
  "telemetry" data files (L0_telemetry) from the "raw plain-text" files
  (L0_raw_ascii) using the standardizing script `standardize_toa5.py`. This
  represents the first step to patching "raw plain-text" files with data in the
  "telemetry" data files. 

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


