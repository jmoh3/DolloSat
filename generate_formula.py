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
            indacies_matrix = labels_dictionary[argument[1]]
            clause_cnf += str(submatrix_labels[indacies_matrix[0]][indacies_matrix[1]])
        else:
            indacies_matrix = labels_dictionary[argument[0]]
            clause_cnf += str(submatrix_labels[indacies_matrix[0]][indacies_matrix[1]])
        clause_cnf += " "
    clause_cnf += "0"
    return clause_cnf

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