import os 
import argparse
import math
import time
import subprocess

from generate_formula import read_matrix, get_cnf

def parse_output(sharpSAT_output):
    return ''

def parse_filename(filename):
    split_filename = filename.split('_')

    param_dict = {}

    param_dict['m'] = int(split_filename[0][1:])
    param_dict['n'] = int(split_filename[1][1:])

    param_dict['loss'] = float(split_filename[4][4:])

    param_dict['fp_rate'] = float(split_filename[5][1:])
    param_dict['fn_rate'] = float(split_filename[6][1:-2])

    return param_dict

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Generate samples for given directories')
    
    parser.add_argument(
        '--sharpSAT',
        type=str,
        default='',
        help='Path to sharpSAT executable'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default='data/5xn/flip',
        help='The directory containing input matrices'
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='num_solutions.csv',
        help='Outfile to write solutions to'
    )
    parser.add_argument(
        '--s',
        type=float,
        default=0.75,
        help='Ratio of cell clusters to m, number of cells in input'
    )
    parser.add_argument(
        '--t',
        type=float,
        default=0.75,
        help='Ratio of mutation clusters to n, number of mutations in input'
    )

    parser.set_defaults(debug=False)
    args = parser.parse_args()

    input_files = os.listdir(args.dir)

    for filename in input_files:
        full_filename = f'{args.dir}/{filename}'
        param_dict = parse_filename(filename)

        cell_clusters = math.ceil(args.s * param_dict['m'])
        mutation_clusters = math.ceil(args.s * param_dict['n'])

        num_entries = param_dict['m'] * param_dict['n']

        expected_fp = math.ceil(num_entries * param_dict['fp_rate'])
        expected_fn = math.ceil(num_entries * param_dict['fn_rate'])

        cnf_filename = f'{filename}.tmp.formula.cnf'
        
        start = time.time()
        get_cnf(full_filename, cnf_filename, cell_clusters, mutation_clusters,
                True, None, expected_fn, expected_fp)
        end = time.time()

        output = subprocess.check_output(f{args.sharpSAT} {cnf_filename}", shell=True)
        
        os.system(f'rm {cnf_filename}')