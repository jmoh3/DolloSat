
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

    cell_to_cluster = [[s*i+j+offset for j in range(s)] for i in range(m)]
    offset += m*s

    mutation_to_cluster = [[t*i+j+offset for j in range(t)] for i in range(n)]
    offset += n*t

    false_positives = [[0 for x in range(n)] for y in range(m)]
    false_negatives = [[0 for x in range(n)] for y in range(m)]
    
    for i in range(m):
        for j in range(n):
            if matrix[i][j] == 1:
                false_positives[i][j] = offset
            if matrix[i][j] == 0:
                false_negatives[i][j] = offset
            offset += 1
    
    is_one = [[t*i+j+offset for j in range(t)] for i in range(s)]
    offset += s*t

    is_two = [[t*i+j+offset for j in range(t)] for i in range(s)]

    variables = {'cell_to_cluster': cell_to_cluster,
                'mutation_to_cluster': mutation_to_cluster,
                'false_positives': false_positives,
                'false_negatives': false_negatives,
                'is_one': is_one,
                'is_two': is_two}
        
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
        for row in variables[key]:
            lines.append(' '.join([str(elem) for elem in row]))
            lines.append('\n')
        lines.append('=========================\n')
    with open(var_filename, 'w') as f:
        f.writelines(lines)