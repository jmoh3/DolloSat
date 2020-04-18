import copy
import sys
from generate_formula import read_matrix


def reconstruct_solutions(matrix_filename, solution_filename, write_file, variables, debug=True):
    """
    Writes k-dollo phylogeny matrices reconstructed from samples in solution_filename to write_file.

    Reconstructed matrices are separated by '======================'

    solution_filename - file containing satisfying variable assignments
    write_file - file to write reconstructed solutions to
    variables - dictionary of variable matrices
    debug - if set to True, will write information about false positives/negatives and clustering to
    write_file, if set to False, only matrices will be written
    """

    matrix = read_matrix(matrix_filename)

    m = len(variables['false_positives'])
    n = len(variables['false_positives'][0])

    num_vars = variables['col_is_duplicate'][n-1]
    solutions = get_binary_vectors(solution_filename, num_vars)

    col_is_duplicate = variables['col_is_duplicate']
    row_is_duplicate = variables['row_is_duplicate']

    f = open(write_file, 'w')

    solution_matrices = []

    for solution in solutions:
        if len(solution) == 0:
            continue
        # resulting_matrix = matrix.copy()
        num_false_positives = 0
        num_false_negatives = 0
        for i in range(m):
            # if col_is_duplicate[i]:
            #     continue
            line = ''
            for j in range(n):
                # if row_is_duplicate[j]:
                #     continue
                is_one_val = 0
                is_two_val = 0

                if matrix[i][j] == 0:
                    false_neg_varname = variables['false_negatives'][i][j] - 1
                    is_two_varname = variables['is_two'][i][j] - 1

                    is_one_val = solution[false_neg_varname] == 1
                    num_false_negatives += is_one_val
                    is_two_val = solution[is_two_varname] == 1

                if matrix[i][j] == 1:
                    false_pos_varname = variables['false_positives'][i][j] - 1
                    is_two_varname = variables['is_two'][i][j] - 1

                    is_one_val = solution[false_pos_varname] == 0
                    num_false_positives += solution[false_pos_varname]
                    is_two_val = solution[is_two_varname] == 1
                
                if is_one_val:
                    # resulting_matrix[i][j] = 1
                    line += '1 '
                elif is_two_val:
                    # resulting_matrix[i][j] = 0
                    line += '2 '
                else:
                    line += '0 '
            line += '\n'
            f.write(line)

        if debug:    
            f.write(f'{num_false_negatives} false negatives, {num_false_positives} false positives\n')
            
        f.write('======================\n')
        # solution_matrices.append(resulting_matrix)


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