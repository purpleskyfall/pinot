#!/usr/bin/env python3
# coding=utf-8
"""Order RINEX files to suit IGS style organization.

An example, order files observed at 2017:

. 2017/
    ...
    |-- 042/
        |-- 17d
            |-- aggo0420.17d
            |-- WARN00DEU_R_20170420000_01D_30S_MO.crx
            ...
        |-- 17m
            |-- daej0420.17m
            |-- DAVS00ATA_R_20170420000_01D_30S_MM.rnx
        |-- 17n
            |-- brdc0420.17n
            |-- ALGO00CAN_R_20170420000_01D_30S_MN.rnx
            ...
        |-- 17o
            |-- bjfs0420.17o
            |-- SHAO00CHN_R_20170420000_01D_30S_MO.rnx
            ...
        ...
    ...

:author: Jon Jiang
:email: jiangyingming@live.com
"""
import argparse
import glob
import itertools
import os
import shutil


def which_kind(filename):
    """Return which kind a source file is, the kind is a 2-digit year
    concat one of a kind char in: d, m, n, o.

    Example:

    >>> which_kind('aggo0420.17d')
    '17d'
    >>> which_kind('WARN00DEU_R_20170420000_01D_30S_MO.crx')
    '17d'

    >>> which_kind('daej0420.17m')
    '17m'
    >>> which_kind('DAVS00ATA_R_20170420000_01D_30S_MM.rnx')
    '17m'

    >>> which_kind('brdc0420.17n')
    '17n'
    >>> which_kind('ALGO00CAN_R_20170420000_01D_30S_MN.rnx')
    '17n'

    >>> which_kind('bjfs0420.17o')
    '17o'
    >>> which_kind('SHAO00CHN_R_20170420000_01D_30S_MO.rnx')
    '17o'
    """
    if filename.endswith('.crx'):
        year = filename[14:16]
        kind = '{yr}d'.format(yr=year)
    elif filename.endswith('.rnx'):
        year, type_code = filename[14:16], filename[-5].lower()
        kind = '{yr}{t}'.format(yr=year, t=type_code)
    else:
        kind = filename[-3:].lower()

    return kind


def which_dir(src_file):
    """Return which directory path a source file should belong, the
    path is concat by 4-digit year, 3-digit day of year and kind.

    Example:

    >>> which_dir('aggo0420.17o').replace('\\\\', '/')
    '2017/042/17o'

    >>> which_dir('ALGO00CAN_R_20170420000_01D_30S_MN.rnx').replace('\\\\', '/')
    '2017/042/17n'

    >>> which_dir('DAVS00ATA_R_20170420000_01D_30S_MM.RNX').replace('\\\\', '/')
    '2017/042/17m'
    """
    filename = os.path.basename(src_file).lower()
    kind = which_kind(filename)
    year = kind[0:2]
    year = '20' + year if year < '80' else '19' + year
    if filename.endswith('.crx') or filename.endswith('.rnx'):
        doy = filename[16:19]
    else:
        doy = filename[4:7]

    return os.path.join(year, doy, kind)


def init_args():
    """Initilize function, parse user input"""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="Order RINEX files to suit IGS style organization."
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.2.0')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-out', metavar='<directory>', default='daily',
                        help='output directory [default: daily in current]')
    parser.add_argument('files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return parser.parse_args()


def main():
    """Main function."""
    args = init_args()
    globstrs, out_dir = args.files, args.out
    keep_src, recursive = args.keep, args.recursive
    # collect input globstrs into a glob list
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    # start process
    print('Start processing: {} ...'.format(', '.join(globstrs)))
    if not keep_src:
        print('Delete source files when complete')
    for src_file in itertools.chain(*globs):
        dst_dir = os.path.join(out_dir, which_dir(src_file))
        os.makedirs(dst_dir, exist_ok=True)
        print('{} => {}'.format(src_file, dst_dir))
        if keep_src:
            shutil.copy2(src_file, dst_dir)
        else:
            shutil.move(src_file, dst_dir)

    return 0


if __name__ == '__main__':
    main()
