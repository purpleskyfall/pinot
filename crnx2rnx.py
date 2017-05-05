#coding=UTF-8
#creater: Jon Jiang
#datetime: 2017-03-26
#Python version: 3.4.3

"""Convert GSI Compact RINEX into Standard RINEX"""

import os
import re
import glob
import argparse

# regex to test if a filename is Compact RINEX
CRINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.+\.\d{2}d$', re.I)


# dir_path: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, keep: keep input files,
# recursive: search file recursively
def crx2rnx(src_dir, out_dir, glob_str, keep, recursive):
    """Convert Compact RINEX to Standard RINEX by crx2rnx"""

    for file in glob.glob(os.path.join(src_dir, glob_str)):
        crx_name = os.path.basename(file)
        # skip not matched filename
        if not CRINEXREG.match(crx_name):
            continue
        # output filename, using casing of the last letter in crx_name
        rnx_name = crx_name[:-1] + ('O' if str.isupper(crx_name[-1]) else 'o')
        rnx_path = os.path.join(out_dir, rnx_name)
        # run crx2rnx
        print('convert: %s ......' %file)
        command = 'crx2rnx - ' + file + ' > ' + rnx_path
        status = os.system(command)
        # delete source file if --keep is not setted
        if not keep and status == 0:
            os.remove(file)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                crx2rnx(child_path, out_dir, glob_str, keep, recursive)


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
        crx2rnx(directory, out_dir, glob_str, args.keep, args.recursive)

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Convert GSI Compact RINEX into Standard RINEX.')
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='crnx2rnx.py 0.1.1')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='keep original file in input dir')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][Dd]',
                        help='filename search mode [default: *.[0-9][0-9][Dd]')
    parser.add_argument('-out', metavar='<output_dir>', default='rinex',
                        help='output dir, [default: rinex in current]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
