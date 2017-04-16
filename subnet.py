#coding=UTF-8
#this script is used to create the subnets by a config.yml file.
#create date: 2016/12/2
#last modify: 2016/12/7
#creater: Jon Jiang
#Python version: 3.4

"""this script is used to create the subnets by a _subnet.yml file."""

#引入所需模块
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

#指定文件夹内搜索文件并拷贝
#site: 站名; globstr: 通配符; srcpath: 源文件夹; aimpath: 目标文件夹; recursive: 是否递归搜索
def copysite(site, globstr, srcpath, aimpath, recursive):
    """Copy site rinex file, if recursive is true, search child folder"""
    #搜索本文件夹内的文件
    for file in glob.glob(os.path.join(srcpath, globstr)):
        filename = os.path.basename(file)
        if site.upper() == filename[0:4].upper():
            print('copy ' + file)
            shutil.copy(file, aimpath)
    #如果指定了-r参数，则递归地搜索子文件夹
    if recursive:
        for child in os.listdir(srcpath):
            childpath = os.path.join(srcpath, child)
            if os.path.isdir(childpath):
                copysite(site, globstr, childpath, aimpath, recursive)

#主函数
#args: 命令行参数表
def main(args):
    """Main function"""
    import yaml
    #检查配置文件是否存在
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: " + args.cfg + ", use -cfg <config> input it!")
        return 1
    #解析 YAML 格式的用户配置文件
    cfgfile = open(args.cfg)
    subnets = yaml.load(cfgfile) #加载用户配置的各子网
    cfgfile.close()
    srcdirs, globstr, outputdir = args.dir, args.glob, args.out
    #输出提示信息
    print('-------------------- input params ----------------------')
    print('source dir: ' + srcdirs)
    print('file mode: ' + globstr)
    print('output dir: ' + outputdir)
    print('config file: ' + args.cfg + '\n')
    #若输出文件夹不存在，则创建它
    createdir(outputdir)
    print('--------------------- start process --------------------')
    #对各子网进行遍历
    for net in subnets:
        print('\nprocess subnet: ' + net + ' ......')
        netdir = os.path.join(outputdir, net) #子网对应的文件夹路径
        createdir(netdir)
        #对子网中的站点进行遍历
        for site in subnets[net]:
            # 对输入文件夹中的所有文件遍历
            for srcdir in glob.glob(srcdirs):
                copysite(site, globstr, srcdir, netdir, args.recursive)

    return 0

#脚本初始化方法，解析用户的输入参数
def init_args():
    """Initilize function"""
    #引入参数解析模块
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description=\
                                    'copy obs file by a YAML subscribe web configuration.')
    #添加所需参数信息
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version', version='subnet.py 0.3.4')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oOdD]*'\
                        , help='mode is filename search mode [default: *.[0-9][0-9][oOdD]*')
    parser.add_argument('-out', metavar='<output>', default='subnets'\
                        , help='output directory [default: subnets in current]')
    parser.add_argument('-cfg', metavar='<config>', default='_subnet.yml'\
                        , help='configuration YAML file [default: ./subnet.yml]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
