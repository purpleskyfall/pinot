#coding=UTF-8
#this script is used to move GAMIT/GLOBK result files.
#create date: 2016/12/26
#last modify: 2016/12/28
#creater: Zhou Maosheng
#modifier: Jon Jiang
#Python version: 3.4

"Copy the GAMIT/GLOBK result file "

import os
import shutil
import glob

#各结果文件所对应的通配符
FILEGLOB = {'o':'o????a.[0-9][0-9][0-9]', 'q':'q????a.[0-9][0-9][0-9]', \
           'h':'h????a.[0-9][0-9][0-9][0-9][0-9]', 'z':'z????[0-9].[0-9][0-9][0-9]',\
           'met':'met_????.[0-9][0-9][0-9][0-9][0-9]', \
           'org':'globk_????_[0-9][0-9][0-9][0-9][0-9].org', \
           'prt':'globk_????_[0-9][0-9][0-9][0-9][0-9].prt'}
#无需检查的文件夹
OTHERDIR = ['archive', 'brdc', 'igs', 'control', 'figs', 'gfiles', 'glbf', \
            'ionex', 'met', 'mkrinex', 'raw', 'rinex', 'tables']

#检查并创建文件夹
#参数表：dirpath: 文件夹路径
def createdir(dirpath):
    "Create new directory if not exist"
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath)
        os.makedirs(dirpath)

#获取文件并实现数据拷贝
def getfile(inputdir, outputdir, filetypes, recursive, force):
    "copy result file by filetypes from inputdir to outputdir"
    #循环输入的文件类型
    for filetype in filetypes:
        #若输入的文件类型不在预设 FILEGLOB 内，则跳过
        if filetype not in FILEGLOB:
            print("Warning:" + "'" + filetype + "'" + " file type is not valid, skip it!")
            continue
        for file in glob.glob(os.path.join(inputdir, FILEGLOB[filetype])):
            aimfilepath = os.path.join(outputdir, os.path.basename(file))
            createdir(outputdir)
            #如果目标文件路径不存在冲突或指定了强制覆盖，直接复制
            if not os.path.exists(aimfilepath) or force:
                shutil.copy(file, outputdir)
                print('copy ' + file)
            else:
                #进行是否覆盖的询问
                overwrite = input(file + " already exists, overwrite it? (y/n): ")
                while True:
                    if overwrite.lower() == 'y' or overwrite == 'yes':
                        shutil.copy(file, outputdir)
                        print('overwrite ' + file)
                        break
                    elif overwrite.lower() == 'n' or overwrite == 'no':
                        print('skip ' + file)
                        break
                    else:
                        print('Warning：input y or n!')
#如果有-r参数，则进行递归查找
    if recursive:
        for child in os.listdir(inputdir):
            childpath = os.path.join(inputdir, child)
            #如果是符合条件的文件夹，则进入查找
            if os.path.isdir(childpath) and child not in OTHERDIR:
                getfile(childpath, outputdir, filetypes, recursive, force)

def main(args):
    "main function"
    inputdirs, outputdir, filetypes = args.dir, args.out, args.files
    #输出提示信息
    print('-------------------------- input params ----------------------------')
    print('source dir: ' + inputdirs)
    print('file types: ' + ', '.join(filetypes))
    print('output dir: ' + outputdir)
    print('--------------------------------------------------------------------', end='\n\n')
    #开始执行
    for inputdir in glob.glob(inputdirs):
        getfile(inputdir, outputdir, filetypes, args.recursive, args.force)

    return 0

def init_args():
    "init function, parse user input"
    import argparse
    parser = argparse.ArgumentParser(description='copy GAMIT/GLOBK result files.')
    #添加所需参数信息
    parser.add_argument('-f', '--force', action='store_true'\
                            , help='whether to overwrite existing files')
    parser.add_argument('-r', '--recursive', action='store_true'\
                            , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version', version='copyfile.py 0.1.3')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                            , help='input dir mode [default: current]')
    parser.add_argument('-files', metavar='<type>', nargs='+', default='o'\
                            , help='type of file: o, q, h, z, met, org, prt. [default: o]')
    parser.add_argument('-out', metavar='<output>', default='./results'\
                            , help='output directory [default: results in current]')

    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
