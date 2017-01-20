#coding=UTF-8
#This is a script for checking data information.
#create date: 2017/1/6
#creater: Jon Jiang
#Python version: 3.4

"check if obs file exist in folder by a sites list in YAML"

import os

#检查某文件夹内是否存在指定文件
#参数表：dirpath: 文件夹路径, filename: 文件名, recursive: 是否递归
def existfile(dirpath, filename, recursive):
    "check if file exist in dirpath"
    #如果 dirpath 中存在 filename, 返回 True
    if os.path.exists(os.path.join(dirpath, filename)):
        return True
    #如果用户设置了递归，则继续搜索子文件夹内容
    if recursive:
        for child in os.listdir(dirpath):
            childpath = os.path.join(dirpath, child)
            #如果当前目录存在子文件夹，继续搜索
            if os.path.isdir(childpath):
                if existfile(childpath, filename, recursive):
                    return True
    #若程序执行到此，说明没有搜索到指定文件
    return False

#主函数
#args: 输入参数
def main(args):
    "main function"
    # 引入 PyYAML 模块
    import yaml
    # 检查配置文件是否存在
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: " + args.cfg + ", use -cfg <config> input it!")
        return 1
    #加载配置文件
    cfgfile = open(args.cfg)
    sites = yaml.load(cfgfile)
    cfgfile.close()
    srcdir, doy, year = args.dir, args.doy, args.yr
    #验证输入的年
    if not(year.isdigit() and (len(year) == 2 or len(year) == 4)):
        print("Error! year of data not vaild!")
        return 1
    #输出提示信息
    print('----------------- input params ---------------')
    print('source dir: ' + srcdir)
    print("data's year: " + year)
    print('day of year: ' + doy)
    print('config file: ' + args.cfg)
    print('----------------------------------------------', end='\n\n')
    #保存找不到的站点
    messingsites = []
    for site in sites:
        #检查的文件名
        filename = site.lower() + doy + '0.' + year[-2:] + 'o'
        #如果检查的文件不存在，则将站点保存到 messingsites
        if not existfile(srcdir, filename, args.recursive):
            messingsites.append(site)
    #若存在找不到的站点，将站点名输出
    if len(messingsites) > 0:
        print('sites not found in ' + year + ' ' + doy + ': ' + ', '.join(messingsites))

    return 0

def init_args():
    "Initilize function"
    #引入 argparse 模块用于解析用户输入
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description=\
                                    'check if obs file exist by a sites list in YAML.')
    #添加所需参数信息
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version'\
                        , version='sitecheck.py 0.1.1')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir [default: current]')
    parser.add_argument('-cfg', metavar='<config>', default='_sites.yml'\
                        , help='configuration YAML file [default: ./_sites.yml]')
    parser.add_argument('-yr', metavar='<year>', required=True\
                        , help='data observation year [required]')
    parser.add_argument('-doy', metavar='<doy>', required=True\
                        , help='observation day of year [required]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
