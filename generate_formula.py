import sys
import os
import time
import argparse
from itertools import permutations 

# USAGE
# $ python3 generate_formula.py --filename=INPUT_MATRIX_FILENAME --outfile=FORMULA_FILENAME
#  --num_rows=CLUSTER_ROWS --num_columns=CLUSTER_COLUMNS
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

def get_forbidden_clause(is_one_sub, is_two_sub, raw_clause):
    split_cnf = raw_clause.split()[:-1]
    clause_cnf = ''
    for argument in split_cnf:
        if argument[0] == '-':
            label = argument[1]
            use_is_two, location = variable_mapping[label][0], variable_mapping[label][1]
            if use_is_two:
                clause_cnf += f'-{is_two_sub[location[0]][location[1]]} '
            else:
                clause_cnf += f'-{is_one_sub[location[0]][location[1]]} '
        else:
            label = argument[0]
            use_is_two, location = variable_mapping[label][0], variable_mapping[label][1]
            if use_is_two:
                clause_cnf += f'{is_two_sub[location[0]][location[1]]} '
            else:
                clause_cnf += f'{is_one_sub[location[0]][location[1]]} '
    clause_cnf += '0\n'
    return clause_cnf

def get_clauses_no_forbidden(is_one, is_two):
    s = len(is_one)
    t = len(is_one[0])

    row_permutations = permutations([i for i in range(s)], 3)
    column_permutations = permutations([i for i in range(t)], 2)

    clauses = []

    for rows in row_permutations:
        for columns in column_permutations:
            row1, row2, row3 = rows[0], rows[1], rows[2]
            col1, col2 = columns[0], columns[1]

            is_one_sub = [[is_one[row1][col1], is_one[row1][col2]],
                            [is_one[row2][col1], is_one[row2][col2]],
                            [is_one[row3][col1], is_one[row3][col2]]]

            is_two_sub = [[is_two[row1][col1], is_two[row1][col2]],
                            [is_two[row2][col1], is_two[row2][col2]],
                            [is_two[row3][col1], is_two[row3][col2]]]

            for possible_submatrix in lookup.keys():
                clause_raw = lookup[possible_submatrix]
                clause = get_forbidden_clause(is_one_sub, is_two_sub, clause_raw)
                clauses.append(clause)
    
    return clauses

def get_formatted_clause(true_vars, false_vars):
    clause = ''
    for var in true_vars:
        clause += f'{var} '
    for var in false_vars:
        clause += f'-{var} '
    clause += '0\n'
    return clause

def get_clauses_mapping(variables):
    cell_to_cluster = variables['cell_to_cluster']
    mutation_to_cluster = variables['mutation_to_cluster']
    false_positives = variables['false_positives']
    false_negatives = variables['false_negatives']
    is_one = variables['is_one']
    is_two = variables['is_two']

    m = len(cell_to_cluster)
    n = len(mutation_to_cluster)
    s = len(is_one)
    t = len(is_one[0])

    clauses = []

    for cell_num in range(m):
        for mutation_num in range(n):
            for cell_cluster in range(s):
                for mutation_cluster in range(t):
                    cell_cluster_var = cell_to_cluster[cell_num][cell_cluster]
                    mutation_cluster_var = mutation_to_cluster[mutation_num][mutation_cluster]

                    is_one_var = is_one[cell_cluster][mutation_cluster]
                    is_two_var = is_two[cell_cluster][mutation_cluster]

                    false_pos_var = false_positives[cell_num][mutation_num]
                    false_neg_var = false_negatives[cell_num][mutation_num]

                    if false_positives[cell_num][mutation_num] != 0:
                        # entry is originally a 1
                        # 1 -> 0 => false positive
                        clauses.append(get_formatted_clause([false_pos_var, is_one_var, is_two_var],
                                                            [cell_cluster_var, mutation_cluster_var]))
                        # 1 -> 1 => not false positive
                        clauses.append(get_formatted_clause([is_one_var],
                                                            [false_pos_var, cell_cluster_var, mutation_cluster_var]))
                        # 1 -> 2 => false positive
                        clauses.append(get_formatted_clause([is_two_var, false_pos_var],
                                                            [cell_cluster_var, mutation_cluster_var]))
                    else:
                        # entry is originally a 0
                        # 0 -> 0 => not false negative
                        clauses.append(get_formatted_clause([is_one_var, is_two_var],
                                                            [cell_cluster_var, mutation_cluster_var, false_neg_var]))
                        # 0 -> 1 => false negative
                        clauses.append(get_formatted_clause([false_neg_var, is_one_var],
                                                            [cell_cluster_var, mutation_cluster_var]))
                        # 0 -> 2 => not false negative
                        clauses.append(get_formatted_clause([is_two_var],
                                                            [cell_cluster_var, mutation_cluster_var, false_neg_var]))
    return clauses

def get_cnf(filename, s, t):
    matrix = read_matrix(filename)
    variables = create_variable_matrices(matrix, s, t)
    forbidden_clauses  = get_clauses_no_forbidden(variables['is_one'], variables['is_two'])
    
    # print(forbidden_clauses)

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
    parser.add_argument(
        '--num_rows',
        type=int,
        default=5,
        help='number of rows in clustered matrix'
    )
    parser.add_argument(
        '--num_columns',
        type=int,
        default=5,
        help='number of columns in clustered matrix'
    )

    args = parser.parse_args()

    filename = args.filename
    outfile = args.outfile
    s = args.num_rows
    t = args.num_columns

    start = time.time()
    get_cnf(filename, s, t)
    end = time.time()

    print(f'Generated cnf formula in {end - start} seconds')