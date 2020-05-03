from generate_formula import read_matrix
from reconstruct_solutions import cluster_matrix

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