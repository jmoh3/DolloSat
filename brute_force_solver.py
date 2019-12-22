from generate_formula import get_zero_labels, generate_cnf, read_matrix
import sys
import time
import argparse
import os

# USAGE:
# $ python3 brute_force_solver.py --matrixfilename=INPUT_MATRIX_FILENAME --solutionfilename=SOLUTION_FILENAME
#
# This will generate all 1-dollo phylogeny solutions to the matrix contained in INPUT_MATRIX_FILENAME

def find_all_solutions(matrix, solution_filename, write=True):
    label_matrix, count = get_zero_labels(matrix)
    labels = []

    for i in range(len(label_matrix)):
        for j in range(len(label_matrix[i])):
            if label_matrix[i][j] != 0:
                labels.append((i, j))
    
    generate_cnf(matrix, 'tmp.cnf')

    cnf_file = open('tmp.cnf', 'r')
    clauses = cnf_file.readlines()
    cnf_file.close()
    
    os.system('rm tmp.cnf')

    solution_file = None
    if write:
        solution_file = open(solution_filename, 'w')
    count = 0

    for i in gen_binary_strings(len(labels)):
        satisifes = True
        # check whether i satisfies the satisfiability problem by checking each of the clauses
        for clause in clauses:
            # if one clause is false, the solution does not work
            if clause[0] != 'p' and not check_clause(i, clause):
                satisifes = False
                break

        # if it does, add it to solutions
        if satisifes:
            if write:
                solution_file.write(i + '\n')
            count += 1
    
    return count
    
def check_clause(solution, clause):
    literals = clause.split()[:-1]

    for literal in literals:
        if literal[0] == '-':
            literal_label = int(literal[1:])
            literal_value = solution[literal_label-1]
            if literal_value == '0':
                return True
        else:
            literal_label = int(literal)
            literal_value = solution[literal_label-1]
            if literal_value == '1':
                return True

    return False

def gen_binary_strings(n):
    for i in range(2**n):
        binary_str = str(bin(i))[2:]
        if len(binary_str) < n:
            padding = n - len(binary_str)
            binary_str = '0' * padding + binary_str
        yield binary_str

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate samples for given directories')

    parser.add_argument(
        '--matrixfilename',
        type=str,
        default='data/example.txt',
        help='the input file containing the matrix to generate samples for'
    )
    parser.add_argument(
        '--solutionfilename',
        default='all_solutions.txt',
        type=str,
        help='outfile to write solutions to'
    )

    args = parser.parse_args()

    matrix = read_matrix(args.matrixfilename)
    start = time.time()
    num_solutions = find_all_solutions(matrix, args.solutionfilename)
    end = time.time()
    print(f'Generated {num_solutions} solutions in {end - start} seconds')