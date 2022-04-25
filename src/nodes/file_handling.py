import os
import csv
FILE_PATHS = '.paths'
FILE_NODES = '.nodes'

# %%
def init_files(file):
    with  open(file,'w', newline="") as f:
        pass    
    os.system(f'attrib +h {file}')

def rem_file(file):
    if os.path.exists(file):
        os.remove(file)

# %%
def write_csv(file, data):
    with open(file, 'a',  newline="") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(data)
    os.system(f'attrib +h {file}')

def line_(file):
    try:
        with open(file) as f:
            x = csv.reader(f)
            for line in x:
                yield line
    except FileNotFoundError:
        init_files(file)
        return -1
def dict_(lines):
    for line in lines:
        yield line


# %%
def open_csv(file, nodes=None):
    lines = line_(file)
    if lines == -1:
        lines = line_(file)
    if nodes is not None:
        return lines
    dicts = dict_(lines)
    return dicts
                