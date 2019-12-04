from generate_formula import get_zero_labels, generate_cnf, read_matrix
import sys
import time

# USAGE:
# $ python3 brute_force_solver.py INPUT_MATRIX_FILENAME SOLUTION_FILENAME
#
# This will generate all 1-dollo phylogeny solutions to the matrix contained in INPUT_MATRIX_FILENAME

def find_all_solutions(matrix, solution_filename, write=True):
    label_matrix = get_zero_labels(matrix)
    labels = []

    for i in range(len(label_matrix)):
        for j in range(len(label_matrix[i])):
            if label_matrix[i][j] != 0:
                labels.append((i, j))
    
    generate_cnf(matrix, 'tmp.cnf')

    cnf_file = open('tmp.cnf', 'r')
    clauses = cnf_file.readlines()
    cnf_file.close()

    solution_file = None
    if write:
        solution_file = open(solution_filename, 'w')
    count = 0

    for i in gen_binary_strings(len(labels)):
        satisifes = True
        # check whether i satisfies the satisfiability problem by checking each of the clauses
        for clause in clauses:
            # if one clause is false, the solution does not work
            if not check_clause(i, clause):
                satisifes = False
                break

        # if it does, add it to solutions
        if satisifes:
            if write:
                solution_file.write(i + '\n')
            else:
                count += 1
    
    if not write:
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
    matrix = read_matrix(sys.argv[1])
    start = time.time()
    find_all_solutions(matrix, sys.argv[2])
    end = time.time()
    print(f'Generated all solutions in {end - start} seconds')