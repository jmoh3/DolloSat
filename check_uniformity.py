
# USAGE
# $ python3 check_uniformity.py INPUT_MATRIX_FILENAME SOLUTION_FILENAME

from brute_force_solver import find_all_solutions
from generate_formula import read_matrix

def check_uniformity(matrix_filename, solution_filename):
    solution_lines = None

    with open(solution_filename, 'r') as solution_file:
        solution_lines = solution_file.readlines()
    
    print(len(solution_lines))
    filtered = set()

    for x in range(1, len(solution_lines), 2):
        solution = solution_lines[x][3:].strip('\n')
        if solution not in filtered:
            filtered.add(solution)
    
    unique_samples = len(filtered)
    
    matrix = read_matrix(matrix_filename)
    all_solutions = find_all_solutions(matrix, None, False)

    print(f'{unique_samples} unique samples generated out of {all_solutions} total solutions')

check_uniformity('data/example.txt', 'quicksampler/formula.cnf.samples')