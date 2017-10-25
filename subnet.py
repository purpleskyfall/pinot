#!/usr/bin/env python3
# coding=utf-8
"""Order RINEX observation files using a subnet configuration.

This script will create directories using subnet name then copy or move
RINEX observation files into the subnet folders.

:author: Jon Jiang
:email: jiangyingming@live.com
"""
import argparse
import glob
import itertools
import os
import shutil

import yaml


def which_nets(src_file, subnets):
    """Locate which nets a source file belong, return a list.

    Example:

    >>> nets = {'net1': {'algo', 'shao'}, 'net2': {'algo', 'warn'}}
    >>> which_nets('wuhn0420.17d', nets)
    []
    >>> which_nets('WARN00DEU_R_20170420000_01D_30S_MO.crx', nets)
    ['net2']
    >>> sorted(which_nets('algo0420.17o', nets))
    ['net1', 'net2']
    """
    filename = os.path.basename(src_file)
    site = filename[0:4].lower()
    return [net for net, sites in subnets.items() if site in sites]


def order_file(src_file, dst_dirs, keep_src):
    """Copy source file into destination directories:
    If keep_src is False, remove source file when complete.
    """
    for dst_dir in dst_dirs:
        print('{} => {}'.format(src_file, dst_dir))
        shutil.copy2(src_file, dst_dir)

    if not keep_src:
        os.remove(src_file)


def init_args():
    """Initilize function, parse user input"""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Order RINEX files using a YAML subnet configuration.'
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.4.0')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file in input_dir')
    parser.add_argument('-cfg', metavar='<config>', default='_subnet.yml',
                        type=argparse.FileType('r'),
                        help='configuration file [default: ./subnet.yml]')
    parser.add_argument('-out', metavar='<directory>', default='subnets',
                        help='output directory [default: subnets in current]')
    parser.add_argument('files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return parser.parse_args()


def main():
    """Main function."""
    args = init_args()
    globstrs, out_dir, config = args.files, args.out, yaml.load(args.cfg)
    keep_src, recursive = args.keep, args.recursive
    # convert sites list into set
    nets = {net: set(sites) for net, sites in config.items()}
    net_dirs = {net: os.path.join(out_dir, net) for net in nets}
    # create folder for every subnet
    for subdir in net_dirs.values():
        os.makedirs(subdir, exist_ok=True)
    # collect input globstrs into a glob list
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    # start process
    print('Start processing: {} ...'.format(', '.join(globstrs)))
    if not keep_src:
        print('Delete source files when complete')
    missing = set()
    for src_file in itertools.chain(*globs):
        belong = which_nets(src_file, nets)
        # if couldn't found a site in any subnets, log it
        if not belong:
            missing.add(os.path.basename(src_file)[0:4].lower())
            continue
        # get all destination directories and copy/move in
        dst_dirs = [net_dirs[net] for net in belong]
        order_file(src_file, dst_dirs, keep_src)

    if missing:
        message = 'Sites not belong to any networks: {}'
        print(message.format(', '.join(missing)))

    return 0


if __name__ == '__main__':
    main()
