#coding=UTF-8
# rename GNSS file by a YAML configuration
# creater: Jon Jiang
# datetime: 2017-01-03
# Python version: 3.4

"rename GNSS file by a YAML configuration"

import os
import glob
import shutil
import re

# 正则表达式，测试一个文件是否为RINEX格式
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[a-z]$', re.I)

# 检查文件夹，若不存在则创建
# 参数表：dirpath: 文件夹路径
def createdir(dirpath):
    "Create new directory if not exist"
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath)
        os.mkdir(dirpath)

# 对文件进行重命名
# 参数表：srcdir: 输入文件夹, globstr: 通配符, outpath: 输出文件夹,
# sitemap: 站名映射表, keep: 是否保留源文件, recursive: 是否递归
def rename(srcdir, globstr, outpath, sitemap, keep, recursive):
    "rename files in dir"
    for file in glob.glob(os.path.join(srcdir, globstr)):
        # 获取文件名、站点名
        filename = os.path.basename(file)
        site = filename[:4].lower()
        # 若文件并非 RINEX 格式命名或站点名不在配置文件中，则跳过
        if not RINEXREG.match(filename) or site not in sitemap:
            continue
        # 新的站点名
        newsite = sitemap[site]
        newname = newsite + filename[4:]
        # 若输出文件夹为空，输出到源文件所在目录
        if outpath is None:
            filedir = os.path.dirname(file)
            newfile = os.path.join(filedir, newname)
        # 若输出文件夹非空，输出到输出文件夹
        else:
            newfile = os.path.join(outpath, newname)
        # 若用户设置了 keep，则保留源文件，否则移动
        print('rename: ' + file + ' => ' + newfile)
        if keep:
            shutil.copy(file, newfile)
        else:
            shutil.move(file, newfile)
    # 若用户设置了递归，则继续处理子文件夹
    if recursive:
        for child in os.listdir(srcdir):
            childpath = os.path.join(srcdir, child)
            if os.path.isdir(childpath):
                rename(childpath, globstr, outpath, sitemap, keep, recursive)

# 主函数
# 参数表：args: 用户输出参数
def main(args):
    "main function"
    import yaml
    # 获取配置文件
    if not os.path.exists(args.cfg):
        print('Error! cfg file not exit!')
        return 1
    # 加载配置文件
    cfgfile = open(args.cfg)
    sitemap = yaml.load(cfgfile)
    cfgfile.close()
    # 从用户输入获取输入文件夹、输出文件夹、搜索通配符
    srcdirs, outpath, globstr = args.dir, args.out, args.glob
    # 打印输出提示
    print('-------------------- input params ----------------------')
    print('source dirs: ' + srcdirs)
    print('config file: ' + args.cfg)
    print('output dir: ' + str(outpath))
    print('file mode: ' + globstr)
    print('--------------------------------------------------------', end='\n\n')
    # 开始处理
    if outpath is not None:
        createdir(outpath)
    for srcdir in glob.glob(srcdirs):
        rename(srcdir, globstr, outpath, sitemap, args.keep, args.recursive)

    return 0

def init_args():
    "parser user input"
    # 引入模块
    import argparse
    # 创建解析器
    parser = argparse.ArgumentParser(description='rename GNSS file by a YAML configuration.')
    # 添加所需参数信息
    parser.add_argument('-v', '--version', action='version'\
                        , version='orderfiles.py 0.1.0')
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-k', '--keep', action='store_true'\
                        , help='keep original file in input_dir')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9]?*'\
                        , help='filename search mode [default: *.[0-9][0-9]?*]')
    parser.add_argument('-cfg', metavar='<config>', default='_sitemap.yml'\
                        , help='configuration YAML file [default: ./_sitemap.yml]')
    parser.add_argument('-out', metavar='<output_dir>'\
                        , help='output dir [None for original]')

    # 运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
