#coding=UTF-8
#creater: Jon Jiang
#datetime: 2016-12-20
#Python version: 3.4

"""Rename filename, upper to lower"""

import os
import sys
import glob
import shutil
import argparse


# dirpath: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, keep: keep input files,
# recursive: search file recursively
def up2lower(src_dir, out_dir, glob_str, keep, recursive):
    """Rename filename, upper to lower"""

    # if the out_dir is None, rename file in original folder
    if out_dir is None:
        for file in glob.glob(os.path.join(src_dir, glob_str)):
            filedir, filename = os.path.split(file)
            print('rename file: %s' %file)
            shutil.move(file, os.path.join(filedir, filename.lower()))

    # if the out_dir is not None and --keep is setted, copy and rename
    elif keep:
        for file in glob.glob(os.path.join(src_dir, glob_str)):
            filename = os.path.basename(file)
            print('rename file: %s' %file)
            shutil.copy(file, os.path.join(out_dir, filename.lower()))

    # if the out_dir is not None and --keep is not setted, move and rename
    else:
        for file in glob.glob(os.path.join(src_dir, glob_str)):
            filename = os.path.basename(file)
            print('rename file: %s' %file)
            shutil.move(file, os.path.join(out_dir, filename.lower()))

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                up2lower(child_path, out_dir, glob_str, keep, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    src_dir, out_dir, glob_str = args.dir, args.out, args.glob

    # if the out_dir is None and --keep is setted, process as an error
    if args.keep and out_dir is None:
        print('Error! blank output_dir is conflict with --keep.', file=sys.stderr)
        return 1

    if out_dir is not None:
        createdir(out_dir)

    print('---------------------- input params ----------------------')
    print('source dir: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('----------------------------------------------------------\n')

    for directory in glob.glob(src_dir):
        up2lower(directory, out_dir, glob_str, args.keep, args.recursive)

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="Rename filename, upper to lower.")

    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='up2lower.py 0.1.7')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file in input dir')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in child folder')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][OD]*',
                        help='filename search mode [default: *.[0-9][0-9][OD]*')
    parser.add_argument('-out', metavar='<output_dir>',
                        help='output dir, [default: self dir]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
