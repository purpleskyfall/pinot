#!/usr/bin/env python3
# coding=utf-8
"""Rename filename, lower to upper.

:author: Jon Jiang
:email: jiangyingming@live.com
"""
import argparse
import glob
import itertools
import os
import shutil
import sys


def low2upper(src_file, out_dir, keep):
    """Rename filename, lower to upper:
    If out_dir is None, rename original file;
    If out_dir is not None and keep is true, rename using copy;
    If out_dir is not None and keep is false, rename using move.
    """
    src_dir, filename = os.path.split(src_file)
    if out_dir is None:
        dst_file = os.path.join(src_dir, filename.upper())
    else:
        dst_file = os.path.join(out_dir, filename.upper())

    if keep:
        shutil.copy2(src_file, dst_file)
    else:
        shutil.move(src_file, dst_file)


def main(args):
    """Main function."""
    globstrs, out_dir = args.files, args.out
    keep, recursive = args.keep, args.recursive
    # if the out_dir is None and --keep is setted, process as an error
    if args.keep and out_dir is None:
        err_message = 'Error! Blank output directory is conflict with --keep.'
        print(err_message, file=sys.stderr)
        return 1
    # start process
    if out_dir is not None:
        os.makedirs(out_dir, exist_ok=True)
    # collect input globstrs into a glob list
    print('Start processing: {} ...'.format(', '.join(globstrs)))
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    count = 0
    for src_file in itertools.chain(*globs):
        low2upper(src_file, out_dir, keep)
        count += 1

    print('{} files have been processed.'.format(count))

    return 0


def init_args():
    """Initilize function, parse user input."""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="Rename filename, lower to upper."
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog) 0.2.0')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-out', metavar='<directory>', default=None,
                        help='output directory, [default: original folder]')
    parser.add_argument('files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
