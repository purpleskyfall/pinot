#coding=UTF-8
#create date: 2017/1/3
#creater: Zhou Maosheng
#Python version: 3.4

"""Convert trimble t00 file to RINEX"""

import os
import sys
import glob
import shutil
import argparse


# dir_path: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('make dir: ' + dir_path + '\n')
        os.makedirs(dir_path)


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, year: year of data observation,
# recursive: search file recursively
def trimble2dat(src_dir, out_dir, year, glob_str, recursive):
    """Convert trimble t00 file to dat"""

    for file in glob.glob(os.path.join(src_dir, glob_str)):
        # run runpkr00
        print('translate file: %s' %file)
        os.system('runpkr00 -d ' + file + ' '+ out_dir)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                trimble2dat(child_path, out_dir, year, glob_str, recursive)


# src_dir: source directory, outputdir: output directory,
# year: year of dara observation
def dat2rnx(src_dir, out_dir, year):
    """Convert trimble dat file to RINEX"""

    file_list = []
    for file in os.listdir(src_dir):
        # get site and doy in filename
        filename = os.path.basename(file)[0:7]
        datfile = os.path.join(src_dir, filename + '??.' +  'DAT')
        if datfile not in file_list:
            file_list.append(datfile)

    for datfile in file_list:
        # name of output file
        rinexfile = os.path.basename(datfile)[0:7] + '0.' + year + 'o'
        gfile = os.path.basename(datfile)[0:7] + '0.' + year + 'g'
        nfile = os.path.basename(datfile)[0:7] + '0.' + year + 'n'
        # path of output file
        rnxfilepath = os.path.join(out_dir, rinexfile.lower())
        gfilepath = os.path.join(out_dir, gfile.lower())
        nfilepath = os.path.join(out_dir, nfile.lower())
        # run teqc
        print('generate file: %s %s %s ......' %(rinexfile, nfile, gfile))
        command = ('teqc +nav ' + nfilepath + ',' + gfilepath + 
                    ' ' + datfile + ' > ' + rnxfilepath)
        os.system(command)


# args: user input arguments
def main(args):
    """Main function"""

    src_dir, out_dir, year, glob_str = args.dir, args.out, args.yr, args.glob
    # valid the input year
    if not (year.isdigit() and (len(year) != 2 or len(year) != 4)) or year == ' ':
        print('Parameter %s is not valid!' %year, file=sys.stderr)
        return 1
    year = str(year)[-2:]

    tempdir = os.path.join(out_dir, 'temp')
    createdir(out_dir)
    createdir(tempdir)

    print('---------------------- input params ----------------------')
    print('source dirs: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('year of data: %s' %year)
    print('----------------------------------------------------------\n')
    
    # Convert t00 file to dat and output to tempdir
    for inputdir in glob.glob(src_dir):
        trimble2dat(inputdir, tempdir, year, glob_str, args.recursive)
    # Convert dat file to RINEX
    dat2rnx(tempdir, out_dir, year)
    shutil.rmtree(tempdir)

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='translate trimble t00 file to rinex.')

    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='trimble2rnx.py 0.1.4')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-yr', metavar='<year>', required=True,
                        help='year of data [required]')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[Tt]02',
                        help='filename search mode [default: *.[Tt]02]')
    parser.add_argument('-out', metavar='<output>', default='rinex',
                        help='output directory [default: rinex in current]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
