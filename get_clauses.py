from itertools import permutations 

def get_lookup(lookup_filename):
    """
    Parses the given forbidden clause lookup table and returns in dictionary
    format.
    """
    lookup_file = open(lookup_filename, 'r')
    lookup = {}
    lines = lookup_file.readlines()
    lookup_file.close()

    for idx in range(0, len(lines), 2):
        lookup[lines[idx].strip()] = lines[idx+1]

    return lookup

lookup = get_lookup('forbidden_clauses.txt')

"""
Lookup table that shows location of each variable in is_one or is_two
"""
variable_mapping = {'a': [0, [0,0]],
                    'b': [0, [0,1]],
                    'c': [0, [1,0]],
                    'd': [0, [1,1]],
                    'e': [0, [2,0]],
                    'f': [0, [2,1]],
                    'g': [1, [0,0]],
                    'h': [1, [0,1]],
                    'i': [1, [1,0]],
                    'j': [1, [1,1]],
                    'k': [1, [2,0]],
                    'l': [1, [2,1]],}

def get_forbidden_clause(is_one_sub, is_two_sub, raw_clause):
    """
    Returns a string that enforces the abscence of the given submatrix.

    is_one_sub - 3x2 matrix of labels corresponding to a certain entry of the clustered matrix
    being 1
    is_two_sub - 3x2 matrix of labels corresponding to a certain entry of the clustered matrix
    being 2
    raw_clause - clause composed of letters that correspond to a position in the given submatrix
    """
    split_cnf = raw_clause.split()[:-1]
    clause_cnf = ''
    for argument in split_cnf:
        if argument[0] == '-':
            label = argument[1]
            use_is_two, location = variable_mapping[label][0], variable_mapping[label][1]
            if use_is_two:
                clause_cnf += f'-{is_two_sub[location[0]][location[1]]} '
            else:
                clause_cnf += f'-{is_one_sub[location[0]][location[1]]} '
        else:
            label = argument[0]
            use_is_two, location = variable_mapping[label][0], variable_mapping[label][1]
            if use_is_two:
                clause_cnf += f'{is_two_sub[location[0]][location[1]]} '
            else:
                clause_cnf += f'{is_one_sub[location[0]][location[1]]} '
    clause_cnf += '0\n'
    return clause_cnf

def get_clauses_no_forbidden(is_one, is_two):
    """
    Returns a list of clauses that enforce that no forbidden submatrices can
    be present in clustered matrix.

    is_one - matrix of boolean variables that are 1 if corresponding entry in matrix being 1
    is_two - matrix of boolean variables that are 1 if corresponding entry in matrix being 2
    """
    s = len(is_one)
    t = len(is_one[0])

    row_permutations = list(permutations(range(s), 3))
    column_permutations = list(permutations([i for i in range(t)], 2))

    clauses = []

    for rows in row_permutations:
        for columns in column_permutations:
            row1, row2, row3 = rows[0], rows[1], rows[2]
            col1, col2 = columns[0], columns[1]

            is_one_sub = [[is_one[row1][col1], is_one[row1][col2]],
                            [is_one[row2][col1], is_one[row2][col2]],
                            [is_one[row3][col1], is_one[row3][col2]]]

            is_two_sub = [[is_two[row1][col1], is_two[row1][col2]],
                            [is_two[row2][col1], is_two[row2][col2]],
                            [is_two[row3][col1], is_two[row3][col2]]]

            for possible_submatrix in lookup.keys():
                clause_raw = lookup[possible_submatrix]
                clause = get_forbidden_clause(is_one_sub, is_two_sub, clause_raw)
                clauses.append(clause)

    return clauses

def get_clauses_mapping(variables, allowed_losses):
    """
    Returns a list of clauses that enforce mapping between input matrix B and clustered matrix
    A relates correctly to false positives and false negatives

    variables - dictionary containing labels for boolean variables in formula
    """
    cell_to_cluster = variables['cell_to_cluster']
    mutation_to_cluster = variables['mutation_to_cluster']
    false_positives = variables['false_positives']
    false_negatives = variables['false_negatives']
    is_one = variables['is_one']
    is_two = variables['is_two']

    m = len(cell_to_cluster)
    n = len(mutation_to_cluster)
    s = len(is_one)
    t = len(is_one[0])

    clauses = []

    for cell_num in range(m):
        for mutation_num in range(n):
            for cell_cluster in range(s):
                for mutation_cluster in range(t):
                    cell_cluster_var = cell_to_cluster[cell_num][cell_cluster]
                    mutation_cluster_var = mutation_to_cluster[mutation_num][mutation_cluster]

                    is_one_var = is_one[cell_cluster][mutation_cluster]
                    is_two_var = is_two[cell_cluster][mutation_cluster]

                    false_pos_var = false_positives[cell_num][mutation_num]
                    false_neg_var = false_negatives[cell_num][mutation_num]

                    if false_positives[cell_num][mutation_num] != 0:
                        # entry is originally a 1
                        # 1 -> 0 => false positive
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} {is_one_var} {is_two_var} {false_pos_var} 0\n")
                        # 1 -> 1 => not false positive
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_one_var} -{false_pos_var} 0\n")
                        if mutation_num in allowed_losses:
                            # 1 -> 2 => false positive
                            clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_two_var} {false_pos_var} 0\n")
                        else:
                            # prohibit is_two when mapping this mutation to this mutation cluster
                            clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_two_var} 0\n")
                    else:
                        # entry is originally a 0
                        # 0 -> 0 => not false negative
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} {is_one_var} {is_two_var} -{false_neg_var} 0\n")
                        # 0 -> 1 => false negative
                        clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_one_var} {false_neg_var} 0\n")
                        if mutation_num in allowed_losses:
                            # 0 -> 2 => not false negative
                            clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_two_var} -{false_neg_var} 0\n")
                        else:
                            # prohibit is_two when mapping this mutation to this mutation cluster
                            clauses.append(f"-{cell_cluster_var} -{mutation_cluster_var} -{is_two_var} 0\n")
    return clauses

def get_clauses_surjective(cluster_mapping):
    """
    Returns a list of clauses that enforce that mapping of cells/mutations to
    clusters is surjective, i.e. that each cell/mutation maps to at most one cluster.

    cluster_mapping - matrix of boolean variables where the entry at row i and column j
    will be 1 if cell/mutation i maps to cluster j, 0 otherwise.
    """
    rows = len(cluster_mapping)
    columns = len(cluster_mapping[0])

    clauses = []

    for i in range(rows):
        for p in range(columns):
            for k in range(columns):
                if p == k:
                    continue
                clauses.append(f'-{cluster_mapping[i][p]} -{cluster_mapping[i][k]} 0\n')
    
    return clauses

def get_at_least_one_cluster(cluster_matrix):
    """
    Returns list of clauses that ensure that cell/mutation maps to at least one cluster.

    cluster_mapping - matrix of boolean variables where the entry at row i and column j
    will be 1 if cell/mutation i maps to cluster j, 0 otherwise.
    """
    clauses = []
    for i in range(len(cluster_matrix)):
        clause = ''
        for j in range(len(cluster_matrix[0])):
            clause += f'{cluster_matrix[i][j]} '
        clause += '0\n'
        clauses.append(clause)
    return clauses

def each_cluster_has_at_least_one(cluster_mapping):
    """
    Returns list of clauses that ensure that each cluster has at least one member. (No 
    empty clusters)

    cluster_mapping - matrix of boolean variables where the entry at row i and column j
    will be 1 if cell/mutation i maps to cluster j, 0 otherwise.
    """
    clauses = []
    for j in range(len(cluster_mapping[0])):
        clause = ''
        for i in range(len(cluster_mapping)):
            clause += f'{cluster_mapping[i][j]} '
        clause += '0\n'
        clauses.append(clause)
    return clauses

def get_clauses_not_one_and_two(is_one, is_two):
    """
    Returns list of clauses enforcing that an entry of the clustered matrix cannot be 
    both 1 and 2 at the same time.

    is_one - matrix of boolean variables that are 1 if corresponding entry in matrix being 1
    is_two - matrix of boolean variables that are 1 if corresponding entry in matrix being 2
    """
    clauses = []
    for i in range(len(is_one)):
        for j in range(len(is_one[0])):
            clauses.append(f'-{is_one[i][j]} -{is_two[i][j]} 0\n')
    return clauses

def constrain_fp(false_vars):
    """
    Returns list of clauses that constrain the number of false positives and false negatives to
    at most 1.

    false_vars - matrix of boolean variable labels where variable at row i, column j is 1 if
    entry i,j of input matrix is a false positive/false negative.
    """
    flatten = []

    for row in false_vars:
        for elem in row:
            if elem != 0:
                flatten.append(elem)
    clauses = []
    for i in range(len(flatten)):
        var1 = flatten[i]
        for j in range(i+1, len(flatten)):
            var2 = flatten[j]
            if var1 != var2 and var2 != 0:
                clauses.append(f'-{var1} -{var2} 0\n')
    return clauses