#!/usr/bin/env python3
# coding=utf-8
"""Convert GSI Compact RINEX into Standard RINEX,
using concurent.futures.

The convert function rely on RNXCMP software. Check if you have
installed RNXCMP by typing `crx2rnx -h` in cmd.

:author: Jon Jiang
:email: jiangyingming@live.com
"""
from concurrent import futures
import argparse
import glob
import itertools
import os
import subprocess
import sys

import tqdm

MAX_THREADING = max(6, os.cpu_count())


def crx2rnx(src_file, out_dir, keep):
    """Convert compact RINEX file to standard RINEX."""
    filename = os.path.basename(src_file)
    if filename.lower().endswith('crx'):
        dst_file = os.path.join(out_dir, filename[0:-3]+'rnx')
    else:
        dst_file = os.path.join(out_dir, filename[0:-1]+'o')
    # run crx2rnx, redirect standard RINEX stdout into destination file
    # and ignore the stderr.
    args = 'crx2rnx', '-', src_file
    with open(dst_file, 'w') as dst_writer:
        status = subprocess.call(
            args, stdout=dst_writer, stderr=subprocess.DEVNULL, shell=True)
    # check exit status of crx2rnx: {0: success, 1: error, 2: warning}
    if status == 1:
        # if run crx2rnx failed, remove dest file and return filename
        os.remove(dst_file)
        return filename
    # remove source file if keep is False when successful
    if not keep:
        os.remove(src_file)

    return


def parallel_run(function, argvs):
    """Parallel run function using argvs, display a process bar."""
    # check platform, use ASCII process bar in Windows
    use_ascii = True if sys.platform == 'win32' else False
    with futures.ThreadPoolExecutor(max_workers=MAX_THREADING) as executor:
        todo_list = [executor.submit(function, *argv) for argv in argvs]
        task_iter = futures.as_completed(todo_list)
        failed_files = []
        for future in tqdm.tqdm(
                task_iter, total=len(todo_list), ascii=use_ascii, unit='file'):
            # return None means task is success
            res = future.result()
            if res:
                failed_files.append(res)

    return failed_files


def init_args():
    """Initilize function, parse user input"""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Convert GSI Compact RINEX into Standard RINEX.'
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.2.1')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-out', metavar='<directory>', default='rinex',
                        help='output directory [default: rinex in current]')
    parser.add_argument('files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return parser.parse_args()


def main():
    """Main function."""
    args = init_args()
    globstrs, out_dir = args.files, args.out
    keep_src, recursive = args.keep, args.recursive
    # create output directory
    os.makedirs(out_dir, exist_ok=True)
    # collect input globstrs into a glob list
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    # make input args for crx2rnx function
    conv_args = ((src, out_dir, keep_src) for src in itertools.chain(*globs))
    print('Start processing: {} ...'.format(', '.join(globstrs)))
    if not keep_src:
        print('Delete source files when complete')
    # start parallel task, get a file name list of convert failed.
    failed = parallel_run(crx2rnx, conv_args)
    if failed:
        print('\nConvert failed filename: {}'.format(', '.join(failed)))
    else:
        print('\nAll convert tasks are finished!')


if __name__ == '__main__':
    main()
