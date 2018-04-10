# Field Timelapse Image Management

## Regional Approaches to Climate Change (2011-2016)

Python scripts to automate file management from the greenhouse gas flux tower
timelapse cameras.

* Project Home: <http://reacchpna.org>
* Flux tower repos
    * [Biomass Sampling Data and Records](https://github.com/wsular/reacchpna-eddyflux-biomass)
    * [Tower Logger Source Code](https://github.com/wsular/reacchpna-eddyflux-tower)
    * [Tower Data Processing](https://github.com/wsular/reacchpna-eddyflux-processing)
    * Field Timelapse Image Management (here)


### Requirements

* Python 2.7 (or time to migrate to 3.x)
* [ExifRead](https://github.com/ianare/exif-py)


### SDTransferUtility.pyw

A graphical program for transferring images captured by timelapse cameras at
monitoring tower sites (via SD card). It provides a simple interface to:

* Identify which site the images were taken at (via right-click)
* Review and update the destination directory
* Copy images to the destination directory under new timestamped names

