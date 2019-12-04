import sys
import time

# USAGE
# $ python3 generate_formula.py INPUT_MATRIX_FILENAME SOLUTION_FILENAME
# 
# Generates a boolean formula in CNF format from the matrix in INPUT_MATRIX_FILENAME
# and writes it to SOLUTION_FILENAME.
#
# The boolean formula corresponds the flipping of 0's in a binary matrix to 2's
# in such a way that produces a 1-dollo phylogeny.
#
# Each clause in the formula corresponds to a given submatrix of the input matrix,
# where a certain flipping of 0's within the submatrix could produce a forbidden
# matrix. The clause evaluates to true if the flipping configuration does NOT produce
# a forbidden submatrix, false if it does.

def get_lookup(lookup_filename):
    lookup_file = open(lookup_filename, 'r')
    lookup = {}
    lines = lookup_file.readlines()
    lookup_file.close()

    for idx in range(0, len(lines), 2):
        lookup[lines[idx].strip()] = lines[idx+1]

    return lookup

def get_clause(submatrix, submatrix_labels, lookup):
    labels_dictionary = {
        "a":[0,0],
        "b":[0,1],
        "c":[1,0],
        "d":[1,1],
        "e":[2,0],
        "f":[2,1],
    }
    
    key = ''

    for row in submatrix:
        for elem in row:
            if(elem == 1):
                key += str(elem)
            else:
                key += '0'
    
    clause_raw = ""

    if key in lookup:
        clause_raw = lookup[key]
    else:
        return None
    
    split_cnf = clause_raw.split()[:-1]
    clause_cnf = ""
    for argument in split_cnf:
        if(argument[0] == '-'):
            clause_cnf += '-'
            indicies_matrix = labels_dictionary[argument[1]]
            clause_cnf += str(submatrix_labels[indicies_matrix[0]][indicies_matrix[1]])
        else:
            indicies_matrix = labels_dictionary[argument[0]]
            clause_cnf += str(submatrix_labels[indicies_matrix[0]][indicies_matrix[1]])
        clause_cnf += " "
    clause_cnf += "0\n"

    return clause_cnf

def get_zero_labels(matrix):
    labels = [[0 for x in range(len(matrix[0]))] for y in range(len(matrix))]
    zero_count = 1

    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] == 0:
                labels[i][j] = zero_count
                zero_count += 1
    
    return labels

def generate_cnf(matrix, outfilename):
    lookup = get_lookup('forbidden-submatrix-enumerations.txt')

    write_file = open(outfilename, 'w')
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    zero_labels = get_zero_labels(matrix)

    for row1 in range(len(matrix)):
        for row2 in range(row1+1, len(matrix)):
            if row1 == row2:
                continue
            for row3 in range(row2+1, len(matrix)):
                if row3 == row2 or row3 == row1:
                    continue
                for col1 in range(len(matrix[0])):
                    for col2 in range(col1+1, len(matrix[0])):
                        if col1 == col2:
                            continue

                        submatrix = [[matrix[row1][col1], matrix[row1][col2]],
                                    [matrix[row2][col1], matrix[row2][col2]],
                                    [matrix[row3][col1], matrix[row3][col2]]]

                        submatrix_labels = [[zero_labels[row1][col1], zero_labels[row1][col2]],
                                           [zero_labels[row2][col1], zero_labels[row2][col2]],
                                           [zero_labels[row3][col1], zero_labels[row3][col2]]]
                                            
                        clause = get_clause(submatrix, submatrix_labels, lookup)

                        if clause:
                            write_file.write(clause)

    
    write_file.close()

def read_matrix(filename):
    matrix_file = open(filename, 'r')
    lines = matrix_file.readlines()[2:]
    
    return [[int(x) for x in line.split()] for line in lines]

def read_and_preprocess_matrix(filename):
    matrix_file = open(filename, 'r')

    # filter out duplicate rows
    lines = matrix_file.readlines()[2:]
    lines = set([line.strip('\n') for line in lines])
    matrix = [[int(x) for x in line.split()] for line in lines]

    # filter out duplicate columns
    columns = [[row[x] for row in matrix] for x in range(len(matrix[0]))]
    columns = [' '.join(map(str,column)) for column in columns]
    columns = list(set(columns))
    columns = [column.split() for column in columns]

    matrix = [[int(columns[x][y]) for x in range(len(columns))] for y in range(len(columns[0]))]

    return matrix

if __name__ == '__main__':
    matrix = read_matrix(sys.argv[1])
    start = time.time()
    generate_cnf(matrix, sys.argv[2])
    end = time.time()
    print(f'Generated cnf formula in {end - start} seconds')