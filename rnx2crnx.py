#coding=UTF-8
# this script is used to rename files' name, upper to lower
# creater: Jon Jiang
# datetime: 2017-03-26
"Convert standard RINEX into GSI compact RINEX"

import os
import re
import glob

#正则表达式，测试文件名是否为 RINEX
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[o]$', re.I)

#若文件夹不存在则创建
#dirpath: 文件夹路径
def createdir(dirpath):
    "Create new directory if not exist"
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath)
        os.mkdir(dirpath)

#调用 rnx2crx 程序进行文件转化
#srcdir: 输出文件夹; outdir: 输出文件夹; globstr: 文件名通配符; keep: 保留源文件; recursive: 递归标记
def rnx2crx(srcdir, outdir, globstr, keep, recursive):
    "convert standard rinex files"
    for file in glob.glob(os.path.join(srcdir, globstr)):
        # 获取 rinex 文件名
        rnxname = os.path.basename(file)
        # 若文件名不符合 rinex 文件命名规则则跳过
        if not RINEXREG.match(rnxname):
            continue
        # 计算输出文件名，保持输入输出文件名大小写一致
        crxname = rnxname[:-1] + 'D' if str.isupper(rnxname[-1]) else rnxname[:-1] + 'd'
        crxpath = os.path.join(outdir, crxname)
        # 运行 rnx2crx 程序
        print('convert: ' + file + ' ......')
        command = 'rnx2crx - ' + file + ' > ' + crxpath
        status = os.system(command)
        # 如果没有设置 --keep，则在转化成功后删除源文件
        if not keep and status == 0:
            os.remove(file)
    #若用户设置了-f参数，则递归处理子文件夹的内容
    if recursive:
        for child in os.listdir(srcdir):
            childpath = os.path.join(srcdir, child)
            if os.path.isdir(childpath):
                rnx2crx(childpath, outdir, globstr, keep, recursive)


def main(args):
    "main function"
    srcdirs, outdir, globstr = args.dir, args.out, args.glob
    # 若输出文件夹不存在则创建
    if outdir is not None:
        createdir(outdir)
    print('-------------------- input params ----------------------')
    print('source dirs: ' + srcdirs)
    print('output dir: ' + outdir)
    print('file mode: ' + globstr)
    print('--------------------------------------------------------', end='\n\n')
    #开始处理
    for srcdir in glob.glob(srcdirs):
        rnx2crx(srcdir, outdir, globstr, args.keep, args.recursive)

#脚本初始化方法，解析用户的输入参数
def init_args():
    "Initilize function"
    #引入参数解析模块
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description="Convert standard RINEX into GSI compact RINEX.")
    #添加所需参数信息
    parser.add_argument('-v', '--version', action='version', version='rnx2crnx.py 0.1.0')
    parser.add_argument('-k', '--keep', action='store_true'\
                        , help='keep original file in input dir')
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][Oo]'\
                        , help='mode is filename search mode [default: *.[0-9][0-9][Oo]')
    parser.add_argument('-out', metavar='<output_dir>', default='crinex'\
                        , help='the output dir, [default: crinex in current]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
