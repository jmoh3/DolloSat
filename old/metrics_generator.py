#!/bin/python

import time
import os 
import argparse 
import pandas as pd

from generate_formula import read_matrix, generate_cnf
from brute_force_solver import find_all_solutions
from file_scripts import get_directory_files, remove_directory, remove_directory_files
from sampler_scripts import unigensampler_generator, quicksampler_generator,convert_unigen_to_quicksample, num_valid_solutions, get_number_of_variables

total_solutions_path = 'csvs/total_solutions.csv'
FORMULAS_DIRECTORY = 'data/formulas'

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

        elapsed_generate_phi = end - start

        num_variables = get_number_of_variables(cnf_file)

        print('Generating Samples with Quicksampler')
        qsampler_time = quicksampler_generator(cnf_file, num_samples)

        print('Validating Quicksampler samples')
        qsampler_valid_samples = num_valid_solutions(cnf_file)

        print('Generating samples with Unigen')
        unigen_time = unigensampler_generator(cnf_file, unigen_outfile, num_samples)

        print('Converting unigen samples to quicksampler format')
        convert_unigen_to_quicksample(unigen_outfile, samples_outfile)
        
        print('Validating unigen samples')
        unigen_valid_samples = num_valid_solutions(cnf_file)

        total_num_solutions = -1

        try:
            total_num_solutions = total_solutions_df[infile]['num_solutions']
        except:
            print('Generating all solutions')
            total_num_solutions = find_all_solutions(matrix, None, False)
            total_solutions_df[infile] = {'num_variables': num_variables, 'num_solutions': total_num_solutions}

        percent_qsampler_correct = qsampler_valid_samples / total_num_solutions
        percent_unigen_correct = unigen_valid_samples / total_num_solutions

        retstr = f'{short_filename}.txt,{rows},{columns},{num_variables},{num_clauses},{elapsed_generate_phi},{qsampler_time},{qsampler_valid_samples},{unigen_time},{unigen_valid_samples},{total_num_solutions},{percent_qsampler_correct},{percent_unigen_correct}'

        return retstr
    else:
        return None

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

            remove_directory_files(FORMULAS_DIRECTORY)

    ofile.close()

    with open(total_solutions_path, 'w') as tsofile:
        tsofile.write('file,num_variables,num_solutions\n')

        for item in total_solutions_df:
            num_variables = total_solutions_df[item]['num_variables']
            num_solutions = total_solutions_df[item]['num_solutions']

            tsofile.write(f'{item},{num_variables},{num_solutions}\n')

    tsofile.close()

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
        '--samples',
        type=int,
        default=10000,
        help='number of samples to generate'
    )

    args = parser.parse_args()

    num_files = abs(args.quantity)
    directory = os.fsencode(args.directory).decode('utf-8')
    out_file = args.outfile
    num_samples = abs(args.samples)

    files = get_directory_files(num_files, directory)

    if not os.path.exists(FORMULAS_DIRECTORY):
        os.makedirs(FORMULAS_DIRECTORY)

    generate_info(files, directory, out_file, num_samples)
    remove_directory(FORMULAS_DIRECTORY)