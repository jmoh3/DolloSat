#!/bin/bash
if [ ! $# -eq 1 ]
then
    echo "Usage: $0 <perturb_executable>" >&2
    exit 1
fi

alpha=0.001
beta=0.01

for n in {5..25}
do
    for m in {5..25}
    do
        for s in {1..5}
        do
            for loss in {0.1,0.2}
            do
                for k in {1..1}
                do
                    filename=m${m}_n${n}_s${s}_k${k}_loss${loss}
                    $1 -a $alpha -b $beta ../k_dollo/$filename.B ${filename}_a${alpha}_b${beta}.B
                done
            done
        done
    done
done