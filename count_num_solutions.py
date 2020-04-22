import os
import os.path
import argparse
import math
import time
import subprocess

from generate_formula import get_cnf, read_matrix
from get_vars import write_vars

def parse_csv(csv_file, dir):
    with open(csv_file, 'r') as fp:
        lines = fp.readlines()
    seen = {}
    seen_files = set()
    for line in lines[1:]:
        split_line = line.split(',')
        full_filename = f'{dir}/{split_line[0]}'
        matrix_str = matrix_to_str(full_filename)
        seen[matrix_str] = (split_line[5], split_line[6])
        seen_files.add(split_line[0])
    return seen, seen_files

def matrix_to_str(filename):
    matrix = read_matrix(filename)
    rows = [''.join([str(elem) for elem in row]) for row in matrix]
    return ''.join(rows)

def get_num_solutions(sharpSAT_path, cnf_filename):
    output = subprocess.check_output(f'{sharpSAT_path} {cnf_filename}', shell=True)
    num_sols = output.splitlines()[-5]
    return int(num_sols)

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
    parser = argparse.ArgumentParser(description='Count number of solutions for inputs in a directory')
    
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
        default=1,
        help='Ratio of cell clusters to m, number of cells in input'
    )
    parser.add_argument(
        '--t',
        type=float,
        default=1,
        help='Ratio of mutation clusters to n, number of mutations in input'
    )

    parser.set_defaults(debug=False)
    args = parser.parse_args()

    input_files = os.listdir(args.dir)

    if os.path.exists(args.outfile):
        seen, seen_files = parse_csv(args.outfile, args.dir)
        out_csv = open(args.outfile, 'a+')
    else:
        seen = {}
        seen_files = set()
        out_csv = open(args.outfile, 'w')
        out_csv.write('filename,m,n,fp_rate,fn_rate,formula_time,num_solutions\n')

    for filename in input_files:
        if filename in seen_files:
            print(f'Skipping {filename}')
            continue
        full_filename = f'{args.dir}/{filename}'
        param_dict = parse_filename(filename)

        m = param_dict['m']
        n = param_dict['n']

        if m * n > 30:
            continue
        
        matrix_str = matrix_to_str(full_filename)

        fp_rate = param_dict['fp_rate']
        fn_rate = param_dict['fn_rate']

        loss = param_dict['loss']

        cell_clusters = math.ceil(args.s * m)
        mutation_clusters = math.ceil(args.t * n)

        num_entries = m * n

        expected_fp = math.ceil(num_entries * fp_rate)
        expected_fn = math.ceil(num_entries * fn_rate)

        if matrix_str in seen:
            total_time = seen[matrix_str][0]
            num_solutions = seen[matrix_str][1]
            row = f'{filename},{m},{n},{fp_rate},{fn_rate},{total_time},{num_solutions}\n'
            out_csv.write(row)
            print(f'Already seen {filename}')
            continue

        cnf_filename = f'{filename}.tmp.formula.cnf'
        
        start = time.time()
        get_cnf(full_filename, cnf_filename, cell_clusters, mutation_clusters,
                True, None, expected_fn, expected_fp)
        total_time = time.time() - start

        print(f'Starting sharpSAT on {filename}')
        num_solutions = get_num_solutions(args.sharpSAT, cnf_filename, output)

        row = f'{filename},{m},{n},{fp_rate},{fn_rate},{total_time},{num_solutions}\n'

        out_csv.write(row)
        print(row)
        os.system(f'rm {cnf_filename}')

        seen[filename] = (total_time,num_solutions)
        seen_files.add(filename)
    
    out_csv.close()