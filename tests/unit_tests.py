import unittest
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generate_formula import get_cnf
from get_vars import write_vars
from utils import get_num_solutions_sharpSAT, read_matrix
from generate_samples import unigensampler_generator

sharpSAT_path = '../../../scratch/software/src/sharpSAT/build/Release/sharpSAT'
tmp_formula_path = 'tmp_formula.cnf'

class CheckFormula(unittest.TestCase):

    # A single forbidden matrix, no clustering allowed, no false positives or false negatives allowed,
    # no losses allowed.
    #
    # No solutions.
    def test_simple_forbidden_no_solutions(self):
        get_cnf('tests/test_inputs/simple_forbidden.txt', tmp_formula_path, 3, 2, [], 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 0)
    
    # A single forbidden matrix, no clustering allowed, no false positives or false negatives allowed,
    # only one loss in 2nd mutation is allowed.
    #
    # 1 solution:
    # 1 2 
    # 0 1
    # 1 1
    def test_simple_allow_one_loss(self):
        get_cnf('tests/test_inputs/simple_forbidden.txt', tmp_formula_path, 3, 2, [1], 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 1)

    # A single forbidden matrix, no clustering allowed, no false positives or false negatives allowed,
    # all losses allowed.
    #
    # 3 solutions are:
    # 1 2   1 0   1 2
    # 0 1   2 1   2 1
    # 1 1 , 1 1,  1 1
    def test_simple_allow_all_losses(self):
        get_cnf('tests/test_inputs/simple_forbidden.txt', tmp_formula_path, 3, 2, None, 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 3)
    
    # A single forbidden matrix, no clustering allowed, only 1 false positive allowed,
    # no losses allowed.
    #
    # 2 solutions are:
    # 1 0   0 0
    # 0 0   0 1
    # 1 1 , 1 1
    # All other choices of false positives lead to unwanted clustering, and no false positives
    # gives us a forbidden matrix.
    def test_simple_one_fp_no_losses(self):
        get_cnf('tests/test_inputs/simple_forbidden.txt', tmp_formula_path, 3, 2, [], 0, 1)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 2)

    # No way to cluster this matrix to a 4x4 using only one false negative.
    #
    # No solutions
    def test_no_solutions_no_clustering(self):
        get_cnf('tests/test_inputs/no_clustering.txt', tmp_formula_path, 4, 4, None, 1, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 0)
    
    # No false positives or false negatives allowed.
    #
    # 6 possible solutions for given matrix:
    # 1 0 0  1 2 0  1 2 2  1 2 2  1 0 0  1 2 0  
    # 1 1 0  1 1 0  1 1 0  1 1 2  1 1 2  1 1 2  
    # 1 1 1, 1 1 1, 1 1 1, 1 1 1, 1 1 1, 1 1 1
    def test_harder_no_error(self):
        get_cnf('tests/test_inputs/test_harder.txt', tmp_formula_path, 3, 3, None, 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 6)
    
    # One false negative is allowed
    # 
    # No false negatives -> 6 solutions (see above)
    # False negative at B[0][1] -> clusters to a 2 x 2 matrix, no solutions
    # False negative at B[0][2] -> 3 solutions
    # False negative at B[1][2] -> clusters to a 2x2 matrix, no solutions
    #
    # Total = 6 + 3 = 9 solutions
    def test_harder_one_fn(self):
        get_cnf('tests/test_inputs/test_harder.txt', tmp_formula_path, 3, 3, None, 1, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 9)

    # A matrix that clusters to a forbidden matrix, no false positives or
    # false negatives allowed, no mutation loss is allowed.
    # 
    # No solutions.
    def test_cell_cluster_to_forbidden(self):
        get_cnf('tests/test_inputs/cluster_cells.txt', tmp_formula_path, 3, 2, [], 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 0)
    
    # A matrix that clusters to a forbidden matrix, no false positives or
    # false negatives allowed, no mutation loss is allowed.
    # 
    # No solutions.
    def test_cell_cluster_to_forbidden(self):
        get_cnf('tests/test_inputs/cluster_mutations.txt', tmp_formula_path, 3, 2, [], 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 0)
    
    # A matrix that clusters to a forbidden matrix, no false positives or
    # false negatives allowed, all mutation loss is allowed.
    # 
    # 3 solutions (should be same as test_simple_allow_all_losses)
    def test_cell_cluster_to_forbidden_allow_losses(self):
        get_cnf('tests/test_inputs/cluster_cells.txt', tmp_formula_path, 3, 2, None, 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 3)
    
    # A matrix that clusters to a forbidden matrix, no false positives or
    # false negatives allowed, all mutation loss is allowed.
    # 
    # 3 solutions (should be same as test_simple_allow_all_losses)
    def test_mutation_cluster_to_forbidden_allow_losses(self):
        get_cnf('tests/test_inputs/cluster_mutations.txt', tmp_formula_path, 3, 2, None, 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 3)
    
    # Matrix should cluster to this matrix, with no false negatives or positives allowed:
    # 1 0 0
    # 1 1 0
    # 1 1 1
    #
    # 6 possible solutions for this clustered matrix:
    # 1 0 0  1 2 0  1 2 2  1 2 2  1 0 0  1 2 0  
    # 1 1 0  1 1 0  1 1 0  1 1 2  1 1 2  1 1 2  
    # 1 1 1, 1 1 1, 1 1 1, 1 1 1, 1 1 1, 1 1 1
    def test_harder_cluster(self):
        get_cnf('tests/test_inputs/test_harder_clustering.txt', tmp_formula_path, 3, 3, None, 0, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 6)
    
    # Input matrix of all 0s, 2 false negatives allowed, 0 false positives, no allowed losses
    #
    # All row permutations of the following solution are valid solutions
    # 3! = 6 solutions for this matrix:
    # 1 0
    # 0 1
    # 0 0
    def test_more_fn(self):
        get_cnf('tests/test_inputs/zero_3x2.txt', tmp_formula_path, 3, 2, [], 2, 0)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 6)
    
    # Input matrix of all 1s, 2 false positives allowed, 0 false negatives, all allowed losses
    #
    # All row permutations of the following 5 solutions are valid:
    # 1 2   1 0   1 0   0 1   0 1   
    # 2 1   2 1   1 2   2 1   1 2  
    # 1 1 , 1 1 , 1 1 , 1 1 , 1 1
    # 5*3! = 30 solutions
    def test_more_fp(self):
        get_cnf('tests/test_inputs/ones_3x2.txt', tmp_formula_path, 3, 2, None, 0, 2)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 30)
    
    # Input matrix is 4x4, clustered to 2x2 matrix, 2 false positives, 0 false negatives, all losses
    #
    # 2 solutions:
    # 1 0  1 2
    # 1 1, 1 1
    def test_small_cluster(self):
        get_cnf('tests/test_inputs/cluster_small.txt', tmp_formula_path, 2, 2, None, 0, 2)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 2)
    
    # A single forbidden matrix, no clustering allowed, 1 false positives and 1 false negatives allowed,
    # no losses allowed.
    #
    # 2 solutions:
    # 0 0  1 0
    # 0 1  0 0
    # 1 1, 1 1
    def test_one_fn_one_fp_no_loss(self):
        get_cnf('tests/test_inputs/simple_forbidden.txt', tmp_formula_path, 3, 2, [], 1, 1)
        num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula_path)
        os.system(f'rm {tmp_formula_path}')

        self.assertEqual(num_sols, 2)

class CheckIndependentSupport(unittest.TestCase):
    def test1(self):
        get_cnf('data/example.txt', tmp_formula_path, 4, 4, None, 2, 2)
        unigensampler_generator(tmp_formula_path, 'tmp.unigen', 100, 120)

        with open('tmp.unigen', 'r') as fp:
            lines = fp.readlines()
        
        for idx, line in enumerate(lines):
            if len(line) <= 1:
                continue
            line = line.strip()
            cleaned_line = line.split('v')[1]
            split_line = cleaned_line.split(' ')[:-1]
            split_line = [f'{lit} 0\n' for lit in split_line]
            
            tmp_formula = f'tmp{idx}.cnf'
            get_cnf('data/example.txt', tmp_formula, 4, 4, None, 2, 2, forced_clauses=split_line)
            
            num_sols = get_num_solutions_sharpSAT(sharpSAT_path, tmp_formula)

            self.assertEqual(num_sols, 1)
            print(f'Passed independent support {idx}')
            os.system(f'rm {tmp_formula}')
        
        os.system(f'rm {tmp_formula_path}')
        os.system('rm tmp.unigen')

if __name__ == '__main__':
    unittest.main()