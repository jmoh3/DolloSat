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
    
    is_one = [[t*i+j+offset for j in range(t)] for i in range(s)]
    offset += s*t

    is_two = [[t*i+j+offset for j in range(t)] for i in range(s)]

    variables = {'cell_to_cluster': cell_to_cluster,
                'mutation_to_cluster': mutation_to_cluster,
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'is_one': is_one,
                'is_two': is_two}
        
    return variables

def write_vars(var_filename, variables):
    lines = []
    for key in variables.keys():
        lines.append(f'{key}\n')
        for row in variables[key]:
            lines.append(' '.join([str(elem) for elem in row]))
            lines.append('\n')
        lines.append('=========================\n')
    with open(var_filename, 'w') as f:
        f.writelines(lines)

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
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} {is_one_var} {is_two_var} {false_pos_var} 0\n")
                        # 1 -> 1 => not false positive
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_one_var} -{false_pos_var} 0\n")
                        # 1 -> 2 => false positive
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_two_var} {false_pos_var} 0\n")
                    else:
                        # entry is originally a 0
                        # 0 -> 0 => not false negative
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} {is_one_var} {is_two_var} -{false_neg_var} 0\n")
                        # 0 -> 1 => false negative
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_one_var} {false_neg_var} 0\n")
                        # 0 -> 2 => not false negative
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_two_var} -{false_neg_var} 0\n")
    return clauses

def get_clauses_surjective(cluster_mapping):
    rows = len(cluster_mapping)
    columns = len(cluster_mapping[0])

    clauses = []

    for i in range(rows):
        for p in range(columns):
            for k in range(columns):
                if p == k:
                    continue
                clauses.append(f'-{cluster_mapping[i][p]} -{cluster_mapping[i][k]} 0\n')
    
    return clauses

def get_clauses_not_one_and_two(is_one, is_two):
    clauses = []
    for i in range(len(is_one)):
        for j in range(len(is_one[0])):
            clauses.append(f'-{is_one[i][j]} -{is_two[i][j]} 0\n')
    return clauses

def get_at_least_one_cluster(cluster_matrix):
    clauses = []
    for i in range(len(cluster_matrix)):
        clause = ''
        for j in range(len(cluster_matrix[0])):
            clause += f'{cluster_matrix[i][j]} '
        clause += '0\n'
        clauses.append(clause)
    return clauses

def each_cluster_has_at_least_one(cluster_matrix):
    clauses = []
    for j in range(len(cluster_matrix[0])):
        clause = ''
        for i in range(len(cluster_matrix)):
            clause += f'{cluster_matrix[i][j]} '
        clause += '0\n'
        clauses.append(clause)
    return clauses

def constrain_fp(false_vars):
    flatten = []

    for row in false_vars:
        for elem in row:
            if elem != 0:
                flatten.append(elem)
    clauses = []
    for i in range(len(flatten)):
        var1 = flatten[i]
        for j in range(i+1, len(flatten)):
            var2 = flatten[j]
            if var1 != var2 and var2 != 0:
                clauses.append(f'-{var1} -{var2} 0\n')
    return clauses

def get_cnf(read_filename, write_filename, s=5, t=5):
    matrix = read_matrix(read_filename)
    variables = create_variable_matrices(matrix, s, t)
    
    forbidden_clauses  = get_clauses_no_forbidden(variables['is_one'], variables['is_two'])
    mapping_clauses = get_clauses_mapping(variables)
    cell_mapping_clauses = get_clauses_surjective(variables['cell_to_cluster'])
    mutation_mapping_clauses = get_clauses_surjective(variables['mutation_to_cluster'])
    not_one_and_two_clauses = get_clauses_not_one_and_two(variables['is_one'], variables['is_two'])
    cell_map_to_one = get_at_least_one_cluster(variables['cell_to_cluster'])
    mutation_map_to_one = get_at_least_one_cluster(variables['mutation_to_cluster'])
    at_least_one_cell_per_cluster = each_cluster_has_at_least_one(variables['cell_to_cluster'])
    at_least_one_mutation_per_cluster = each_cluster_has_at_least_one(variables['mutation_to_cluster'])
    one_fp = constrain_fp(variables['false_positives'])
    one_fn = constrain_fp(variables['false_negatives'])

    enforce_clustering = []
    for i in range(3):
        enforce_clustering.append(f"{variables['cell_to_cluster'][i][i]} 0\n")
    
    for i in range(2):
        enforce_clustering.append(f"{variables['mutation_to_cluster'][i][i]} 0\n")

    with open(write_filename, 'w') as f:
        f.writelines(forbidden_clauses)
        f.writelines(mapping_clauses)
        f.writelines(cell_mapping_clauses)
        f.writelines(mutation_mapping_clauses)
        f.writelines(not_one_and_two_clauses)
        f.writelines(cell_map_to_one)
        f.writelines(mutation_map_to_one)
        f.writelines(at_least_one_cell_per_cluster)
        f.writelines(at_least_one_mutation_per_cluster)
        f.writelines(enforce_clustering)
        f.writelines(one_fp)
        f.writelines(one_fn)

    return variables

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
    get_cnf(filename, outfile, s, t)
    end = time.time()

    print(f'Generated cnf formula in {end - start} seconds')