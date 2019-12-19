#!/bin/python

from __future__ import print_function
from generate_formula import read_matrix, generate_cnf
from brute_force_solver import find_all_solutions

import sys
import time
import os 
import argparse 
import pandas as pd

total_solutions_path = 'total_solutions.csv'
FORMULAS_DIRECTORY = 'data/formulas'

def get_files(num_files, directory):
    files = []

    for file in os.listdir(directory):
        filename = os.fsencode(file)
        if filename.endswith(b'.txt'):
            files.append(f'{directory}/{filename.decode("utf-8")}')
            if num_files > 0 and len(files) == num_files:
                break

    return files

def get_info(infile, directory, num_samples, total_solutions_df):
    print(infile)

    split_filename = infile.split('/')[2].split('_')
    short_filename = infile.split('/')[2].split('.')[0]

    rows = split_filename[0][1:]
    columns = split_filename[1][1:]
    
    if int(rows) < 100 and int(columns) < 100:
        matrix = read_matrix(infile)

        cnf_file = f'data/formulas/{short_filename}.cnf'
        samples_outfile = cnf_file + '.samples'
        unigen_outfile = cnf_file + '.unigen'

        print('Generating CNF Formula')
        start = time.time()
        num_clauses = generate_cnf(matrix, cnf_file)
        end = time.time()
        print('CNF Formula Generated!')

        elapsed_generate_phi = end - start

        num_variables = get_number_of_variables(cnf_file)

        print('Generating Samples with Quicksampler')
        qsampler_time = quicksampler_generator(cnf_file, num_samples)
        print('Quicksampler files generated')

        print('Validating Quicksampler samples')
        qsampler_valid_samples = num_valid_solutions(cnf_file)
        print('Quicksampler samples validated')

        print('Generating samples with Unigen')
        unigen_time = unigensampler_generator(cnf_file, unigen_outfile, num_samples)
        print('Unigen samples generated')

        print('Converting unigen samples to quicksampler format')
        convert_unigen_to_quicksample(unigen_outfile, samples_outfile)
        
        print('Validating unigen samples')
        unigen_valid_samples = num_valid_solutions(cnf_file)
        print('Unigen samples validated')

        total_num_solutions = -1

        try:
            total_num_solutions = total_solutions_df[infile]['num_solutions']
        except:
            print('Generating all solutions')
            total_num_solutions = find_all_solutions(matrix, None, False)
            total_solutions_df[infile] = {'num_variables': num_variables, 'num_solutions': total_num_solutions}
            print('All solutions generated')

        percent_qsampler_correct = qsampler_valid_samples / total_num_solutions
        percent_unigen_correct = unigen_valid_samples / total_num_solutions

        retstr = f'{short_filename}.txt,{rows},{columns},{num_variables},{num_clauses},{elapsed_generate_phi},{qsampler_time},{qsampler_valid_samples},{unigen_time},{unigen_valid_samples},{total_num_solutions},{percent_qsampler_correct},{percent_unigen_correct}'

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
    unigen_cmd = f'./samplers/unigen --samples={num_samples} {infile} {outfile} > /dev/null 2>&1'

    start = time.time()

    os.system(unigen_cmd)

    end = time.time()

    return end - start

def convert_unigen_to_quicksample(unigen_outfile, samples_outfile):
    unigen_file = open(unigen_outfile, 'r')
    samples_file = open(samples_outfile, 'w')

    for unigen_sample in unigen_file.readlines():
        unigen_sample = unigen_sample.strip()

        if len(unigen_sample) == 0:
            break

        unigen_sample = unigen_sample[1:].split(' ')

        num_times_sampled = unigen_sample[-1].split(':')[1]

        qsampler_binary = ''

        for variable in unigen_sample:
            if variable[0] != '0':
                qsampler_binary += '0' if variable[0] == '-' else '1'

        qsample = f'{num_times_sampled}: {qsampler_binary}'

        samples_file.write(qsample + '\n')

    unigen_file.close()
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
    metrics = ['filename', 'num_cells', 'num_characters', 'num_variables', 'num_clauses', 'phi_generation_time', 'qsampler_time', 'qsampler_valid_samples', 'unigen_time', 'unigen_valid_samples', 'total_num_solution', 'percent_qsampler_correct', 'percent_unigen_correct']

    try:
        total_solutions_df = pd.read_csv(total_solutions_path, index_col='file')
        total_solutions_df = total_solutions_df.to_dict('index')
    except:
        total_solutions_df = {}

    with open(outfile, 'w') as ofile:
        ofile.write(','.join(metrics) + '\n')

        for file in files:
            line = get_info(file, directory, num_samples, total_solutions_df)
            ofile.write(line + '\n')

    ofile.close()

    with open(total_solutions_path, 'w') as tsofile:
        tsofile.write('file,num_variables,num_solutions\n')

        for item in total_solutions_df:
            num_variables = total_solutions_df[item]['num_variables']
            num_solutions = total_solutions_df[item]['num_solutions']

            tsofile.write(f'{item},{num_variables},{num_solutions}\n')

    tsofile.close()

def clear_files(directory):
    os.system('rm tmp.cnf')

    if not os.path.exists(directory):
        return

    rm_files_cmd = f'rm {directory}/*'

    os.system(rm_files_cmd)
    os.removedirs(directory)


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

    if not os.path.exists(FORMULAS_DIRECTORY):
        os.makedirs(FORMULAS_DIRECTORY)

    generate_info(files, directory, out_file, num_samples)
    clear_files(FORMULAS_DIRECTORY)