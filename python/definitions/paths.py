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

import os.path as osp

from definitions.version import __version__


#### Base directory
HOME_DIR = r'B:\proj\2011_REACCH' # Share folder host computer

#### Path to recently downloaded telemetry files
DOWNLOAD_DIR = r'C:\Campbellsci\Loggernet'

#### Drive letters, no need for trailing slash
CF_DRIVE = 'D:\\' # used by `CF Transfer Utility`
SD_DRIVE = 'F:\\' # used by `Transfer timelapse photo` script


#### Search pattern to find default image storage directories on SD cards
SD_DEF_IMG_DIR = r'DCIM\*_WSCT\*.jpg' # w.r.t. SD_DRIVE (e.g. F:\DCIM\...)


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

TELEMETRY_LOG = pathjoin(BASE_LOG_DIR, 'process_new_telemetry_data.log')


#### Path templates
#
# Substitute dict-style:
#
#   raw_binary_path = RAW_BINARY_DIR % {'site' : site_code,
#                                       'table' : table_name}
#
# Available substitutions:
#
# %(site)s      replaced with four-character site code
#               (e.g.: 'CFNT', 'LIND', 'MSLK', ...)
# %(table)s     replaced with data file's table name
#               (e.g.: 'tsdata', 'stats5', 'site_info', ...)
#
HOME = r'D:\proj\2011_REACCH'

TOWERDATA = osp.join(HOME, r'tower_%(site)s')

RAW_ASCII = osp.join(TOWERDATA, r'L0_raw_ascii')
RAW_BINARY = osp.join(TOWERDATA, r'L0_raw_binary')
RAW_STDFMT = osp.join(TOWERDATA, r'L0_standard_format')


