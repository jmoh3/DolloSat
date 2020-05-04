import os
import os.path
import argparse
import math
import time
import subprocess
import pandas as pd

from generate_formula import get_cnf, read_matrix
from get_vars import write_vars
from utils import get_matrix_info, parse_filename

FORMULAS_DIRECTORY = 'data/formulas'

def parse_appmc_output(num_sols_str):
    prefix = int(num_sols_str.decode("ascii").split(':')[1].split(' ')[1])
    power_of_two = int(num_sols_str.decode("ascii").split(':')[1].split(' ')[3].split('^')[1])

    return prefix, power_of_two

def matrix_to_str(filename):
    matrix = read_matrix(filename)
    rows = [''.join([str(elem) for elem in row]) for row in matrix]
    return ''.join(rows)

def get_num_solutions_sharpSAT(sharpSAT_path, cnf_filename):
    output = subprocess.check_output(f'{sharpSAT_path} {cnf_filename}', shell=True)
    num_sols = output.splitlines()[-5]
    return int(num_sols)

def get_num_solutions(approxMC_path, cnf_filename):
    try:
        output = subprocess.check_output(f'{approxMC_path} {cnf_filename}', shell=True, timeout=3600)
    except subprocess.CalledProcessError as err:
        output = err.output.splitlines()
    except subprocess.TimeoutExpired as err:
        return -1, -1
    prefix, power_of_two = parse_appmc_output(output[-1])
    return prefix, power_of_two

def get_info(infile, directory):
    row_info = parse_filename(infile)
    full_filename = f'{directory}/{infile}'

    m = row_info['m']
    n = row_info['n']

    if m > 10:
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

    print(f'Starting approxMC on {infile}')
    row_info['prefix'], row_info['power_of_two'] = get_num_solutions(args.approxMC, cnf_filename)
    print(f'Finished {infile}')

    os.system(f'rm {cnf_filename}')
    
    return row_info

def generate_info(files, directory, outfile):
    metrics = ['filename', 'm', 'n', 'num_cell_clusters', 'num_mutation_clusters',
                'num_variables', 'num_clauses', 'formula_gen_time', 'prefix', 'power_of_two']

    df = pd.read_csv(outfile)
    seen = set(df['filename'].values)
    files = [file for file in files if file not in seen]

    with open(outfile, 'a+') as ofile:
        # ofile.write(','.join(metrics) + '\n')

        sorted_files = sorted(files, key=lambda a: parse_filename(a)['m'])

        for file in sorted_files:
            row_info = get_info(file, directory)
            if row_info:
                row = f'{file}'
                for metric in metrics[1:]:
                    row = f'{row},{row_info[metric]}'
                print(row)
                ofile.write(f'{row}\n')
        
    ofile.close()

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Count number of solutions for inputs in a directory')
    
    parser.add_argument(
        '--approxMC',
        type=str,
        default='/home/jmoh3/bin/approxmc',
        help='Path to approxMC executable'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default='data/nx5/flip',
        help='The directory containing input matrices'
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='num_solutions_mx5.csv',
        help='Outfile to write solutions to'
    )

    parser.set_defaults(debug=False)
    args = parser.parse_args()

    input_files = os.listdir(args.dir)
    directory = args.dir
    
    generate_info(input_files, directory, args.outfile)