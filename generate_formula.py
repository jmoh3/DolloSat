import sys
import os
import argparse
from itertools import permutations 

# USAGE
# $ python3 generate_formula.py --filename=INPUT_MATRIX_FILENAME --num_rows=CLUSTER_ROWS
#   --num_columns=CLUSTER_COLUMNS --outfile=FORMULA_FILENAME
# 
# Generates a boolean formula in CNF format that maps the matrix in INPUT_MATRIX_FILENAME
# to a smaller 1 dollo matrix with CLUSTER_ROWS rows and CLUSTER_COLUMNS and writes it to
# FORMULA_FILENAME.

def get_lookup(lookup_filename):
    lookup_file = open(lookup_filename, 'r')
    lookup = {}
    lines = lookup_file.readlines()
    lookup_file.close()

    for idx in range(0, len(lines), 2):
        lookup[lines[idx].strip()] = lines[idx+1]

    return lookup

lookup = get_lookup('forbidden_clauses.txt')

variable_mapping = {'a': [0, [0,0]],
                    'b': [0, [0,1]],
                    'c': [0, [1,0]],
                    'd': [0, [1,1]],
                    'e': [0, [2,0]],
                    'f': [0, [2,1]],
                    'g': [1, [0,0]],
                    'h': [1, [0,1]],
                    'i': [1, [1,0]],
                    'j': [1, [1,1]],
                    'k': [1, [2,0]],
                    'l': [1, [2,1]],}

def create_variable_matrices(matrix, s, t):
    m = len(matrix)
    n = len(matrix[0])
    offset = 1

    cell_to_cluster = [[s*i+j+offset for j in range(s)] for i in range(m)]
    offset += m*s

    mutation_to_cluster = [[t*i+j+offset for j in range(t)] for i in range(n)]
    offset += n*t

    false_positives = [[0 for x in range(n)] for y in range(m)]
    false_negatives = [[0 for x in range(n)] for y in range(m)]
    
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == 1:
                false_positives[i][j] = offset
            if matrix[i][j] == 0:
                false_negatives[i][j] = offset
            offset += 1
    
    is_one = [[s*i+j+offset for j in range(t)] for i in range(s)]
    is_two = [[s*i+j+offset for j in range(t)] for i in range(s)]

    variables = {'cell_to_cluster': cell_to_cluster,
                'mutation_to_cluster': mutation_to_cluster,
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'is_one': is_one,
                'is_two': is_two}
    
    return variables

def get_clauses_no_forbidden(is_one, is_two):
    s = len(is_one)
    t = len(is_one[0])

    row_permutations = permutations([i for i in range(s)], 3)
    column_permutations = permutations([i for i in range(t)], 2)

    for rows in row_permutations:
        for columns in column_permutations:
            submatrix = [[matrix[row1][col1], matrix[row1][col2]],
                        [matrix[row2][col1], matrix[row2][col2]],
                        [matrix[row3][col1], matrix[row3][col2]]]

            submatrix_labels = [[zero_labels[row1][col1], zero_labels[row1][col2]],
                                [zero_labels[row2][col1], zero_labels[row2][col2]],
                                [zero_labels[row3][col1], zero_labels[row3][col2]]]
                                            
            clause = get_clause(submatrix, submatrix_labels, lookup)

def read_matrix(filename):
    matrix_file = open(filename, 'r')
    lines = matrix_file.readlines()[2:]
    
    return [[int(x) for x in line.split()] for line in lines]

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate samples for given directories')

    parser.add_argument(
        '--filename',
        type=str,
        default='data/example.txt',
        help='the input file containing the matrix to generate samples for'
    )
    parser.add_argument(
        '--outfile',
        type=str,
        default='formula.cnf',
        help='outfile to write formula to'
    )

    args = parser.parse_args()

    matrix = read_matrix(args.filename)
    start = time.time()
    generate_cnf(matrix, args.outfile)
    end = time.time()
    print(f'Generated cnf formula in {end - start} seconds')