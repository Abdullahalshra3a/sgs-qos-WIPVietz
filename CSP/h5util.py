#- * - coding: utf - 8
# Created By: Frauke Oest

import pandas as pd
import numpy as np
import h5py
import pickle
import os
#from CSP.SmartGridApplication import Candicate


def save(filename, attr, obj, mode='w'):
    print("save to hdf5")
    pickled_obj = pickle.dumps(obj)
    with h5py.File(filename, mode) as f:
        if attr in f:
            data = f[attr]
            data[...] = np.void(pickled_obj)
        else:
            dset = f.create_dataset(attr, data=np.void(pickled_obj))



def read(filename, attr):
    print("read from hdf5")
    with h5py.File(filename, "r") as f:
        print("Keys: %s" % f.keys())
        obj = f[attr][()]
        result = pickle.loads(obj)
    return result

def read_candidate(tagname, index):

    filename = f'{tagname}.h5'
    with h5py.File(filename, 'r') as f:
        bitrates = f['bitrates'][index]
        latency = f['latency'][index]
        server = f['server'][index]
        ot_device = f['ot_device'][index]
        multipaths = f['multipaths'][index]

    # candidate = Candicate(server=server, ot_device=ot_device)
    # candidate.latency_sc = latency
    # #candidate.multipaths = multipaths
    # candidate.bitrate_sc = bitrates
    # return candidate

cwd = os.getcwd()  # Get the current working directory (cwd)
files = os.listdir(cwd)  # Get all the files in that directory
print("Files in %r: %s" % (cwd, files))
