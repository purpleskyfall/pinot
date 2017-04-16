#coding=UTF-8
# this script is used to rename files' name, upper to lower
# creater: Jon Jiang
# datetime: 2016-12-20
"""Rename files' name, upper to lower"""

import os
import shutil
import glob

#若文件夹不存在则创建
#dirpath: 文件夹路径
def createdir(dirpath):
    """Create new directory if not exist"""
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath)
        os.mkdir(dirpath)

# 重命名函数
# 参数表 srcpath: 输入文件夹, outpath: 输出文件夹, globstr: 通配符, recursive: 是否递归
def low2upper(srcpath, outpath, globstr, keep, recursive):
    """rename file name upper to lower"""
    # 如果输出文件夹为空，则在当前文件夹下执行重命名操作
    if outpath is None:
        for file in glob.glob(os.path.join(srcpath, globstr)):
            filedir, filename = os.path.split(file)
            print('rename file: ' + file)
            shutil.move(file, os.path.join(filedir, filename.upper()))
    # 如果输出文件夹不为空且设置了 keep 参数，则拷贝并重命名
    elif keep:
        for file in glob.glob(os.path.join(srcpath, globstr)):
            filename = os.path.basename(file)
            print('rename file: ' + file)
            shutil.copy(file, os.path.join(outpath, filename.upper()))
    # 如果输出文件夹不为空且为设置 keep 参数，则剪切并重命名
    else:
        for file in glob.glob(os.path.join(srcpath, globstr)):
            filename = os.path.basename(file)
            print('rename file: ' + file)
            shutil.move(file, os.path.join(outpath, filename.upper()))
    # 是否递归搜索
    if recursive:
        for child in os.listdir(srcpath):
            childpath = os.path.join(srcpath, child)
            if os.path.isdir(childpath):
                low2upper(childpath, outpath, globstr, keep, recursive)

def main(args):
    """main function"""
    srcdirs, outpath, globstr = args.dir, args.out, args.glob
    # 若用户设置了 keep 且输出文件夹为空，则报错
    if args.keep and outpath is None:
        print('Error! these was a conflict of blank outpath between --keep.')
        return 1
    if outpath is not None:
        createdir(outpath)
    print('-------------------- input params ----------------------')
    print('source dirs: ' + srcdirs)
    print('output dir: ' + str(outpath))
    print('file mode: ' + globstr)
    print('--------------------------------------------------------', end='\n\n')
    #开始处理
    for srcdir in glob.glob(srcdirs):
        low2upper(srcdir, outpath, globstr, args.keep, args.recursive)

#脚本初始化方法，解析用户的输入参数
def init_args():
    """Initilize function"""
    #引入参数解析模块
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description="rename files' name to upper.")
    #添加所需参数信息
    parser.add_argument('-k', '--keep', action='store_true'\
                        , help='keep original file in input dir')
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version', version='low2upper.py 0.1.6')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][od]*'\
                        , help='mode is filename search mode [default: *.[0-9][0-9][od]*')
    parser.add_argument('-out', metavar='<output_dir>'\
                        , help='the output dir, [default: self dir]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
