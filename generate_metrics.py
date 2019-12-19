#!/bin/python

from __future__ import print_function
from generate_formula import read_matrix, generate_cnf
from brute_force_solver import find_all_solutions

import sys
import time
import os 
import argparse 
import subprocess
import pandas as pd

def get_files(num_files, directory):
    files = []

    for file in os.listdir(directory):
        filename = os.fsencode(file)
        if filename.endswith(b'.txt'):
            files.append(f'{directory}/{filename.decode("utf-8")}')
            if num_files > 0 and len(files) == num_files:
                break

    return files

def get_info(infile, directory, num_samples):
    print(infile)

    split_filename = infile.split('/')[2].split('_')
    short_filename = infile.split('/')[2].split('.')[0]

    rows = split_filename[0][1:]
    columns = split_filename[1][1:]
    
    if int(rows) < 100 and int(columns) < 100:
        matrix = read_matrix(infile)

        cnf_file = f'data/formulas/{short_filename}.cnf'
        samples_outfile = f'{cnf_file}.samples'
        unigen_outfile = f'data/formulas/{short_filename}.unigen'

        start = time.time()
        num_clauses = generate_cnf(matrix, cnf_file)
        end = time.time()

        elapsed_generate_phi = end - start

        num_variables = get_number_of_variables(cnf_file)

        qsampler_time = quicksampler_generator(cnf_file, num_samples)

        qsampler_valid_samples = num_valid_solutions(cnf_file)

        unigen_time = unigensampler_generator(infile, unigen_outfile, num_samples)

        convert_unigen_to_quicksample(unigen_outfile, samples_outfile)

        ugen_valid_samples = num_valid_solutions(cnf_file)

        retstr = f'{short_filename}.txt,{rows},{columns},{num_variables},{num_clauses},{elapsed_generate_phi},{qsampler_time},{qsampler_valid_samples},{unigen_time},{ugen_valid_samples}'

        return retstr
    else:
        return None

def get_number_of_variables(cnf_file):
    try:
        infile = open(cnf_file, 'r')

        firstline = infile.readline()

        if firstline[0] != 'p':
            return 0
        
        metainfo = firstline.split(' ')

        return int(metainfo[-1])

        infile.close()
    except:
        return 0

def unigensampler_generator(infile, outfile, num_samples):
    unigen_cmd = f'./sampelrs/unigen --samples={num_samples} {infile} {outfile} > /dev/null 2>&1'

    start = time.time()

    os.system(unigen_cmd)

    end = time.time()

    return end - start

def convert_unigen_to_quicksample(unigen_outfile, samples_outfile):
    ugen_file = open(unigen_outfile, 'r')
    samples_file = open(samples_outfile, 'w')

    for ugen_sample in ugen_file.readlines():
        ugen_sample = ugen_sample.strip()

        if len(ugen_sample) == 0:
            break

        ugen_sample = ugen_sample[1:].split(' ')

        num_times_sampled = ugen_sample[-1].split(':')[1]

        qsampler_binary = ''

        for variable in ugen_sample:
            if variable[0] != '0':
                qsampler_binary += '0' if variable[0] == '-' else '1'

        qsample = f'{num_times_sampled}: {qsampler_binary}'

        samples_file.write(qsample + '\n')

    ugen_file.close()
    samples_file.close()

def quicksampler_generator(cnf_file, num_samples):    
    q_cmd = f'./samplers/quicksampler -n {num_samples} -t 7200.0 {cnf_file} > /dev/null 2>&1'

    start = time.time()

    os.system(q_cmd)
    
    end = time.time()

    return end - start

def num_valid_solutions(cnf_file):
    z3_cmd = f'./samplers/z3 sat.quicksampler_check=true {cnf_file} > /dev/null 2>&1'

    os.system(z3_cmd)

    valid_samples_file = f'{cnf_file}.samples.valid'

    try:
        num_valid = 0

        with open(valid_samples_file, 'r') as s_file:
            num_valid = len(s_file.readlines())
            s_file.close()

        return num_valid
    except:
        return -1

def generate_info(files, directory, outfile, num_samples):
    metrics = ['filename', 'num_cells', 'num_characters', 'num_variables', 'num_clauses', 'phi_generation_time', 'qsampler_time', 'qsampler_valid_samples', 'unigen_time', 'unigen_valid_samples']

    with open(outfile, 'w') as ofile:
        ofile.write(','.join(metrics) + '\n')

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

    if not os.path.exists('data/formulas'):
        os.makedirs('data/formulas')

    generate_info(files, directory, out_file, num_samples)