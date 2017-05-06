#coding=UTF-8
#create date: 2016/12/9
#creater: Zhou Maosheng
#modifier: Jon Jiang
#Python version: 3.4

"""Check if site information changed"""

import os
import re
import sys
import glob
import yaml
import argparse

# test if a file is RINEX observation file or Compact RINEX
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[od]$', re.I)
# mapping of information to RINEX flag
SITEINFO = {'receiver': {'flag': 'REC # / TYPE / VERS', 'start': 20, 'end': 40}\
            , 'antenna': {'flag': 'ANT # / TYPE', 'start': 20, 'end': 40}\
            , 'delta': {'flag': 'ANTENNA: DELTA H/E/N', 'start': 0, 'end': 42}\
            , 'position': {'flag': 'APPROX POSITION XYZ', 'start': 0, 'end': 42}}
# save the site not found in configuration file
MISSINGSITES = []


# info: site information, file: RINEX file
# threshold: threshold of position change
# out_type: list or table
def compareinfo(info, file, threshold, out_type):
    """Compare site information and RINEX file"""

    header, differences = [], []
    filename = os.path.basename(file)
    # load RINEX file header
    with open(file) as ofile:
        for line in ofile:
            header.append(line)
            if -1 != line.find('END OF HEADER'):
                break
    # start information check
    for item in info:
        # if a information item is not in SITEINFO, skip it
        if item not in SITEINFO:
            continue
        for line in header:
            # if can not find flag in this line, continue to check next line
            if -1 == line.find(SITEINFO[item]['flag']):
                continue
            # get information from RINEX header
            fileinfostr = line[SITEINFO[item]['start']: SITEINFO[item]['end']]
            # if the checking item is approx position
            if item == 'position':
                # get position from configuration file and RINEX file
                cfgposis = info[item].split()
                fileposis = fileinfostr.split()
                # check position
                for (cfgposi, fileposi) in zip(cfgposis, fileposis):
                    # if any difference is large than threshold, it should be outputed
                    if threshold < abs(float(cfgposi) - float(fileposi)):
                        if out_type == 'list' or out_type == 'l':
                            differences.append(item + ' in cfg file: ' + ', '.join(cfgposis))
                            differences.append(item + ' in obs file: ' + ', '.join(fileposis))
                        else:
                            message = (file.center(40, ' ') + item.center(14, ' ') +
                                        (','.join(cfgposis)).center(46, ' ') +
                                        (','.join(fileposis)).center(46, ' '))
                            differences.append(message)
                        break
                break
            # check other information
            if info[item] != fileinfostr.strip():
                if out_type == 'list' or out_type == 'l':
                    differences.append(item + ' in cfg file: ' + info[item])
                    differences.append(item + ' in obs file: ' + fileinfostr.strip())
                else:
                    message = (filename.center(16, ' ') + item.center(14, ' ') + 
                                info[item].center(46, ' ') +
                                fileinfostr.strip().center(46, ' '))
                    differences.append(message)
                break
    # output differences
    if len(differences):
        if out_type == 'list' or out_type == 'l':
            print('\n%s has differences:' %file)
        print('\n'.join(differences))


# src_dir: source directory, glob_str: glob string,
# sitesinfo: sitesinfo in configuration file, 
# threshold: threshold of position difference
# out_type: list or table, recursive: search file recursively
def checksite(glob_str, src_dir, sitesinfo, out_type, threshold, recursive):
    """Check site info, search children folder in recursive is set"""

    for file in glob.glob(os.path.join(src_dir, glob_str)):
        filename = os.path.basename(file)
        # if a file is not RINEX, skip it
        if not RINEXREG.match(filename):
            continue
        # git file info in configuration file
        site = filename[0:4].lower()
        info = sitesinfo.get(site)
        # if a site information not found in configuration file
        if info is None:
            if site not in MISSINGSITES:
                MISSINGSITES.append(site)
            continue
        compareinfo(info, file, threshold, out_type)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            childpath = os.path.join(src_dir, child)
            if os.path.isdir(childpath):
                checksite(glob_str, childpath, sitesinfo, out_type, threshold, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    # valid the configuration file
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: %s" %args.cfg, file=sys.stderr)
        return 1
    # load sites information from configuration file
    with open(args.cfg) as cfgfile:
        sitesinfo = yaml.load(cfgfile)

    src_dir, glob_str, out_type, threshold = args.dir, args.glob, args.out, args.thd
    
    print('---------------------- input params ----------------------')
    print('source dirs: %s' %src_dir)
    print('file mode: %s' %glob_str)
    print('config file: %s' %args.cfg)
    print('----------------------------------------------------------')

    # if out_type is table, print a table header first
    if out_type == 'table' or out_type == 't':
        print('\n' + 'file'.center(16, ' ') + 'type'.center(14, ' ')
                + 'cfgfile'.center(46, ' ') + 'obsfile'.center(46, ' '))
    
    for directory in glob.glob(src_dir):
        checksite(glob_str, directory, sitesinfo, out_type, threshold, args.recursive)
    
    if len(MISSINGSITES) > 0:
        print('\nsites not found in cfg file: %s.' %', '.join(MISSINGSITES))
    
    return 0


#脚本初始化方法，解析用户的输入参数
def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="compare RINEX files' meta between YAML configuration.")
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='metacheck.py 0.3.10')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oOdD]',
                        help='filename search mode [default: *.[0-9][0-9][oOdD]')
    parser.add_argument('-cfg', metavar='<config>', default='_sitesinfo.yml',
                        help='configuration YAML file [default: _sitesinfo.yml]')
    parser.add_argument('-out', metavar='<type>', default='list',
                        choices=['list', 'l', 'table', 't'],
                        help='format of output messages, list or table [default: list]')
    parser.add_argument('-thd', metavar='<threshold>', default=10, type=int,
                        help='threshold of position change [default: 10]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
