#!/bin/python

import os 
import argparse 

from generate_formula import read_matrix, generate_cnf
from brute_force_solver import find_all_solutions
from file_scripts import get_directory_files, remove_directory, remove_directory_files
from sampler_scripts import unigensampler_generator, quicksampler_generator,convert_unigen_to_quicksample, num_valid_solutions, get_sample_distribution

FORMULAS_DIRECTORY = 'data/formulas'

def get_info(infile, directory, num_samples):
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
        valid_outfile = cnf_file + '.samples.valid'

        print('Generating CNF Formula')
        num_clauses = generate_cnf(matrix, cnf_file)

        print('Generating Samples with Quicksampler')
        qsampler_time = quicksampler_generator(cnf_file, num_samples)

        print('Validating Quicksampler samples')
        qsampler_valid_samples = num_valid_solutions(cnf_file)

        print('Generating distribution of quicksampler')
        q_sampler_solution_distribution = get_sample_distribution(valid_outfile)

        print('Generating samples with Unigen')
        unigen_time = unigensampler_generator(cnf_file, unigen_outfile, num_samples)

        print('Converting unigen samples to quicksampler format')
        convert_unigen_to_quicksample(unigen_outfile, samples_outfile)
        
        print('Validating unigen samples')
        unigen_valid_samples = num_valid_solutions(cnf_file)

        print('Generating distribution of unigen')
        unigen_sampler_solution_distribution = get_sample_distribution(valid_outfile)

        q_sampler_solutions = ','.join(q_sampler_solution_distribution.keys())
        q_sampler_distribution = ','.join(q_sampler_solution_distribution.values())
        unigen_solutions = ','.join(unigen_sampler_solution_distribution.keys())
        unigen_distribution = ','.join(unigen_sampler_solution_distribution.values())

        if not q_sampler_solutions:
            q_sampler_solutions = "NA"
        if not q_sampler_distribution:
            q_sampler_distribution = "NA"
        if not unigen_solutions:
            unigen_solutions = "NA"
        if not unigen_distribution:
            unigen_distribution = "NA"

        retstr = f'{short_filename}.txt\n{q_sampler_solutions}\n{q_sampler_distribution}\n{unigen_solutions}\n{unigen_distribution}'

        return retstr
    else:
        return None

def generate_info(files, directory, outfile, num_samples):
    with open(outfile, 'w') as ofile:
        for file in files:
            line = get_info(file, directory, num_samples).strip()
            ofile.write(line + '\n')

            remove_directory_files(FORMULAS_DIRECTORY)

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
        default='uniformity-metrics.txt',
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