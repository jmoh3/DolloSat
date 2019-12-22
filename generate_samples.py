#!/bin/python

# USAGE
# $ python3 generate_samples.py --filename=INPUT_MATRIX_FILENAME --outfile=SOLUTIONS_OUTFILE --timeout=TIMEOUT --num_samples=NUMBER_OF_SAMPLES --sampler=SAMPLER_TYPE
# 
# Generates samples for matrix in INPUT_MATRIX_FILENAME and saves reconstructed k-Dollo matrices to SOLUTIONS_OUTFILE.

from generate_formula import read_matrix, generate_cnf
from reconstruct_solutions import reconstruct_solutions

import sys
import time
import os 
import argparse
import platform

def unigensampler_generator(infile, outfile, num_samples):
    unigen_cmd = f'./samplers/unigen --samples={num_samples} {infile} {outfile}'

    os.system(unigen_cmd)

def quicksampler_generator(cnf_file, num_samples, timeout, osname):
    q_cmd = f'./samplers/quicksampler -n {num_samples} -t {timeout} {cnf_file}'
    z3_cmd = f'./samplers/z3 sat.quicksampler_check=true {cnf_file}'

    if osname == 'macOS':
        q_cmd = f'./samplers/macOS/quicksampler -n {num_samples} -t {timeout} {cnf_file}'
        z3_cmd = f'./samplers/macOS/z3 sat.quicksampler_check=true {cnf_file}'

    os.system(q_cmd)
    os.system(z3_cmd)

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

def clean_up(shortened_filename, unigen):
    remove_formula = f'rm {shortened_filename}.tmp.formula.cnf'
    remove_samples = f'rm {shortened_filename}.tmp.formula.cnf.samples'
    remove_valid = f'rm {shortened_filename}.tmp.formula.cnf.samples.valid'

    os.system(remove_formula)
    os.system(remove_samples)
    os.system(remove_valid)

    if unigen:
        remove_unigen_file = f'rm {shortened_filename}.tmp.formula.cnf.unigen'
        os.system(remove_unigen_file)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Generate samples for given directories')

    parser.add_argument(
        '--filename',
        type=str,
        default='data/example.txt',
        help='The input file containing the matrix to generate samples for'
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='solutions.txt',
        help='Outfile to write solutions to'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=7200.0,
        help='Timeout for samplers (seconds), default is 7200'
    )
    parser.add_argument(
        '--num_samples',
        type=int,
        default=10000,
        help='number of samples to generate'
    )
    parser.add_argument(
        '--sampler',
        type=int,
        default=1,
        help='1 to use Quicksampler, 2 to use Unigen.'
    )

    os_name = ''

    if platform.system() == "linux" or platform.system() == "linux2":
        os_name = 'linux'
    elif platform.system() == "Darwin":
        os_name = 'macOS'
    elif platform.system() == "win32":
        os_name = 'win'

    args = parser.parse_args()

    shortened_filename = args.filename.split('.')[0]
    cnf_filename = f'{shortened_filename}.tmp.formula.cnf'

    matrix = read_matrix(args.filename)
    clause_count = generate_cnf(matrix, cnf_filename)

    if args.sampler == 1:
        quicksampler_generator(cnf_filename, args.num_samples, args.timeout, os_name)
        valid_solutions = f'{shortened_filename}.tmp.formula.cnf.samples.valid'
        reconstruct_solutions(matrix, valid_solutions, args.outfile)
        clean_up(shortened_filename, False)
    else:
        if os_name == 'macOS':
            print('Unigen not compatible with OS X')
        else:
            unigen_outfile = cnf_filename + '.unigen'
            samples_outfile = cnf_filename + '.samples'

            unigensampler_generator(cnf_filename, unigen_outfile, args.num_samples)
            convert_unigen_to_quicksample(unigen_outfile, samples_outfile)

            z3_cmd = f'./samplers/z3 sat.quicksampler_check=true {cnf_filename} > /dev/null 2>&1'
            os.system(z3_cmd)

            valid_solutions = f'{shortened_filename}.tmp.formula.cnf.samples.valid'
            reconstruct_solutions(matrix, valid_solutions, args.outfile)
            clean_up(shortened_filename, True)