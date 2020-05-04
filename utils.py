from generate_formula import read_matrix
from reconstruct_solutions import cluster_matrix
import subprocess

def parse_filename(filename):
    split_filename = filename.split('_')

    param_dict = {}

    param_dict['m'] = int(split_filename[0][1:])
    param_dict['n'] = int(split_filename[1][1:])

    param_dict['loss'] = float(split_filename[4][4:])

    param_dict['fp_rate'] = float(split_filename[5][1:])
    param_dict['fn_rate'] = float(split_filename[6][1:-2])

    return param_dict

def get_matrix_info(matrix_filename, directory):
    full_filename = f'{directory}/{matrix_filename}'

    matrix = read_matrix(full_filename)
    ones_count = 0
    for row in matrix:
        for elem in row:
            if elem == 1:
                ones_count += 1
    
    data_dir = '/'.join(directory.split('/')[:-1])
    perfect_phylogeny_filename = '_'.join(matrix_filename.split('_')[:3])

    perfect_phylogeny_full_filename = f'{data_dir}/perfect_phylogeny/{perfect_phylogeny_filename}.txt'
    perfect_phylogeny_matrix = read_matrix(perfect_phylogeny_full_filename)

    row_is_duplicate, col_is_duplicate = cluster_matrix(perfect_phylogeny_matrix)

    num_row_duplicates = 0
    for elem in row_is_duplicate:
        if elem:
            num_row_duplicates += 1
    
    row_clusters = len(matrix) - num_row_duplicates
    
    num_col_duplicates = 0
    for elem in col_is_duplicate:
        if elem:
            num_col_duplicates += 1
    
    cell_clusters = len(matrix[0]) - num_col_duplicates

    return ones_count, row_clusters, cell_clusters

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

def get_num_solutions_appmc(approxMC_path, cnf_filename):
    try:
        output = subprocess.check_output(f'{approxMC_path} {cnf_filename}', shell=True, timeout=3600)
    except subprocess.CalledProcessError as err:
        output = err.output.splitlines()
    except subprocess.TimeoutExpired as err:
        return -1, -1
    prefix, power_of_two = parse_appmc_output(output[-1])
    return prefix * 2**power_of_two