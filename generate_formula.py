import sys

def get_lookup(filename):
    lookup_file = open(filename, 'r')
    lookup = {}
    lines = lookup_file.readlines()
    lookup_file.close()

    for idx in range(0, len(lines), 2):
        lookup[lines[idx].strip()] = lines[idx+1]

    return lookup

lookup = get_lookup('forbidden-submatrix-enumerations.txt')

def get_clause(submatrix, submatrix_labels):
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
    write_file = open(outfilename, 'w')
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    zero_labels = get_zero_labels(matrix)

    for row1 in range(len(matrix)):
        for row2 in range(len(matrix)):
            for row3 in range(len(matrix)):
                for col1 in range(len(matrix[0])):
                    for col2 in range(len(matrix[0])):

                        submatrix = [[matrix[row1][col1], matrix[row1][col2]],
                                    [matrix[row2][col1], matrix[row2][col2]],
                                    [matrix[row3][col1], matrix[row3][col2]]]

                        submatrix_labels = [[zero_labels[row1][col1], zero_labels[row1][col2]],
                                           [zero_labels[row2][col1], zero_labels[row2][col2]],
                                           [zero_labels[row3][col1], zero_labels[row3][col2]]]
                                            
                        clause = get_clause(submatrix, submatrix_labels)

                        if clause:
                            write_file.write(clause)

    
    write_file.close()

def read_matrix(filename):
    matrix_file = open(filename, 'r')
    lines = matrix_file.readlines()[2:]
    matrix = []
    
    for line in lines:
        matrix.append([int(x) for x in line.split()])
    
    return matrix

if __name__ == '__main__':
    matrix = read_matrix(sys.argv[1])
    generate_cnf(matrix, sys.argv[2])
    print('Generated cnf formula')