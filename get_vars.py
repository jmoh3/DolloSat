def create_variable_matrices(matrix, s, t):
    """
    Returns dictionary where keys are the names of the variable matrices,
    and values are matrices containing labels for boolean variables in formula.

    matrix - input matrix for which we are creating a formula
    s - number of rows in clustered matrix
    t - number of columns in clustered matrix
    """
    m = len(matrix)
    n = len(matrix[0])
    offset = 1

    false_positives = [[0 for x in range(n)] for y in range(m)]
    false_negatives = [[0 for x in range(n)] for y in range(m)]
    
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == 1:
                false_positives[i][j] = offset
            if matrix[i][j] == 0:
                false_negatives[i][j] = offset
            offset += 1
    
    is_two = [[n*i+j+offset for j in range(n)] for i in range(m)]
    offset += m*n

    pair_in_row_equal = [[[0 for l in range(n)] for k in range(n)] for i in range(m)]

    for i in range(m):
        for k in range(n):
            for l in range(k+1,n):
                pair_in_row_equal[i][k][l] = offset
                offset += 1

    pair_in_col_equal = [[[0 for k in range(n)] for j in range(m)] for i in range(m)]

    for i in range(m):
        for j in range(i+1,m):
            for k in range(n):
                pair_in_col_equal[i][j][k] = offset
                offset += 1

    row_is_duplicate = [i+offset for i in range(m)]
    offset += m

    col_is_duplicate = [i+offset for i in range(n)]
    offset += n

    variables = {'false_positives': false_positives,
                'false_negatives': false_negatives,
                'is_two': is_two,
                'pair_in_row_equal': pair_in_row_equal,
                'pair_in_col_equal': pair_in_col_equal,
                'row_is_duplicate': row_is_duplicate,
                'col_is_duplicate': col_is_duplicate}
        
    return variables

def write_vars(var_filename, variables):
    """
    Writes variables to given file for debugging purposes.

    var_filename - file to write variables to
    variables - dictionary of variable matrices
    """
    lines = []
    for key in variables.keys():
        lines.append(f'{key}\n')
        if key == 'pair_in_row_equal':
            for i, row in enumerate(variables[key]):
                lines.append(f'row {i}\n')
                for j, col1 in enumerate(row):
                    for k, col2 in enumerate(col1):
                        if k > j:
                            lines.append(f'B[{i}][{j}] == B[{i}][{k}] = var {col2}\n')
        elif key == 'pair_in_col_equal':
            for k in range(len(variables[key][0][0])):
                lines.append(f'col {k}\n')
                for i in range(len(variables[key][0])):
                    for j in range(i+1,len(variables[key][0])):
                        if j > i:
                            lines.append(f'B[{i}][{k}] == B[{j}][{k}] = var {variables[key][i][j][k]}\n')
        elif key == 'row_is_duplicate':
            lines.append(' '.join([str(elem) for elem in variables[key]]))
            lines.append('\n')
        elif key == 'col_is_duplicate':
            lines.append(' '.join([str(elem) for elem in variables[key]]))
            lines.append('\n')
        else:
            for row in variables[key]:
                lines.append(' '.join([str(elem) for elem in row]))
                lines.append('\n')
        
        lines.append('=========================\n')
    with open(var_filename, 'w') as f:
        f.writelines(lines)