import os
import csv
FILE_ = '.paths'

# %%
def init_files(file=FILE_):
    with open(file,'w', newline="") as f:
        pass
    os.system(f'attrib +h {file}')

# %%
def write_csv(file, data):
    with open(file, 'a',  newline="") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerows(data)

# %%
def open_csv(file):
    try:
        lines = (line for line in csv.reader(open(file)))
    except FileNotFoundError:
        init_files()
        lines = (line for line in csv.reader(open(file)))
    dicts = list(data for data in lines)
    return dicts