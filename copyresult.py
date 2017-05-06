#coding=UTF-8
#create date: 2016/12/26
#modifier: Jon Jiang
#Python version: 3.4

"""Copy GAMIT/GLOBK result file"""

import os
import sys
import glob
import shutil
import argparse

# global search mode of result files
FILEGLOB = {'o':'o????a.[0-9][0-9][0-9]', 'q':'q????a.[0-9][0-9][0-9]', \
           'h':'h????a.[0-9][0-9][0-9][0-9][0-9]', 'z':'z????[0-9].[0-9][0-9][0-9]',\
           'met':'met_????.[0-9][0-9][0-9][0-9][0-9]', \
           'org':'globk_????_[0-9][0-9][0-9][0-9][0-9].org', \
           'prt':'globk_????_[0-9][0-9][0-9][0-9][0-9].prt'}
# skip folders
OTHERDIR = ['archive', 'brdc', 'igs', 'control', 'figs', 'gfiles', 'glbf', \
            'ionex', 'met', 'mkrinex', 'raw', 'rinex', 'tables']


# dir_path: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('make dir: %s' %dir_path)
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# filetypes: file types, force: force overwrite,
# recursive: search file recursively
def copyfile(src_dir, out_dir, filetypes, recursive, force):
    """copy result file by filetypes from inputdir"""

    for filetype in filetypes:
        # if filetype is not in FILEGLOB, skip it
        if filetype not in FILEGLOB:
            print("Warning: file type %s is not valid, skip it!" %filetype, file=sys.stderr)
            continue
        for file in glob.glob(os.path.join(src_dir, FILEGLOB[filetype])):
            # get aim file path
            aimfilepath = os.path.join(out_dir, os.path.basename(file))
            # if aim file not exist or --force are setted
            if not os.path.exists(aimfilepath) or force:
                shutil.copy(file, out_dir)
                print('copy: %s' %file)
            else:
                # ask if overwrite
                overwrite = input("%s already exists, overwrite it? (y/n): " %file)
                while True:
                    if overwrite.lower() == 'y' or overwrite.lower() == 'yes':
                        shutil.copy(file, out_dir)
                        print('overwrite: %s' %file)
                        break
                    elif overwrite.lower() == 'n' or overwrite.lower == 'no':
                        print('skip: %s' %file)
                        break
                    else:
                        overwrite = input('Warning：input y or n: ')

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path) and child not in OTHERDIR:
                copyfile(child_path, out_dir, filetypes, recursive, force)


# args: user input arguments
def main(args):
    """Main function"""
    
    src_dir, out_dir, filetypes = args.dir, args.out, args.file
    createdir(out_dir)
  
    print('---------------------- input params ----------------------')
    print('source dir: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file types: %s' %', '.join(filetypes))
    print('----------------------------------------------------------\n')
  
    for directory in glob.glob(src_dir):
        copyfile(directory, out_dir, filetypes, args.recursive, args.force)

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Copy GAMIT/GLOBK result files.')
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='copyfile.py 0.1.6')
    parser.add_argument('-f', '--force', action='store_true',
                        help='force overwrite existing files')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-file', metavar='<type>', nargs='+', required=True,
                        help='type of file: o, q, h, z, met, org, prt [required]')
    parser.add_argument('-out', metavar='<output>', default='results',
                        help='output directory [default: results in current]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
