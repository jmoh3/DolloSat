import os

directory = os.fsencode('data/perfect_phylogeny')

for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".txt"): 
        print(filename)
    else:
        continue