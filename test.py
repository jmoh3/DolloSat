import sys
from generate_formula import read_matrix

# USAGE:
# python3 test.py MATRIX_FILENAME SOLUTION_FILENAME
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
        assert(verify_solution(solution))

def read_matrices(matrix_filename, num_rows):
    lines = None

    with open(matrix_filename, 'r') as f:
        lines = f.readlines()
    
    matrices = []
    seen = set()

    for i in range(0, len(lines), num_rows+1):
        matrix_slice = lines[i:i+num_rows+1]

        matrix_str = str(matrix_slice)
        if matrix_str in seen:
            continue
        seen.add(matrix_str)

        matrix = [line.split() for line in matrix_slice]
        matrices.append(matrix)

    print(f'Number solutions: {len(lines) // (num_rows+1)}')
    print(f'Number unique: {len(matrices)}')
    return matrices

if __name__ == "__main__":
    verify_solutions(sys.argv[1], sys.argv[2])
