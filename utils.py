import subprocess

def read_matrix(filename):
    """
    Returns matrix parsed from given file.
    First two lines of matrix file must specify number of cells and mutations of input.

    For example:
    5 # cells
    5 # mutations
    0 1 0 0 0
    0 0 1 0 1
    0 0 0 0 0
    0 0 0 0 0
    1 0 0 1 0

    filename - file that contains input matrix
    """
    matrix_file = open(filename, 'r')
    lines = matrix_file.readlines()[2:]
    matrix_file.close()
    
    return [[int(x) for x in line.split()] for line in lines]

def cluster_matrix(matrix):
    row_is_duplicate = [False for x in range(len(matrix))]
    col_is_duplicate = [False for x in range(len(matrix[0]))]

    for row in range(len(matrix)):
        for larger_row in range(row+1, len(matrix)):
            if row_is_duplicate[larger_row]:
                continue
            larger_row_is_dup = True

            for col in range(len(matrix[0])):
                if matrix[row][col] != matrix[larger_row][col]:
                    larger_row_is_dup = False
                    break

            if larger_row_is_dup:
                row_is_duplicate[larger_row] = True
    
    for col in range(len(matrix[0])):
        for larger_col in range(col+1, len(matrix[0])):
            if col_is_duplicate[larger_col]:
                continue
            
            larger_col_is_dup = True

            for row in range(len(matrix)):
                if matrix[row][col] != matrix[row][larger_col]:
                    larger_col_is_dup = False
                    break
            
            if larger_col_is_dup:
                col_is_duplicate[larger_col] = True
    
    return row_is_duplicate, col_is_duplicate

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

def parse_allowed_losses_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        if len(lines) > 0:
            allowed = lines[0].split(',')
            return set([int(i) for i in allowed])
        else:
            return set()

def parse_allowed_losses(matrix_filename, directory):
    full_filename = f'{directory}/{matrix_filename}'
    
    data_dir = '/'.join(directory.split('/')[:-1])
    perfect_phylogeny_filename = '_'.join(matrix_filename.split('_')[:3])

    perfect_phylogeny_full_filename = f'{data_dir}/perfect_phylogeny/{perfect_phylogeny_filename}.txt'
    perfect_phylogeny_matrix = read_matrix(perfect_phylogeny_full_filename)

    dollo_filename = '_'.join(matrix_filename.split('_')[:5])

    dollo_full_filename = f'{data_dir}/k_dollo/{dollo_filename}.B'
    dollo_matrix = read_matrix(dollo_full_filename)

    m = len(dollo_matrix)
    n = len(dollo_matrix[0])
    L = set()

    for j in range(n):
        for i in range(m):
            if perfect_phylogeny_matrix[i][j] == 1 and dollo_matrix[i][j] == 0:
                L.add(j)
                break
    
    return L