#!/bin/python
import time
import os 
import argparse 
import math

from generate_formula import get_cnf
from generate_samples import unigensampler_generator
from utils import get_matrix_info, parse_filename
from count_num_solutions import get_num_solutions_sharpSAT

total_solutions_path = 'total_solutions.csv'
FORMULAS_DIRECTORY = 'data/formulas'
sharpSAT_path = '../../../scratch/software/src/sharpSAT/build/Release/sharpSAT'

def get_unigen_frequencies(cnf_filename, num_samples, timeout):
    unigen_outfile = cnf_filename + '.unigen'

    start = time.time()
    unigensampler_generator(cnf_filename, unigen_outfile, num_samples, timeout)
    total_ugen_time = time.time() - start

    fp = open(unigen_outfile)
    lines = fp.readlines()
    fp.close()

    frequencies = []
    
    for line in lines:
        sampled_freq = int(line.split(':')[1])
        frequencies.append(sampled_freq)

    os.system(f'rm {unigen_outfile}')

    return frequencies

def get_info(infile, directory, num_samples, timeout, s, t):
    row_info = parse_filename(infile)
    full_filename = f'{directory}/{infile}'

    m = row_info['m']
    n = row_info['n']

    if n > 8:
        return None

    print(f'Starting {infile}')

    fp_rate = row_info['fp_rate']
    fn_rate = row_info['fn_rate']

    cnf_filename = f'{FORMULAS_DIRECTORY}/{infile}.tmp.formula.cnf'

    num_ones, cell_clusters, mutation_clusters = get_matrix_info(infile, directory)
    num_zeroes = m * n - num_ones

    row_info['num_cell_clusters'] = cell_clusters
    row_info['num_mutation_clusters'] = mutation_clusters

    expected_fp = math.floor(num_ones * fp_rate)
    expected_fn = math.floor(num_zeroes * fn_rate)

    start = time.time()
    row_info['num_variables'], row_info['num_clauses'] = get_cnf(full_filename, cnf_filename, cell_clusters,
                                                                mutation_clusters, None, expected_fn, expected_fp, True)
    row_info['formula_gen_time'] = time.time() - start

    num_solutions = get_num_solutions_sharpSAT(sharpSAT_path, cnf_filename)
    frequencies = get_unigen_frequencies(cnf_filename, num_samples, timeout)
    frequencies = [float(frequency)/num_solutions for frequency in frequencies]

    if len(frequencies) == 0:
        row_info['min_freq'] = 1
        row_info['max_freq'] = 1
    else:
        row_info['min_freq'] = min(frequencies)
        row_info['max_freq'] = max(frequencies)

    os.system(f'rm {cnf_filename}')
    
    return row_info

def generate_info(files, directory, outfile, num_samples, timeout, s, t):
    metrics = ['filename', 'm', 'n', 'num_cell_clusters', 'num_mutation_clusters',
                'num_variables', 'num_clauses', 'formula_gen_time', 'min_freq', 'max_freq']

    with open(outfile, 'w') as ofile:
        ofile.write(','.join(metrics) + '\n')

        sorted_files = sorted(files, key=lambda a: parse_filename(a)['m'])

        for file in sorted_files:
            row_info = get_info(file, directory, num_samples, timeout, s, t)
            if row_info:
                row = f'{file}'
                for metric in metrics[1:]:
                    row = f'{row},{row_info[metric]}'
                print(row)
                ofile.write(f'{row}\n')
        
    ofile.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Generate metrics for given directories')

    parser.add_argument(
        '--dir',
        type=str,
        default='data/nx5/flip',
        help='directory of input matrices to generate metrics for'
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='uniformity.csv',
        help='outfile to write metrics to'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=11000,
        help='number of samples to generate'
    )
    parser.add_argument(
        '--timeout',
        type=float,
        default=7200.0,
        help='number of samples to generate'
    )
    parser.add_argument(
        '--s',
        type=float,
        default=0.8,
        help='Ratio of cell clusters to m, number of cells in input'
    )
    parser.add_argument(
        '--t',
        type=float,
        default=0.8,
        help='Ratio of mutation clusters to n, number of mutations in input'
    )

    parser.set_defaults(debug=False)
    args = parser.parse_args()

    directory = os.fsencode(args.dir).decode('utf-8')
    out_file = args.outfile
    num_samples = args.samples

    files = os.listdir(directory)

    if not os.path.exists(FORMULAS_DIRECTORY):
        os.makedirs(FORMULAS_DIRECTORY)

    generate_info(files, directory, out_file, num_samples, args.timeout, args.s, args.t)