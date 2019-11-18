# 1-Dollo Solution Sampler

A tool that samples solutions to the k-Dollo Phylogeny Problem for k = 1, a variant of the Two State Perfect Phylogeny Problem in which we are trying to infer a character-based phylogenetic tree T where each character is gained once and can be lost at most once.

## Requirements

First, clone this repository with the ```-r``` flag in order to ensure submodules are properly cloned.

This tool uses QuickSampler to sample solutions to the 1-Dollo Phylogeny Problem. Follow the instructions to install dependencies for QuickSampler as found here: https://github.com/RafaelTupynamba/quicksampler.

After this, you should be good to go!

## Usage Instructions

### Generating 1-dollo phylogenies for a given input matrix using QuickSampler

Run with:

```
sh generate_samples.sh INPUT_MATRIX_FILENAME NUM_SAMPLES
```

This will sample 1-dollo phylogeny matrices for the matrix in INPUT_MATRIX_FILENAME and save NUM_SAMPLES of those samples to samples.txt.

### Generating 1-dollo phylogenies for a given input matrix using UniGen

In progress

### Generating all 1-dollo phylogenies for a given input matrix

In progress

### Evaluating how well the solution space is sampled

In progress