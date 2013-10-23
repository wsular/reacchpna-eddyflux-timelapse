# -*- coding: utf-8 -*-
"""Common settings location for REACCH Obj2 data scripts

This module defines a host of common data and functions which are in turn
used by nearly all other data scripts. Some of the stuff here includes:

    Paths
        There is an object ``pathto`` which contains a variety of string
        attributes corresponding to relevant file/directory paths. For ex:

        >>> from definitions import pathto
        >>> pathto.raw_ascii
        {ex1_results}

    Table/column name look-up
        The function ``current_names`` will look up any pair of table and
        column names from a valid EC tower data file and return the names
        as defined in the most recent program release.

        >>> from definitions import current_names
        >>> current_names('flux', 'l')
        ('stats30', 'L')

    File I/O
        Several functions offer a standard way to interact with data files:

            * ``open_toa5``
            * ``write_csv``
            * ``open_csv``

    Field site data
        The list ``site_list`` contains ``FieldSite`` objects named after
        each site's four-character code which have properties describing
        aspects of that site. For instance:

            >>> from definitions import site_list
            >>> for site in site_list:
            ...     print site.name
            ...
            Cook Agronomy Farm no-till
            Lind Dryland Research Station
            Cook Agronomy Farm conventional till
            Moscow Mountain

        See the FieldSite help/docstring for details about what's available.

Created on Fri Sep 14 08:09:41 2012

@author: Patrick O'Keeffe <pokeeffe@wsu.edu
""".format(ex1_results=lambda x: pathto.raw_ascii)

__version_info__ = (0, 1, '20130401')
__version__ = '.'.join(str(x) for x in __version_info__)

from copy import copy
from warnings import warn

import pandas as pd
import os

from pandas import DataFrame
from pandas.tseries.offsets import Day, MonthBegin, YearBegin


MAX_RAW_FILE_SIZE = 200 * 1024 * 1024  #split raw data files > this, bytes


class pathto(object):
    """Object containing up-to-date directory locations

    There are several well-defined directories that various scripts may
    need to access. This object provides a high-level interface that
    insulates the user from changes and minute details.

    These directories are all with-respect-to the share workstation local
    environment. You might want to write an analogous function for your
    own workstation to override these paths.

    Paths are available as attributes:  ``pathto.home`` or ``pathto.cf_card``

    +---------------------+-----------------------------------------------+
    | Attribute           | Path description                              |
    +=====================+===============================================+
    | home                | Base project directory (root of share)        |
    +---------------------+-----------------------------------------------+
    | nethome             | Base project directory as used in network     |
    |                     | addresses                                     |
    +---------------------+-----------------------------------------------+
    | cf_card             | CompactFlash card reader drive letter         |
    +---------------------+-----------------------------------------------+
    | sd_card             | SD card reader drive letter                   |
    +---------------------+-----------------------------------------------+
    | sd_card_photos      | Storage location of photos on SD cards by     |
    |                     | timelapse cameras                             |
    +---------------------+-----------------------------------------------+
    | downloads           | Location data files retrieved via cellular    |
    |                     | link are stored                               |
    +---------------------+-----------------------------------------------+
    | script_logs         | Location scripts should write log files to    |
    +---------------------+-----------------------------------------------+
    | raw_ascii           | Location of unprocessed, text-formatted data  |
    |                     | files in Campbellsci long-header (TOA5)       |
    |                     | format                                        |
    |                     |                                               |
    |                     | Expects user to substitute 4-char site code:  |
    |                     | ``pathto.raw_ascii % 'CFNT'``                 |
    +---------------------+-----------------------------------------------+
    | raw_binary          | Location of unprocessed, binary data files in |
    |                     | Campbellsci TOB3 format                       |
    |                     |                                               |
    |                     | Expects user to substitute 4-char site code:  |
    |                     | ``pathto.raw_binary % 'MMTN'``                |
    +---------------------+-----------------------------------------------+
    | telemetry           | Location of unprocessed, cumulative 5- & 30-  |
    |                     | minute statistics data files                  |
    |                     |                                               |
    |                     | Expects user to substitute 4-char site code:  |
    |                     | ``pathto.telemetry % 'LIND'``                 |
    +---------------------+-----------------------------------------------+
    | timelapse_photos    | Location of photos taken by timelapse camera  |
    |                     | at the site                                   |
    |                     |                                               |
    |                     | Expects user to substitute 4-char site code:  |
    |                     | ``pathto.timelapse_photos % 'CFCT'``          |
    +---------------------+-----------------------------------------------+
    | raw_std             | Location of standardized data files in CSV    |
    |                     | format.                                       |
    |                     |                                               |
    |                     | Expects user to substitute 4-char site code   |
    |                     | as well as table name in that order:          |
    |                     | ``pathto.raw_std % ('LIND', 'stats30')``      |
    +---------------------+-----------------------------------------------+

    """
    _raw_std_subdir = r'\L0_%s' # substitute table name ('stats5', 'tsdata'...)
    _raw_ascii_subdir = r'\L0_raw_ascii'
    _raw_bin_subdir = r'\L0_raw_binary'
    _tele_subdir = r'\L0_telemetry'
    _tl_photo_subdir = r'\photos_timelapsecam'
    _tl_video_subdir = r'\videos_timelapsecam'
    _tower_subdir = r'\tower_%s' # substitute site code ('CFNT', 'LIND',...)

    home = r'B:\projects\2011_REACCH'
    nethome = r'/projects/2011_REACCH/'
    cf_card = r'D:'
    sd_card = r'F:'
    sd_card_photos = r'F:\DCIM\100_WSCT'
    downloads = r'C:\Campbellsci\Loggernet'
    script_logs = home + r'\scripts\logs'
    raw_ascii = home + _tower_subdir + _raw_ascii_subdir
    raw_binary = home + _tower_subdir + _raw_bin_subdir
    telemetry = home + _tower_subdir + _tele_subdir
    timelapse_photos = home + _tower_subdir + _tl_photo_subdir
    raw_std = home + _tower_subdir + _raw_std_subdir


def get_table_name(toa5_file):
    """Return name of table given rel. or abs. file path to TOA5 file

    Reads header of Campbell Scientific long-header (TOA5) formatted data
    files and returns name of data table.

    Parameters
    ----------
    toa5_file : file-like object
        Source data file in CSI long-header (TOA5) format

    Returns
    -------
    str : name of data table or None if not a valid table file
    """
    with open(toa5_file, mode='r') as f:
        l = f.readline().strip().split(',')
    try:
        assert l[0] == '"TOA5"' # 1st item, 1st row must be "TOA5"
        tblname = l[-1].strip('"') #last item, first row
    except:
        tblname = None
    return tblname

def get_site_code(toa5_file):
    """Return text code of site where TOA5 data file was created
    
    Reads header of Campbell Scientific long-header (TOA5) formatted data 
    files and returns four-character site code (e.g. CFNT, LIND, MMTN, etc)
    
    Parameters
    ----------
    toa5_file : file-like object
        Source data file in CSI long-header (TOA5) format

    Returns
    -------
    str : four character site code or None if not a valid table file
    """
    with open(toa5_file, mode='r') as f:
        l = f.readline().strip()
    sn = l.split(',')[3].strip('"') #fourth item, first row
    try:
        sitecode = sn2code[sn]
    except KeyError:
        sitecode = None
    return sitecode
    

#def open_toa5(fname):
#    """Open TOA5 file and return pandas DataFrame
#
#    Parameters
#    ----------
#    fname : str
#        path to source TOA5 file
#
#    Returns
#    -------
#    pandas.DataFrame instance containing data from source file
#    """
#    try:
#        print "> Loading %s" % os.path.basename(fname)
#        df = pd.read_csv(fname,
#                         header=1,
#                         skiprows=[2,3],
#                         index_col=0,
#                         parse_dates=True,
#                         na_values=['"NAN"', 'NAN'])
#    except Exception as err:
#        print 'Serious problem!'
#        raise err
#    df.index.name = 'TIMESTAMP'
#    duptest = list(df.index.get_duplicates())
#    if len(duptest) > 1000:
#        print '  ! More than 1000 duplicate indices found! (Did the file ring?)'
#    elif len(duptest):
#        print '  ! Duplicate index values found:'
#        for each in duptest:
#            print '      ', each, len(df.ix[each]), 'rows'
#        print '  * Removing earliest duplicate indices...'
#    else:
#        return df #short-circuit if no dups
#    return df.groupby(df.index).last()

def open_toa5(fname):
    """Opens CSI TOA5-formatted data files in standard fashion

    Loads data from TOA5-formatted data file into pandas.DataFrame object. The
    timestamp column is used as the dataframe index (axis 0). Column names
    are used for names along DF axis 1. Progam info (line 0), column units
    (line 2) and record type (line 3) are ignored. Null values are recognized
    ("NAN", NAN, 7999, -7999 and -2147483648) and set to np.nan

    Parameters
    ----------
    fname : str
        path to TOA5 file to open

    Returns
    -------
    pandas.DataFrame
    """
    df = pd.read_csv(fname,
                     header=1,
                     skiprows=[2,3],
                     index_col=0,
                     parse_dates=True,
                     na_values=['"NAN"', 'NAN', 7999, -7999, -2147483648])
    if len(df.index.get_duplicates()) or not df.index.is_monotonic:
        warn('Warning: open_toa5 removed duplicate indices (%s)' % fname)
        df = df.groupby(level=0).last()
    df.index.name = 'TIMESTAMP'
    return df


def read_csv(file_name):
    """Read DataFrame previously written to CSV file in standard format

    Parameters
    ----------
    file_name : str
        path to source CSV file

    Returns
    -------
    pandas.DataFrame object
    """
    #try:
    df = pd.read_csv(file_name,
                     index_col=0,
                     parse_dates=True,
                     na_values=['NAN'])
    df.index.name = 'TIMESTAMP'
    #except IOError:
    #    df = None
    return df


def write_csv(df, file_name):
    """Write DataFrame to CSV file in standard format

    Parameters
    ----------
    df : pandas.DataFrame
        source dataframe to write to file
    file_name : str
        name of file to write to

    Returns
    -------
    Nothing at the moment
    """
    der = os.path.dirname(file_name)
    if der:
        # this illogically logical try-except block brought to you by:
        #    http://stackoverflow.com/a/14364249
        try:
            os.makedirs(der)
        except OSError:
            if not os.path.isdir(der):
                raise
    print '>>> writing to csv: %s ...' % file_name,
    df.to_csv(file_name,
              na_rep='NAN',
              float_format='%.3f',
              index_label='TIMESTAMP')
    print 'done.'


def current_names(table, column):
    """Get current (table, column) names from historical aliases

    Provides the current table & column name for any given table & column
    name from REACCH Objective 2 EC tower data files. If column is no longer
    included, the tuple ``(None, None)`` is returned. See Details for an
    explanation of how it works.

    Parameters
    ----------
    table : str
        name of data table, as deployed, case-sensitive; can be found at the
        end of the first line in files with original headers
    column : str
        name of data file column, as deployed, case-sensitive;

    Returns
    -------
    Tuple of table name and column name according to present definitions or
    ``(None, None)`` if column is no longer present.

    Examples
    --------

    The sonic diagnostic flags are no longer totaled:

        >>> current_names('flux', 'sonic_cal_err_f_Tot')
        (None, None)

    Oldest data table columns are translated to current names:

        >>> current_names('flux', 'l')
        ('stats30', 'L')

    But if it's a current set of names, the input is returned:

        >>> current_names('stats30', 'L')
        ('stats30', 'L')

    Details
    -------
    Internally, ``current_names`` uses a dictionary whereby keys and values
    are tuples of the form (table name, column name). All current and prior
    table and column pairs are described a key. Table/column pairs which are
    defined in the current data schema have values of ``('','')``. Those
    columns which are dropped from the data schema have values of
    ``(None, None)``. When a table and/or column name is changed, the
    table/column key is retired by changing the corresponding tuple value(s)
    to the new name(s); unless the column has been dropped, a new dictionary
    entry must also be added with the new table/column name as the key and a
    tuple of empty strings as the value.

    By structuring the dictionary in this way, the actual look-up performed
    by ``current_names`` happens recursively:

        ('flux', 'WS_ms_WVc(1)')] => ('', '034b_ws') --->

        ('flux', '034b_ws')] => ('CFNT_stats30', 'Met1_wnd_spd') --->

        ('CFNT_stats30', 'Met1_wnd_wpd')] => ('stats30', '') --->

        ('stats30', 'Met1_wnd_spd')] => ('', '') # current tbl/col names

    This mimics how you might actually figure out what the current table and
    column name of a given column is. So long as the dictionary is correct,
    things are gravy, and despite being long, the dictionary is simple.
    Additionally, there are internal functions for checking the validity of
    the dictionary -- run (double-click) the source file to use them, they
    take too long to be suitable for running upon import.
    """
    try:
        tbl, col = col_alias[(table, column)]
    except KeyError:
        #print ('>>>> Unable to find historical names for column "%s" of table "%s"' 
        #        % (column, table))
        raise ColumnNotFoundError
    if (tbl, col) == (None, None):
        return (None, None)
    elif (tbl, col) == ('', ''):
        return (table, column)
    elif tbl == '':
        return current_names(table, col)
    elif col == '':
        return current_names(tbl, column)
    else:
        return current_names(tbl, col)

class ColumnNotFoundError(Exception):
    pass

class FieldSite(object):
    """Represent an objective 2 monitoring site

    Parameters
    ----------
    name: str
        full name of the field site
    code: str
        unique four-character designation for the site; will be
        converted to upper-case
    serial_num: int
        serial number of the datalogger at the site. Retained as string
        to avoid future incompatibilities -- convert to integer yourself
    local_IP: str tuple
        IP address and netmask of the datalogger's ethernet adapter
        example: ('192.168.0.0','255.255.255.0')
    remote_IP: str tuple
        internet-facing IP address and netmask of the broadband modem
        at the site in same format as `local_IP`

    Returns
    -------
    New instance of the FieldSite class

    Details
    -------

    Class also contains object with some pre-populated site-specific paths:

        ``FieldSite.pathto.raw_ascii`` or ``FieldSite.pathto.telemetry``

    +---------------------+-----------------------------------------------+
    | FieldSite.pathto.*  | Description                                   |
    +=====================+===============================================+
    | raw_ascii           | Location of unprocessed, text-formatted data  |
    |                     | files in Campbellsci long-header (TOA5)       |
    |                     | format                                        |
    +---------------------+-----------------------------------------------+
    | raw_binary          | Location of unprocessed, binary data files in |
    |                     | Campbellsci TOB3 format                       |
    +---------------------+-----------------------------------------------+
    | telemetry           | Location of unprocessed, cumulative 5- & 30-  |
    |                     | minute statistics data files                  |
    +---------------------+-----------------------------------------------+
    | timelapse_photos    | Location of photos taken by timelapse camera  |
    |                     | at the site                                   |
    +---------------------+-----------------------------------------------+
    | raw_std             | Location of standardized data files in CSV    |
    |                     | format.                                       |
    |                     |                                               |
    |                     | Expects user to substitute table name:        |
    |                     | ``Site.pathto.raw_std % 'stats30'``           |
    +---------------------+-----------------------------------------------+
    """
    def __init__(self, name, code, serial_num, local_IP=None, remote_IP=None):
        self.name = name
        self.code = str(code).upper()
        self.serial_num = serial_num
        self.local_IP = local_IP
        self.remote_IP = remote_IP
        self.SN = self.serial_num

        class _pathto2(object):
            raw_ascii = pathto.raw_ascii % self.code
            raw_binary = pathto.raw_binary % self.code
            telemetry = pathto.telemetry % self.code
            timelapse_photos = pathto.timelapse_photos % self.code
            raw_std = pathto.raw_std % (self.code, '%s')
        self.pathto = _pathto2()

    def __repr__(self):
        return '<FieldSite: {name} [{code}]>'.format(name=self.name,
                                                     code=self.code)


"""Premade site objects available upon import"""
cfnt = FieldSite('Cook Agronomy Farm no-till',
                 'CFNT',
                 '6034',
                 ('192.168.174.33','255.255.255.0'),
                 ('166.139.116.107','255.255.255.0'))
lind = FieldSite('Lind Dryland Research Station',
                 'LIND',
                 '6035',
                 ('192.168.174.32','255.255.255.0'),
                 ('166.140.215.10','255.255.255.0'))
cfct = FieldSite('Cook Agronomy Farm conventional till',
                 'CFCT',
                 '6503',
                ('192.168.174.34','255.255.255.0'),
                 ('166.140.215.11','255.255.255.0'))
mmtn = FieldSite('Moscow Mountain',
                 'MMTN',
                 '6504',
                 ('192.168.174.35','255.255.255.0'),
                 ('166.140.215.12','255.255.255.0'))
mslk = FieldSite('Moses Lake',
                 'MSLK',
                 '6505',
                 ('192.168.174.36','255.255.255.0'),
                 ('166.154.195.59','255.255.255.0'))

site_list = [cfnt, lind, cfct, mmtn, mslk]
"""List of Site objects to iterate through

It's particularly useful to import this list as it contains all the objects
and their attributes. Iteration is straightforward:

    for site in site_list:
        print site.name
        srchdir = site.timelapse_photos
        # find files, do something
"""

sn2code = dict([[x.SN,x.code] for x in site_list])
"""Dictionary to look up site code from serial number

You can also get just the serial #s: sn2code.keys()
Or just the site codes: sn2code.values()

If you really need to get site SN based on 4char code, try using site_list:
    [site.SN for site in site_list if site.code='XXXX'][0]
or some similarly ridiculous alternative.
"""




table_definitions = {
    'tsdata' : ['TIMESTAMP',
                'RECORD',
                'Ux',
                'Uy',
                'Uz',
                'Ts',
                'diag_sonic',
                'CO2',
                'H2O',
                'diag_irga',
                'amb_tmpr',
                'amb_press',
                'CO2_signal',
                'H2O_signal'],

    # definition for stats5 after end of initial dict def.
    'stats30' : ['TIMESTAMP',
                 'RECORD',
                 'L',
                 'u_star',
                 'tau',
                 'Fc_wpl',
                 'LE_wpl',
                 'Hc',
                 'Ts_Avg',
                 'Ts_Std',
                 'Tc_Avg',
                 'Uz_Std',
                 'wnd_spd',
                 'rslt_wnd_spd',
                 'rslt_wnd_dir',
                 'std_wnd_dir',
                 'sonic_uptime',
                 'CO2_ppm_Avg',
                 'CO2_mg_m3_Avg',
                 'CO2_mg_m3_Std',
                 'CO2_signal_Avg',
                 'H2O_g_kg_Avg',
                 'H2O_g_m3_Avg',
                 'H2O_g_m3_Std',
                 'H2O_signal_Avg',
                 'amb_tmpr_Avg',
                 'amb_press_Avg',
                 'irga_uptime',
                 'T_hmp_Avg',
                 'RH_hmp_Avg',
                 'e_hmp_Avg',
                 'e_sat_hmp_Avg',
                 'Rn_Avg',
                 'Rn_meas_Avg',
                 'PAR_totflx_Tot',
                 'PAR_flxdens_Avg',
                 'Met1_wnd_spd',
                 'Met1_rslt_wnd_spd',
                 'Met1_rslt_wnd_dir',
                 'Met1_std_wnd_dir',
                 'Rain_mm_Tot',
                 'soil_5TM_ID5_E_Avg',
                 'soil_5TM_ID5_T_Avg',
                 'soil_5TM_ID5_VWC_Avg',
                 'soil_5TM_ID6_E_Avg',
                 'soil_5TM_ID6_T_Avg',
                 'soil_5TM_ID6_VWC_Avg',
                 'soil_5TM_ID7_E_Avg',
                 'soil_5TM_ID7_T_Avg',
                 'soil_5TM_ID7_VWC_Avg',
                 'soil_5TM_ID8_E_Avg',
                 'soil_5TM_ID8_T_Avg',
                 'soil_5TM_ID8_VWC_Avg',
                 'soil_5TM_ID9_E_Avg',
                 'soil_5TM_ID9_T_Avg',
                 'soil_5TM_ID9_VWC_Avg',
                 'soil_hfp1_heat_flux_Avg',
                 'soil_hfp1_sensitivity',
                 'soil_hfp2_heat_flux_Avg',
                 'soil_hfp2_sensitivity',
                 'panel_tmpr_Avg',
                 'batt_volt_Avg',
                 ],

    'site_daily' : ['TIMESTAMP',
                    'RECORD',
                    'latitude_Med',
                    'longitude_Med',
                    'magnetic_variation_Med',
                    'nmbr_satellites_Avg',
                    'altitude_Med',
                    'altitude_Avg',
                    'gps_ready_Min',
                    'max_clock_change',
                    'nmbr_clock_change',
                    'batt_volt_Min',
                    'batt_volt_TMn',
                    'batt_volt_Max',
                    'batt_volt_TMx',
                    'T_hmp_Min',
                    'T_hmp_TMn',
                    'T_hmp_Max',
                    'T_hmp_TMx'],

    'diagnostics' : ['TIMESTAMP',
                     'RECORD',
                     'total_scans',
                     'scans_1hz',
                     'scans_5s',
                     'skipped_10hz_scans',
                     'skipped_1hz_scans',
                     'skipped_5s_scans',
                     'watchdog_errors'],

    'site_info' : ['TIMESTAMP',
                   'RECORD',
                   'UTC_offset',
                   'sonic_azimuth',
                   'NRLite2_sens',
                   'LI190SB_sens',
                   'HFP_1_sens',
                   'HFP_2_sens',
                   'CompileResults',
                   'CardStatus',
                   'RunSig',
                   'ProgSig',
                   'hfp_installed'],

    'extra_info' : ['TIMESTAMP',
                    'RECORD',
                    'Decagon_NDVI_installed',
                    'Decagon_PRI_installed',
                    'LGR_n2oco_installed',
                    'lgr_n2o_mult',
                    'lgr_n2o_offset',
                    'lgr_co_mult',
                    'lgr_co_offset',
                    'lgr_h2o_mult',
                    'lgr_h2o_offset',
                    'Picarro_co2ch4_installed',
                    'pic_co2_mult',
                    'pic_co2_offset',
                    'pic_ch4_mult',
                    'pic_ch4_offset',
                    'pic_h2o_mult',
                    'pic_h2o_offset'],

    'tsdata_extra' : ['TIMESTAMP',
                      'RECORD',
                      'lgr_n2o',
                      'lgr_co',
                      'lgr_h2o',
                      'pic_co2',
                      'pic_ch4',
                      'pic_h2o'],

    # definitions for stats5_ui below dictionary definition
    'stats30_ui' : ['TIMESTAMP',
                    'RECORD',
                    'dec_ndvi_up1_Avg',
                    'dec_ndvi_up2_Avg',
                    'dec_ndvi_dn1_Avg',
                    'dec_ndvi_dn2_Avg',
                    'dec_pri_up1_Avg',
                    'dec_pri_up2_Avg',
                    'dec_pri_dn1_Avg',
                    'dec_pri_dn2_Avg',
                    'tblcalls_Tot'],

    # definition for stats5_6rad below dict def.
    'stats30_6rad' : ['TIMESTAMP',
                      'RECORD',
                      'dec_6rad_uplook_Avg(1)',
                      'dec_6rad_uplook_Avg(2)',
                      'dec_6rad_uplook_Avg(3)',
                      'dec_6rad_uplook_Avg(4)',
                      'dec_6rad_uplook_Avg(5)',
                      'dec_6rad_uplook_Avg(6)',
                      'dec_6rad_dnlook_Avg(1)',
                      'dec_6rad_dnlook_Avg(2)',
                      'dec_6rad_dnlook_Avg(3)',
                      'dec_6rad_dnlook_Avg(4)',
                      'dec_6rad_dnlook_Avg(5)',
                      'dec_6rad_dnlook_Avg(6)',
                      'tblcalls_Tot']
}
"""This dict holds lists describing the order of columns because the
   look-up dict cannot hold that information in a straightforward way. """
table_definitions['stats5'] = copy(table_definitions['stats30'])
table_definitions['stats5_6rad'] = copy(table_definitions['stats30_6rad'])
table_definitions['stats5_ui'] = copy(table_definitions['stats30_ui'])


table_baleinfo = {
    # dictionary holds info necessary to write output files of specific size
    #   outer key is name of existing table
    #   outer value is tuple of file-specific info
    #   tuple values, in order:
    #       grpby - specify data grouping for export; by months, days or if not
    #               broken up by dates, None
    #       start - function to obtain first timestamp of 'proper' file; since
    #               data column may not start at beginning of period (think
    #               file starts @ 8am for daily, not midnight) calculate the
    #               first timestamp
    #       offset - pandas.tseries.offsets object corresponding to size of
    #               desired output file or None if not splitting by date
    #       freq - intended frequency of output (and input) files. required
    #               and is used to properly pad output files; if table is
    #               recorded to irregularly (eg site_info) then freq is None
    #               and files are not padded to a standard frequency
    'tsdata' : ( [lambda x: x.year, lambda x: x.month, lambda x: x.day],
                 lambda x: x.index.normalize()[0],
                 Day(),
                 '100ms' ),

    'stats30' : ( [lambda x: x.year, lambda x: x.month],
                  lambda x: MonthBegin().rollback(x.index.normalize()[0]),
                  MonthBegin(),
                  '30T' ),

    'stats5' : ( [lambda x: x.year, lambda x: x.month],
                 lambda x: MonthBegin().rollback(x.index.normalize()[0]),
                 MonthBegin(),
                 '5T' ),

    'site_daily' : (None, lambda x: x.index.normalize()[0], None, '1D'),

    'diagnostics' : (None, lambda x: x.index.normalize()[0], None, None),

    'site_info' : (None, lambda x: x.index.normalize()[0], None, None),

    'extra_info' : (None, lambda x: x.index.normalize()[0], None, None),

    'tsdata_extra' : ( [lambda x: x.year, lambda x: x.month, lambda x: x.day],
                       lambda x: x.index.normalize()[0],
                       Day(),
                       '100ms' ),

    'stats30_ui' : ( [lambda x: x.year, lambda x: x.month],
                     lambda x: MonthBegin().rollback(x.index.normalize()[0]),
                     MonthBegin(),
                     '30T' ),

    'stats5_ui' : ( [lambda x: x.year, lambda x: x.month],
                    lambda x: MonthBegin().rollback(x.index.normalize()[0]),
                    MonthBegin(),
                    '5T' ),

    'stats30_6rad' : ( [lambda x: x.year, lambda x: x.month],
                       lambda x: MonthBegin().rollback(x.index.normalize()[0]),
                       MonthBegin(),
                       '30T' ),

    'stats5_6rad' : ( [lambda x: x.year, lambda x: x.month],
                      lambda x: MonthBegin().rollback(x.index.normalize()[0]),
                      MonthBegin(),
                      '5T' ),
    }


col_alias = {
    ########## 20130507_XXXX - CURRENT #####################################
    ('stats30_ui', 'TIMESTAMP') : ('', ''),
    ('stats30_ui', 'RECORD') : ('', ''),
    ('stats30_ui', 'dec_ndvi_up1_Avg') : ('', ''),
    ('stats30_ui', 'dec_ndvi_up2_Avg') : ('', ''),
    ('stats30_ui', 'dec_ndvi_dn1_Avg') : ('', ''),
    ('stats30_ui', 'dec_ndvi_dn2_Avg') : ('', ''),
    ('stats30_ui', 'dec_pri_up1_Avg') : ('', ''),
    ('stats30_ui', 'dec_pri_up2_Avg') : ('', ''),
    ('stats30_ui', 'dec_pri_dn1_Avg') : ('', ''),
    ('stats30_ui', 'dec_pri_dn2_Avg') : ('', ''),
    ('stats30_ui', 'tblcalls_Tot') : ('', ''),

    ('stats5_ui', 'TIMESTAMP') : ('', ''),
    ('stats5_ui', 'RECORD') : ('', ''),
    ('stats5_ui', 'dec_ndvi_up1_Avg') : ('', ''),
    ('stats5_ui', 'dec_ndvi_up2_Avg') : ('', ''),
    ('stats5_ui', 'dec_ndvi_dn1_Avg') : ('', ''),
    ('stats5_ui', 'dec_ndvi_dn2_Avg') : ('', ''),
    ('stats5_ui', 'dec_pri_up1_Avg') : ('', ''),
    ('stats5_ui', 'dec_pri_up2_Avg') : ('', ''),
    ('stats5_ui', 'dec_pri_dn1_Avg') : ('', ''),
    ('stats5_ui', 'dec_pri_dn2_Avg') : ('', ''),
    ('stats5_ui', 'tblcalls_Tot') : ('', ''),

    ('diagnostics', 'TIMESTAMP') : ('', ''),
    ('diagnostics', 'RECORD') : ('', ''),
    ('diagnostics', 'total_scans') : ('', ''),
    ('diagnostics', 'scans_1hz') : ('', ''),
    ('diagnostics', 'scans_5s') : ('', ''),
    ('diagnostics', 'skipped_10hz_scans') : ('', ''),
    ('diagnostics', 'skipped_1hz_scans') : ('', ''),
    ('diagnostics', 'skipped_5s_scans') : ('', ''),
    ('diagnostics', 'watchdog_errors') : ('', ''),

    ('tsdata_extra', 'TIMESTAMP') : ('', ''),
    ('tsdata_extra', 'RECORD') : ('', ''),
    ('tsdata_extra', 'lgr_n2o') : ('', ''),
    ('tsdata_extra', 'lgr_co') : ('', ''),
    ('tsdata_extra', 'lgr_h2o') : ('', ''),
    ('tsdata_extra', 'pic_co2') : ('', ''),
    ('tsdata_extra', 'pic_ch4') : ('', ''),
    ('tsdata_extra', 'pic_h2o') : ('', ''),

    ('extra_info', 'TIMESTAMP') : ('', ''),
    ('extra_info', 'RECORD') : ('', ''),
    ('extra_info', 'Decagon_NDVI_installed') : ('', ''),
    ('extra_info', 'Decagon_PRI_installed') : ('', ''),
    ('extra_info', 'LGR_n2oco_installed') : ('', ''),
    ('extra_info', 'lgr_n2o_mult') : ('', ''),
    ('extra_info', 'lgr_n2o_offset') : ('', ''),
    ('extra_info', 'lgr_co_mult') : ('', ''),
    ('extra_info', 'lgr_co_offset') : ('', ''),
    ('extra_info', 'lgr_h2o_mult') : ('', ''),
    ('extra_info', 'lgr_h2o_offset') : ('', ''),
    ('extra_info', 'Picarro_co2ch4_installed') : ('', ''),
    ('extra_info', 'pic_co2_mult') : ('', ''),
    ('extra_info', 'pic_co2_offset') : ('', ''),
    ('extra_info', 'pic_ch4_mult') : ('', ''),
    ('extra_info', 'pic_ch4_offset') : ('', ''),
    ('extra_info', 'pic_h2o_mult') : ('', ''),
    ('extra_info', 'pic_h2o_offset') : ('', ''),
    ########################################################################


    ########## 20120810_LIND - CURRENT #####################################
    ('stats30_hfp', 'TIMESTAMP') : (None, None),
    ('stats30_hfp', 'RECORD') : (None, None),
    ('stats30_hfp', 'soil_hfp1_heat_flux_Avg') : ('stats30', ''),
    ('stats30_hfp', 'soil_hfp1_sensitivity') : ('stats30', ''),
    ('stats30_hfp', 'soil_hfp2_heat_flux_Avg') : ('stats30', ''),
    ('stats30_hfp', 'soil_hfp2_sensitivity') : ('stats30', ''),
    ('stats30_hfp', 'hfp1_samples_Tot') : (None, None), # 20120824_LIND
    ('stats30_hfp', 'hfp2_samples_Tot') : (None, None), # 20120824_LIND
    ('stats30_hfp', 'tblcalls_Tot') : (None, None),

    ('stats5_hfp', 'TIMESTAMP') : (None, None),
    ('stats5_hfp', 'RECORD') : (None, None),
    ('stats5_hfp', 'soil_hfp1_heat_flux_Avg') : ('stats5', ''),
    ('stats5_hfp', 'soil_hfp1_sensitivity') : ('stats5', ''),
    ('stats5_hfp', 'soil_hfp2_heat_flux_Avg') : ('stats5', ''),
    ('stats5_hfp', 'soil_hfp2_sensitivity') : ('stats5', ''),
    ('stats5_hfp', 'hfp1_samples_Tot') : (None, None), # 20120824_LIND
    ('stats5_hfp', 'hfp2_samples_Tot') : (None, None), # 20120824_LIND
    ('stats5_hfp', 'tblcalls_Tot') : (None, None),
    ########################################################################


    ########## 20120627_CFCT - CURRENT #####################################
    ('site_info', 'TIMESTAMP') : ('', ''),
    ('site_info', 'RECORD') : ('', ''),
    ('site_info', 'UTC_offset') : ('', ''),
    ('site_info', 'sonic_azimuth') : ('', ''),
    ('site_info', 'NRLite2_sens') : ('', ''),
    ('site_info', 'LI190SB_sens') : ('', ''),
    ('site_info', 'HFP_1_sens') : ('', ''),
    ('site_info', 'HFP_2_sens') : ('', ''),
    ('site_info', 'CompileResults') : ('', ''),
    ('site_info', 'CardStatus') : ('', ''),
    ('site_info', 'RunSig') : ('', ''),
    ('site_info', 'ProgSig') : ('', ''),
    ('site_info', 'SENSOR_DEC_5TM') : (None, None), # 20120810_LIND
    ('site_info', 'SENSOR_DEC_6RAD') : ('', 'Dec_6rad_installed'),
    # XXX should these *installed variables be retained somehow?
    ('site_info', 'Dec_6rad_installed') : (None, None),
    ('site_info', 'SENSOR_LGR_N2OCO') : ('', 'LGR_n2o_co_installed'),
    ('site_info', 'LGR_n2o_co_installed') : ('extra_info', 'LGR_n2oco_installed'),
    ('site_info', 'SENSOR_PIC_CO2CH4') : ('', 'Pic_co2_ch4_installed'),
    ('site_info', 'Pic_co2_ch4_installed') : ('extra_info', 'Picarro_co2ch4_installed'),
    ('site_info', 'SENSOR_HFP01SC') : ('', 'hfp_installed'),
    ('site_info', 'hfp_installed') : ('', ''),
    ########################################################################


    ########## 20120627_CFCT - CURRENT #####################################
    ########## 20120427_CFNT  #############################################
    ('stats30_6rad', 'TIMESTAMP') : ('', ''),
    ('stats30_6rad', 'RECORD') : ('', ''),
    ('stats30_6rad', 'dec_6rad_up_Avg(1)') : ('', 'dec_6rad_uplook_Avg(1)'),
    ('stats30_6rad', 'dec_6rad_up_Avg(2)') : ('', 'dec_6rad_uplook_Avg(2)'),
    ('stats30_6rad', 'dec_6rad_up_Avg(3)') : ('', 'dec_6rad_uplook_Avg(3)'),
    ('stats30_6rad', 'dec_6rad_up_Avg(4)') : ('', 'dec_6rad_uplook_Avg(4)'),
    ('stats30_6rad', 'dec_6rad_up_Avg(5)') : ('', 'dec_6rad_uplook_Avg(5)'),
    ('stats30_6rad', 'dec_6rad_up_Avg(6)') : ('', 'dec_6rad_uplook_Avg(6)'),
    ('stats30_6rad', 'dec_6rad_dn_Avg(1)') : ('', 'dec_6rad_dnlook_Avg(1)'),
    ('stats30_6rad', 'dec_6rad_dn_Avg(2)') : ('', 'dec_6rad_dnlook_Avg(2)'),
    ('stats30_6rad', 'dec_6rad_dn_Avg(3)') : ('', 'dec_6rad_dnlook_Avg(3)'),
    ('stats30_6rad', 'dec_6rad_dn_Avg(4)') : ('', 'dec_6rad_dnlook_Avg(4)'),
    ('stats30_6rad', 'dec_6rad_dn_Avg(5)') : ('', 'dec_6rad_dnlook_Avg(5)'),
    ('stats30_6rad', 'dec_6rad_dn_Avg(6)') : ('', 'dec_6rad_dnlook_Avg(6)'),
    ('stats30_6rad', 'dec_6rad_uplook_Avg(1)') : ('', ''), # 20120627 - CURRENT
    ('stats30_6rad', 'dec_6rad_uplook_Avg(2)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_uplook_Avg(3)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_uplook_Avg(4)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_uplook_Avg(5)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_uplook_Avg(6)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_dnlook_Avg(1)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_dnlook_Avg(2)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_dnlook_Avg(3)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_dnlook_Avg(4)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_dnlook_Avg(5)') : ('', ''),
    ('stats30_6rad', 'dec_6rad_dnlook_Avg(6)') : ('', ''),
    ('stats30_6rad', 'tblcalls_Tot') : ('', ''), # add 20120824_LIND

    ('stats5_6rad', 'TIMESTAMP') : ('', ''),
    ('stats5_6rad', 'RECORD') : ('', ''),
    ('stats5_6rad', 'dec_6rad_up_Avg(1)') : ('', 'dec_6rad_uplook_Avg(1)'),
    ('stats5_6rad', 'dec_6rad_up_Avg(2)') : ('', 'dec_6rad_uplook_Avg(2)'),
    ('stats5_6rad', 'dec_6rad_up_Avg(3)') : ('', 'dec_6rad_uplook_Avg(3)'),
    ('stats5_6rad', 'dec_6rad_up_Avg(4)') : ('', 'dec_6rad_uplook_Avg(4)'),
    ('stats5_6rad', 'dec_6rad_up_Avg(5)') : ('', 'dec_6rad_uplook_Avg(5)'),
    ('stats5_6rad', 'dec_6rad_up_Avg(6)') : ('', 'dec_6rad_uplook_Avg(6)'),
    ('stats5_6rad', 'dec_6rad_dn_Avg(1)') : ('', 'dec_6rad_dnlook_Avg(1)'),
    ('stats5_6rad', 'dec_6rad_dn_Avg(2)') : ('', 'dec_6rad_dnlook_Avg(2)'),
    ('stats5_6rad', 'dec_6rad_dn_Avg(3)') : ('', 'dec_6rad_dnlook_Avg(3)'),
    ('stats5_6rad', 'dec_6rad_dn_Avg(4)') : ('', 'dec_6rad_dnlook_Avg(4)'),
    ('stats5_6rad', 'dec_6rad_dn_Avg(5)') : ('', 'dec_6rad_dnlook_Avg(5)'),
    ('stats5_6rad', 'dec_6rad_dn_Avg(6)') : ('', 'dec_6rad_dnlook_Avg(6)'),
    ('stats5_6rad', 'dec_6rad_uplook_Avg(1)') : ('', ''), # 20120627 - CURRENT
    ('stats5_6rad', 'dec_6rad_uplook_Avg(2)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_uplook_Avg(3)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_uplook_Avg(4)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_uplook_Avg(5)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_uplook_Avg(6)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_dnlook_Avg(1)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_dnlook_Avg(2)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_dnlook_Avg(3)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_dnlook_Avg(4)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_dnlook_Avg(5)') : ('', ''),
    ('stats5_6rad', 'dec_6rad_dnlook_Avg(6)') : ('', ''),
    ('stats5_6rad', 'tblcalls_Tot') : ('', ''), # add 20120824_LIND
    #######################################################################


    ########## 20120309_LIND - CURRENT #####################################
    ('tsdata', 'TIMESTAMP') : ('', ''),
    ('tsdata', 'RECORD') : ('', ''),
    ('tsdata', 'Ux') : ('', ''),
    ('tsdata', 'Uy') : ('', ''),
    ('tsdata', 'Uz') : ('', ''),
    ('tsdata', 'Ts') : ('', ''),
    ('tsdata', 'diag_sonic') : ('', ''),
    ('tsdata', 'CO2') : ('', ''),
    ('tsdata', 'H2O') : ('', ''),
    ('tsdata', 'diag_irga') : ('', ''),
    ('tsdata', 'amb_tmpr') : ('', ''),
    ('tsdata', 'amb_press') : ('', ''),
    ('tsdata', 'CO2_signal') : ('', ''),
    ('tsdata', 'H2O_signal') : ('', ''),

    ('stats30', 'TIMESTAMP') : ('', ''),
    ('stats30', 'RECORD') : ('', ''),
    ('stats30', 'L') : ('', ''),
    ('stats30', 'u_star') : ('', ''),
    ('stats30', 'tau') : ('', ''),
    ('stats30', 'Fc_wpl') : ('', ''),
    ('stats30', 'LE_wpl') : ('', ''),
    ('stats30', 'Hc') : ('', ''),
    ('stats30', 'Ts_Avg') : ('', ''),
    ('stats30', 'Ts_Std') : ('', ''),
    ('stats30', 'Tc_Avg') : ('', ''),
    ('stats30', 'Uz_Std') : ('', ''),
    ('stats30', 'wnd_spd') : ('', ''),
    ('stats30', 'rslt_wnd_spd') : ('', ''),
    ('stats30', 'rslt_wnd_dir') : ('', ''),
    ('stats30', 'std_wnd_dir') : ('', ''),
    ('stats30', 'sonic_uptime') : ('', ''), # added 20120215_CFNT
    ('stats30', 'CO2_ppm_Avg_Avg') : ('', 'CO2_ppm_Avg'), # FIX see 20131018_XXXX
    ('stats30', 'CO2_ppm_Avg') : ('', ''),
    ('stats30', 'CO2_mg_m3_Avg') : ('', ''),
    ('stats30', 'CO2_mg_m3_Std') : ('', ''),
    ('stats30', 'CO2_signal_Avg') : ('', ''),
    ('stats30', 'H2O_g_kg_Avg') : ('', ''), # added 20120215_CFNT
    ('stats30', 'H2O_g_m3_Avg') : ('', ''),
    ('stats30', 'H2O_g_m3_Std') : ('', ''),
    ('stats30', 'H2O_signal_Avg') : ('', ''),
    ('stats30', 'amb_tmpr_Avg') : ('', ''), # added 20120215_CFNT
    ('stats30', 'amb_press_Avg') : ('', ''),
    ('stats30', 'irga_uptime') : ('', ''), # added 20120215_CFNT
    ('stats30', 'T_hmp_Avg') : ('', ''),
    ('stats30', 'RH_hmp_Avg') : ('', ''),
    ('stats30', 'e_hmp_Avg') : ('', ''), # added 20120215_CFNT
    ('stats30', 'e_sat_hmp_Avg') : ('', ''), # added 20120215_CFNT
    ('stats30', 'Rn_Avg') : ('', ''),
    ('stats30', 'Rn_meas_Avg') : ('', ''),
    ('stats30', 'PAR_totflx_Tot') : ('', ''),
    ('stats30', 'PAR_flxdens_Avg') : ('', ''),
    ('stats30', 'Met1_wnd_spd') : ('', ''),
    ('stats30', 'Met1_rslt_wnd_spd') : ('', ''),
    ('stats30', 'Met1_wnd_dir') : ('', 'Met1_rslt_wnd_dir'),#20120316_CFNT
    ('stats30', 'Met1_rslt_wnd_dir') : ('', ''),
    ('stats30', 'Met1_std_wnd_dir') : ('', ''),
    ('stats30', 'Rain_mm_Tot') : ('', ''),
    ('stats30', 'soil_5TM_ID5_epsilon_Avg') : ('', 'soil_5TM_ID5_E_Avg'),#20120824_LIND
    ('stats30', 'soil_5TM_ID5_E_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID5_T_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID5_VWC_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID6_epsilon_Avg') : ('', 'soil_5TM_ID6_E_Avg'),#20120824_LIND
    ('stats30', 'soil_5TM_ID6_E_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID6_T_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID6_VWC_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID7_epsilon_Avg') : ('', 'soil_5TM_ID7_E_Avg'),#20120824_LIND
    ('stats30', 'soil_5TM_ID7_E_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID7_T_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID7_VWC_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID8_epsilon_Avg') : ('', 'soil_5TM_ID8_E_Avg'),#20120824_LIND
    ('stats30', 'soil_5TM_ID8_E_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID8_T_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID8_VWC_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID9_epsilon_Avg') : ('', 'soil_5TM_ID9_E_Avg'),#20120824_LIND
    ('stats30', 'soil_5TM_ID9_E_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID9_T_Avg') : ('', ''),
    ('stats30', 'soil_5TM_ID9_VWC_Avg') : ('', ''),
    ('stats30', 'soil_hfp1_heat_flux_Avg') : ('', ''), # 20130507_XXXX
    ('stats30', 'soil_hfp1_sensitivity') : ('', ''), # 20130507_XXXX
    ('stats30', 'soil_hfp2_heat_flux_Avg') : ('', ''), # 20130507_XXXX
    ('stats30', 'soil_hfp2_sensitivity') : ('', ''), # 20130507_XXXX
    ('stats30', 'panel_tmpr_Avg') : ('', ''),
    ('stats30', 'batt_volt_Avg') : ('', ''),

    ('stats5', 'TIMESTAMP') : ('', ''),
    ('stats5', 'RECORD') : ('', ''),
    ('stats5', 'L') : ('', ''),
    ('stats5', 'u_star') : ('', ''),
    ('stats5', 'tau') : ('', ''),
    ('stats5', 'Fc_wpl') : ('', ''),
    ('stats5', 'LE_wpl') : ('', ''),
    ('stats5', 'Hc') : ('', ''),
    ('stats5', 'Ts_Avg') : ('', ''),
    ('stats5', 'Ts_Std') : ('', ''),
    ('stats5', 'Tc_Avg') : ('', ''),
    ('stats5', 'Uz_Std') : ('', ''),
    ('stats5', 'wnd_spd') : ('', ''),
    ('stats5', 'rslt_wnd_spd') : ('', ''),
    ('stats5', 'rslt_wnd_dir') : ('', ''),
    ('stats5', 'std_wnd_dir') : ('', ''),
    ('stats5', 'sonic_uptime') : ('', ''), # added 20120215_CFNT
    ('stats5', 'CO2_ppm_Avg_Avg') : ('', 'CO2_ppm_Avg'), # FIX see 20131018_XXXX
    ('stats5', 'CO2_ppm_Avg') : ('', ''),
    ('stats5', 'CO2_mg_m3_Avg') : ('', ''),
    ('stats5', 'CO2_mg_m3_Std') : ('', ''),
    ('stats5', 'CO2_signal_Avg') : ('', ''),
    ('stats5', 'H2O_g_kg_Avg') : ('', ''), # added 20120215_CFNT
    ('stats5', 'H2O_g_m3_Avg') : ('', ''),
    ('stats5', 'H2O_g_m3_Std') : ('', ''),
    ('stats5', 'H2O_signal_Avg') : ('', ''),
    ('stats5', 'amb_tmpr_Avg') : ('', ''), # added 20120215_CFNT
    ('stats5', 'amb_press_Avg') : ('', ''),
    ('stats5', 'irga_uptime') : ('', ''), # added 20120215_CFNT
    ('stats5', 'T_hmp_Avg') : ('', ''),
    ('stats5', 'RH_hmp_Avg') : ('', ''),
    ('stats5', 'e_hmp_Avg') : ('', ''), # added 20120215_CFNT
    ('stats5', 'e_sat_hmp_Avg') : ('', ''), # added 20120215_CFNT
    ('stats5', 'Rn_Avg') : ('', ''),
    ('stats5', 'Rn_meas_Avg') : ('', ''),
    ('stats5', 'PAR_totflx_Tot') : ('', ''),
    ('stats5', 'PAR_flxdens_Avg') : ('', ''),
    ('stats5', 'Met1_wnd_spd') : ('', ''),
    ('stats5', 'Met1_rslt_wnd_spd') : ('', ''),
    ('stats5', 'Met1_wnd_dir') : ('', 'Met1_rslt_wnd_dir'),#20120316_CFNT
    ('stats5', 'Met1_rslt_wnd_dir') : ('', ''),
    ('stats5', 'Met1_std_wnd_dir') : ('', ''),
    ('stats5', 'Rain_mm_Tot') : ('', ''),
    ('stats5', 'soil_5TM_ID5_epsilon_Avg') : ('', 'soil_5TM_ID5_E_Avg'),#20120824_LIND
    ('stats5', 'soil_5TM_ID5_E_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID5_T_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID5_VWC_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID6_epsilon_Avg') : ('', 'soil_5TM_ID6_E_Avg'),#20120824_LIND
    ('stats5', 'soil_5TM_ID6_E_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID6_T_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID6_VWC_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID7_epsilon_Avg') : ('', 'soil_5TM_ID7_E_Avg'),#20120824_LIND
    ('stats5', 'soil_5TM_ID7_E_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID7_T_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID7_VWC_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID8_epsilon_Avg') : ('', 'soil_5TM_ID8_E_Avg'),#20120824_LIND
    ('stats5', 'soil_5TM_ID8_E_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID8_T_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID8_VWC_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID9_epsilon_Avg') : ('', 'soil_5TM_ID9_E_Avg'),#20120824_LIND
    ('stats5', 'soil_5TM_ID9_E_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID9_T_Avg') : ('', ''),
    ('stats5', 'soil_5TM_ID9_VWC_Avg') : ('', ''),
    ('stats5', 'soil_hfp1_heat_flux_Avg') : ('', ''), # 20130507_XXXX
    ('stats5', 'soil_hfp1_sensitivity') : ('', ''), # 20130507_XXXX
    ('stats5', 'soil_hfp2_heat_flux_Avg') : ('', ''), # 20130507_XXXX
    ('stats5', 'soil_hfp2_sensitivity') : ('', ''), # 20130507_XXXX
    ('stats5', 'panel_tmpr_Avg') : ('', ''),
    ('stats5', 'batt_volt_Avg') : ('', ''),

    ('site_daily', 'TIMESTAMP') : ('', ''),
    ('site_daily', 'RECORD') : ('', ''),
    # TODO should some daily values be moved into to site_info table?
    ('site_daily', 'sonic_azimuth') : (None, None), # 20120627_CFCT
    ('site_daily', 'latitude') : ('', 'latitude_Med'), #20120323_LIND
    ('site_daily', 'latitude_Med') : ('', ''),
    ('site_daily', 'latitude_a_Avg') : (None, None), # 20120316_CFNT
    ('site_daily', 'latitude_b_Avg') : (None, None), # 20120316_CFNT
    ('site_daily', 'longitude') : ('', 'longitude_Med'), # 20120323_LIND
    ('site_daily', 'longitude_Med') : ('', ''),
    ('site_daily', 'longitude_a_Avg') : (None, None), # 20120316_CFNT
    ('site_daily', 'longitude_b_Avg') : (None, None), # 20120316_CFNT
    ('site_daily', 'magnetic_variation_Med') : ('', ''), # add 20120309_LIND
    ('site_daily', 'magnetic_variation_Avg') : (None, None), # 20120323_LIND
    ('site_daily', 'nmbr_satellites_Avg') : ('', ''),
    ('site_daily', 'altitude_Med') : ('', ''), # add 20120309_LIND
    ('site_daily', 'altitude_Avg') : ('', ''),
    ('site_daily', 'gps_ready_Min') : ('', ''),
    ('site_daily', 'max_clock_change') : ('', ''),
    ('site_daily', 'nmbr_clock_change') : ('', ''),
    # TODO figure out how to integrate disparate time-base variables like runsig
    ('site_daily', 'RunSig') : (None, None), # 20120627_CFCT
    ('site_daily', 'ProgSig') : (None, None), # 20120627_CFCT
    ('site_daily', 'batt_volt_Min') : ('', ''), # add 20130507_XXXX
    ('site_daily', 'batt_volt_TMn') : ('', ''), #
    ('site_daily', 'batt_volt_Max') : ('', ''), #
    ('site_daily', 'batt_volt_TMx') : ('', ''), #  ..
    ('site_daily', 'T_hmp_Min') : ('', ''), #
    ('site_daily', 'T_hmp_TMn') : ('', ''), #
    ('site_daily', 'T_hmp_Max') : ('', ''), #
    ('site_daily', 'T_hmp_TMx') : ('', ''), # add 20130507_XXXX
    ########################################################################


    ########## 20120330_CFNT - 20120727_LIND ###############################
    ('stats30_soil', 'TIMESTAMP') : (None, None), # merged into stats30 table
    ('stats30_soil', 'RECORD') : (None, None),
    ('stats30_soil', 'soil_5TM_ID5_epsilon_Avg') : ('stats30', ''), #20120810_LIND
    ('stats30_soil', 'soil_5TM_ID5_T_Avg') : ('stats30', ''), # all are affected
    ('stats30_soil', 'soil_5TM_ID5_VWC_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID6_epsilon_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID6_T_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID6_VWC_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID7_epsilon_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID7_T_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID7_VWC_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID8_epsilon_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID8_T_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID8_VWC_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID9_epsilon_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID9_T_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_5TM_ID9_VWC_Avg') : ('stats30', ''),
    ('stats30_soil', 'soil_hfp1_heat_flux_Avg') : ('stats30_hfp', ''),
    ('stats30_soil', 'soil_hfp1_sensitivity') : ('stats30_hfp', ''),
    ('stats30_soil', 'soil_hfp2_heat_flux_Avg') : ('stats30_hfp', ''),
    ('stats30_soil', 'soil_hfp2_sensitivity') : ('stats30_hfp', ''),

    ('stats5_soil', 'TIMESTAMP') : (None, None), # merged into stats5 table
    ('stats5_soil', 'RECORD') : (None, None),
    ('stats5_soil', 'soil_5TM_ID5_epsilon_Avg') : ('stats5', ''), #20120810_LIND
    ('stats5_soil', 'soil_5TM_ID5_T_Avg') : ('stats5', ''), # all are affected
    ('stats5_soil', 'soil_5TM_ID5_VWC_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID6_epsilon_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID6_T_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID6_VWC_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID7_epsilon_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID7_T_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID7_VWC_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID8_epsilon_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID8_T_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID8_VWC_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID9_epsilon_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID9_T_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_5TM_ID9_VWC_Avg') : ('stats5', ''),
    ('stats5_soil', 'soil_hfp1_heat_flux_Avg') : ('stats5_hfp', ''),
    ('stats5_soil', 'soil_hfp1_sensitivity') : ('stats5_hfp', ''),
    ('stats5_soil', 'soil_hfp2_heat_flux_Avg') : ('stats5_hfp', ''),
    ('stats5_soil', 'soil_hfp2_sensitivity') : ('stats5_hfp', ''),
    #########################################################################


    ###### 20120504_LIND, 20120628_CFNT and 20120720_CFNT #################
    # TODO what to do with LGR data?
    ('tsdata_n2o_co', 'TIMESTAMP') : (None, None),
    ('tsdata_n2o_co', 'RECORD') : (None, None),
    ('tsdata_n2o_co', 'lgr_n2o') : ('tsdata_extra', 'lgr_n2o'),
    ('tsdata_n2o_co', 'lgr_co') : ('tsdata_extra', 'lgr_co'),

    ('stats30_n2o_co', 'TIMESTAMP') : ('', ''),
    ('stats30_n2o_co', 'RECORD') : ('', ''),
    ('stats30_n2o_co', 'lgr_n2o_Avg') : ('', ''),
    ('stats30_n2o_co', 'lgr_n2o_Std') : ('', ''),
    ('stats30_n2o_co', 'lgr_co_Avg') : ('', ''),
    ('stats30_n2o_co', 'lgr_co_Std') : ('', ''),
    ('stats30_n2o_co', 'lgr_uptime') : ('', 'lgr_n2o_co_uptime'),
    ('stats30_n2o_co', 'cov_n2o_Uz') : (None, None), # cfnt update
    ('stats30_n2o_co', 'cov_co_Uz') : (None, None), # cfnt update
    ('stats30_n2o_co', 'lgr_n2o_co_uptime') : ('', ''), # cfnt update

    ('stats5_n2o_co', 'TIMESTAMP') : ('', ''),
    ('stats5_n2o_co', 'RECORD') : ('', ''),
    ('stats5_n2o_co', 'lgr_n2o_Avg') : ('', ''),
    ('stats5_n2o_co', 'lgr_n2o_Std') : ('', ''),
    ('stats5_n2o_co', 'lgr_co_Avg') : ('', ''),
    ('stats5_n2o_co', 'lgr_co_Std') : ('', ''),
    ('stats5_n2o_co', 'lgr_uptime') : ('', 'lgr_n2o_co_uptime'),
    ('stats5_n2o_co', 'cov_n2o_Uz') : (None, None), # cfnt update
    ('stats5_n2o_co', 'cov_co_Uz') : (None, None), # cfnt update
    ('stats5_n2o_co', 'lgr_n2o_co_uptime') : ('', ''), # cfnt update
    ########################################################################


    ########## 20120420_LIND only ##########################################
    ## re-adopted this format with 20130507_XXXX
    #('tsdata_extra', 'TIMESTAMP') : ('tsdata_n2o_co', ''),
    #('tsdata_extra', 'RECORD') : ('tsdata_n2o_co', ''),
    #('tsdata_extra', 'lgr_n2o') : ('tsdata_n2o_co', ''),
    #('tsdata_extra', 'lgr_co') : ('tsdata_n2o_co', ''),
    ##

    ('stats30_extra', 'TIMESTAMP') : ('stats30_n2o_co', ''),
    ('stats30_extra', 'RECORD') : ('stats30_n2o_co', ''),
    ('stats30_extra', 'lgr_n2o_Avg') : ('stats30_n2o_co', ''),
    ('stats30_extra', 'lgr_n2o_Std') : ('stats30_n2o_co', ''),
    ('stats30_extra', 'lgr_co_Avg') : ('stats30_n2o_co', ''),
    ('stats30_extra', 'lgr_co_Std') : ('stats30_n2o_co', ''),
    ('stats30_extra', 'lgr_uptime') : ('stats30_n2o_co', ''),
    ('stats30_extra', 'cov_n2o_Uz') : ('stats30_n2o_co', ''), # 20120504_LIND
    ('stats30_extra', 'cov_co_Uz') : ('stats30_n2o_co', ''), # 20120504_LIND

    ('stats5_extra', 'TIMESTAMP') : ('stats5_n2o_co', ''),
    ('stats5_extra', 'RECORD') : ('stats5_n2o_co', ''),
    ('stats5_extra', 'lgr_n2o_Avg') : ('stats5_n2o_co', ''),
    ('stats5_extra', 'lgr_n2o_Std') : ('stats5_n2o_co', ''),
    ('stats5_extra', 'lgr_co_Avg') : ('stats5_n2o_co', ''),
    ('stats5_extra', 'lgr_co_Std') : ('stats5_n2o_co', ''),
    ('stats5_extra', 'lgr_uptime') : ('stats5_n2o_co', ''),
    ('stats5_extra', 'cov_n2o_Uz') : ('stats5_n2o_co', ''), # 20120504_LIND
    ('stats5_extra', 'cov_co_Uz') : ('stats5_n2o_co', ''), # 20120504_LIND
    ########################################################################


    ########## 20120210_CFNT - 20120309_CFNT ###############################
    ('CFNT_tsdata', 'TIMESTAMP') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'RECORD') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'Ux') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'Uy') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'Uz') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'Ts') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'diag_sonic') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'CO2') : ('tsdata', ''),  #20120309_LIND
    ('CFNT_tsdata', 'H2O') : ('tsdata', ''), #20120309_LIND
    ('CFNT_tsdata', 'diag_irga') : ('tsdata', ''),  #20120309_LIND
    ('CFNT_tsdata', 'amb_tmpr') : ('tsdata', ''),  #20120309_LIND
    ('CFNT_tsdata', 'amb_press') : ('tsdata', ''),  #20120309_LIND
    ('CFNT_tsdata', 'CO2_signal') : ('tsdata', ''),  #20120309_LIND
    ('CFNT_tsdata', 'H2O_signal') : ('tsdata', ''), #20120309_LIND

    ('CFNT_stats30', 'TIMESTAMP') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'RECORD') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'L') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'u_star') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'tau') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Fc_wpl') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'LE_wpl') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Hc') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Ts_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Ts_Std') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Tc_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Tc_Std') : (None, None), # 20120215_CFNT
    ('CFNT_stats30', 'Uz_Std') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'wnd_spd') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'rslt_wnd_spd') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'std_wnd_dir') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'wnd_dir_compass') : ('stats30', 'rslt_wnd_dir'),#20120309_LIND
    ('CFNT_stats30', 'sonic_samples_Tot') : (None, None), # 20120215_CFNT
    ('CFNT_stats30', 'sonic_uptime') : ('stats30', ''), # added 20120215_CFNT
    ('CFNT_stats30', 'CO2_ppm_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'CO2_ppm_Std') : (None, None), # only in 20120224_LIND
    ('CFNT_stats30', 'CO2_mg_m3_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'CO2_mg_m3_Std') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'CO2_signal_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'H2O_g_kg_Avg') : ('stats30', ''), # added 20120215_CFNT
    ('CFNT_stats30', 'H2O_g_kg_Std') : (None, None), # only in 20120224_LIND
    ('CFNT_stats30', 'H2O_g_m3_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'H2O_g_m3_Std') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'H2O_signal_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'amb_tmpr_Avg') : ('stats30', ''), # added 20120215_CFNT
    ('CFNT_stats30', 'amb_press_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'irga_samples_Tot') : (None, None), # only in 20120224_LIND
    ('CFNT_stats30', 'irga_uptime') : ('stats30', ''), # added 20120215_CFNT
    ('CFNT_stats30', 'T_hmp_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'RH_hmp_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'e_hmp_Avg') : ('stats30', ''), # added 20120215_CFNT
    ('CFNT_stats30', 'e_sat_hmp_Avg') : ('stats30', ''), # added 20120215_CFNT
    ('CFNT_stats30', 'hmp_uptime') : (None, None), # only in 20120224_LIND
    ('CFNT_stats30', 'Rn_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Rn_meas_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'PAR_totflx_Tot') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'PAR_flxdens_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Met1_wnd_spd') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Met1_rslt_wnd_spd') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Met1_wnd_dir') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Met1_std_wnd_dir') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'Met1_uptime') : (None, None), # only in 20120224_LIND
    ('CFNT_stats30', 'Rain_mm_Tot') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'panel_tmpr_Avg') : ('stats30', ''), #20120309_LIND
    ('CFNT_stats30', 'batt_volt_Avg') : ('stats30', ''), #20120309_LIND

    ('CFNT_stats5', 'TIMESTAMP') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'RECORD') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'L') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'u_star') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'tau') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Fc_wpl') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'LE_wpl') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Hc') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Ts_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Ts_Std') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Tc_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Tc_Std') : (None, None), # 20120215_CFNT
    ('CFNT_stats5', 'Uz_Std') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'wnd_spd') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'rslt_wnd_spd') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'std_wnd_dir') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'wnd_dir_compass') : ('stats5', 'rslt_wnd_spd'), #20120309_LIND
    ('CFNT_stats5', 'sonic_samples_Tot') : (None, None), # 20120215_CFNT
    ('CFNT_stats5', 'sonic_uptime') : ('stats5', ''), # added 20120215_CFNT
    ('CFNT_stats5', 'CO2_ppm_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'CO2_ppm_Std') : (None, None), # only in 20120224_LIND
    ('CFNT_stats5', 'CO2_mg_m3_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'CO2_mg_m3_Std') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'CO2_signal_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'H2O_g_kg_Avg') : ('stats5', ''), # added 20120215_CFNT
    ('CFNT_stats5', 'H2O_g_kg_Std') : (None, None), # only in 20120224_LIND
    ('CFNT_stats5', 'H2O_g_m3_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'H2O_g_m3_Std') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'H2O_signal_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'amb_tmpr_Avg') : ('stats5', ''), # added 20120215_CFNT
    ('CFNT_stats5', 'amb_press_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'irga_samples_Tot') : (None, None), # only in 20120224_LIND
    ('CFNT_stats5', 'irga_uptime') : ('stats5', ''), # added 20120215_CFNT
    ('CFNT_stats5', 'T_hmp_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'RH_hmp_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'e_hmp_Avg') : ('stats5', ''), # added 20120215_CFNT
    ('CFNT_stats5', 'e_sat_hmp_Avg') : ('stats5', ''), # added 20120215_CFNT
    ('CFNT_stats5', 'hmp_uptime') : (None, None), # only in 20120224_LIND
    ('CFNT_stats5', 'Rn_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Rn_meas_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'PAR_totflx_Tot') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'PAR_flxdens_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Met1_wnd_spd') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Met1_rslt_wnd_spd') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Met1_wnd_dir') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Met1_std_wnd_dir') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'Met1_uptime') : (None, None), # only in 20120224_LIND
    ('CFNT_stats5', 'Rain_mm_Tot') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'panel_tmpr_Avg') : ('stats5', ''), #20120309_LIND
    ('CFNT_stats5', 'batt_volt_Avg') : ('stats5', ''), #20120309_LIND

    ('CFNT_site_daily', 'TIMESTAMP') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'RECORD') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'sonic_azimuth') : ('site_daily', ''), #add 20120215_CFNT
    ('CFNT_site_daily', 'latitude_a_Avg') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'latitude_b_Avg') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'longitude_a_Avg') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'longitude_b_Avg') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'latitude_a_Std') : (None, None), # 20120215_CFNT
    ('CFNT_site_daily', 'latitude_b_Std') : (None, None), # 20120215_CFNT
    ('CFNT_site_daily', 'longitude_a_Std') : (None, None), # 20120215_CFNT
    ('CFNT_site_daily', 'longitude_b_Std') : (None, None), # 20120215_CFNT
    ('CFNT_site_daily', 'magnetic_variation_Avg') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'magnetic_variation_Std') : (None, None), # 20120215_CFNT
    ('CFNT_site_daily', 'nmbr_satellites_Avg') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'altitude_Avg') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'altitude_Std') : (None, None), # 20120215_CFNT
    ('CFNT_site_daily', 'gps_ready_Min') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'max_clock_change') : ('site_daily', ''), #20120309_LIND
    ('CFNT_site_daily', 'nmbr_clock_change') : ('site_daily', ''), #20120309_LIND
    ########################################################################


    ########## 20120204_CFNT only ###########################################
    ('CFNT_met_5min', 'TIMESTAMP') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'RECORD') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'L') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'Hs') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'u_star') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'Ts_stdev') : ('CFNT_stats5', 'Ts_Std'), # 20120210_CFNT
    ('CFNT_met_5min', 'Uz_stdev') : ('CFNT_stats5', 'Uz_Std'), # 20120210_CFNT
    ('CFNT_met_5min', 'wnd_spd') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'rslt_wnd_spd') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'std_wnd_dir') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'wnd_dir_compass') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'Ts_Avg') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'sonic_samples_Tot') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'Fc_wpl') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'LE_wpl') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'Hc') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'CO2_stdev') : ('CFNT_stats5', 'CO2_mg_m3_Std'), # 20120210_CFNT
    ('CFNT_met_5min', 'H2O_stdev') : ('CFNT_stats5', 'H2O_g_m3_Std'), # 20120210_CFNT
    ('CFNT_met_5min', 'Tc_stdev') : ('CFNT_stats5', 'Tc_Std'), # 20120210_CFNT
    ('CFNT_met_5min', 'CO2_mean') : ('CFNT_stats5', 'CO2_mg_m3_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'H2O_mean') : ('CFNT_stats5', 'H2O_g_m3_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'amb_press_mean') : ('CFNT_stats5', 'amb_press_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'Tc_mean') : ('CFNT_stats5', 'Tc_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'CO2_sig_strgth_mean') : ('CFNT_stats5', 'CO2_signal_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'H2O_sig_strgth_mean') : ('CFNT_stats5', 'H2O_signal_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'T_hmp_mean') : ('CFNT_stats5', 'T_hmp_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'RH_hmp_mean') : ('CFNT_stats5', 'RH_hmp_Avg'), # 20120210_CFNT
    ('CFNT_met_5min', 'Rn_Avg') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'Rn_meas_Avg') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'PAR_totflx_Tot') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'PAR_flxdens_Avg') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', '034b_ws2') : ('CFNT_stats5', 'Met1_wnd_spd'), # 20120210_CFNT
    ('CFNT_met_5min', '034b_wd2') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', '034b_stdwd2') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'Rain_mm_Tot') : ('CFNT_stats5', ''), # 20120210_CFNT
    # TODO should this 5min GPS data be merged into site daily files?
    ('CFNT_met_5min', 'latitude_a') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'latitude_b') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'longitude_a') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'longitude_b') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'magnetic_variation') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'altitude') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'max_clock_change') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'nmbr_clock_change') : (None, None), # 20120210_CFNT
    ('CFNT_met_5min', 'panel_tmpr_Avg') : ('CFNT_stats5', ''), # 20120210_CFNT
    ('CFNT_met_5min', 'batt_volt_Avg') : ('CFNT_stats5', ''), # 20120210_CFNT
    #########################################################################


    ########## 20111024_CFNT to 20111027_CFNT ###############################
    ('extra_gas', 'TIMESTAMP') : (None, None),
    ('extra_gas', 'RECORD') : (None, None),
    ('extra_gas', 'n2o_Avg') : (None, None),
    ('extra_gas', 'c_monoxide_Avg') : (None, None),
    ('extra_gas', 'ch4_Avg') : (None, None),
    ('extra_gas', 'co2_picarro_Avg') : (None, None),
    ('extra_gas', 'co2_mix_ratio_Avg') : (None, None),
    ('extra_gas', 'h2o_mix_ratio_Avg') : (None, None),
    ('extra_gas', '034b_ws') : (None, None), # add 20111027
    ('extra_gas', '034b_wd') : (None, None), # add 20111027
    ('extra_gas', '034b_stdwd') : (None, None), # add 20111027
    #########################################################################


    ########## 20110819_CFNT to 20120204_CFNT ###############################
    ('ts_data', 'TIMESTAMP') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'RECORD') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'Ux') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'Uy') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'Uz') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'Ts') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'diag_sonic') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'atiUx') : (None, None), # 20111009_CFNT
    ('ts_data', 'atiUy') : (None, None), # 20111009_CFNT
    ('ts_data', 'atiUz') : (None, None), # 20111009_CFNT
    ('ts_data', 'atiTs') : (None, None), # 20111009_CFNT
    ('ts_data', 'CO2_molar') : ('', 'co2_molar_density'), # 20111009_CFNT
    ('ts_data', 'H2O_molar') : ('', 'h2o_molar_density'), # 20111009_CFNT
    ('ts_data', 'co2_molar_density') : (None, None), # 20120210_CFNT
    ('ts_data', 'h2o_molar_density') : (None, None), # 20120210_CFNT
    ('ts_data', 'co2_mix_ratio') : ('', 'co2_molar_density'), # 20111024_CFNT
    ('ts_data', 'h2o_mix_ratio') : ('', 'h2o_molar_density'), # 20111024_CFNT
    ('ts_data', 'n2o') : ('tsdata_extra', 'lgr_n2o'), # 20111024_CFNT
    ('ts_data', 'c_monoxide') : ('tsdata_extra', 'lgr_co'), # 20111024_CFNT
    ('ts_data', 'ch4') : ('tsdata_extra', 'pic_ch4'), # 20111024_CFNT
    ('ts_data', 'co2_picarro') : ('tsdata_extra', 'pic_co2'), # 20111024_CFNT
    ('ts_data', 'CO2') : ('CFNT_tsdata', ''),  # 20120210_CFNT
    ('ts_data', 'H2O') : ('CFNT_tsdata', ''), # 20120210_CFNT
    ('ts_data', 'diag_irga') : ('CFNT_tsdata', ''),  # 20120210_CFNT
    ('ts_data', 'amb_tmpr') : ('CFNT_tsdata', ''),  # 20120210_CFNT
    ('ts_data', 'amb_press') : ('CFNT_tsdata', ''),  # 20120210_CFNT
    ('ts_data', 'CO2_sig_strgth') : ('CFNT_tsdata', 'CO2_signal'), # 20120210_CFNT
    ('ts_data', 'H2O_sig_strgth') : ('CFNT_tsdata', 'H2O_signal'), # 20120210_CFNT

    ('flux', 'TIMESTAMP') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'RECORD') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'l') : ('', 'L'), # 20120204_CFNT
    ('flux', 'L') : ('CFNT_stats30', ''), # 20120204_CFNT
    ('flux', 'Hs') : (None, None), # 20120210_CFNT
    ('flux', 'tau') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'u_star') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'Ts_stdev') : ('CFNT_stats30', 'Ts_Std'), # 20120210_CFNT
    ('flux', 'Ts_Ux_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Ts_Uy_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Ts_Uz_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Ux_stdev') : (None, None), # 20120210_CFNT
    ('flux', 'Ux_Uy_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Ux_Uz_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Uy_stdev') : (None, None), # 20120210_CFNT
    ('flux', 'Uy_Uz_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Uz_stdev') : ('CFNT_stats30', 'Uz_Std'), # 20120210_CFNT
    ('flux', 'wnd_spd') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'rslt_wnd_spd') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'wnd_dir_sonic') : (None, None), # 20120210_CFNT
    ('flux', 'std_wnd_dir') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'wnd_dir_compass') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'Ux_Avg') : (None, None), # 20120210_CFNT
    ('flux', 'Uy_Avg') : (None, None), # 20120210_CFNT
    ('flux', 'Uz_Avg') : (None, None), # 20120210_CFNT
    ('flux', 'Ts_Avg') : ('CFNT_stats30', ''),  # 20120210_CFNT
    ('flux', 'sonic_azimuth') : (None, None), # 20120210_CFNT
    ('flux', 'sonic_samples_Tot') : (None, None), # 20120215_CFNT
    ('flux', 'no_sonic_head_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'no_new_sonic_data_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'amp_l_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'amp_h_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'sig_lck_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'del_T_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'aq_sig_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'sonic_cal_err_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'Fc_wpl') : ('CFNT_stats30', ''),  # 20120210_CFNT
    ('flux', 'LE_wpl') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'Hc') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'CO2_stdev') : ('CFNT_stats30', 'CO2_mg_m3_Std'), # 20120210_CFNT
    ('flux', 'CO2_Ux_cov') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_Uy_cov') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_Uz_cov') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_stdev') : ('CFNT_stats30', 'H2O_g_m3_Std'), # 20120210_CFNT
    ('flux', 'H2O_Ux_cov') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_Uy_cov') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_Uz_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Tc_stdev') : ('CFNT_stats30', 'Tc_Std'), # 20120210_CFNT
    ('flux', 'Tc_Ux_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Tc_Uy_cov') : (None, None), # 20120210_CFNT
    ('flux', 'Tc_Uz_cov') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_mean') : ('CFNT_stats30', 'CO2_mg_m3_Avg'), # 20120210_CFNT
    ('flux', 'H2O_mean') : ('CFNT_stats30', 'H2O_g_m3_Avg'), # 20120210_CFNT
    ('flux', 'amb_press_mean') : ('CFNT_stats30', 'amb_press_Avg'), # 20120210_CFNT
    ('flux', 'Tc_mean') : ('CFNT_stats30', 'Tc_Avg'), # 20120210_CFNT
    ('flux', 'rho_a_mean') : (None, None), # 20120210_CFNT
    ('flux', 'Fc_irga') : (None, None), # 20120210_CFNT
    ('flux', 'LE_irga') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_wpl_LE') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_wpl_H') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_wpl_LE') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_wpl_H') : (None, None), # 20120210_CFNT
    ('flux', 'irga_samples_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'no_irga_head_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'no_new_irga_data_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'irga_bad_data_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'gen_sys_fault_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'sys_startup_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'motor_spd_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'tec_tmpr_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'src_pwr_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'src_tmpr_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'src_curr_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'irga_off_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'irga_sync_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'amb_tmpr_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'amb_press_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_I_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_Io_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_I_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_Io_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_Io_var_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_Io_var_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_sig_strgth_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'H2O_sig_strgth_f_Tot') : (None, None), # 20120210_CFNT
    ('flux', 'CO2_sig_strgth_mean') : ('CFNT_stats30', 'CO2_signal_Avg'), # 20120210_CFNT
    ('flux', 'H2O_sig_strgth_mean') : ('CFNT_stats30', 'H2O_signal_Avg'), # 20120210_CFNT
    ('flux', 'T_hmp_mean') : ('CFNT_stats30', 'T_hmp_Avg'), # 20120210_CFNT
    #####('flux', 'e_hmp_mean') : (None, None), # 20120210_CFNT #####
    ('flux', 'e_hmp_mean') : ('CFNT_stats30', 'e_hmp_Avg'), # 20120215_CFNT
    #####('flux', 'e_sat_hmp_mean') : (None, None), # 20120210_CFNT #####
    ('flux', 'e_sat_hmp_mean') : ('CFNT_stats30', 'e_sat_hmp_Avg'), # 2012015_CFNT
    ('flux', 'H2O_hmp_mean') : (None, None), # 20120210_CFNT
    ('flux', 'RH_hmp_mean') : ('CFNT_stats30', 'RH_hmp_Avg'), # 20120210_CFNT
    ('flux', 'rho_a_mean_hmp') : (None, None), # 20120210_CFNT
    ('flux', 'Rn_Avg') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'Rn_meas_Avg') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'par_totflx_Tot') : ('', 'PAR_totflx_Tot'), # 20120204_CFNT
    ('flux', 'PAR_totflx_Tot') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'par_flxdens_Avg') : ('', 'PAR_flxdens_Avg'), # 20120204_CFNT
    ('flux', 'PAR_flxdens_Avg') : ('CFNT_stats30', ''), # 20120210_CFNT
    ('flux', 'WS_ms_Avg') : (None, None), # 20111011_CFNT
    ('flux', 'WS_ms_WVc(1)') : ('', '034b_ws'), # 20111011_CFNT
    ('flux', '034b_ws') : ('CFNT_stats30', 'Met1_wnd_spd'), # 20120210_CFNT
    ('flux', 'WS_ms_WVc(2)') : ('', '034b_wd'), # 20111011_CFNT
    ('flux', '034b_wd') : (None, None), # 20120210_CFNT
    ('flux', 'WS_ms_WVc(3)') : ('', '034b_stdwd'), # 20111011_CFNT
    ('flux', '034b_stdwd') : (None, None), # 20120210_CFNT
    ('flux', 'ati_azimuth') : (None, None), # found in CFNT_20110923.1655_flux.dat
    ('flux', 'ati_ws') : (None, None), # found in CFNT_20110923.1655_flux.dat
    ('flux', 'ati_wd') : (None, None), # found in CFNT_20110923.1655_flux.dat
    ('flux', 'ati_stdwd') : (None, None), # found in CFNT_20110923.1655_flux.dat
    ('flux', 'atiUavg') : (None, None), # found in CFNT_20110923.1655_flux.dat
    ('flux', 'atiVavg') : (None, None), # found in CFNT_20110923.1655_flux.dat)
    ('flux', 'atiWavg') : (None, None), # found in CFNT_20110923.1655_flux.dat
    ('flux', 'atitmpavg') : (None, None), # found in CFNT_20110923.1655_flux.dat
    ('flux', 'Rain_mm_Tot') : ('CFNT_stats30', ''),  # 20120210_CFNT
    # TODO should this 30min GPS data be merged into daily files?
    ('flux', 'latitude_a') : (None, None), # 20120210_CFNT
    ('flux', 'latitude_b') : (None, None), # 20120210_CFNT
    ('flux', 'longitude_a') : (None, None), # 20120210_CFNT
    ('flux', 'longitude_b') : (None, None), # 20120210_CFNT
    ('flux', 'speed') : (None, None), # 20120210_CFNT
    ('flux', 'course') : (None, None), # 20120210_CFNT
    ('flux', 'magnetic_variation') : (None, None), # 20120210_CFNT
    ('flux', 'fix_quality') : (None, None), # 20120210_CFNT
    ('flux', 'nmbr_satellites') : (None, None), # 20120210_CFNT
    ('flux', 'altitude') : (None, None), # 20120210_CFNT
    ('flux', 'pps') : (None, None), # 20120210_CFNT
    ('flux', 'dt_since_gprmc') : (None, None), # 20120210_CFNT
    ('flux', 'gps_ready') : (None, None), # 20120210_CFNT
    ('flux', 'max_clock_change') : (None, None), # 20120210_CFNT
    ('flux', 'nmbr_clock_change') : (None, None), # 20120210_CFNT
    ('flux', 'panel_tmpr_Avg') : ('CFNT_stats30', ''),  # 20120210_CFNT
    ('flux', 'batt_volt_Avg') : ('CFNT_stats30', ''),  # 20120210_CFNT
    ('flux', 'slowsequence_Tot') : (None, None), # 20120210_CFNT
    #########################################################################
}
"""Column name aliases

Dictionary keys & values are tuples of the form (table name, column name).
All current/prior table and column pairs are described by keys; superceding
pairs are described by the values. A value tuple of (None, None) indicates
the column is no longer recorded in data tables. A blank string in the value
tuple means that item in the tuple is the same as the corresponding item in
the key (ie remains unchanged).

For example:

    col_alias[('flux', 'gps_ready')] => (None, None) # no longer recorded

    col_alias[('flux', 'WS_ms_WVc(1)')] => ('', '034b_ws') --->
    col_alias[('flux', '034b_ws')] => ('CFNT_stats30', 'Met1_wnd_spd') --->
    col_alias[('CFNT_stats30', 'Met1_wnd_wpd')] => ('stats30', '') --->
    col_alias[('stats30', 'Met1_wnd_spd')] => ('', '') # current tbl/col names
"""

# make list of all unique table names present in col_alias dict
historical_table_names = set([ k[0] for (k,v) in col_alias.iteritems()])


def raw_std_balers(tbl_name):
    """Defines size of standardized raw ascii files

    Yes it's messy. It may become a subclass of pandas.DateOffset somehow"""
    if tbl_name == 'tsdata':
        grpbykey = lambda x: x.day
        def get_start_end(df):
            start = df.index[0].date()
            return start, start+Day()
    elif tbl_name in ['stats5', 'stats30']:
        grpbykey = lambda x: x.month
        def get_start_end(df):
            offset = MonthBegin()
            start = offset.rollback(df.index[0]).date()
            return start, start+offset
    elif tbl_name == 'site_daily':
        grpbykey = lambda x: x.year
        def get_start_end(df):
            offset = YearBegin()
            start = offset.rollback(df.index[0]).date()
            return start, start+offset
    else:
        print '!!!!! BAD CASE ~~~~~~'
        grpbykey = None
        get_start_end = None
    return grpbykey, get_start_end


def _verify_col_alias():
    """Follow all past column names to current name to verify lookup table

    Return truth of whether column lookup table is free of missing data
    """
    # TODO make output shown only for errors
    errs = ''
    print ('Verifying column alias dictionary...\n')
    for (st, sc) in sorted(col_alias):
        try:
            dt, dc = current_names(st, sc)
        except KeyError:
            errs = errs + ('- unable to complete lookup for table:column '
                '"%s:%s"\n' % (st, sc))
            continue
        #print (('%s:%s' % (st, sc)).ljust(39) + ('%s:%s\n' % (dt,dc)))
    if errs:
        print ('\nWARNINGS:\n'+errs+'\n')
        return False
    else:
        print ('No warnings.\n')
        return True


def _verify_table_definitions():
    """Attempt to look up each column in header definition

    Return truth of whether all defined headers are current based on col_alias
    """
    # TODO make output shown only for errors
    errmsg = ''
    print ('Verifying column order defintions...\n')
    for tbl in table_definitions:
        for col in table_definitions[tbl]:
            try:
                t, c = current_names(tbl, col)
            except KeyError:
                errmsg = errmsg + ('- header definition "%s:%s" not found in '
                    'lookup table\n' % (tbl, col))
                continue
            #print (('%s:%s' % (tbl, col)).ljust(39) + ('%s:%s\n' % (t,c)))
            if (t != tbl) or (c != col):
                errmsg = errmsg + ('- header definition "%s:%s" does not '
                    'match lookup table "%s:%s"\n' % (tbl, col, t, c))
    if errmsg:
        print ('WARNINGS:\n'+errmsg+'\n')
        return False
    else:
        print ('No warnings.\n')
        return True


if __name__ == '__main__':
    if raw_input('Press "y" to test historical column alias dictionary; else to skip') in 'yY':
        try:
            _verify_col_alias()
        except Exception as ex:
            print ('/*- A problem occurred while verifying the historical column '
                    'alias dictionary (``col_alias``): \n{err}'.format(err=ex))
    if raw_input('Press "y" to test table column definitions; else to skip') in 'yY':
        try:
            _verify_table_definitions()
        except Exception as ex:
            print ('/*- A problem occurred while verifying the table column '
                    'definitions (``table_definitions``): \n{err})'.format(err=ex))
    raw_input('Press <enter> to exit')
