#coding=UTF-8
#creater: Jon Jiang
#datetime: 2017-03-26
#Python version: 3.4.3

"""Convert Standard RINEX into GSI Compact RINEX"""

import os
import re
import glob
import argparse

# regex to test if a filename is Standard RINEX
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.+\.\d{2}o$', re.I)


# dir_path: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, keep: keep input files,
# recursive: search file recursively
def rnx2crx(src_dir, out_dir, glob_str, keep, recursive):
    """Convert Standard RINEX to Compact RINEX by rnx2crx"""

    for file in glob.glob(os.path.join(src_dir, glob_str)):
        rnx_name = os.path.basename(file)
        # skip not matched filename
        if not RINEXREG.match(rnx_name):
            continue
        # output filename, using casing of the last letter in crx_name
        crx_name = rnx_name[:-1] + ('D' if str.isupper(rnx_name[-1]) else 'd')
        crx_path = os.path.join(out_dir, crx_name)
        # run rnx2crx
        print('convert: %s ......' %file)
        command = 'rnx2crx - ' + file + ' > ' + crx_path
        status = os.system(command)
        # delete source file if --keep is not setted
        if not keep and status == 0:
            os.remove(file)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                rnx2crx(child_path, out_dir, glob_str, keep, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    src_dir, out_dir, glob_str = args.dir, args.out, args.glob
    createdir(out_dir)

    print('---------------------- input params ----------------------')
    print('source dirs: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('----------------------------------------------------------\n')

    for directory in glob.glob(src_dir):
        rnx2crx(directory, out_dir, glob_str, args.keep, args.recursive)

    return 0

def init_args():
    """Initilize function"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="Convert Standard RINEX into GSI Compact RINEX.")
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='rnx2crnx.py 0.1.1')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file in input dir')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][Oo]',
                        help='filename search mode [default: *.[0-9][0-9][Oo]')
    parser.add_argument('-out', metavar='<output_dir>', default='crinex',
                        help='output dir, [default: crinex in current]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
