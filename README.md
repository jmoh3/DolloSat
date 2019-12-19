# 1-Dollo Solution Sampler

A tool that samples solutions to the k-Dollo Phylogeny Problem for k = 1, a variant of the Two State Perfect Phylogeny Problem in which we are trying to infer a character-based phylogenetic tree T where each character is gained once and can be lost at most once.

## Requirements

This repository uses two SAT Solution samples: [QuickSampler](https://github.com/RafaelTupynamba/quicksampler) and [UniGen](https://bitbucket.org/kuldeepmeel/unigen/src/master/). QuickSampler also requires the z3 binary specified in the installation instructions.

All of these binaries should be provided, but if none of them work, please see the GitHub pages for further instructions.

## Usage Instructions

### Generating 1-dollo phylogenies for a given input matrix using QuickSampler

Run with:

```
sh generate_samples.sh INPUT_MATRIX_FILENAME
```

This will sample 1-dollo phylogeny matrices for the matrix in INPUT_MATRIX_FILENAME and save NUM_SAMPLES of those samples to samples.txt.

### Generating CNF formulae

Run with:

```
python3 generate_formula.py INPUT_MATRIX_FILENAME SOLUTION_FILENAME
```

This takes in a matrix specified in INPUT_MATRIX_FILENAME and writes the cnf formula to SOLUTION_FILENAME

### Generating Metrics

Run with:

```
python3 generate_metrics.py --directory=DIRECTORY --quantity=NUMBER_OF_FILES --outfile=METRICS_OUTFILE --num_samples=NUMBER_OF_SAMPLES
```

This takes NUMBER_OF_FILES files from the DIRECTORY, and generates a cnf formula, then samples NUMBER_OF_SAMPLES each from UniGen and QuickSampler. All of the compiled data is written to METRICS_OUTFILE. As data is generated, the amount of total solutions is saved to `total_solutions.csv` in order to speed up the process on further runs.