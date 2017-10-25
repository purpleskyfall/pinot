#!/usr/bin/env python3
# coding=utf-8
"""Rename GNSS RINEX file, using a YAML site map configuration file.

:author: Jon Jiang
:email: jiangyingming@live.com
"""
import argparse
import glob
import itertools
import os
import shutil

import yaml


def rename_site(src_file, out_dir, sitemap, keep_src):
    """Rename src_file output to out_dir using a sitemap:
    1. If site isn't in sitemap, do nothing and return site name;
    2. If out_dir is None, rename original file;
    3. If out_dir is not None and keep_src is true, rename using copy;
    4. If out_dir is not None and keep_src is false, rename using move.
    """
    src_dir, filename = os.path.split(src_file)
    site = filename[0:4]
    site_key = site.lower()
    # if site isn't in sitemap
    if site_key not in sitemap:
        return site_key
    # get destination file name
    newsite = sitemap[site_key]
    dst_name = (newsite if site.islower() else newsite.upper()) + filename[4:]
    # get destination file path
    if out_dir is None:
        dst_file = os.path.join(src_dir, dst_name)
    else:
        dst_file = os.path.join(out_dir, dst_name)
    # start file rename
    print('{} => {}'.format(src_file, dst_file))
    if keep_src:
        shutil.copy2(src_file, dst_file)
    else:
        shutil.move(src_file, dst_file)


def init_args():
    """Initilize function, parse user input"""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Rename GNSS file using a YAML configuration.'
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.2.0')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-cfg', metavar='<config>', default='_sitemap.yml',
                        type=argparse.FileType('r'),
                        help='configuration YAML file [default: _sitemap.yml]')
    parser.add_argument('-out', metavar='<directory>', default=None,
                        help='output directory [default: original folder]')
    parser.add_argument('files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return parser.parse_args()


def main():
    """Main function."""
    args = init_args()
    globstrs, out_dir, sitemap = args.files, args.out, yaml.load(args.cfg)
    keep_src, recursive = args.keep, args.recursive
    # make output directory if out_dir is set
    if out_dir is not None:
        os.makedirs(out_dir, exist_ok=True)
    # collect input globstrs into a glob list
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    # start process
    print('Start processing: {} ...'.format(', '.join(globstrs)))
    if not keep_src:
        print('Delete source files when complete')
    missing = set()
    for src_file in itertools.chain(*globs):
        res = rename_site(src_file, out_dir, sitemap, keep_src)
        # if return is not None, means site not found in sitemap
        if res is not None:
            missing.add(res)

    if missing:
        print('Sites not found in sitemap: {}'.format(', '.join(missing)))

    return 0


if __name__ == '__main__':
    main()
