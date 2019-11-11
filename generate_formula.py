def get_lookup(filename):
    lookup_file = open(filename, 'r')
    lookup = {}
    lines = lookup_file.readlines()

    for idx in range(0, len(lines), 2):
        lookup[lines[idx].strip()] = lines[idx+1]

    lookup_file.close()

    return lookup

lookup = get_lookup('forbidden-submatrix-enumerations.txt')

def get_clause(submatrix, submatrix_labels):
    key = ''

    for row in submatrix:
        for elem in row:
            key += str(elem)
    
    if key in lookup:
        return lookup[key]
    else:
        return None

def generate_cnf(matrix, outfilename):
    write_file = open(outfilename, 'w')
    num_rows = len(matrix)
    num_cols = len(matrix[0])

    for row1 in range(len(matrix)):
        for row2 in range(len(matrix)):
            for row3 in range(len(matrix)):
                for col1 in range(len(matrix[0])):
                    for col2 in range(len(matrix[0])):

                        submatrix = [[matrix[row1][col1], matrix[row1][col2]],
                                    [matrix[row2][col1], matrix[row2][col2]],
                                    [matrix[row3][col1], matrix[row3][col2]]]

                        submatrix_labels = [[row1 * num_rows + col1, row1 * num_rows + col2],
                                            [row2 * num_rows + col1, row2 * num_rows + col2],
                                            [row3 * num_rows + col1, row3 * num_rows + col2]]
                                            
                        clause = get_clause(submatrix, submatrix_labels)

                        if clause:
                            write_file.write(clause)

    
    write_file.close()

generate_cnf([[1, 0, 0, 0],[0, 1, 0, 1],[1, 1, 1, 1],[1, 0, 0, 1]],'hello.txt')