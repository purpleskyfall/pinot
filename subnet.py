#coding=UTF-8
#create date: 2016/12/2
#creater: Jon Jiang
#Python version: 3.4

"""Create the subnets by a configuration file."""

import os
import sys
import glob
import shutil
import argparse
import yaml


# dir_path: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# site: site name, src_dir: source directory,
# out_dir: output directory, glob_str: glob string,
# recursive: search file recursively
def copysite(site, glob_str, src_dir, out_dir, recursive):
    """Copy RINEX file to subnet folders"""

    for file in glob.glob(os.path.join(src_dir, glob_str)):
        filename = os.path.basename(file)
        if site.upper() == filename[0:4].upper():
            print('copy: %s' %file)
            shutil.copy(file, out_dir)

    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                copysite(site, glob_str, child_path, out_dir, recursive)

# args: user input arguments
def main(args):
    """Main function"""

    # check if the configuration file exist
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: %s!" %args.cfg, file=sys.stderr)
        return 1

    with open(args.cfg) as cfgfile:
        subnets = yaml.load(cfgfile)

    src_dir, glob_str, out_dir = args.dir, args.glob, args.out
    createdir(out_dir)

    print('---------------------- input params ----------------------')
    print('source dir: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('config file: %s' %args.cfg)
    print('-------------------------------------------------------------------------------------\n')

    for net in subnets:
        print('process subnet: %s ......' %net)
        netdir = os.path.join(out_dir, net)
        createdir(netdir)
        for site in subnets[net]:
            for srcdir in glob.glob(src_dir):
                copysite(site, glob_str, srcdir, netdir, args.recursive)

    return 0


#脚本初始化方法，解析用户的输入参数
def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='Create the subnets by a configuration file.')
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='subnet.py 0.3.5')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oOdD]*',
                        help='mode is filename search mode [default: *.[0-9][0-9][oOdD]*')
    parser.add_argument('-out', metavar='<output>', default='subnets',
                        help='output dir [default: subnets in current]')
    parser.add_argument('-cfg', metavar='<config>', default='_subnet.yml',
                        help='configuration YAML file [default: ./subnet.yml]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
