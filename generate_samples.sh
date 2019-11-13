INPUT_FILENAME=$1
NUM_SAMPLES=$2

python3 generate_formula.py $INPUT_FILENAME quicksampler/formula.cnf

cd quicksampler

./quicksampler -n 10000000 -t 60.0 formula.cnf

cd ..

python3 reconstruct_solutions.py $INPUT_FILENAME quicksampler/formula.cnf.samples $NUM_SAMPLES