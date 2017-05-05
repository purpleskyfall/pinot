#coding=UTF-8
#create date: 2017/1/2
#creater: Zhou Maosheng
#Python version: 3.4

"""Convert leica m00 file to RINEX"""

import os
import sys
import glob
import argparse


# dir_path: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, year: year of data observation,
# recursive: search file recursively
def leica2rnx(src_dir, out_dir, year, glob_str, recursive):
    """Convert leica m00 file to RINEX using TEQC"""

    file_list = []
    for file in glob.glob(os.path.join(src_dir, glob_str)):
        # get site and doy in filename
        filename = os.path.basename(file)[0:7]
        # get global mode of source files
        sourcefile = os.path.join(src_dir, filename + '?.' +  'm00')
        if sourcefile not in file_list:
            file_list.append(sourcefile)

    for sourcefile in file_list:
        # name of output file
        rinexfile = os.path.basename(sourcefile)[0:7] + '0.' + year + 'o'
        gfile = os.path.basename(sourcefile)[0:7] + '0.' + year + 'g'
        nfile = os.path.basename(sourcefile)[0:7] + '0.' + year + 'n'
        # path of output file
        rnxfilepath = os.path.join(out_dir, rinexfile.lower())
        gfilepath = os.path.join(out_dir, gfile.lower())
        nfilepath = os.path.join(out_dir, nfile.lower())
        # run teqc
        print('generate file: %s %s %s ......' %(rinexfile, nfile, gfile))
        command = ('teqc +nav ' + nfilepath + ',' + gfilepath + 
                    ' ' + sourcefile + ' > ' + rnxfilepath)
        os.system(command)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                leica2rnx(child_path, out_dir, year, glob_str, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    src_dir, out_dir, year, glob_str = args.dir, args.out, args.yr, args.glob
    # valid the input year
    if not (year.isdigit() and (len(year) != 2 or len(year) != 4)):
        print('Parameter %s is not valid!' %year, file=sys.stderr)
        return 1
    year = year[-2:]
    createdir(out_dir)

    print('-------------------- input params ----------------------')
    print('source dirs: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('year of data: %s' %year)
    print('--------------------------------------------------------\n')

    for directory in glob.glob(src_dir):
        leica2rnx(directory, out_dir, year, glob_str, args.recursive)

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='translate leica m00 file to rinex.')
    
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='leica2rnx.py 0.1.6')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-yr', metavar='<year>', required=True,
                        help='year of data [required]')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[Mm]00',
                        help='filename search mode [default: *.[Mm]00]')
    parser.add_argument('-out', metavar='<output>', default='rinex',
                        help='output dir [default: rinex in current]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
