from get_clauses import *
from get_vars import create_variable_matrices, write_vars

import sys
import os
import time
import argparse
import shutil

"""
USAGE
$ python3 generate_formula.py --filename=INPUT_MATRIX_FILENAME
                            --outfile=FORMULA_FILENAME
                            --s=NUM_CELL_CLUSTERS
                            --t=NUM_MUTATION_CLUSTERS
                            --allowed_losses=LOSSES_FILENAME
                            --sampler=SAMPLER_TYPE

Generates a boolean formula in CNF format that maps the matrix in INPUT_MATRIX_FILENAME
to a smaller 1 dollo matrix with NUM_CELL_CLUSTERS rows and NUM_MUTATION_CLUSTERS where only losses
specified in LOSSES_FILENAME are allowed. The formula is in the format required by SAMPLER_TYPE and is
written to FORMULA_FILENAME.
"""

def get_cnf(read_filename, write_filename, s, t, unigen=True, losses_filename=None, fn=1, fp=1, return_num_vars_clauses=False):
    """
    Writes a cnf formula for matrix specified in read_filename to write_filename using s
    rows and t columns for clustered matrix.

    read_filename - file containing input matrix
    write_filename - file to write formula to
    s - number of rows in clustered matrix/cell clusters
    t - number of columns in clustered matrix/mutation clusters
    """
    matrix = read_matrix(read_filename)

    num_rows = len(matrix)
    num_cols = len(matrix[0])

    variables = create_variable_matrices(matrix, s, t)
    allowed_losses = parse_allowed_losses(losses_filename, len(matrix[0]))

    unsupported_losses = []

    for i in range(num_cols):
        if i not in allowed_losses:
            unsupported_losses.append(i)
    
    false_positives = variables['false_positives']
    false_negatives = variables['false_negatives']

    pair_in_row_equal = variables['pair_in_row_equal']
    pair_in_col_equal = variables['pair_in_col_equal']

    row_is_duplicate = variables['row_is_duplicate']
    col_is_duplicate = variables['col_is_duplicate']

    row_is_duplicate_of = variables['row_is_duplicate_of']
    col_is_duplicate_of = variables['col_is_duplicate_of']

    is_two = variables['is_two']
    is_one = generate_is_one(matrix, false_positives, false_negatives, is_two)

    num_row_duplicates = len(row_is_duplicate) - s
    num_col_duplicates = len(col_is_duplicate) - t

    independent_lines = []

    c_ind = 'c ind '
    num_ind = 0

    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == 0:
                elem = false_negatives[i][j]
            else:
                elem = false_positives[i][j]
            c_ind += f'{elem} '
            num_ind += 1
            if num_ind == 10:
                c_ind += '0\n'
                independent_lines.append(c_ind)
                c_ind = 'c ind '
                num_ind = 0

    for row in is_two:
        for elem in row:
            c_ind += f'{elem} '
            num_ind += 1
            if num_ind == 10:
                c_ind += '0\n'
                independent_lines.append(c_ind)
                c_ind = 'c ind '
                num_ind = 0
        
    if num_ind != 0:
        c_ind += '0\n'
        independent_lines.append(c_ind)

    write_file = open(write_filename + '.tmp', 'w')
    write_file.writelines(independent_lines)
    
    clause_count = get_clauses_no_forbidden(is_one, is_two, row_is_duplicate, col_is_duplicate, write_file)

    clause_count += get_clauses_not_one_and_two(is_one, is_two, write_file)

    clause_count += get_row_duplicate_clauses(pair_in_col_equal, row_is_duplicate, row_is_duplicate_of, write_file)
    
    clause_count += get_col_duplicate_clauses(pair_in_row_equal, col_is_duplicate, unsupported_losses, is_two, col_is_duplicate_of, write_file)

    clause_count += get_col_pairs_equal_clauses(is_one, is_two, pair_in_col_equal, write_file)

    clause_count += get_row_pairs_equal_clauses(is_one, is_two, pair_in_row_equal, write_file)

    clause_count += clause_forbid_unsupported_losses(unsupported_losses, is_two, write_file)

    extra_vars, num_constraints_clauses = encode_constraints(false_positives, false_negatives,
                                                        row_is_duplicate, col_is_duplicate,
                                                        fp, fn, num_row_duplicates, num_col_duplicates, write_file)
    clause_count += num_constraints_clauses

    num_vars = col_is_duplicate[num_cols-1] + extra_vars

    first_line = f'p cnf {num_vars} {clause_count}\n'

    write_file.close()

    from_file = open(write_filename + '.tmp') 
    
    to_file = open(write_filename,mode="w")
    to_file.write(first_line)
    shutil.copyfileobj(from_file, to_file)
    
    to_file.close()
    from_file.close()

    os.system(f'rm {write_filename}.tmp')

    if return_num_vars_clauses:
        return num_vars, num_clauses
    else:
        return variables

def parse_allowed_losses(filename, num_mutations):
    if not filename:
        return set([i for i in range(num_mutations)])
    with open(filename, 'r') as f:
        lines = f.readlines()
        if len(lines) > 0:
            allowed = lines[0].split(',')
            return set([int(i) for i in allowed])
        else:
            return set()

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
    matrix_file.close()
    
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
        default=4,
        help='number of columns in clustered matrix'
    )
    parser.add_argument(
        '--fn',
        type=int,
        default=4,
        help='number of false negatives'
    )
    parser.add_argument(
        '--fp',
        type=int,
        default=2,
        help='number of false positives'
    )
    parser.add_argument(
        '--sampler',
        type=int,
        default=2,
        help='1 to use Quicksampler, 2 to use Unigen.'
    )
    parser.add_argument(
        '--allowed_losses',
        type=str,
        default=None,
        help='Filename containing allowed mutation losses, listed on one line, separated by commas.'
    )

    args = parser.parse_args()

    filename = args.filename
    outfile = args.outfile
    s = args.s
    t = args.t

    start = time.time()
    variables = get_cnf(filename, outfile, s, t, args.sampler == 2, args.allowed_losses, args.fn, args.fp)
    end = time.time()

    write_vars("formula.vars", variables)

    print(f'Generated cnf formula in {end - start} seconds')