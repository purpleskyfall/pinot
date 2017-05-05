#coding=UTF-8
#creater: Jon Jiang
#datetime: 2017-01-03
#Python version: 3.4

"""Rename GNSS file by a YAML configuration"""

import os
import re
import sys
import glob
import yaml
import shutil
import argparse

# test if a filename is RINEX
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.+\.\d{2}[a-z]$', re.I)


#dir_path: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, keep: keep input files,
# sitemap: map of old site and new site name
# recursive: search file recursively
def rename(src_dir, glob_str, out_dir, sitemap, keep, recursive):
    """Rename files in src_dir by sitemap"""

    for file in glob.glob(os.path.join(src_dir, glob_str)):
        # get filename and site
        filename = os.path.basename(file)
        site = filename[:4].lower()
        # if file is not match RINEXREG or site is not in sitemap, skip it
        if not RINEXREG.match(filename) or site not in sitemap:
            continue

        # new site and filename
        newsite = sitemap[site]
        newname = newsite + filename[4:]

        # if out_dir is None, output to original folder
        if out_dir is None:
            filedir = os.path.dirname(file)
            newfile = os.path.join(filedir, newname)
        else:
            newfile = os.path.join(out_dir, newname)
        print('rename: ' + file + ' => ' + newfile)

        if keep:
            shutil.copy(file, newfile)
        else:
            shutil.move(file, newfile)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                rename(child_path, glob_str, out_dir, sitemap, keep, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    if not os.path.exists(args.cfg):
        print('Error! configuration file not exit!', file=sys.stderr)
        return 1

    src_dir, out_dir, glob_str = args.dir, args.out, args.glob

    # load configuration file
    with open(args.cfg) as cfgfile:
        sitemap = yaml.load(cfgfile)

    if out_dir is not None:
        createdir(out_dir)

    print('---------------------- input params ----------------------')
    print('source dir: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('config file: %s' %args.cfg)
    print('----------------------------------------------------------', end='\n\n')

    for directory in glob.glob(src_dir):
        rename(directory, glob_str, out_dir, sitemap, args.keep, args.recursive)

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Rename GNSS file by a YAML configuration.')

    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='renamesite.py 0.1.1')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file in input_dir')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9]?*',
                        help='filename search mode [default: *.[0-9][0-9]?*]')
    parser.add_argument('-cfg', metavar='<config>', default='_sitemap.yml',
                        help='configuration YAML file [default: _sitemap.yml]')
    parser.add_argument('-out', metavar='<output_dir>',
                        help='output dir [default: self dir]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
