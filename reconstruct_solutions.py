import copy
import sys
from generate_formula import read_matrix


def reconstruct_solutions(solution_filename, write_file, variables, debug=True):
    """
    Writes k-dollo phylogeny matrices reconstructed from samples in solution_filename to write_file.

    Reconstructed matrices are separated by '======================'

    solution_filename - file containing satisfying variable assignments
    write_file - file to write reconstructed solutions to
    variables - dictionary of variable matrices
    debug - if set to True, will write information about false positives/negatives and clustering to
    write_file, if set to False, only matrices will be written
    """

    m = len(variables['false_positives'])
    n = len(variables['false_positives'][0])
    s = len(variables['is_one'])
    t = len(variables['is_one'][0])

    num_vars = variables['is_two'][s-1][t-1]
    solutions = get_binary_vectors(solution_filename, num_vars)

    f = open(write_file, 'w')

    solution_matrices = []

    for solution in solutions:
        if len(solution) == 0:
            continue
        clustered_matrix = [[0 for i in range(t)] for j in range(s)]
        for i in range(s):
            line = ''
            for j in range(t):
                is_one_varname = variables['is_one'][i][j] - 1
                is_two_varname = variables['is_two'][i][j] - 1

                is_one_val = solution[is_one_varname] == 1
                is_two_val = solution[is_two_varname] == 1
                
                if is_one_val:
                    clustered_matrix[i][j] = 1
                    line += '1 '
                elif is_two_val:
                    clustered_matrix[i][j] = 0
                    line += '2 '
                else:
                    line += '0 '
            line += '\n'
            f.write(line)

        if debug:
            num_false_positives = 0
            num_false_negatives = 0

            for i in range(m):
                for j in range(n):
                    if variables['false_positives'][i][j] != 0:
                        false_pos_var = variables['false_positives'][i][j] - 1
                        if solution[false_pos_var] == 1:
                            num_false_positives += 1
                    if variables['false_negatives'][i][j] != 0:
                        false_neg_var = variables['false_negatives'][i][j] - 1
                        if solution[false_neg_var] == 1:
                            num_false_negatives += 1
            
            f.write(f'{num_false_negatives} false negatives, {num_false_positives} false positives\n')
            cell_mappings = []
            for i in range(m):
                found = False
                cluster_num = -1
                for j in range(s):
                    cell_to_cluster_var = variables['cell_to_cluster'][i][j] - 1
                    cell_to_cluster = solution[cell_to_cluster_var]
                    if cell_to_cluster:
                        cluster_num = j
                cell_mappings.append(f'cell {i} mapped to row {cluster_num}\n')
            
            mutation_mappings = []
            for i in range(n):
                cluster_num = -1
                for j in range(t):
                    mutation_to_cluster_var = variables['mutation_to_cluster'][i][j] - 1
                    mutation_to_cluster = solution[mutation_to_cluster_var]
                    if mutation_to_cluster:
                        cluster_num = j
                mutation_mappings.append(f'mutation {i} mapped to column {cluster_num}\n')
            f.writelines(cell_mappings)
            f.writelines(mutation_mappings)
        f.write('======================\n')
        solution_matrices.append(clustered_matrix)


def get_binary_vectors(valid_sample_filename, num_vars):
    """
    Returns a list of binary vectors corresponding to solutions in valid_sample_filename.

    valid_sample_filename - file that contains satisfying variable assignments
    """
    valid = []

    with open(valid_sample_filename, 'r') as f:
        valid = f.readlines()

    out = []

    for line in valid:
        split_line = line.split(' ')
        if len(split_line)-1 != num_vars:
            continue
        binary_str = ''
        line_vec = []
        for arg in split_line:
            if arg[0] == '-':
                line_vec.append(0)
            elif arg[0] != '0':
                line_vec.append(1)
            else:
                break
        if len(line_vec) > 0:
            out.append(line_vec)
    
    return out