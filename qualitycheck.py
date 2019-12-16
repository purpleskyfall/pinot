#!/usr/bin/env python3
# coding=UTF-8
"""Quality check for RINEX observation files using TEQC software.

Will print primary marks of data quality. Using concurent.futures. The
RINEX file quality check function rely on TEQC software, Check ifyou
have installed TEQC by typing `teqc -help` in cmd.

:author: Jon Jiang
:email: jiangyingming@live.com
:modify: Nov 1, 2019
"""
from concurrent import futures
from textwrap import shorten
import argparse
import datetime
import glob
import itertools
import os
import subprocess

MAX_THREADING = max(6, os.cpu_count())
QUALITYINFO = (
    {'name': 'start', 'flag': 'Time of start of window :', 'pos': slice(25, 51)},
    {'name': 'end', 'flag': 'Time of  end  of window :', 'pos': slice(37, 51)},
    {'name': 'length', 'flag': 'Time line window length :', 'pos': slice(26, 42)},
    {'name': 'MP1', 'flag': 'Moving average MP12     :', 'pos': slice(26, 32)},
    {'name': 'MP2', 'flag': 'Moving average MP21     :', 'pos': slice(26, 32)},
    {'name': 'SN1', 'flag': 'Mean S1                 :', 'pos': slice(26, 31)},
    {'name': 'SN2', 'flag': 'Mean S2                 :', 'pos': slice(26, 31)}
)


def quality_check(src_file, nav_file):
    """Run quality check for source file using TEQC software.

    1. If run TEQC successfully, return quality check report;
    2. If run TEQC failed, return None.
    """
    if nav_file:
        args = 'teqc', '+qc', '-plot', '-rep', '-nav', nav_file, src_file
    else:
        args = 'teqc', '+qc', '-plot', '-rep', src_file
    status, output = subprocess.getstatusoutput(' '.join(args))
    # If exit status of TEQC software is not 0, means error
    return None if status > 0 else output.split('\n')


def parse_report(report):
    """Parse TEQC quality check report.

    Return a tuple: (date, start, end, length, SN1, SN2, MP1, MP2, CSR).

    Example:
    >>> report = [
    ... 'Time of start of window : 2017 Aug 10  00:00:00.000',
    ... 'Time of  end  of window : 2017 Aug 10  23:59:30.000',
    ... 'Time line window length : 23.99 hour(s), ticked every ...',
    ... 'Moving average MP12     : 0.425582 m',
    ... 'Moving average MP21     : 0.384306 m',
    ... 'Mean S1                 : 46.95 (sd=5.80 n=49483)',
    ... 'Mean S2                 : 42.21 (sd=8.18 n=48411)',
    ... '      first epoch    last epoch    hrs   dt  #expt  #have   %'
    ... '   mp1   mp2 o/slps',
    ... 'SUM 17  8 10 00:00 17  8 10 23:59 14.52  30  24054  23997 100 '
    ... '  0.43  0.38   3972'
    ... ]
    >>> result = parse_report(report) # doctest: +NORMALIZE_WHITESPACE
    >>> result[0:3]
    ('2017-08-10', '00:00:00.000', '23:59:30.000')
    >>> [round(num, 2) for num in result[3:]]
    [14.52, 46.95, 42.21, 0.43, 0.38, 0.25]

    """
    # Search quality marks in the report
    marks = {}
    for item in QUALITYINFO:
        for line in report:
            if item['flag'] in line:
                marks[item['name']] = line[item['pos']].strip()
                break
    # Restruct the quality marks into a tuple
    # Get SN1, SN2, MP1 & MP2, they may not found in the report
    sn1, sn2 = float(marks.get('SN1', 'nan')), float(marks.get('SN2', 'nan'))
    mp1, mp2 = float(marks.get('MP1', 'nan')), float(marks.get('MP2', 'nan'))
    date = datetime.datetime.strptime(marks['start'][0:11], '%Y %b %d')
    start, end = marks['start'][11:].strip(), marks['end']
    # Get observation data length, TEQC may output a warn at the tail
    last_line = next(l for l in reversed(report) if l.startswith('SUM'))
    last_line_pieces = last_line.split()
    length = float(last_line_pieces[-8])
    # Get the percentage of data, maybe unknown
    percentage = last_line_pieces[-4]
    percentage = float('nan') if percentage == '-' else float(percentage)
    # Get CSR from the last line of report, the olps may equal 0
    olps = float(last_line_pieces[-1])
    csr = float('nan') if olps == 0 else 1000 / olps

    result = (date.strftime('%Y-%m-%d'), start, end, length, percentage, sn1,
              sn2, mp1, mp2, csr)

    return result


def print_marks(marks, out_fmt):
    """Print marks of quality check, the out_fmt is list or table."""
    if out_fmt == 'list' or out_fmt == 'l':
        message = ('\n{0} quality marks:\n' 'date: {1}\n' 'start: {2}\n'
                   'end: {3}\n' 'hours: {4}\n' 'percent {5:.2f}\n'
                   'SN1: {6:.2f}\n' 'SN2: {7:.2f}\n' 'MP1: {8:.2f}\n'
                   'MP2: {9:.2f}\n' 'CSR: {10:.2f}')
        print(message.format(*marks))
    else:
        message = ('{0: ^14s} {1: ^12s} {2: ^14s} {3: ^14s} {4: 6.2f} '
                   '{5: 7.1f}  {6: 6.2f}  {7: 6.2f}  {8: 6.2f}  {9: 5.2f}  '
                   '{10: 5.2f}  ')
        print(message.format(os.path.basename(marks[0]), *marks[1:]))


def parallel_teqc(src_files, nav_file, out_fmt):
    """Parallel run function using argvs."""
    with futures.ThreadPoolExecutor(max_workers=MAX_THREADING) as executor:
        todo_map = {}
        for src_file in src_files:
            future = executor.submit(quality_check, src_file, nav_file)
            todo_map[future] = src_file
        task_iter = futures.as_completed(todo_map)
        failed_files = []
        for future in task_iter:
            src_file = todo_map[future]
            # return None means task is success
            res = future.result()
            if res:
                record = (src_file, *parse_report(res))
                print_marks(record, out_fmt)
            else:
                failed_files.append(os.path.basename(src_file))

    return failed_files


def init_args():
    """Initilize function, parse user input."""
    # initilize a argument parser
    parser = argparse.ArgumentParser(
        description="Quality check for RINEX observation files using TEQC."
    )
    # add arguments
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.4.6')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='search file recursively')
    parser.add_argument('-nav', metavar='<file>', default='',
                        help='navigation file, for complete mode')
    parser.add_argument('-out', metavar='<format>', default='table',
                        choices=['list', 'l', 'table', 't'],
                        help='output format, list or table [default: table]')
    parser.add_argument('files', metavar='<file>', nargs='+',
                        help='file will be processed')

    return parser.parse_args()


def main():
    """Main function."""
    args = init_args()
    globstrs, out_fmt, recursive = args.files, args.out, args.recursive
    # collect input globstrs into a glob list
    globs = [glob.iglob(globstr, recursive=recursive) for globstr in globstrs]
    src_files = [src for src in itertools.chain(*globs)]
    # make input args for teqc function
    print('Start processing: {}'.format(shorten(', '.join(globstrs), 62)))
    # if output format is table, print a table header first
    if out_fmt == 'table' or out_fmt == 't':
        header = ('file', 'date', 'start', 'end', 'hours', 'percent',
                  'SN1', 'SN2', 'MP1', 'MP2', 'CSR')
        style = ('\n{0: ^14s} {1: ^12s} {2: ^14s} {3: ^14s} {4: >6s}  {5: >7s}'
                 '{6: >6s}  {7: >6s}  {8: >6s}  {9: >5s}  {10: >5s}')
        print(style.format(*header))
    # start parallel processing
    failed = parallel_teqc(src_files, args.nav, out_fmt)
    if failed:
        print('\nQuality check failed files: {}'.format(', '.join(failed)))

    return 0


if __name__ == '__main__':
    main()
