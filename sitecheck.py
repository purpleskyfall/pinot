#coding=UTF-8
#create date: 2017/1/6
#creater: Jon Jiang
#Python version: 3.4

"""Check if RINEX observation file exist in source folder by a sites list in YAML"""

import os
import sys
import yaml
import argparse


# dir_path: directory path, filename: name of file,
# recursive: search file recursively
def existfile(dir_path, filename, recursive):
    """check if file exist in dirpath"""
    # if file in dir_path, return True
    if os.path.exists(os.path.join(dir_path, filename)):
        return True

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(dir_path):
            child_path = os.path.join(dir_path, child)
            if os.path.isdir(child_path):
                if existfile(child_path, filename, recursive):
                    return True

    return False


# args: user input arguments
def main(args):
    """Main function"""

    # vaild the configuration file
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: %s!" %args.cfg, file=sys.stderr)
        return 1

    src_dir, doy, year = args.dir, args.doy, args.yr
    # laod configuration file
    with open(args.cfg) as cfgfile:
        sites = yaml.load(cfgfile)
    # get 3 digit doy
    doy = doy.rjust(3, '0')
    # valid year
    if not(year.isdigit() and (len(year) == 2 or len(year) == 4)):
        print("Error! year of data isn't vaild!", file=sys.stderr)
        return 1
    # valid doy
    if not doy.isdigit() or int(doy) > 366 :
        print("Error! day of year isn't vaild!", file=sys.stderr)
        return 1

    print('---------------------- input params ----------------------')
    print('source dir: %s' %src_dir)
    print('year of data: %s' %year)
    print('day of year: %s' %doy)
    print('config file: %s' %args.cfg)
    print('----------------------------------------------------------\n')

    messingsites = []
    for site in sites:
        # get observation file name
        ofilename = site.lower() + doy + '0.' + year[-2:] + 'o'
        dfilename = site.lower() + doy + '0.' + year[-2:] + 'd'        
        #add messing site into messingsites
        if not (existfile(src_dir, ofilename, args.recursive) or
                existfile(src_dir, dfilename, args.recursive)):
            messingsites.append(site)

    if len(messingsites) > 0:
        print('sites not found in %s %s: %s.' %(year, doy, ', '.join(messingsites)))

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='check if obs file exist by a sites list in YAML.')
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='sitecheck.py 0.1.4')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir [default: current]')
    parser.add_argument('-cfg', metavar='<config>', default='_sites.yml',
                        help='configuration YAML file [default: _sites.yml]')
    parser.add_argument('-yr', metavar='<year>', required=True,
                        help='data observation year [required]')
    parser.add_argument('-doy', metavar='<doy>', required=True,
                        help='observation day of year [required]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
