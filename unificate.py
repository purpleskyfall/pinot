#!/usr/bin/env python3
# coding=UTF-8
"""Unificate rinex files by a config.yml file.

The RINEX file edit function rely on TEQC software, Check if you have
installed TEQC by typing `teqc -help` in cmd.

:author: Jon Jiang
:email: jiangyingming@live.com
"""
from concurrent import futures
import argparse
import glob
import itertools
import os
import re
import subprocess

import tqdm
import yaml

MAX_THREADING = max(6, os.cpu_count())
ALPHAREG = re.compile(r'[a-z]+\s*', re.I)
TEQCITEM = {'agency': '-O.ag', 'antenna': '-O.at', 'delta': '-O.pe',
            'interval': '-O.dec', 'obs_type': '-O.obs', 'observer': '-O.o',
            'position': '-O.px', 'receiver': '-O.rt', 'rm_sys': ''}


def get_info(site, sitesinfo):
    """Get site information from sitesinfo. Use 'all' as default if a
    site or a item not found in sitesinfo.

    Example:

    >>> default = {'interval': 30, 'observer': 'Jon'}
    >>> special = {'antenna': 'TRM59900.00     SCIS', 'interval': 15}
    >>> sitesinfo = {'all': default, 'bjfs': special}
    >>> info = get_info('bjfs', sitesinfo)
    >>> info['antenna'], info['interval'], info['observer']
    ('TRM59900.00     SCIS', 15, 'Jon')
    """
    special = sitesinfo.get(site.lower(), {})
    # get default information by key of 'all'
    default = {}
    if 'all' in sitesinfo:
        default = sitesinfo['all'].copy()
    # update default using special information
    default.update(special)

    return default


def arg_wraper(key, value):
    """Make argument for TEQC software by key, value, return a tuple.

    Example:

    >>> arg_wraper('rm_sys', ['R', 'E'])
    ('', '-R -E')

    >>> arg_wraper('obs_type', ['C1', 'P1', 'L1'])
    ('-O.obs', 'C1,P1,L1')

    >>> arg_wraper('antenna', 'TRM59900.00     SCIS')
    ('-O.at', '"TRM59900.00     SCIS"')

    >>> arg_wraper('interval', 30)
    ('-O.dec', '30')
    """
    if key == 'rm_sys':
        argument = '-' + ' -'.join(value)
    elif key == 'obs_type':
        argument = ','.join(value)
    elif ALPHAREG.match(str(value)):
        argument = '"{}"'.format(value)
    else:
        argument = str(value)

    return TEQCITEM[key], argument


def make_args(src_file, sitesinfo):
    """Get arguments for teqc function."""
    site = os.path.basename(src_file)[0:4]
    # get configuration for site
    siteinfo = get_info(site, sitesinfo)
    # make an arguments list by site configuration
    arguments = []
    for key, value in siteinfo.items():
        arguments.extend(arg_wraper(key, value))

    return arguments


def teqc(src_file, args, out_dir, keep):
    """Run TEQC software to unificate a RINEX Obs file."""
    filename = os.path.basename(src_file)
    dst_file = os.path.join(out_dir, filename)
    # run TEQC, redirect stdout into dst_file, and ignore stderr
    args = ' '.join(['teqc', *args, src_file])
    with open(dst_file, 'w') as dst_writer:
        status = subprocess.call(args, stdout=dst_writer, stderr=subprocess.DEVNULL)
    # check exit status of teqc: {0: success, >0: error}
    if status > 0:
        # if run teqc failed, remove dest file and return filename
        os.remove(dst_file)
        return filename
    # remove source file if keep is False when successful
    if not keep:
        os.remove(src_file)

    return


def parallel_run(function, argvs):
    """Parallel run function using argvs, display a process bar."""
    with futures.ThreadPoolExecutor(max_workers=MAX_THREADING) as executor:
        todo_list = [executor.submit(function, *argv) for argv in argvs]
        task_iter = futures.as_completed(todo_list)
        failed_files = []
        for future in tqdm.tqdm(task_iter, total=len(todo_list), unit='file'):
            # return None means task is success
            res = future.result()
            if res:
                failed_files.append(res)

        return failed_files


def main(args):
    """Main function"""
    globstrs, out_dir, infos = args.files, args.out, yaml.load(args.cfg)
    keep_src, recursive = args.keep, args.recursive
    # create output directory
    os.makedirs(out_dir, exist_ok=True)
    # collect input globstrs into a glob list
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    files = itertools.chain(*globs)
    # make input args for teqc function
    teqc_args = ((src, make_args(src, infos), out_dir, keep_src) for src in files)
    print('Start processing: {} ...'.format(', '.join(globstrs)))
    # start parallel task, get a filename list of unificate failed.
    failed = parallel_run(teqc, teqc_args)
    if failed:
        print('\nUnificate failed filename: {}'.format(', '.join(failed)))
    else:
        print('\nAll unificate tasks are finished!')

    return 0


def init_args():
    """Initilize function, parse user input"""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Unificate RINEX Obs file using a YAML infomation.')
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.5.0')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-cfg', metavar='<config>', default='_sitesinfo.yml',
                        type=argparse.FileType('r'),
                        help='configuration YAML file [default: _sitesinfo.yml]')
    parser.add_argument('-out', metavar='<directory>', default='unificated',
                        help='output directory [default: unificated in current]')
    parser.add_argument(dest='files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
