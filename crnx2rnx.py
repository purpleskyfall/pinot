#coding=UTF-8
# this script is used to rename files' name, upper to lower
# creater: Jon Jiang
# datetime: 2017-03-26
"Convert GSI compact RINEX into standard RINEX"

import os
import re
import glob

#正则表达式，测试文件名是否为 Compact RINEX
CRINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[d]$', re.I)

#若文件夹不存在则创建
#dirpath: 文件夹路径
def createdir(dirpath):
    "Create new directory if not exist"
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath)
        os.mkdir(dirpath)

#调用 crx2rnx 程序进行文件转化
#srcdir: 输出文件夹; outdir: 输出文件夹; globstr: 文件名通配符; keep: 保留源文件; recursive: 递归标记
def crx2rnx(srcdir, outdir, globstr, keep, recursive):
    "convert compact rinex files"
    for file in glob.glob(os.path.join(srcdir, globstr)):
        # 获取 compact rinex 文件名
        crxname = os.path.basename(file)
        # 若文件名不符合 crinex 文件命名规则则跳过
        if not CRINEXREG.match(crxname):
            continue
        # 计算输出文件名，保持输入输出文件名大小写一致
        rnxname = crxname[:-1] + 'O' if str.isupper(crxname[-1]) else crxname[:-1] + 'o'
        rnxpath = os.path.join(outdir, rnxname)
        # 运行 crx2rnx 程序
        print('convert: ' + file + ' ......')
        command = 'crx2rnx - ' + file + ' > ' + rnxpath
        status = os.system(command)
        # 如果没有设置 --keep，则在转化成功后删除源文件
        if not keep and status == 0:
            os.remove(file)
    #若用户设置了-f参数，则递归处理子文件夹的内容
    if recursive:
        for child in os.listdir(srcdir):
            childpath = os.path.join(srcdir, child)
            if os.path.isdir(childpath):
                crx2rnx(childpath, outdir, globstr, keep, recursive)


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
        crx2rnx(srcdir, outdir, globstr, args.keep, args.recursive)

#脚本初始化方法，解析用户的输入参数
def init_args():
    "Initilize function"
    #引入参数解析模块
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description="Convert GSI compact RINEX into standard RINEX.")
    #添加所需参数信息
    parser.add_argument('-v', '--version', action='version', version='crnx2rnx.py 0.1.0')
    parser.add_argument('-k', '--keep', action='store_true'\
                        , help='keep original file in input dir')
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][Dd]'\
                        , help='mode is filename search mode [default: *.[0-9][0-9][Dd]')
    parser.add_argument('-out', metavar='<output_dir>', default='rinex'\
                        , help='the output dir, [default: rinex in current]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
