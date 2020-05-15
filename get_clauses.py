from itertools import permutations 
import os 
import math
from CNF import CNF

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

def generate_is_one(matrix, false_pos, false_neg, is_two):
    m = len(matrix)
    n = len(matrix[0])
    is_one = []

    for i in range(m):
        curr_row = []
        for j in range(n):
            if matrix[i][j] == 1:
                curr_row.append(f'-{false_pos[i][j]}')
            else:
                curr_row.append(str(false_neg[i][j]))
        is_one.append(curr_row)
    
    return is_one

def negate(literal):
    if literal[0] == '-':
        return literal[1:]
    else:
        return f'-{literal}'

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
                clause_cnf += f'{negate(is_one_sub[location[0]][location[1]])} '
        else:
            label = argument[0]
            use_is_two, location = variable_mapping[label][0], variable_mapping[label][1]
            if use_is_two:
                clause_cnf += f'{is_two_sub[location[0]][location[1]]} '
            else:
                clause_cnf += f'{is_one_sub[location[0]][location[1]]} '
    return clause_cnf

def get_clauses_no_forbidden(is_one, is_two, row_is_duplicate, col_is_duplicate, write_file):
    """
    Returns a list of clauses that enforce that no forbidden submatrices can
    be present in clustered matrix.

    is_one - matrix of boolean variables that are 1 if corresponding entry in matrix being 1
    is_two - matrix of boolean variables that are 1 if corresponding entry in matrix being 2
    """
    m = len(is_one)
    n = len(is_one[0])

    row_permutations = list(permutations(range(m), 3))
    column_permutations = list(permutations([i for i in range(n)], 2))

    clause_count = 0

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

                row_duplicates = f'{row_is_duplicate[row1]} {row_is_duplicate[row2]} {row_is_duplicate[row3]}'
                col_duplicates = f'{col_is_duplicate[col1]} {col_is_duplicate[col2]}'

                total_clause = f'{clause} {row_duplicates} {col_duplicates} 0\n'

                write_file.write(total_clause)
                clause_count += 1

    return clause_count

def get_clauses_not_one_and_two(is_one, is_two, write_file):
    """
    Returns list of clauses enforcing that an entry of the clustered matrix cannot be 
    both 1 and 2 at the same time.

    is_one - matrix of boolean variables that are 1 if corresponding entry in matrix being 1
    is_two - matrix of boolean variables that are 1 if corresponding entry in matrix being 2
    """
    clause_count = 0
    for i in range(len(is_one)):
        for j in range(len(is_one[0])):
            write_file.write(f'{negate(is_one[i][j])} -{is_two[i][j]} 0\n')
            clause_count += 1
    
    return clause_count

def get_row_duplicate_clauses(pair_in_col_equal, row_is_duplicate, row_is_duplicate_of, write_file):
    clause_count = 0

    num_rows = len(row_is_duplicate)
    num_columns = len(pair_in_col_equal[0][0])

    for row in range(1, num_rows):
        # Clause that is satisfied if
        # row_is_duplicate[row] => row_is_duplicate_of[0][row] or row_is_duplicate_of[1][row] or ... row_is_duplicate_of[row-1][row]
        # is satisfied
        clause_only_if = f'-{row_is_duplicate[row]} '
        for smaller_row in range(row):
            # Clause that is satisfied if
            # pair_in_col_equal[smaller][row][0] and pair_in_col_equal[smaller][row][1] and ... pair_in_col_equal[smaller][row][n]
            # => row_is_duplicate_of[smaller][row]
            # is satisfied
            clause_if = ''
            
            for col in range(num_columns):
                clause_if += f'-{pair_in_col_equal[smaller_row][row][col]} '
                # Clause that enforces
                # row_is_duplicate_of[smaller][row] => pair_in_col_equal[smaller][row][col]
                # is satisfied
                write_file.write(f'-{row_is_duplicate_of[smaller_row][row]} {pair_in_col_equal[smaller_row][row][col]} 0\n')
                clause_count += 1
            
            clause_if += f'{row_is_duplicate_of[smaller_row][row]} 0\n'
            write_file.write(clause_if)

            # Clause that enforces
            # row_is_duplicate_of[smaller][row] => row_is_duplicate[row]
            # is satisfied
            write_file.write(f'-{row_is_duplicate_of[smaller_row][row]} {row_is_duplicate[row]} 0\n')
            clause_count += 2

            clause_only_if += f'{row_is_duplicate_of[smaller_row][row]} '
        
        clause_only_if += '0\n'
        write_file.write(clause_only_if)
        clause_count += 1
    
    # first row cannot be a duplicate
    write_file.write(f'-{row_is_duplicate[0]} 0\n')
    clause_count += 1

    return clause_count

def get_col_duplicate_clauses(pair_in_row_equal, col_is_duplicate, unsupported_losses, is_two, col_is_duplicate_of, write_file):
    clause_count = 0

    num_cols = len(col_is_duplicate)
    num_rows = len(pair_in_row_equal)

    for col in range(1, num_cols):
        # Clause that is satisfied if
        # col_is_duplicate[col] => col_is_duplicate_of[0][col] or col_is_duplicate_of[1][col] or ... col_is_duplicate_of[col-1][col]
        # is satisfied
        clause_only_if = f'-{col_is_duplicate[col]} '

        for smaller_col in range(col):
            # Clause that is satisfied if
            # pair_in_row_equal[0][smaller_col][col] and pair_in_row_equal[1][smaller_col][col] and ... pair_in_row_equal[n][smaller_col][col]
            # => col_is_duplicate_of[smaller_col][col]
            # is satisfied
            clause_if = ''

            for row in range(num_rows):
                clause_if += f'-{pair_in_row_equal[row][smaller_col][col]} '
                # Clause that enforces
                # col_is_duplicate_of[smaller_col][col] => pair_in_row_equal[row][smaller_col][col]
                # is satisfied
                write_file.write(f'-{col_is_duplicate_of[smaller_col][col]} {pair_in_row_equal[row][smaller_col][col]} 0\n')
                clause_count += 1
            
            if col in unsupported_losses:
                clause_forbid_is_two = f'{col_is_duplicate_of[smaller_col][col]} -{is_two[row][smaller_col]} 0\n'
                write_file.write(clause_forbid_is_two)
                clause_count +=1

            clause_if += f'{col_is_duplicate_of[smaller_col][col]} 0\n'
            write_file.write(clause_if)

            # Clause that enforces
            # col_is_duplicate_of[smaller][col] => col_is_duplicate[col]
            # is satisfied
            write_file.write(f'-{col_is_duplicate_of[smaller_col][col]} {col_is_duplicate[col]} 0\n')
            clause_count += 2

            clause_only_if += f'{col_is_duplicate_of[smaller_col][col]} '
        
        clause_only_if += '0\n'
        write_file.write(clause_only_if)
        clause_count += 1
    
    # first col cannot be a duplicate
    write_file.write(f'-{col_is_duplicate[0]} 0\n')
    clause_count += 1

    return clause_count

def get_col_pairs_equal_clauses(is_one, is_two, pair_in_col_equal, write_file):
    clause_count = 0

    num_rows = len(is_one)
    num_cols = len(is_one[0])

    for col in range(num_cols):
        for row1 in range(num_rows):
            for row2 in range(row1 + 1, num_rows):
                ## BOTH ENTRIES ARE 1
                # B[row1][col] == 1 and B[row2][col] == 1 => pair_in_col_equal[row1][row2][col]
                write_file.write(f'{negate(is_one[row1][col])} {negate(is_one[row2][col])} {pair_in_col_equal[row1][row2][col]} 0\n')

                # pair_in_col_equal[row1][row2][col] and B[row1][col] == 1 => B[row2][col] == 1
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} {negate(is_one[row1][col])} {is_one[row2][col]} 0\n')

                # pair_in_col_equal[row1][row2][col] and B[row2][col] == 1 => B[row1][col] == 1
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} {negate(is_one[row2][col])} {is_one[row1][col]} 0\n')

                ## BOTH ENTRIES ARE 2
                # B[row1][col] == 2 and B[row2][col] == 2 => pair_in_col_equal[row1][row2][col]
                write_file.write(f'-{is_two[row1][col]} -{is_two[row2][col]} {pair_in_col_equal[row1][row2][col]} 0\n')

                # pair_in_col_equal[row1][row2][col] and B[row1][col] == 2 => B[row2][col] == 2
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} -{is_two[row1][col]} {is_two[row2][col]} 0\n')

                # pair_in_col_equal[row1][row2][col] and B[row1][col] == 2 => B[row2][col] == 2
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} -{is_two[row2][col]} {is_two[row1][col]} 0\n')

                ## BOTH ENTRIES ARE 0
                # B[row1][col] == 0 and B[row2][col] == 0 => pair_in_col_equal[row1][row2][col]
                #
                # equivalent to B[row1][col] != 1 and B[row2][col] != 1 
                # and B[row1][col] != 2 and B[row2][col] != 2
                write_file.write(f'{is_one[row1][col]} {is_one[row2][col]} {is_two[row1][col]} {is_two[row2][col]} {pair_in_col_equal[row1][row2][col]} 0\n')

                # pair_in_col_equal[row1][row2][col] and B[row1][col] != 1 and B[row1][col] != 2 => B[row2][col] != 1 and B[row2][col] != 2
                # (expands into 2 clauses)
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} {is_one[row1][col]} {is_two[row1][col]} {negate(is_one[row2][col])} 0\n')
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} {is_one[row1][col]} {is_two[row1][col]} -{is_two[row2][col]} 0\n')

                # pair_in_col_equal[row1][row2][col] and B[row2][col] != 1 and B[row2][col] != 2 => B[row1][col] != 1 and B[row1][col] != 2
                # (expands into 2 clauses)
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} {is_one[row2][col]} {is_two[row2][col]} {negate(is_one[row1][col])} 0\n')
                write_file.write(f'-{pair_in_col_equal[row1][row2][col]} {is_one[row2][col]} {is_two[row2][col]} -{is_two[row1][col]} 0\n')

                clause_count += 11

    return clause_count

def get_row_pairs_equal_clauses(is_one, is_two, pair_in_row_equal, write_file):
    clause_count = 0

    num_rows = len(is_one)
    num_cols = len(is_one[0])

    for row in range(num_rows):
        for col1 in range(num_cols):
            for col2 in range(col1 + 1, num_cols):
                # BOTH ENTRIES ARE 1
                # B[row][col1] == 1 and B[row][col2] == 1 => pair_in_row_equal[row][col1][col2]
                write_file.write(f'{negate(is_one[row][col1])} {negate(is_one[row][col2])} {pair_in_row_equal[row][col1][col2]} 0\n')

                # pair_in_row_equal[row][col1][col2] and B[row][col1] == 1 => B[row][col2] == 1
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} {negate(is_one[row][col1])} {is_one[row][col2]} 0\n')

                # pair_in_row_equal[row][col1][col2] and B[row][col2] == 1 => B[row][col1] == 1
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} {negate(is_one[row][col2])} {is_one[row][col1]} 0\n')

                # BOTH ENTRIES ARE 2
                # B[row1][col] == 2 and B[row2][col] == 2 => pair_in_row_equal[row][col1][col2]
                write_file.write(f'-{is_two[row][col1]} -{is_two[row][col2]} {pair_in_row_equal[row][col1][col2]} 0\n')

                # pair_in_row_equal[row][col1][col2] and B[row][col1] == 2 => B[row][col2] == 2
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} -{is_two[row][col1]} {is_two[row][col2]} 0\n')

                # pair_in_row_equal[row][col1][col2] and B[row][col2] == 2 => B[row][col1] == 2
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} -{is_two[row][col2]} {is_two[row][col1]} 0\n')

                # BOTH ENTRIES ARE 0
                # B[row][col1] == 0 and B[row][col2] == 0 => pair_in_row_equal[row][col1][col2]
                #
                # equivalent to B[row][col1] != 1 and B[row][col2] != 1 
                # and B[row][col1] != 2 and B[row][col2] != 2
                write_file.write(f'{is_one[row][col1]} {is_one[row][col2]} {is_two[row][col1]} {is_two[row][col2]} {pair_in_row_equal[row][col1][col2]} 0\n')

                # pair_in_row_equal[row][col1][col2] and B[row][col1] != 1 and B[row][col1] != 2 => B[row][col2] != 1 and B[row][col2] != 2
                # (expands into 2 clauses)
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} {is_one[row][col1]} {is_two[row][col1]} {negate(is_one[row][col2])} 0\n')
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} {is_one[row][col1]} {is_two[row][col1]} -{is_two[row][col2]} 0\n')

                # pair_in_row_equal[row][col1][col2] and B[row][col2] != 1 and B[row][col2] != 2 => B[row][col1] != 1 and B[row][col1] != 2
                # (expands into 2 clauses)
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} {is_one[row][col2]} {is_two[row][col2]} {negate(is_one[row][col1])} 0\n')
                write_file.write(f'-{pair_in_row_equal[row][col1][col2]} {is_one[row][col2]} {is_two[row][col2]} -{is_two[row][col1]} 0\n')
                
                clause_count += 11
    
    return clause_count

# credit to:
# https://github.com/elkebir-group/UniPPM/blob/dd650648c7b04cfa083ff0af3c4f1e0f926854ba/PPM2SAT.py#L143
def to_bin_list(val,n_bits,CNF_obj):
    # Convert a integer to a vector of binary values
    lb=bin(val)[2:][::-1]
    ans=[]
    for i in range(n_bits):
        if i<len(lb):
            ans.append(CNF_obj.true() if lb[i]=="1" else CNF_obj.false())
        else: ans.append(CNF_obj.false())
    return ans

# credit to:
# https://github.com/elkebir-group/UniPPM/blob/dd650648c7b04cfa083ff0af3c4f1e0f926854ba/PPM2SAT.py#L143
def encode_at_most_k(vars_to_sum, constraint, CNF_obj, N):
    to_sum = [[var] for var in vars_to_sum]

    while len(to_sum) > 1:
        result = []
        for i in range(0, len(to_sum) - (len(to_sum) % 2), 2):
            to_sum[i].append(CNF_obj.false()) # pad by 1
            to_sum[i+1].append(CNF_obj.false()) # pad by 1
            result.append(CNF_obj.add(to_sum[i], to_sum[i+1]))
        if len(to_sum) % 2 != 0:
            to_sum[-1].append(CNF_obj.false())
            result.append(to_sum[-1])
        to_sum = result

    constraint_binary = to_bin_list(constraint, len(to_sum[0]), CNF_obj)
    CNF_obj.leq(to_sum[0], constraint_binary)

# credit to:
# https://github.com/elkebir-group/UniPPM/blob/dd650648c7b04cfa083ff0af3c4f1e0f926854ba/PPM2SAT.py#L143
def encode_eq_k(vars_to_sum, constraint, CNF_obj, N):
    to_sum = [[var] for var in vars_to_sum]

    while len(to_sum) > 1:
        result = []
        for i in range(0, len(to_sum) - (len(to_sum) % 2), 2):
            to_sum[i].append(CNF_obj.false()) # pad by 1
            to_sum[i+1].append(CNF_obj.false()) # pad by 1
            result.append(CNF_obj.add(to_sum[i], to_sum[i+1]))
        if len(to_sum) % 2 != 0:
            to_sum[-1].append(CNF_obj.false())
            result.append(to_sum[-1])
        to_sum = result
    
    constraint_binary = to_bin_list(constraint, len(to_sum[0]), CNF_obj)
    CNF_obj.eq(to_sum[0], constraint_binary)

def encode_none(vars, CNF_obj):
    for var in vars:
        CNF_obj.set_true(-var)
    

def encode_constraints(false_pos, false_neg, row_duplicates, col_duplicates,
                        false_pos_constraint, false_neg_constraint,
                        row_dup_constraint, col_dup_constraint, write_file, CNF_obj):

    false_pos_vars = [var for row in false_pos for var in row if var != 0]
    if (len(false_pos_vars) > 0):
        N=math.ceil(math.log(len(false_pos_vars), 2)) # bits required to encode sum of fp variables
        encode_at_most_k(false_pos_vars, false_pos_constraint, CNF_obj, N)
    
    false_neg_vars = [var for row in false_neg for var in row if var != 0]
    if (len(false_neg_vars) > 0):
        N=math.ceil(math.log(len(false_neg_vars), 2)) # bits required to encode sum of fp variables
        encode_at_most_k(false_neg_vars, false_neg_constraint, CNF_obj, N)
    
    N=math.ceil(math.log(len(row_duplicates), 2))
    encode_eq_k(row_duplicates, row_dup_constraint, CNF_obj, N)

    N=math.ceil(math.log(len(col_duplicates), 2))
    encode_eq_k(col_duplicates, col_dup_constraint, CNF_obj, N)

    for cl in CNF_obj.clauses:
        if cl[0]=="c":
            continue
        for lit in cl:
            write_file.write("%d "%lit)
        write_file.write("0\n")
        
    return len(CNF_obj.clauses)

def clause_forbid_unsupported_losses(forbidden_losses, is_two, write_file):
    clause_count = 0
    for forbidden_loss in forbidden_losses:
        for row in range(len(is_two)):
            write_file.write(f'-{is_two[row][forbidden_loss]} 0\n')
            clause_count += 1
    
    return clause_count