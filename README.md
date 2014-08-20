Timelapse Image Management & Processing
=======================================

Regional Approaches to Climate Change (2011-2016)
-------------------------------------------------

This folder contains the data management scripts used with REACCH Objective 2 
monitoring sites. Several of these are scheduled to run automatically and 
should not be edited directly. 

- Repository: <https://lar-d216-share.cee.wsu.edu/repos/git/reacch-obj2/ectower_data_scripts>
- Project page: <https://lar-d216-share.cee.wsu.edu/redmine/projects/id24>

The security certificate is self-signed. Non-SSL (http://) is available while
using the WSU CEE network. For access from outside the WSU CEE network use:
<https://lar-d216-share.cee.wsu.edu:8080> ...


### In the 'igorpro' folder

<...>

### In the 'python' folder

Some of the scripts are meant to be run as programs:

#### CFTransferUtility.pyw

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

#### SDTransferUtility.pyw

A graphical program for transferring images captured by timelapse cameras at
monitoring tower sites (via SD card). It provides a simple interface to:

* Identify which site the images were taken at
* Review and update the destination directory
* Copy images to the destination directory under new timestamped names

This program is linked to by a shortcut on the share host computer desktop
and start menu.

Others run automatically as scheduled tasks:

#### process_new_telemetry_data.py

When this script runs each morning, it calls `email_telemetry_plots.py` first
and then uses `standardize_toa5.py` to append new data collected from the 
monitoring sites to the appropriate files under the "L0_telemetry" folder on
the network share. Telemetry data files are deleted after being successfully
processed.

Still other scripts can be run as programs but since they are incorporated
into scheduled tasks or solve one-time maintenance issues, it is rarely
necessary to run them:

#### email_telemetry_plots.py

Plots any telemetry data collected since `process_new_telemetry_data.py` last
ran, exports it to a PDF file, then emails the file to a preset list. This
script can be run alone but is normally called when the scheduled task
`process_new_telemetry-data.py` runs.

#### rebuild_telemetry_files.py

This command-line program will use the `standardize_toa5.py` module to 
reconstruct all available plain-text raw data files ("L0_raw_ascii") into
corresponding cumulative raw telemetry data files ("L0_telemetry"). 
The impetus for this module was to, in effect, patch data missing from the 
telemetry files with data from the raw plain-text files.

#### split_toa5.py

Simple module to re-write monstrous text files (>1GB) produced by converting
binary data file to plain-text into manageable chunks (~100MB by default).
  
#### standardize_toa5.py

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

#### definitions/fileio.py

Functions to facilitate easy & consistent access to data files

#### definitions/paths.py

String constants defining local file paths and project directory structure

#### definitions/sites.py

Classes describing monitoring sites and their associated datalogger 

#### definitions/tables.py

Data table definitions for current and previous datalogger programs. Has 
function to translate data files of previous formats to the current format.

#### telemetry_plot_template.vsz

This Veusz document acts as the template for telemetry data plots exported by
`email_telemetry_plots.py`. Updates to this template document are reflected 
when the script next runs.

#### usb_disk_eject.exe

Both `CFTransferUtility.pyw` and `SDTransferUtility.pyw` use this executable
to eject removable media (CF & SD cards).

