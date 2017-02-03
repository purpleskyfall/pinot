#coding=UTF-8
#This is a script for checking data information.
#create date: 2016/12/9
#last modify: 2016/12/11
#creater: Zhou Maosheng
#modifier: Jon Jiang
#Python version: 3.4

"This is a script for checking site information"

import os
import glob
import re
import math

#判别文件名是否为 RINEX 格式 O-文件或 D-文件
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[od]$', re.I)
#站点信息文件键与观测文件标志对应表
SITEINFO = {'receiver': {'flag': 'REC # / TYPE / VERS', 'start': 20, 'end': 40}\
            , 'antenna': {'flag': 'ANT # / TYPE', 'start': 20, 'end': 40}\
            , 'delta': {'flag': 'ANTENNA: DELTA H/E/N', 'start': 0, 'end': 42}\
            , 'position': {'flag': 'APPROX POSITION XYZ', 'start': 0, 'end': 42}}
#保存找不到的站点
MISSINGSITES = []

#比较站点信息与RINEX文件
#info: 站点信息, file: 观测文件
def compareinfo(info, file, threshold, outtype):
    "Compare site info and rinex file"
    #header用于保持文件头信息，differences用于保持不一致处
    header, differences = [], []
    filename = os.path.basename(file)
    ofile = open(file)
    #加载文件头信息
    while True:
        line = ofile.readline()
        #查找到文件头结束时跳出
        if -1 != line.find('END OF HEADER'):
            break
        header.append(line)
    #关闭文件
    ofile.close()
    #检查信息
    for item in info:
        #若配置中的项目不在 SITEINFO 中，直接处理下一项
        if item not in SITEINFO:
            continue
        for line in header:
            #若该行中未找到要检查的信息的标志，直接检查下一行
            if -1 == line.find(SITEINFO[item]['flag']):
                continue
            #从文件中按照 SITEINFO 中的配置找出所需的文本串
            fileinfostr = line[SITEINFO[item]['start']: SITEINFO[item]['end']]
            #如果比较项目为先验坐标
            if item == 'position':
                #分割配置信息和观测文件中的先验坐标
                cfgposis = info[item].split()
                fileposis = fileinfostr.split()
                #遍历对配置和观测文件中的先验坐标进行比较
                for (cfgposi, fileposi) in zip(cfgposis, fileposis):
                    #如果任何一个坐标分量的差异超出了阈值，就应作为结果输出
                    if threshold < math.fabs(float(cfgposi) - float(fileposi)):
                        if outtype == 'list' or outtype == 'l':
                            differences.append(item + ' in cfg file: ' + ', '.join(cfgposis))
                            differences.append(item + ' in obs file: ' + ', '.join(fileposis))
                        else:
                            message = file.center(40, ' ') + item.center(14, ' ') \
                                    + (','.join(cfgposis)).center(46, ' ') \
                                    + (','.join(fileposis)).center(46, ' ')
                            differences.append(message)
                        break
                break
                #其它比较类型
            if info[item] != fileinfostr.strip():
                if outtype == 'list' or outtype == 'l':
                    differences.append(item + ' in cfg file: ' + info[item])
                    differences.append(item + ' in obs file: ' \
                                + fileinfostr.strip())
                else:
                    message = filename.center(16, ' ') + item.center(14, ' ') \
                            + info[item].center(46, ' ') + fileinfostr.strip().center(46, ' ')
                    differences.append(message)
                break
    #检查是否有不同
    if len(differences):
        if outtype == 'list' or outtype == 'l':
            print('\n' + file + ' has differences:')
        print('\n'.join(differences))

#检查输入文件夹中的与通配符匹配的文件
#globstr: 通配符, srcpath: 输入文件夹, sitesinfo: 站点信息表, outtype: 消息输出类型, threshold: 先验坐标阈值, recursive: 是否递归
def checksite(globstr, srcpath, sitesinfo, outtype, threshold, recursive):
    "Check site info, search children folder in recursive is set"
    #对符合通配符的文件进行遍历
    for file in glob.glob(os.path.join(srcpath, globstr)):
        filename = os.path.basename(file)
        #忽略非RINEX文件
        if not RINEXREG.match(filename):
            continue
        site = filename[0:4].lower()
        #获取站点信息
        info = sitesinfo.get(site)
        #若站点信息为空，将该站点保存在缺失站点数组中
        if info is None:
            if site not in MISSINGSITES:
                MISSINGSITES.append(site)
            continue
        compareinfo(info, file, threshold, outtype)
    #若用户设置了递归，则继续搜索子文件夹
    if recursive:
        for child in os.listdir(srcpath):
            childpath = os.path.join(srcpath, child)
            if os.path.isdir(childpath):
                checksite(globstr, childpath, sitesinfo, outtype, threshold, recursive)

#主函数
#args: 输入参数
def main(args):
    "Main function"
    #引入 PyYAML 模块
    import yaml
    #检查配置文件是否存在
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: " + args.cfg + ", use -cfg <config> input it!")
        return 1
    #加载配置文件
    cfgfile = open(args.cfg)
    sitesinfo = yaml.load(cfgfile) #加载用户配置信息
    srcdirs, globstr, outtype, threshold = args.dir, args.glob, args.out, args.thd
    #输出提示信息
    print('----------------- input params ---------------')
    print('source dirs: ' + srcdirs)
    print('file mode: ' + globstr)
    print('config file: ' + args.cfg)
    print('----------------------------------------------')
    #若输出形式为表格，则首先打印一个表头
    if outtype == 'table' or outtype == 't':
        print('\n' + 'file'.center(16, ' ') + 'type'.center(14, ' ') + 'cfgfile'.center(46, ' ') \
                + 'obsfile'.center(46, ' '))
    #开始检查
    for srcdir in glob.glob(srcdirs):
        checksite(globstr, srcdir, sitesinfo, outtype, threshold, args.recursive)
    #输出配置文件中找不到的站点
    if len(MISSINGSITES) > 0:
        print('\n' + 'sites not found in cfg file: ' + ', '.join(MISSINGSITES))

    return 0

#脚本初始化方法，解析用户的输入参数
def init_args():
    "Initilize function"
    #引入 argparse 模块用于解析用户输入
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description=\
                        "compare rinex obs files' meta info from YAML configuration.")
    #添加所需参数信息
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version', version='metacheck.py 0.3.9')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oOdD]'\
                        , help='mode is filename search mode [default: *.[0-9][0-9][oOdD]')
    parser.add_argument('-cfg', metavar='<config>', default='_sitesinfo.yml'\
                        , help='configuration YAML file [default: ./_sitesinfo.yml]')
    parser.add_argument('-out', metavar='<type>', default='list'\
                        , choices=['list', 'l', 'table', 't']\
                        , help='format of output messages, list or table [default: list]')
    parser.add_argument('-thd', metavar='<threshold>', default=10, type=int\
                        , help='threshold of position change [default: 10]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
