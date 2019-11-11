FILENAME=$1

python3 generate_formula.py $FILENAME quicksampler/formula.cnf

cd quicksampler

./quicksampler -n 10000000 -t 7200.0 formula.cnf