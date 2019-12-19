# run with sh generate_samples_many DIRECTORY_NAME
# where DIRECTORY_NAME is the name of a directory under formulas/

DIRECTORY=$1

cd formulas/$DIRECTORY

arr=()

for f in * ; do
    # echo $f
    arr+=($f)
done

cd ..
cd ..

for f in "${arr[@]}"
do
    echo $f
    cd quicksampler

    ./quicksampler -n 10000000 -t 30.0 ../formulas/$DIRECTORY/$f

    cd ..

    z3 sat.quicksampler_check=true sat.quicksampler_check.timeout=60.0 formulas/$DIRECTORY/$f
    wc -l formulas/$DIRECTORY/$f.samples.valid >> num_solutions.txt
done