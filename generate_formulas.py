import os
import sys
from solve_k_dollo.generate_formula import read_matrix, generate_cnf

# USAGE:
# python3 generate_formulas.py INPUT_DIRECTORY_NAME
#
# Make sure your INPUT_DIRECTORY_NAME contains ONLY input matrices in the following
# file format:

# 5 # cells
# 5 # mutations
# 0 1 0 0 0
# 0 0 1 0 1
# 0 0 0 0 0
# 0 0 0 0 0
# 1 0 0 1 0

# And no other files/directories

if __name__ == '__main__':
    dir = sys.argv[1]
    input_files = os.listdir(dir)
    formulas_dir = dir + '/formulas'

    if not os.path.exists(formulas_dir):
        os.mkdir(formulas_dir)

    for file in input_files:
        shortened_filename = file.split('.')[0]
        matrix = read_matrix(f'{dir}/{file}')
        generate_cnf(matrix, f'{dir}/formulas/{shortened_filename}.formula.cnf')