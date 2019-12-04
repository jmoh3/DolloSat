import copy
import sys
from generate_formula import read_matrix

# USAGE
# $ python3 reconstruct_solutions.py INPUT_MATRIX_FILENAME SOLUTION_FILENAME NUM_SAMPLES
#
# Writes max(NUM_SAMPLES, number of samples in SOLUTION_FILENAME) k-dollo phylogeny matrices
# reconstructed from samples in SOLUTION_FILENAME to samples.txt.
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
# 0 0 1 0 
# 1 0 2 0 
# 1 0 0 0 
# 1 2 0 0 
#
# Reconstructed matrices are separated by '======================'

def reconstruct_solutions(matrix, solution_filename, write_file):
    solution_lines = get_binary_strings(solution_filename)
    solutions = []

    for x in range(len(solution_lines)):
        solution = solution_lines[x]
        solution_matrix = copy.deepcopy(matrix)

        solution_idx = 0

        for i in range(len(solution_matrix)):
            for j in range(len(solution_matrix[i])):
                if solution_matrix[i][j] == 0:
                    if solution[solution_idx] == '1':
                        solution_matrix[i][j] = 2
                    solution_idx += 1

        assert(solution_idx == len(solution))
        solutions.append(solution_matrix)
    
    write_file = open(write_file, 'w')
    
    for solution in solutions:
        for row in solution:
            row_str = ''
            for elem in row:
                row_str += str(elem) + ' '
            row_str += '\n'
            write_file.write(row_str)
        write_file.write('======================\n')

    write_file.close()

def get_binary_strings(valid_sample_filename):
    valid = []

    with open(valid_sample_filename, 'r') as f:
        valid = f.readlines()

    out = []

    for line in valid:
        split_line = line.split()
        binary_str = ''
        for arg in split_line:
            if arg[0] == '0':
                continue
            if arg[0] == '-':
                binary_str += '0'
            else:
                binary_str += '1'
        if len(binary_str) > 0:
            out.append(binary_str)
    
    return out

# print(get_binary_strings('quicksampler/formula.cnf.samples.valid'))

if __name__ == '__main__':
    matrix = read_matrix(sys.argv[1])
    reconstruct_solutions(matrix, sys.argv[2], 'samples.txt')