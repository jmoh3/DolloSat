import copy
import sys
from generate_formula import read_matrix

def reconstruct_solutions(matrix, filename, write_file, num_samples):
    solution_file = open(filename, 'r')
    solution_lines = solution_file.readlines()
    solution_file.close()

    solutions = []

    for x in range(1, num_samples*2, 2):
        solution = solution_lines[x]
        solution_matrix = copy.deepcopy(matrix)

        solution_idx = 0

        for i in range(len(solution_matrix)):
            for j in range(len(solution_matrix[i])):
                if solution_matrix[i][j] == 0:
                    if solution[solution_idx] == '1':
                        solution_matrix[i][j] = 2
                    solution_idx += 1

        solutions.append(solution_matrix)
    
    write_file = open(write_file, 'w')
    
    for solution in solutions:
        for row in solution:
            row_str = ''
            for elem in row:
                row_str += str(elem) + ' '
            row_str += '\n'
            write_file.write(row_str)
        write_file.write('======================\n')

    write_file.close()

if __name__ == '__main__':
    matrix = read_matrix(sys.argv[1])
    reconstruct_solutions(matrix, sys.argv[2], 'samples.txt', int(sys.argv[3]))