#!/usr/bin/env python3
# coding=utf-8
"""Check if some sites' observation files have meta infomation changed,
reference infomation is inputed using a YAML configuration file.

:author: Jon Jiang
:email: jiangyingming@live.com
"""
from textwrap import shorten
import argparse
import glob
import itertools
import os

import yaml

SITEINFO = {
    'receiver': {'flag': 'REC # / TYPE / VERS', 'pos': slice(20, 40)},
    'antenna': {'flag': 'ANT # / TYPE', 'pos': slice(20, 40)},
    'delta': {'flag': 'ANTENNA: DELTA H/E/N', 'pos': slice(0, 42)},
    'position': {'flag': 'APPROX POSITION XYZ', 'pos': slice(0, 42)}
}


def get_meta(rnx_reader):
    """Get meta-infomation in source RINEX observation file header."""
    # get RINEX header lines
    head = itertools.takewhile(lambda n: 'END OF HEADER' not in n, rnx_reader)
    meta = {}
    for line in head:
        for key, value in SITEINFO.items():
            if value['flag'] in line:
                meta[key] = line[value['pos']].strip()

    return meta


def compare_info(fileinfo, reference, threshold):
    """Compare meta-infomation in source file and reference dictionary,
    Return a dict contains different items.

    Example:

    >>> fileinfo = {'receiver': 'TRIMBLE NETR9'}
    >>> reference = {'receiver': 'TRIMBLE NETR8'}
    >>> compare_info(fileinfo, reference, 10)
    {'receiver': ('TRIMBLE NETR8', 'TRIMBLE NETR9')}

    >>> fileinfo = {'receiver': 'ASHTECH UZ-12'}
    >>> reference = {'receiver': 'ASHTECH UZ-12'}
    >>> compare_info(fileinfo, reference, 10)
    {}

    >>> fileinfo = {'position': '-2148744.84 4426642.96 4044657.86'}
    >>> reference = {'position': '-2148755.84 4426642.96 4044657.85'}
    >>> compare_info(fileinfo, reference, 10)
    ... # doctest: +NORMALIZE_WHITESPACE
    {'position': ('-2148755.84 4426642.96 4044657.85',
                  '-2148744.84 4426642.96 4044657.86')}
    """
    difference = {}
    for key, value in fileinfo.items():
        ref_val = reference.get(key, '').strip()
        if key == 'position':
            f_pos = [float(num) for num in value.split()]
            r_pos = [float(num) for num in ref_val.split()]
            if any(abs(fp - rp) > threshold for fp, rp in zip(f_pos, r_pos)):
                difference[key] = (ref_val, value)
        else:
            if value != ref_val:
                difference[key] = (ref_val, value)

    return difference


def show_difference(src_file, difference, out_fmt):
    """Show difference, print it to stdout. The out_fmt indicate format
    of output message, it can be list or table.
    """
    if out_fmt == 'list' or out_fmt == 'l':
        print('\n{} has difference:'.format(src_file))
        for key, value in difference.items():
            print('{} in cfg file: {}'.format(key, value[0]))
            print('{} in obs file: {}'.format(key, value[1]))
    else:
        filename = os.path.basename(src_file)
        for key, value in difference.items():
            record = '{: <20s} {: <10s} {: <44s} {: <44s}'
            print(record.format(filename, key, value[0], value[1]))


def init_args():
    """Initilize function, parse user input"""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="Compare site's meta between files and reference."
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.4.1')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-cfg', metavar='<config>', default='_sitesinfo.yml',
                        type=argparse.FileType('r'),
                        help='configuration file [default: _sitesinfo.yml]')
    parser.add_argument('-out', metavar='<format>', default='list',
                        choices=['list', 'l', 'table', 't'],
                        help='output format, list or table [default: list]')
    parser.add_argument('-thd', metavar='<threshold>', default=10, type=int,
                        help='threshold for position change [default: 10(m)]')
    parser.add_argument('files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return parser.parse_args()


def main():
    """Main function."""
    args = init_args()
    globstrs, out_fmt, sitesinfo = args.files, args.out, yaml.load(args.cfg)
    threshold, recursive = args.thd, args.recursive
    # collect input globstrs into a glob list
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    # start process
    print('Start processing: {}'.format(shorten(', '.join(globstrs), 62)))
    # if output format is table, print a table header first
    if out_fmt == 'table' or out_fmt == 't':
        header = 'file', 'type', 'in cfgfile', 'in obsfile'
        print('\n{: <20s} {: <10s} {: <44s} {: <44s}'.format(*header))
    # a set named missing collects site not found in reference file
    missing = set()
    for src_file in itertools.chain(*globs):
        filename = os.path.basename(src_file)
        site = filename[0:4].lower()
        # if site not in sitesinfo, add this site info missing
        if site not in sitesinfo:
            missing.add(site)
            continue
        fileinfo = get_meta(open(src_file))
        difference = compare_info(fileinfo, sitesinfo[site], threshold)
        if difference:
            show_difference(src_file, difference, out_fmt)

    if missing:
        message = '\nSites not found in configuration file: {}'
        print(message.format(', '.join(sorted(list(missing)))))

    return 0


if __name__ == '__main__':
    main()
