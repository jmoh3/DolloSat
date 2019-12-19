INPUT_FILENAME=$1

python3 solve_k_dollo/generate_formula.py $INPUT_FILENAME quicksampler/formula.cnf

# cd quicksampler

# ./quicksampler -n 10000000 -t 60.0 formula.cnf

# cd ..

# z3 sat.quicksampler_check=true sat.quicksampler_check.timeout=3600.0 quicksampler/formula.cnf

# python3 solve_k_dollo/reconstruct_solutions.py $INPUT_FILENAME quicksampler/formula.cnf.samples.valid