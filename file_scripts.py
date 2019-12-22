#!/bin/python

import os 

def get_directory_files(num_files, directory):
    files = []

    for file in os.listdir(directory):
        filename = os.fsencode(file)
        if filename.endswith(b'.txt'):
            files.append(f'{directory}/{filename.decode("utf-8")}')
            if num_files > 0 and len(files) == num_files:
                break

    return files

def remove_directory(directory, remove_temp=True):
    if remove_temp:
        os.system('rm tmp.cnf')

    if not os.path.exists(directory):
        return

    os.removedirs(directory)

def remove_directory_files(directory):
    if not os.path.exists(directory):
        return

    rm_files_cmd = f'rm {directory}/*'

    os.system(rm_files_cmd)