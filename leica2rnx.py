#coding=UTF-8
#this script is used to convert trimble file to rinex file.
#create date: 2017/1/2
#last modify: 2017/1/5
#creater: Zhou Maosheng
#Python version: 3.4
"""Convert leica receiver data to rinex"""

import os
import argparse
import glob

#检查并创建文件夹
#参数表 outdir:结果输出路径
def createdir(outdir):
    """Create new directory if not exist"""
    if not os.path.exists(outdir):
        print('make dir: ' + outdir + '\n')
        os.makedirs(outdir)

#徕卡原始数据转rinex数据
#参数表：inputdir: 输入文件的路径, outputdir: 结果输出路径, year: 需要处理的数据的年份 recursive:是否递归查找子文件夹
def leica2rnx(inputdir, outputdir, year, globstr, recursive):
    """a function of leica2rinex"""
    listfile = []
    for file in glob.glob(os.path.join(inputdir, globstr)):
        #获取到文件的站名和年积日，如bjfs001
        filename = os.path.basename(file)[0:7]
        #转换前的文件名
        sourcefile = os.path.join(inputdir, filename + '?.' +  'm00')
        if sourcefile not in listfile:
            listfile.append(sourcefile)

    for sourcefile in listfile:
        rinexfile = os.path.basename(sourcefile)[0:7] + '0.' + year + 'o'
        gfile = os.path.basename(sourcefile)[0:7] + '0.' + year + 'g'
        nfile = os.path.basename(sourcefile)[0:7] + '0.' + year + 'n'
        #rinex o文件路径 glonass导航文件路径 gps导航文件路径
        rnxfilepath = os.path.join(outputdir, rinexfile.lower())
        gfilepath = os.path.join(outputdir, gfile.lower())
        nfilepath = os.path.join(outputdir, nfile.lower())
        command = 'teqc +nav ' + nfilepath + ',' + gfilepath + \
                  ' ' + sourcefile + ' > ' + rnxfilepath
        print('generate file: ' + rinexfile.lower() +' '+ \
              gfile.lower() + ' ' + nfile.lower() + ' ......')
        os.system(command)
    #如果有-r参数，则进行递归查找
    if recursive:
        for child in os.listdir(inputdir):
            childpath = os.path.join(inputdir, child)
            #如果是符合条件的文件夹，则进入查
            if os.path.isdir(childpath):
                leica2rnx(childpath, outputdir, year, globstr, recursive)

def main(args):
    """main function"""
    inputdirs, outputdir, year, globstr = args.dir, args.out, args.yr, args.glob
    #检查输入的年份是否合法
    if not (year.isdigit() and (len(year) != 2 or len(year) != 4)):
        print('Parameter ' + year +' is not valid!')
        return 1
    #若输出文件夹不存在
    createdir(outputdir)
    print('-------------------- input params ----------------------')
    print('source  dirs: ' + inputdirs)
    print('output   dir: ' + outputdir)
    print('file    mode: ' + globstr)
    print('year of data: ' + year)
    print('--------------------------------------------------------\n')
    #获取两位年份
    year = year[-2:]
    for inputdir in glob.glob(inputdirs):
        leica2rnx(inputdir, outputdir, year, globstr, args.recursive)

    return 0

def init_args():
    """parse the user input"""
    parser = argparse.ArgumentParser(description='translate leica m00 file to rinex.')
    #添加所需参数信息
    parser.add_argument('-r', '--recursive', action='store_true'\
                            , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version', version='leica2rnx.py 0.1.5')
    parser.add_argument('-yr', metavar='<year>', required=True\
                            , help='year of data [required]')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                            , help='input dir mode [default: current]')
    parser.add_argument('-out', metavar='<output>', default='rinex'\
                            , help='output directory [default: rinex in current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[Tt]02'\
                        , help='mode is filename search mode [default: *.[Tt]02]')
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
