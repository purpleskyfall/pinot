#coding=UTF-8
#this script is used to convert trimble file to rinex file.
#create date: 2017/1/3
#last modify: 2017/1/5
#creater: Zhou Maosheng
#Python version: 3.4

"""Translate trimble t00 file to rinex"""

import os
import glob
import shutil

#检查并创建文件夹
#参数表 dirpath: 结果输出路径
def createdir(dirpath):
    """Create new directory if not exist"""
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath + '\n')
        os.mkdir(dirpath)

#将天宝原始数据转化为 dat 数据
#参数表：inputdir: 输入文件的路径, outputdir: 结果输出路径, year: 需要处理的数据的年份 recursive:是否递归查找子文件夹
def trimble2dat(inputdir, outputdir, year, globstr, recursive):
    """a function of trimble2rinex"""
    for file in glob.glob(os.path.join(inputdir, globstr)):
        tempdir = os.path.join(outputdir, 'temp')
        print('translate file: ' + file)
        os.system('runpkr00 -d ' + file + ' '+ tempdir)
    #若用户设置了递归，则继续处理子文件夹
    if recursive:
        for child in os.listdir(inputdir):
            childpath = os.path.join(inputdir, child)
            #如果是符合条件的文件夹，则进入查
            if os.path.isdir(childpath):
                trimble2dat(childpath, outputdir, year, globstr, recursive)

#将天宝 dat 数据转为 rinex 数据
#参数表：tempdir: dat文件输出的临时文件夹路径, outputdir: rinex文件输出文件夹, year: 要处理的数据的年份
def dat2rnx(tempdir, outputdir, year):
    """a function of datfile2rinexfile"""
    #需使用TEQC进行处理的数据集列表
    listfile = []
    #对temp文件夹的文件进行遍历
    for file in os.listdir(tempdir):
        #获取到文件的站名和年积日，如bjfs001
        filename = os.path.basename(file)[0:7]
        #转换前的文件名
        datfile = os.path.join(tempdir, filename + '??.' +  'DAT')
        if datfile not in listfile:
            listfile.append(datfile)

    for datfile in listfile:
        #生成的O文件、N文件、G文件文件名
        rinexfile = os.path.basename(datfile)[0:7] + '0.' + year + 'o'
        gfile = os.path.basename(datfile)[0:7] + '0.' + year + 'g'
        nfile = os.path.basename(datfile)[0:7] + '0.' + year + 'n'
        #rinex o文件路径 glonass导航文件路径 gps导航文件路径
        rnxfilepath = os.path.join(outputdir, rinexfile.lower())
        gfilepath = os.path.join(outputdir, gfile.lower())
        nfilepath = os.path.join(outputdir, nfile.lower())
        #需执行的TEQC命令
        command = 'teqc +nav ' + nfilepath + ',' + gfilepath + \
                  ' ' + datfile + ' > ' + rnxfilepath
        #打印提示
        print('generate file: ' + rinexfile.lower() +' '+ \
              gfile.lower() + ' ' + nfile.lower() + ' ......')
        #开始执行TEQC
        os.system(command)

def main(args):
    """main function"""
    inputdirs, outputdir, year, globstr = args.dir, args.out, args.yr, args.glob
    #检查输入的年份是否合法
    if not (year.isdigit() and (len(year) != 2 or len(year) != 4)) or year == ' ':
        print('Parameter ' + '\'' + 'year' +'\'' + ' is not valid!')
        return 1
    tempdir = os.path.join(outputdir, 'temp')
    print('-------------------- input params ----------------------')
    print('source  dirs: ' + inputdirs)
    print('output   dir: ' + outputdir)
    print('file    mode: ' + globstr)
    print('year of data: ' + year)
    print('--------------------------------------------------------\n')
    #若临时输出文件夹不存在
    createdir(outputdir)
    createdir(tempdir)
    #获取两位年份,如16
    year = str(year)[-2:]
    #将T00文件转化为DAT，输出到临时文件夹内
    for inputdir in glob.glob(inputdirs):
        trimble2dat(inputdir, outputdir, year, globstr, args.recursive)
    #将DAT文件转换为RINEX格式
    dat2rnx(tempdir, outputdir, year)
    #删除临时文件夹
    shutil.rmtree(tempdir)

    return 0

def init_args():
    """parse the user input"""
    #引入参数解析模块
    import argparse
    #解析用户输入参数
    parser = argparse.ArgumentParser(description='translate trimble t00 file to rinex.')
    #添加所需参数信息
    parser.add_argument('-v', '--version', action='version', version='trimble2rnx.py 0.1.3')
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-yr', metavar='<year>', required=True\
                        , help='year of data [required]')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                            , help='input dir mode [default: current]')
    parser.add_argument('-out', metavar='<output>', default='./rinex'\
                            , help='output directory [default: rinex in Upper directory]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[tT]02'\
                        , help='mode is filename search mode [default: *.[tT]02]')

    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
