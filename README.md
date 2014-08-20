Timelapse Image Management & Processing
=======================================

Regional Approaches to Climate Change (2011-2016)
-------------------------------------------------

The eddy covariance tower subgroup of the Objective 2 Monitoring team deploys
consumer-grade time-lapse cameras at each monitoring site. This repository 
tracks scripts for:

- transferring retrieved images to final storage location
- extracting Exif metadata and renaming files to standard convention
- [**FUTURE**] generating timelapse videos

### Links 

- Project home: <http://reacchpna.org>
- Repositories
    - Standard Operating Procedures: <https://bitbucket.org/wsular/2011-reacch-sops>
    - Tower datalogger program: <https://bitbucket.org/wsular/2011-reacch-tower-logger>
    - Tower data processing: <https://bitbucket.org/wsular/2011-reacch-tower-data>
    - Timelapse cameras (**HERE**): <https://bitbucket.org/wsular/2011-reacch-timelapse>

### Components

Available scripts are described briefly below. For more complete operating
instructions refer to `Monitoring Towers SOP.docx` within the 
[SOP repository](https://bitbucket.org/wsular/2011-reacch-sops).

#### SDTransferUtility.pyw

A graphical program for transferring images captured by timelapse cameras at
monitoring tower sites (via SD card). It provides a simple interface to:

* Identify which site the images were taken at
* Review and update the destination directory
* Copy images to the destination directory under new timestamped names

