#coding=UTF-8
#create date: 2016/12/5
#creater: Zhou Maosheng
#Python version: 3.4

"""Unificate rinex files by a config.yml file"""

import os
import re
import sys
import glob
import time
import argparse
import threading
import yaml

# test if a filename is RINEX
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[o]$', re.I)
# test if a string contains alpha letters
ALPHAREG = re.compile(r'[a-z]+\s*', re.I)
# mapping of sites info and TEQC param
TEQCITEM = {'observer': '-O.o', 'agency': '-O.ag', 'rm_sys': '', 'obs_type': '-O.obs',
            'interval': '-O.dec', 'receiver': '-O.rt', 'antenna': '-O.at', 'delta': '-O.pe',
            'position': '-O.px'}
# params for multithread
THREADSIZE = 6
THREADCOUNT = 0
MUTEXCOUNT = threading.Lock()


# dirpath: directory path
def createdir(dir_path):
    """Create new directory if not exist"""

    if not os.path.exists(dir_path):
        print('create directory: %s' %dir_path)
        os.makedirs(dir_path)


# site: site name, sitesinfo: information in configuration file
def getinfo(site, sitesinfo):
    """Get information from cfgfile"""

    # get special site information from configuration
    info = sitesinfo.get(site.lower(), {})
    # get default information for 'all'
    default = {}
    if 'all' in sitesinfo:
        default = sitesinfo['all'].copy()
    # use site information to overwrite default
    for key in info:
        default[key] = info[key]

    return default


# info: site information
def getparams(info):
    """Get teqc params from user config info"""
    params = ''
    #遍历站点信息中的项目
    for key in info:
        if key == 'rm_sys':
            params += ' ' + TEQCITEM[key] + ' -' + ' -'.join(info[key])
        elif key == 'obs_type':
            params += ' ' + TEQCITEM[key] + ' ' + ','.join(info[key])
        else:
            if ALPHAREG.match(str(info[key])):
                params += ' ' + TEQCITEM[key] + ' "' + str(info[key]) + '"'
            else:
                params += ' ' + TEQCITEM[key] + ' ' + str(info[key]) + ''

    return params


# file: file path, params: teqc params, out_dir: output directory
def teqc(file, params, out_dir):
    """Execute TEQC command by os.system()"""

    global THREADCOUNT
    filename = os.path.basename(file)
    os.system('teqc' + params + ' ' + file + ' > ' + os.path.join(out_dir, filename))
    # decrease the THREADCOUNT when finished
    if MUTEXCOUNT.acquire():
        THREADCOUNT -= 1
        MUTEXCOUNT.release()


# commands: commands needed to be executed
def runtaskasync(commands):
    """Run commands async"""

    global THREADCOUNT
    thread = None

    while len(commands) > 0:
        # create new thread when THREADCOUNT less than THREADSIZE
        if THREADCOUNT < THREADSIZE and MUTEXCOUNT.acquire():
            #从待执行命令列表中取出一个执行
            cmd = commands.pop()
            print('unificate %s ......' %cmd['file'])
            thread = threading.Thread(target=teqc, args=(cmd['file'], cmd['params'], cmd['output']))
            thread.setDaemon(True)
            thread.start()
            # increase the THREADCOUNT
            THREADCOUNT += 1
            MUTEXCOUNT.release()

    #若待执行命令已经为空，则等待所有线程执行完毕之后退出
    # when commands are empty, wait all executing task are finished
    if thread is not None:
        thread.join()


# src_dir: source directory, out_dir: output directory,
# glob_str: glob string, sitesinfo: information in configuration file
# recursive: search file recursively
def process(glob_str, src_dir, out_dir, sitesinfo, recursive):
    """Unificate rinex files by user config info"""

    commands = []
    for file in glob.glob(os.path.join(src_dir, glob_str)):
        filename = os.path.basename(file)
        # if a file is not RINEX, skip it
        if not RINEXREG.match(filename):
            continue
        # get site name and information
        info = getinfo(filename[0:4], sitesinfo)
        params = getparams(info)
        commands.append({'file': file, 'params': params, 'output': out_dir})

    # run commands async
    runtaskasync(commands[::-1])
    # process subfolders if --recursive is setted
    if recursive:
        for child in os.listdir(src_dir):
            child_path = os.path.join(src_dir, child)
            if os.path.isdir(child_path):
                process(glob_str, child_path, out_dir, sitesinfo, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    # valid configuration file
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: %s" %args.cfg, file=sys.stderr)
        return 1

    # load configuration file
    with open(args.cfg) as cfgfile:
        sitesinfo = yaml.load(cfgfile)

    src_dir, glob_str, out_dir = args.dir, args.glob, args.out
    createdir(out_dir)

    print('---------------------- input params ------------------------')
    print('source dirs: %s' %src_dir)
    print('output dir: %s' %out_dir)
    print('file mode: %s' %glob_str)
    print('config file: %s' %args.cfg)
    print('------------------------------------------------------------\n')

    # save start time
    start = time.clock()

    for directory in glob.glob(src_dir):
        process(glob_str, directory, out_dir, sitesinfo, args.recursive)

    # calculate running time
    end = time.clock()
    print('\nuse seconds: %.5f' %(end - start))

    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description='unificate RINEX obs file by a YAML configuration.')
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='unificate.py 0.4.5')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='.',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oO]',
                        help='filename search mode [default: *.[0-9][0-9][oO]')
    parser.add_argument('-out', metavar='<output>', default='unificated',
                        help='output dir [default: unificated in current]')
    parser.add_argument('-cfg', metavar='<config>', default='_sitesinfo.yml',
                        help='configuration YAML file [default: _sitesinfo.yml]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
