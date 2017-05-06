#coding=UTF-8
#creater: Jon Jiang
#datetime: 2016-12-20
#Python version: 3.4
#TEQC version: 2016Nov7

"""Check the quality of RINEX observation files by TEQC"""

import os
import re
import glob
import argparse
import datetime


# test if a file is RINEX observation file
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[o]$', re.I)
# flag of quality message in TEQC output file
QUALITYINFO = [
    {'name': 'start', 'flag': 'Time of start of window :', 'start': 38, 'end': None, 'len': 16},
    {'name': 'end', 'flag': 'Time of  end  of window :', 'start': 38, 'end': None, 'len': 16},
    {'name': 'length', 'flag': 'Time line window length :', 'start': 26, 'end': 42, 'len': 16},
    {'name': 'SN1', 'flag': 'Mean S1                 :', 'start': 26, 'end': 31, 'len': 9},
    {'name': 'SN2', 'flag': 'Mean S2                 :', 'start': 26, 'end': 31, 'len': 9}]
# flag of MP1, MP2, CSR
MPCSRFLAG = 'first epoch    last epoch    hrs   dt  #expt  #have   %   mp1   mp2 o/slps'
# other file type maybe output after quality check
OTHERFILES = ['.azi', '.ele', '.iod', '.ion', '.mp1', '.mp2', '.sn1', '.sn2']


def tableheader():
    """Create a table header for table output mode"""

    tabheaders = []

    tabheaders.append('file'.center(14, ' '))
    tabheaders.append('date'.center(12, ' '))
    for item in QUALITYINFO:
        tabheaders.append(item['name'].center(item['len'], ' '))
    tabheaders.append('MP1'.center(8, ' '))
    tabheaders.append('MP2'.center(8, ' '))
    tabheaders.append('CSR'.center(8, ' '))

    return ''.join(tabheaders)


# filename: name of file
def getyear(filename):
    """Get 4 digit year from RINEX filename"""

    year = int(filename[-3:-1])
    return 2000 + year if year < 80 else 1900 + year


# filename: name of file
def getdoy(filename):
    """Get day of year from rinex obs filename"""

    doy = filename[4:7]
    return int(doy)


# year: year of observation data, doy: day of year
def getdate(year, doy):
    """Convert year and doy to date"""

    initdate = datetime.date(year, 1, 1)
    delta = datetime.timedelta(doy - 1)
    result = initdate + delta

    return result


# result_file: result file of quality check, out_type: list or table
def getqualitymarks(result_file, out_type):
    """Return qualitycheck marks from result file, list or table"""

    # output info
    outputs = []
    # index of QUALITYINFO
    infoindex = 0

    with open(result_file) as result_reader:
        for line in result_reader:
            # because the order of output messages are same, so we can only check a message flag once
            if infoindex < len(QUALITYINFO) and line.find(QUALITYINFO[infoindex]['flag']) != -1:
                # get value of quality check result
                info = QUALITYINFO[infoindex]
                value = line[info['start']: info['end']].strip()
                # when process the length of observation, need to split the output by ','
                if infoindex == 2 and value.find(',') != -1:
                    value = value.split(',')[0]
                if out_type == 'list' or out_type == 'l':
                    outputs.append(info['name'] + ': ' + value)
                else:
                    outputs.append(value.center(info['len'], ' '))
                # increase the index to check next message
                infoindex += 1
                continue
            # when the check of QUALITYINFO is finished, start to process MP1, MP2 and CSR
            if infoindex == len(QUALITYINFO) and line.find(MPCSRFLAG) != -1:
                # messages are in next line
                line = result_reader.readline()
                mp1, mp2, o_slps = line[63:67].strip(), line[69:73].strip(), line[75:].strip()
                # calculate CSR by o_slps
                csr = round(1000 / float(o_slps), 2)
                # add to output info
                if out_type == 'list' or out_type == 'l':
                    outputs.append('MP1: ' + mp1)
                    outputs.append('MP2: ' + mp2)
                    outputs.append('CSR: ' + str(csr))
                else:
                    outputs.append(mp1.center(8, ' '))
                    outputs.append(mp2.center(8, ' '))
                    outputs.append(str(csr).center(8, ' '))
                break

    return outputs


# file: RINEX observation file, out_type: list or table
def execteqc(file, out_type):
    """Execute TEQC quality check"""
    # get file directory path and filename
    filedir, filename = os.path.split(file)
    # get the path of result file
    result_file = os.path.join(filedir, filename[0:-1] + 'S')
    outputs = []
    # run teqc
    os.system('teqc +out temp.log ++err temp.log +qc ' + file)
    # get quality check info and remove the result file
    if os.path.exists(result_file):
        outputs = getqualitymarks(result_file, out_type)
        os.remove(result_file)
    # remove other file maybe create in quality check
    for file_type in OTHERFILES:
        tempfile = os.path.join(filedir, filename[0:-4] + file_type)
        if os.path.exists(tempfile):
            os.remove(tempfile)
    # get the observation date of RINEX file
    dateofdata = getdate(getyear(filename), getdoy(filename))
    strdate = dateofdata.strftime('%Y-%m-%d')
    
    # output the quality check info
    if out_type == 'list' or out_type == 'l':
        print('\n%s quality marks:' %file)
        print('date: %s' %strdate)
        for output in outputs:
            print(output)
    else:
        outputs.insert(0, strdate.center(12, ' '))
        outputs.insert(0, filename.ljust(14, ' '))
        print(''.join(outputs))


# src_dir: source directory, glob_str: glob string,
# out_type: list or table, recursive: search file recursively
def qualitycheck(src_dir, glob_str, out_type, recursive):
    """check obs quality by TEQC"""
    for file in glob.glob(os.path.join(src_dir, glob_str)):
        filename = os.path.basename(file)
        #使用正则表达式检查文件名是否为RINEX
        if not RINEXREG.match(filename):
            continue
        #使用TEQC程序进行质量检查处理
        execteqc(file, out_type)
    #如果用户设置了递归，则继续处理子文件夹
    if recursive:
        for child in os.listdir(src_dir):
            childpath = os.path.join(src_dir, child)
            if os.path.isdir(childpath):
                qualitycheck(childpath, glob_str, out_type, recursive)


# args: user input arguments
def main(args):
    """Main function"""

    src_dir, glob_str, out_type = args.dir, args.glob, args.out

    print('----------------- input params ---------------')
    print('source dir: %s' %src_dir)
    print('file mode: %s' %glob_str)
    print('----------------------------------------------')

    # if the out_type is table, print a table header first
    if out_type == 'table' or out_type == 't':
        print('\n' + tableheader())
    # start quality check
    for srcdir in glob.glob(src_dir):
        qualitycheck(srcdir, glob_str, out_type, args.recursive)
    # remove temp file
    if os.path.exists('temp.log'):
        os.remove('temp.log')
    
    return 0


def init_args():
    """Initilize function, parse user input"""

    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="rinex quality check script used TEQC.")
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='qualitycheck.py 0.2.2')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file in subfolders')
    parser.add_argument('-dir', metavar='<input_dir>', default='./',
                        help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oO]',
                        help='filename search mode [default: *.[0-9][0-9][oO]')
    parser.add_argument('-out', metavar='<type>', default='list',
                        choices=['list', 'l', 'table', 't'],
                        help='format of output messages, list or table [default: list]')

    return main(parser.parse_args())


if __name__ == '__main__':
    init_args()
