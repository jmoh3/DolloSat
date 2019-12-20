import sys
import argparse
from generate_formula import read_matrix

# USAGE:
# $ python3 test.py --matrixfilename=MATRIX_FILENAME --solutionfilename=SOLUTION_FILENAME
#
# Checks for the prescence of forbidden submatrices in reconstructed samples

forbidden_submatrices = { '1 0 0 1 1 1', '1 0 0 1 1 2',
                          '1 0 0 2 1 1', '1 0 0 2 1 2',
                          '1 0 0 1 2 1', '1 0 0 1 2 2',
                          '1 0 0 2 2 1', '1 0 0 2 2 2',
                          '2 0 0 1 1 1', '2 0 0 1 1 2',
                          '2 0 0 2 1 1', '2 0 0 2 1 2',
                          '2 0 0 1 2 1', '2 0 0 1 2 2',
                          '2 0 0 2 2 1', '2 0 0 2 2 2',
                          '1 1 0 2 1 2', '1 1 0 2 2 2',
                          '2 1 0 2 1 2', '2 1 0 2 2 2',
                          '2 0 1 1 2 1', '2 0 1 1 2 2',
                          '2 0 1 2 2 1', '2 0 1 2 2 2',
                          '2 1 1 2 2 2'
                          }

def verify_solution(matrix):
    for row1 in range(len(matrix)):
        for row2 in range(len(matrix)):
            if row1 == row2:
                continue
            for row3 in range(len(matrix)):
                if row3 == row2 or row3 == row1:
                    continue
                for col1 in range(len(matrix[0])):
                    for col2 in range(len(matrix[0])):
                        if col1 == col2:
                            continue

                        submatrix = f'{matrix[row1][col1]} {matrix[row1][col2]} {matrix[row2][col1]} {matrix[row2][col2]} {matrix[row3][col1]} {matrix[row3][col2]}'

                        if submatrix in forbidden_submatrices:
                            print(f'Found forbidden submatrix: {submatrix}')
                            return False
                            
    return True

def verify_solutions(matrix_filename, solution_filename):
    matrix = read_matrix(matrix_filename)
    solutions = read_matrices(solution_filename, len(matrix))
    
    for solution in solutions:
        verify_solution(solution)
        assert(verify_solution(solution))
    
    print('No invalid solutions found.')

def read_matrices(matrix_filename, num_rows):
    lines = None

    with open(matrix_filename, 'r') as f:
        lines = f.readlines()
    
    matrices = []
    seen = set()

    for i in range(0, len(lines), num_rows+1):
        matrix_slice = lines[i:i+num_rows]

        matrix_str = str(matrix_slice)
        if matrix_str in seen:
            continue
        seen.add(matrix_str)

        matrix = [line.split() for line in matrix_slice]
        matrices.append(matrix)

    return matrices

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate samples for given directories')

    parser.add_argument(
        '--matrixfilename',
        type=str,
        default='data/example.txt',
        help='the input file containing the matrix to generate samples for'
    )
    parser.add_argument(
        '--solutionfilename',
        type=str,
        help='outfile to write formula to'
    )

    args = parser.parse_args()

    verify_solutions(args.matrixfilename, args.solutionfilename)