import os
import sys
from solve_k_dollo.generate_formula import read_matrix, generate_cnf

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