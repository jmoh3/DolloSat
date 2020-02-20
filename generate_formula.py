from get_clauses import *
from get_vars import create_variable_matrices, write_vars

import sys
import os
import time
import argparse

"""
USAGE
$ python3 generate_formula.py --filename=INPUT_MATRIX_FILENAME
                            --outfile=FORMULA_FILENAME
                            --s=NUM_CELL_CLUSTERS
                            --t=NUM_MUTATION_CLUSTERS

Generates a boolean formula in CNF format that maps the matrix in INPUT_MATRIX_FILENAME
to a smaller 1 dollo matrix with NUM_CELL_CLUSTERS rows and NUM_MUTATION_CLUSTERS and writes it to
FORMULA_FILENAME.
"""

def get_cnf(read_filename, write_filename, s=5, t=5):
    """
    Writes a cnf formula for matrix specified in read_filename to write_filename using s
    rows and t columns for clustered matrix.

    read_filename - file containing input matrix
    write_filename - file to write formula to
    s - number of rows in clustered matrix/cell clusters
    t - number of columns in clustered matrix/mutation clusters
    """
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
        f.writelines(one_fp)
        f.writelines(one_fn)

    return variables

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
        '--s',
        type=int,
        default=5,
        help='number of rows in clustered matrix'
    )
    parser.add_argument(
        '--t',
        type=int,
        default=5,
        help='number of columns in clustered matrix'
    )

    args = parser.parse_args()

    filename = args.filename
    outfile = args.outfile
    s = args.s
    t = args.t

    start = time.time()
    variables = get_cnf(filename, outfile, s, t)
    end = time.time()

    write_vars("formula.vars", variables)

    print(f'Generated cnf formula in {end - start} seconds')