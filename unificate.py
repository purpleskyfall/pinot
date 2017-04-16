#coding=UTF-8
#this script is used to unificate rinex files by a config.yml file.
#create date: 2016/12/5
#creater: Zhou Maosheng
#modifer: Jon Jiang
#Python version: 3.4

"""Unificate rinex files by a config.yml file"""

#引入所需模块
import os
import glob
import re
import threading

#正则表达式，测试文件名是否为 RINEX
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[o]$', re.I)
#正则表达式，测试字符串中是否包含字母
ALPHAREG = re.compile(r'[a-z]+\s*', re.I)
#站点信息配置项与TEQC参数对应表
TEQCITEM = {'observer': '-O.o', 'agency': '-O.ag', 'rm_sys': '', 'obs_type': '-O.obs',
            'interval': '-O.dec', 'receiver': '-O.rt', 'antenna': '-O.at', 'delta': '-O.pe',
            'position': '-O.px'}
#同时执行的线程数
THREADSIZE = 6
#正在执行的线程数
THREADCOUNT = 0
#线程锁定标志
MUTEXCOUNT = threading.Lock()

#若文件夹不存在则创建
#dirpath: 文件夹路径
def createdir(dirpath):
    """Create new directory if not exist"""
    if not os.path.exists(dirpath):
        print('make dir: ' + dirpath)
        os.mkdir(dirpath)

#返回配置文件中某个站点的信息，若没有该站点，返回 all 中的信息作为默认配置
#site: 站点名; cfgfile: 配置文件
def getinfo(site, sitesinfo):
    """Get information from cfgfile"""
    #获得特定站点的信息
    site = site.lower()
    info = sitesinfo.get(site, {})
    #加载 all 中的信息作为默认配置
    default = {}
    if 'all' in sitesinfo:
        default = sitesinfo['all'].copy()
    #对于重复的属性，使用站点中的项目
    for key in info:
        default[key] = info[key]

    return default

#将用户配置信息转化为对应的TEQC参数
#info: 站点配置信息
def getparams(info):
    """Get teqc params from user config info"""
    params = ''
    #遍历站点信息中的项目
    for key in info:
        if key == 'rm_sys':
            params += ' ' + TEQCITEM[key] + ' -' + ' -'.join(info[key])
        elif key == 'obs_type':
            params += ' ' + TEQCITEM[key] + ' ' + ','.join(info[key])
        else:
            #如果站点信息中包含字母，说明该项是字符串，需要用双引号包裹
            if ALPHAREG.match(str(info[key])):
                params += ' ' + TEQCITEM[key] + ' "' + str(info[key]) + '"'
            else:
                params += ' ' + TEQCITEM[key] + ' ' + str(info[key]) + ''

    return params

#使用 os.system() 方法执行 TEQC 程序进行标准化
#参数表：file: 文件及路径, params: teqc 参数, outputpath: 输出路径
def teqc(file, params, outputpath):
    """execute system command by os.system()"""
    global THREADCOUNT
    filename = os.path.basename(file)
    os.system('teqc' + params + ' ' + file + ' > ' + os.path.join(outputpath, filename)) #执行TEQC
    #TEQC 程序执行完毕之后，将正在执行线程数减1
    if MUTEXCOUNT.acquire():
        THREADCOUNT -= 1
        MUTEXCOUNT.release()

#采用异步多线程的方式执行命令
#参数表：commands: 待执行命令列表
def runtaskasync(commands):
    """execute commands async"""
    global THREADCOUNT
    thread = None
    while len(commands) > 0:
        #当前运行的线程数小于 THREADSIZE 时，获得对 THREADCOUNT 的锁定，创建新线程
        if THREADCOUNT < THREADSIZE and MUTEXCOUNT.acquire():
            #从待执行命令列表中取出一个执行
            cmd = commands.pop()
            print('unificate ' + cmd['file'] + ' ......')
            thread = threading.Thread(target=teqc, args=(cmd['file'], cmd['params'], cmd['output']))
            thread.setDaemon(True)
            thread.start()
            #线程数增1
            THREADCOUNT += 1
            #解除对 THREADCOUNT 的锁定
            MUTEXCOUNT.release()
    #若待执行命令已经为空，则等待所有线程执行完毕之后退出
    if thread is not None:
        thread.join()

#对输入文件夹内所有符合通配符的文件进行处理
#globstr: 通配符; srcpath: 源文件夹路径; outputpath: 输出文件夹; sitesinfo: 用户配置信息; recursive: 是否递归搜索
def process(globstr, srcpath, outputpath, sitesinfo, recursive):
    """Unificate rinex files by user config info"""
    commands = [] #用于保存所需执行的teqc命令的数组
    #遍历与通配符匹配的文件，将需执行的命令加入 commands
    for file in glob.glob(os.path.join(srcpath, globstr)):
        filename = os.path.basename(file)
        #忽略非RINEX文件
        if not RINEXREG.match(filename):
            continue
        #从文件名中获得4字符站点名，并查找站点信息
        info = getinfo(filename[0:4], sitesinfo) #获得站点信息
        params = getparams(info) #获得对应于站点信息的TEQC命令参数
        commands.append({'file': file, 'params': params, 'output': outputpath})
    #以多线程的方式执行 commands 中的命令
    runtaskasync(commands[::-1])
    #若用户设置了-f参数，则递归处理子文件夹的内容
    if recursive:
        for child in os.listdir(srcpath):
            childpath = os.path.join(srcpath, child)
            if os.path.isdir(childpath):
                process(globstr, childpath, outputpath, sitesinfo, recursive)

#主函数
#args: 命令行参数表
def main(args):
    """Main function"""
    import time
    import yaml
    #检查配置文件是否存在
    if not os.path.exists(args.cfg):
        print("Error! Can't find config file: " + args.cfg + ", use -cfg <config> input it!")
        return 1
    #解析用户的 YAML 配置文件
    cfgfile = open(args.cfg)
    sitesinfo = yaml.load(cfgfile) #加载用户配置
    cfgfile.close()
    srcdirs, globstr, outputdir = args.dir, args.glob, args.out
    #记录开始时间
    start = time.clock()
    #输出提示信息
    print('-------------------- input params ------------------------')
    print('source dirs: ' + srcdirs)
    print('file mode: ' + globstr)
    print('output dir: ' + outputdir)
    print('config file: ' + args.cfg + '\n')
    createdir(outputdir) #若输出文件夹不存在，则创建它
    print('--------------------- start process ----------------------')
    #进行标准化处理
    for srcdir in glob.glob(srcdirs):
        process(globstr, srcdir, outputdir, sitesinfo, args.recursive)
    #记录结束时间
    end = time.clock()
    #计算并输出运行时间
    print('\nuse seconds: ' + str(end - start))

    return 0

#脚本初始化方法，解析用户的输入参数
def init_args():
    """Initilize function"""
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description=\
                                    'unificate rinex obs file by a YAML configuration.')
    #添加所需参数信息
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version', version='unificate.py 0.4.4')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oO]'\
                        , help='mode is filename search mode [default: *.[0-9][0-9][oO]')
    parser.add_argument('-out', metavar='<output>', default='unificated'\
                        , help='output directory [default: unificated in current]')
    parser.add_argument('-cfg', metavar='<config>', default='_sitesinfo.yml'\
                        , help='configuration YAML file [default: _sitesinfo.yml]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
