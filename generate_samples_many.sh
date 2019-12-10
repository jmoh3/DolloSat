cd formulas/5x5

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

    ./quicksampler -n 10000000 -t 30.0 ../formulas/5x5/$f

    cd ..

    z3 sat.quicksampler_check=true sat.quicksampler_check.timeout=60.0 formulas/5x5/$f
    wc -l formulas/5x5/$f.samples.valid >> num_solutions.txt
done