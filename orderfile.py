#coding=UTF-8
# a GNSS files order script, make files suit IGS style
# creater: Jon Jiang
# datetime: 2017-01-03
# Python version: 3.4

"""a GNSS files order script, make files suit IGS style"""

import os
import glob
import shutil
import re

# 正则表达式，测试一个文件是否为RINEX格式
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}.$', re.I)

#检查文件夹，若不存在则创建
#参数表：dirpath: 文件夹路径
def createdir(dirpath):
    """Create new directory if not exist"""
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath)
        os.mkdir(dirpath)

#将输入文件夹内的文件按照 IGS 的方式整理，并输出到输出文件夹中
#如果用户设置了 keep 选项，保存源文件不变（拷贝），否则移动源文件至输出文件夹
#如果用户设置了 recursive 选项，则递归地搜索子文件夹的内容
#参数表：srcpath: 源文件路径, globstr: 需处理文件通配符, outputdir: 输出文件夹, keep: 是否保留源文件, recursive: 是否递归
def orderdir(srcpath, globstr, outputdir, keep, recursive):
    """order dir to IGS style, recursive if setted"""
    # 遍历符合通配符的文件进行处理
    for file in glob.glob(os.path.join(srcpath, globstr)):
        filename = os.path.basename(file)
        # 如果文件名不符合 RINEX 格式，直接跳过
        if not RINEXREG.match(filename):
            continue
        # 从文件名获取年、年积日、文件类型
        year, doy, filetype = filename[-3:-1], filename[4:7], filename[-3:]
        year = '20' + year if int(year) < 80 else '19' + year
        # 生成年文件夹路径、年积日文件夹路径、文件类型文件夹路径
        yearpath = os.path.join(outputdir, year)
        doypath = os.path.join(yearpath, doy)
        typepath = os.path.join(doypath, filetype)
        # 若以上文件夹不存在则创建
        createdir(yearpath)
        createdir(doypath)
        createdir(typepath)
        # 开始整理文件
        if keep:
            print('copy file: ' + file)
            shutil.copy(file, typepath)
        else:
            print('move file: ' + file)
            shutil.move(file, typepath)
    # 如果用户设置了递归，则继续搜索子文件夹
    if recursive:
        for child in os.listdir(srcpath):
            childpath = os.path.join(srcpath, child)
            if os.path.isdir(childpath):
                orderdir(childpath, globstr, outputdir, keep, recursive)

# 程序主函数
# 参数表：args: 用户输入参数
def main(args):
    """main function"""
    # 从用户输入获取输入文件夹、输出文件夹、搜索通配符
    srcdirs, outpath, globstr = args.dir, args.out, args.glob
    # 打印输出提示
    print('-------------------- input params ----------------------')
    print('input path: ' + srcdirs)
    print('output path: ' + str(outpath))
    print('file mode: ' + globstr)
    print('--------------------------------------------------------', end='\n\n')
    # 开始处理
    createdir(outpath)
    for srcdir in glob.glob(srcdirs):
        orderdir(srcdir, globstr, outpath, args.keep, args.recursive)

    return 0

# 初始化函数，解析用户输入参数
def init_args():
    """parse user input"""
    # 引入参数解析模块
    import argparse
    # 创建解析器
    parser = argparse.ArgumentParser(description="order rinex files suit IGS style.")
    # 添加所需参数信息
    parser.add_argument('-v', '--version', action='version'\
                        , version='orderfile.py 0.1.3')
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-k', '--keep', action='store_true'\
                        , help='keep original file in input_dir')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9]?*'\
                        , help='filename search mode [default: *.[0-9][0-9]?*]')
    parser.add_argument('-out', metavar='<output_dir>', default='daily'
                        , help='output dir [default: daily in current]')

    # 运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
