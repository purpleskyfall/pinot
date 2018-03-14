#!/usr/bin/env python3
# coding=utf-8
"""Check if some RINEX observation files exist in source folder,
the site list is input using a YAML configuration file.

:author: Jon Jiang
:email: jiangyingming@live.com
"""
from textwrap import shorten
import argparse
import os
import re

import yaml


def is_correct_rinex(src_file, year, doy):
    """Check if a source file is RINEX observation file observed at
    given year and doy(day of year), return True or False.

    Example:

    >>> is_correct_rinex('aggo0420.17o', 2017, 42)
    True

    >>> is_correct_rinex('ALGO0420.17D', 2017, 42)
    True

    >>> is_correct_rinex('bjfs0420.17n', 2017, 42)
    False

    >>> is_correct_rinex('WARN00DEU_R_20170420000_01D_30S_MO.crx', 2017, 42)
    True

    >>> is_correct_rinex('DAVS00ATA_R_20170420000_01D_30S_MM.RNX', 2017, 42)
    False
    """
    year, doy = str(year), '{:03d}'.format(doy)
    rnxregs = ('^[0-9a-z]{4}' + doy + '[0-9a-z]{1,3}\\.' + year[2:] + '[do]$',
               '^[0-9a-z]{4}[0-9]{2}[a-z]{3}_[rs]_' + year + doy + '[0-9]{4}'
               '_[0-9]{2}[dhm]_[0-9]{2}[sz]_[mgcreij]o.(crx|rnx)$')

    return any(re.match(reg, src_file, re.IGNORECASE) for reg in rnxregs)


def check_dir(src_dir, year, doy, missing, recursive):
    """Check if some sites in missing set have RINEX observation file
    observed at given year and doy(day of year), if a site observation
    file exists, remove this site in missing set.
    """
    if not os.path.isdir(src_dir):
        raise ValueError('{} is not a directory!'.format(src_dir))
    # check files in source directory one by one
    for _, _, files in os.walk(src_dir):
        for name in files:
            correctobs = is_correct_rinex(name, year, doy)
            if correctobs:
                site = name[0:4].lower()
                missing.discard(site)
        # if not recursive, only check the first level files
        if not recursive:
            break


def init_args():
    """Initilize function, parse user input"""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Check if some RINEX observation files exist.'
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.2.1')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-cfg', metavar='<config>', default='_sites.yml',
                        type=argparse.FileType('r'),
                        help='YAML site list file [default: _sites.yml]')
    parser.add_argument('-yr', metavar='<year>', dest='year', required=True,
                        type=int, choices=range(1980, 2050),
                        help='year for observation file [required]')
    parser.add_argument('-doy', metavar='<doy>', dest='doy', required=True,
                        type=int, choices=range(1, 367),
                        help='doy for observation file [required]')
    parser.add_argument('dirs', metavar='<directory>', nargs='+',
                        help='directory will be searched')

    return parser.parse_args()


def main():
    """Main function."""
    args = init_args()
    dirs, year, doy = args.dirs, args.year, args.doy
    sites, recursive = yaml.load(args.cfg), args.recursive
    # create a set of missing sites, initialize it using all sites
    missing = set(sites)
    # start process
    print('Start processing: {}'.format(shorten(', '.join(dirs), 62)))
    for directory in dirs:
        check_dir(directory, year, doy, missing, recursive)
    # if still some sites in missing, print them
    if missing:
        names = sorted(list(missing))
        message = "Observations not found at {0}, {1} for: {2}"
        print(message.format(year, doy, ', '.join(names)))

    return 0


if __name__ == '__main__':
    main()
