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

    solutions = get_binary_vectors(solution_filename)

    col_is_duplicate = variables['col_is_duplicate']
    row_is_duplicate = variables['row_is_duplicate']

    f = open(write_file, 'w')

    solution_matrices = []

    for solution in solutions:
        if len(solution) == 0:
            continue
        
        num_false_positives = 0
        num_false_negatives = 0
        idx = 0

        solution_matrix = [[0 for j in range(n)] for i in range(m)]

        for i in range(m):
            for j in range(n):
                if matrix[i][j] == 0 and solution[idx] == 1:
                    # is false negative, 0 -> 1
                    solution_matrix[i][j] = 1
                    num_false_negatives += 1
                elif matrix[i][j] == 1 and solution[idx] == 0:
                    # is a true positive, entry is 1
                    solution_matrix[i][j] = 1
                elif matrix[i][j] == 1 and solution[idx] == 1:
                    num_false_positives += 1
                idx += 1
        
        for i in range(m):
            for j in range(n):
                if solution[idx] == 1:
                    solution_matrix[i][j] = 2
                idx += 1

        row_is_duplicate, col_is_duplicate = cluster_matrix(solution_matrix)
        
        for i in range(m):
            if row_is_duplicate[i]:
                continue
            line = ''
            for j in range(n):
                if col_is_duplicate[j]:
                    continue
                line += f'{solution_matrix[i][j]} '
            line += '\n'
            f.write(line)

        if debug:    
            f.write(f'{num_false_negatives} false negatives, {num_false_positives} false positives\n')
            
        f.write('======================\n')

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

def get_binary_vectors(valid_sample_filename):
    """
    Returns a list of binary vectors corresponding to solutions in valid_sample_filename.
    valid_sample_filename - file that contains satisfying variable assignments
    """
    valid = []

    with open(valid_sample_filename, 'r') as f:
        valid = f.readlines()

    out = []

    for line in valid:
        if len(line) <= 1:
            continue
        cleaned_line = line.split('v')[1]
        split_line = cleaned_line.split(' ')
        if len(split_line)-1 <= 0:
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

def write_vars_debug(var_filename, variables, solution):
    """
    Writes variables to given file for debugging purposes.
    var_filename - file to write variables to
    variables - dictionary of variable matrices
    """
    lines = []
    for key in variables.keys():
        lines.append(f'{key}\n')
        if key == 'pair_in_row_equal':
            for i, row in enumerate(variables[key]):
                lines.append(f'row {i}\n')
                for j, col1 in enumerate(row):
                    for k, col2 in enumerate(col1):
                        if k > j:
                            lines.append(f'B[{i}][{j}] == B[{i}][{k}] = {solution[col2-1]}\n')
        elif key == 'pair_in_col_equal':
            for k in range(len(variables[key][0][0])):
                lines.append(f'col {k}\n')
                for i in range(len(variables[key][0])):
                    for j in range(i+1,len(variables[key][0])):
                        if j > i:
                            lines.append(f'B[{i}][{k}] == B[{j}][{k}] = {solution[variables[key][i][j][k]-1]}\n')
        elif key == 'row_is_duplicate' or key == 'col_is_duplicate':
            lines.append(' '.join([str(solution[elem-1]) for elem in variables[key]]))
            lines.append('\n')
        else:
            for row in variables[key]:
                line = ''
                for elem in row:
                    if elem != 0:
                        line += f'{solution[elem-1]} '
                    else: 
                        line += f'x '
                lines.append(line)
                lines.append('\n')
        
        lines.append('=========================\n')
    with open(var_filename, 'w') as f:
        f.writelines(lines)