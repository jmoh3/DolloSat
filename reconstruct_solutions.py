import copy
import sys
from generate_formula import read_matrix

# USAGE
# $ python3 reconstruct_solutions.py INPUT_MATRIX_FILENAME SOLUTION_FILENAME 
#
# Writes k-dollo phylogeny matrices reconstructed from samples in SOLUTION_FILENAME to samples.txt.
#
# For each '1' in a solution, the corresponding zero in the input matrix specified in 
# INPUT_MATRIX_FILENAME will be flipped to a 2 to indicate a mutation that was present in 
# a sample but then lost due to a copy number abberation.
#
# For a INPUT_MATRIX_FILENAME whose contents look like this:
# 4 # cells
# 4 # mutations
# 0 0 1 0
# 1 0 0 0
# 1 0 0 0
# 1 0 0 0
#
# One of the reconstructed solutions written to SOLUTION_FILENAME could look like this:
#
# 0 2 1 2 
# 1 0 0 2 
# 1 0 0 2 
# 1 0 0 2 
#
# Reconstructed matrices are separated by '======================'

def reconstruct_solutions(solution_filename, write_file, variables, debug=False):
    solutions = get_binary_vector(solution_filename)

    m = len(variables['false_positives'])
    n = len(variables['false_positives'][0])
    s = len(variables['is_one'])
    t = len(variables['is_one'][0])

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
                mutation_mappings.append(f'mutation {i} mapped to row {cluster_num}\n')
            f.writelines(cell_mappings)
            f.writelines(mutation_mappings)
        f.write('======================\n')
        solution_matrices.append(clustered_matrix)


def get_binary_vector(valid_sample_filename):
    valid = []

    with open(valid_sample_filename, 'r') as f:
        valid = f.readlines()

    out = []

    for line in valid:
        split_line = line.split(' ')
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

if __name__ == '__main__':
    matrix = read_matrix(sys.argv[1])
    reconstruct_solutions(matrix, sys.argv[2], 'samples.txt')