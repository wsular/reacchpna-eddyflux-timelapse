# -*- coding: utf-8 -*-
"""Paths to important local directories

    Edit this file as needed to describe your file system. Use the module
    like this:

        from definitions.paths import HOME_DIR, CF_DRIVE

    Tips for defining paths:
        - don't use trailing slash
        - prefix strings with 'r' to avoid escaping slashes


@author: Patrick O'Keeffe <pokeeffe@wsu.edu>
"""

from os.path import join as pathjoin

from definitions.version import __version__


#### Base directory
#HOME_DIR = r'B:\proj\2011_REACCH' # Share folder host computer
HOME_DIR = r'D:\proj\2011_REACCH' # pokeeffe workstation

#### Path to recently downloaded telemetry files
DOWNLOAD_DIR = r'C:\Campbellsci\Loggernet'

#### Drive letters, no need for trailing slash
CF_DRIVE = r'D:' # used by `CF Transfer Utility`
#SD_DRIVE = r'F:' # used by `Transfer timelapse photo` script
SD_DRIVE = r'D:' # pokeeffe workstation

#### Subdirectory mask for tower data folders
#### Use keyword substitute (e.g. tower_LIND, tower_CFNT...)
TOWER_DIR = pathjoin(HOME_DIR, 'tower_%(code)s')

#### Tower data paths
RAW_ASCII_DIR = pathjoin(TOWER_DIR, 'L0_raw_ascii')
RAW_BINARY_DIR = pathjoin(TOWER_DIR, 'L0_raw_binary')
STD_FORMAT_DIR = pathjoin(TOWER_DIR, 'L0_standard_format')
TELEMETRY_DIR = pathjoin(TOWER_DIR, 'L0_telemetry')

#### Timelapse cam paths
TIMELAPSE_PHOTO_DIR = pathjoin(TOWER_DIR, 'photos_timelapse')
TIMELAPSE_VIDEO_DIR = pathjoin(TOWER_DIR, 'videos_timelapse')

#### Agweathernet data storage location
AGWEATHERNET_DIR = pathjoin(HOME_DIR, 'agweathernet_data')


#### FUll paths to log files
BASE_LOG_DIR = r'B:\proj\2011_REACCH\scripts\logs'

TELEMETRY_LOG = pathjoin(BASE_LOG_DIR, 'telemetry.log')



