#coding=UTF-8
#creater: Jon Jiang
#datetime: 2017-01-03
#Python version: 3.4

"""Order rinex files to suit IGS style."""

import os
import re
import glob
import shutil
import argparse

# test if a filename is RINEX
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.+\.\d{2}[a-z]$', re.I)

# dirpath: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, keep: keep input files,
# recursive: search file recursively
def orderdir(src_dir, glob_str, out_dir, keep, recursive):
    """Order GNSS files into IGS style"""

    for file in glob.glob(os.path.join(src_dir, glob_str)):
        filename = os.path.basename(file)
        # if file is not match RINEXREG, skip it
        if not RINEXREG.match(filename):
            continue
        # get year, doy file type from filename
        year, doy, filetype = filename[-3:-1], filename[4:7], filename[-3:]
        year = '20' + year if int(year) < 80 else '19' + year
        # calculate filepath
        yearpath = os.path.join(out_dir, year)
        doypath = os.path.join(yearpath, doy)
        typepath = os.path.join(doypath, filetype)
        # create directory
        createdir(yearpath)
        createdir(doypath)
        createdir(typepath)
        # if --keep is setted, use copy
        if keep:
            print('copy file: %s' %file)
            shutil.copy(file, typepath)
        else:
            print('move file: %s' %file)
            shutil.move(file, typepath)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                orderdir(child_path, glob_str, out_dir, keep, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    src_dir, out_dir, glob_str = args.dir, args.out, args.glob
    createdir(out_dir)

    print('---------------------- input params ----------------------')
    print('source dir: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('----------------------------------------------------------\n')

    for directory in glob.glob(src_dir):
        orderdir(directory, glob_str, out_dir, args.keep, args.recursive)

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="Order rinex files to suit IGS style.")

    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='orderfile.py 0.1.4')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file in input_dir')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9]?*',
                        help='filename search mode [default: *.[0-9][0-9]?*]')
    parser.add_argument('-out', metavar='<output_dir>', default='daily',
                        help='output dir [default: daily in current]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
