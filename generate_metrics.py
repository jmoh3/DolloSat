#!/bin/python

from __future__ import print_function
from generate_formula import read_matrix, generate_cnf
from brute_force_solver import find_all_solutions

import sys
import time
import os 
import argparse 
import subprocess

def get_files(num_files, directory):
    files = []

    for file in os.listdir(directory):
        filename = os.fsencode(file)
        if filename.endswith(b'.txt'):
            files.append(f'{directory}/{filename.decode("utf-8")}')
            if num_files > 0 and len(files) == num_files:
                break

    return files

def get_info(filename, directory, num_samples):
    print(filename)

    split_filename = filename.split('/')[2].split('_')
    short_filename = filename.split('/')[2].split('.')[0]
    
    print(f'split_filename: {split_filename}')
    print(f'short_filename: {short_filename}')

    rows = split_filename[0][1:]
    columns = split_filename[1][1:]
    
    if int(rows) < 100 and int(columns) < 100:
        start = time.time()
        matrix = read_matrix(filename)
        num_clauses = generate_cnf(matrix, f'data/formulas/{short_filename}.cnf')
        end = time.time()

        elapsed_generate_cnf = end - start

        outfile = f'data/formulas/{short_filename}.cnf'

        qsampler_time = quicksampler_generator(outfile, num_samples)
        # qsampler_time = 0

        retstr = f'{short_filename}.txt,{rows},{columns},{elapsed_generate_cnf},{qsampler_time}'

        print(retstr)

        return retstr
        # matrix = read_matrix(filename)

        # solutions = find_all_solutions(matrix, None, False)

        # print(f'{short_filename}.txt,{rows},{columns},{elapsed},{num_clauses}')

        # return f'{short_filename}.txt,{rows},{columns},{elapsed},{num_clauses}'
    else:
        return None

def quicksampler_generator(outfile, num_samples):
    # in_cmd = 'cd quicksampler/'

    # sys.stdout.flush()
    # os.system(in_cmd)

    # _cmd = f'chmod +x ./quicksampler'
    # sys.stdout.flush()
    # os.system(q_cmd)
    
    q_cmd = f'./samplers/quicksampler -n {num_samples} -t 7200.0 {outfile} > /dev/null 2>&1'

    start = time.time()

    # sys.stdout.flush()
    os.system(q_cmd)
    
    end = time.time()

    z3_cmd = f'./samplers/z3 sat.quicksampler_check=true {outfile} > /dev/null 2>&1'

    os.system(z3_cmd)

    # out_cmd = 'cd ..'

    # sys.stdout.flush()
    # os.system(out_cmd)

    return end - start

def generate_info(files, directory, outfile, num_samples):
    with open(outfile, 'w') as ofile:
        ofile.write('filename,num_rows,num_columns,cnf_generation_time,num_clauses\n')

        for file in files:
            line = get_info(file, directory, num_samples)
            ofile.write(line + '\n')

    ofile.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Generate metrics for given directories')

    parser.add_argument(
        '--directory',
        type=str,
        default='data/5x5',
        help='directory to generate metrics of'
    )
    parser.add_argument(
        '--quantity',
        type=int,
        default=0,
        help='number of files to generate metrics on; 0 means all files will be scanned'
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='metrics.csv',
        help='outfile to write metrics to'
    )
    parser.add_argument(
        '--num_samples',
        type=int,
        default=10000,
        help='number of samples to generate'
    )

    args = parser.parse_args()

    num_files = abs(args.quantity)
    directory = os.fsencode(args.directory).decode('utf-8')
    out_file = args.outfile
    num_samples = abs(args.num_samples)

    files = get_files(num_files, directory)

    generate_info(files, directory, out_file, num_samples)