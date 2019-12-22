#!/bin/python

import time
import os

def unigensampler_generator(infile, outfile, num_samples):
    unigen_cmd = f'./samplers/unigen --samples={num_samples} {infile} {outfile} > /dev/null 2>&1'

    start = time.time()

    os.system(unigen_cmd)

    end = time.time()

    return end - start

def quicksampler_generator(cnf_file, num_samples):    
    q_cmd = f'./samplers/quicksampler -n {num_samples} -t 7200.0 {cnf_file} > /dev/null 2>&1'

    start = time.time()

    os.system(q_cmd)
    
    end = time.time()

    return end - start

def num_valid_solutions(cnf_file):
    z3_cmd = f'./samplers/z3 sat.quicksampler_check=true {cnf_file} > /dev/null 2>&1'

    os.system(z3_cmd)

    valid_samples_file = f'{cnf_file}.samples.valid'

    try:
        num_valid = 0

        with open(valid_samples_file, 'r') as s_file:
            num_valid = len(s_file.readlines())
            s_file.close()

        return num_valid
    except:
        return -1

def convert_unigen_to_quicksample(unigen_outfile, samples_outfile):
    unigen_file = open(unigen_outfile, 'r')
    samples_file = open(samples_outfile, 'w')

    for unigen_sample in unigen_file.readlines():
        unigen_sample = unigen_sample.strip()

        if len(unigen_sample) == 0:
            break

        unigen_sample = unigen_sample[1:].split(' ')

        num_times_sampled = unigen_sample[-1].split(':')[1]

        qsampler_binary = ''

        for variable in unigen_sample:
            if variable[0] != '0':
                qsampler_binary += '0' if variable[0] == '-' else '1'

        qsample = f'{num_times_sampled}: {qsampler_binary}'

        samples_file.write(qsample + '\n')

    unigen_file.close()
    samples_file.close()

def get_number_of_variables(cnf_file):
    try:
        infile = open(cnf_file, 'r')

        firstline = infile.readline()

        if firstline[0] != 'p':
            return 0
        
        metainfo = firstline.split(' ')

        return int(metainfo[-1])

        infile.close()
    except:
        return 0

def get_sample_distribution(valid_file):
    sample_dist = {}
    
    vfile = open(valid_file, 'r')

    for unigen_sample in vfile.readlines():
        unigen_sample = unigen_sample.strip()

        if len(unigen_sample) == 0:
            break

        unigen_sample = unigen_sample.split(' ')

        num_times_sampled = unigen_sample[-1].split(':')[1]

        sample_binary = ''

        for variable in unigen_sample:
            if variable[0] != '0':
                sample_binary += '0' if variable[0] == '-' else '1'

        sample_dist[sample_binary] = str(num_times_sampled)

    vfile.close()
    return sample_dist
