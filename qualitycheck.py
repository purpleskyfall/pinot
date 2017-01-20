#coding=UTF-8
# this script is used to check quality of RINEX obs files, by TEQC
# creater: Jon Jiang
# datetime: 2016-12-20
# Python version: 3.4
"a RINEX obs files quality check script used TEQC"

import os
import glob
import re

#正则表达式，测试一个文件是否为RINEX格式
RINEXREG = re.compile(r'^[a-z0-9]{4}\d{3}.*\.\d{2}[o]$', re.I)
#质量信息在输出文件中的对应关系
QUALITYINFO = [{'name': 'start', 'flag': 'Time of start of window :', 'start': 38, 'end': None, 'len': 16}\
                , {'name': 'end', 'flag': 'Time of  end  of window :', 'start': 38, 'end': None, 'len': 16}\
                , {'name': 'length', 'flag': 'Time line window length :', 'start': 26, 'end': 42, 'len': 16}\
                , {'name': 'SN1', 'flag': 'Mean S1                 :', 'start': 26, 'end': 31, 'len': 9}\
                , {'name': 'SN2', 'flag': 'Mean S2                 :', 'start': 26, 'end': 31, 'len': 9}]
#MP1, MP2, CSR信息的标志
MPCSRFLAG = 'first epoch    last epoch    hrs   dt  #expt  #have   %   mp1   mp2 o/slps'

#返回一个表头
def tableheader():
    "create a table header"
    tabheaders = []
    tabheaders.append('file'.center(16, ' '))
    tabheaders.append('date'.center(12, ' '))
    for item in QUALITYINFO:
        tabheaders.append(item['name'].center(item['len'], ' '))
    tabheaders.append('MP1'.center(8, ' '))
    tabheaders.append('MP2'.center(8, ' '))
    tabheaders.append('CSR'.center(8, ' '))
    #返回连接的表头
    return ''.join(tabheaders)

#从RINEX格式Obs文件返回年
#参数表：filename: 文件名
def getyear(filename):
    "get 4 digit year from rinex obs filename"
    year = int(filename[-3:-1])
    return 2000 + year if year < 80 else 1900 + year

#从RINEX格式Obs文件返回年积日
#参数表：filename: 文件名
def getdoy(filename):
    "get day of year from rinex obs filename"
    doy = filename[4:7]
    return int(doy)

#将年与年积日转换到日期
#参数表：year: 年, doy: 年积日
def getdate(year, doy):
    "translate year and doy to date"
    import datetime
    initdate = datetime.date(year, 1, 1)
    delta = datetime.timedelta(doy - 1)
    result = initdate + delta

    return result

#从质量检查结果文件中获取质量指标
#参数表：resultfile: 结果文件, outtype: 输出类型
def getqualitymarks(resultfile, outtype):
    "return qualitycheck marks from result file, list or table"
    outputs = []
    resultreader = open(resultfile)
    infoindex = 0 #需要检查的信息的索引号
    while True:
        line = resultreader.readline()
        #如果line为空，说明已经读取到文件尾
        if line == '':
            break
        #因为信息在结果文件中出现的顺序是与QUALITYINFO中一致的，因此，每次检查时只需检查一条信息
        if infoindex < len(QUALITYINFO) and line.find(QUALITYINFO[infoindex]['flag']) != -1:
            info = QUALITYINFO[infoindex]
            value = line[info['start']: info['end']].strip()
            #处理观测时长时，仅截取其中逗号之前的部分
            if infoindex == 2 and value.find(',') != -1:
                value = value.split(',')[0]
            if outtype == 'list' or outtype == 'l':
                outputs.append(info['name'] + ': ' + value)
            else:
                outputs.append(value.center(info['len'], ' '))
            infoindex += 1 #索引号加1，之后的循环中检查下一个信息
            continue
        #如果QUALITYINFO中的信息已经检查完毕，则开始搜索剩下的信息：MP1, MP2, CSR
        if infoindex == len(QUALITYINFO) and line.find(MPCSRFLAG) != -1:
            line = resultreader.readline() #信息在标志的下一行
            mp1, mp2, o_slps = line[63:67].strip(), line[69:73].strip(), line[75:].strip()
            csr = round(1000 / float(o_slps), 2) #计算csr的值
            if outtype == 'list' or outtype == 'l':
                outputs.append('MP1: ' + mp1)
                outputs.append('MP2: ' + mp2)
                outputs.append('CSR: ' + str(csr))
            else:
                outputs.append(mp1.center(8, ' '))
                outputs.append(mp2.center(8, ' '))
                outputs.append(str(csr).center(8, ' '))
            break
    #信息读取结束，关闭文件并返回
    resultreader.close()
    return outputs

#执行TEQC程序进行数据质量检查
#参数表：file: obs文件及路径
def execteqc(file, outtype):
    "exec TEQC quality check"
    #分离文件路径、文件名
    filedir, filename = os.path.split(file)
    #获取质量检查结果文件路径
    resultfile = os.path.join(filedir, filename[0:-1] + 'S')
    outputs = []
    #运行TEQC
    os.system('teqc +out temp.log ++err temp.log +qc ' + file)
    #检查输出文件
    if os.path.exists(resultfile):
        #获取质量检查结果并删除结果文件
        outputs = getqualitymarks(resultfile, outtype)
        os.remove(resultfile)
    #输出检查结果，检查是否以列表形式输出
    if outtype == 'list' or outtype == 'l':
        print('\n' + file + ' quality marks:')
        for output in outputs:
            print(output)
    #以表格形式输出
    else:
        dateofdata = getdate(getyear(filename), getdoy(filename))
        strdate = dateofdata.strftime('%Y-%m-%d')
        outputs.insert(0, strdate.center(12, ' '))
        outputs.insert(0, filename.center(16, ' '))
        print(''.join(outputs))

#进行质量检查
#参数表: srcpath: 观测文件路径, globstr: 观测文件通配符, recursive: 是否递归
def qualitycheck(srcpath, globstr, outtype, recursive):
    "check obs quality by TEQC"
    for file in glob.glob(os.path.join(srcpath, globstr)):
        filename = os.path.basename(file)
        #使用正则表达式检查文件名是否为RINEX
        if not RINEXREG.match(filename):
            continue
        #使用TEQC程序进行质量检查处理
        execteqc(file, outtype)
    #如果用户设置了递归，则继续处理子文件夹
    if recursive:
        for child in os.listdir(srcpath):
            childpath = os.path.join(srcpath, child)
            if os.path.isdir(childpath):
                qualitycheck(childpath, globstr, outtype, recursive)

#主函数
#参数表: args: 用户输入参数表
def main(args):
    "main function"
    srcdirs, globstr, outtype = args.dir, args.glob, args.out
    #输出提示
    print('----------------- input params ---------------')
    print('source dir: ' + srcdirs)
    print('file mode: ' + globstr)
    print('----------------------------------------------')
    #如果输出为表格模式，需打印表头
    if outtype == 'table' or outtype == 't':
        print('\n' + tableheader())
    #开始质量检查
    for srcdir in glob.glob(srcdirs):
        qualitycheck(srcdir, globstr, outtype, args.recursive)
    #删除临时文件
    if os.path.exists('temp.log'):
        os.remove('temp.log')
    return 0

#脚本初始化方法，解析用户的输入参数
def init_args():
    "Initilize function"
    #引入参数解析模块
    import argparse
    #创建解析器
    parser = argparse.ArgumentParser(description="rinex quality check script used TEQC.")
    #添加所需参数信息
    parser.add_argument('-r', '--recursive', action='store_true'\
                        , help='search file in child folder')
    parser.add_argument('-v', '--version', action='version'\
                        , version='qualitycheck.py 0.1.9')
    parser.add_argument('-dir', metavar='<input_dir>', default='./'\
                        , help='input dir mode [default: current]')
    parser.add_argument('-glob', metavar='<mode>', default='*.[0-9][0-9][oO]'\
                        , help='mode is filename search mode [default: *.[0-9][0-9][oO]')
    parser.add_argument('-out', metavar='<type>', default='list'\
                        , choices=['list', 'l', 'table', 't']\
                        , help='format of output messages, list or table [default: list]')

    #运行主程序方法
    return main(parser.parse_args())

if __name__ == '__main__':
    init_args()
