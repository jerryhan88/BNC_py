import sys, platform
import ctypes.util

if platform.system() == "Windows":
    path_libc = ctypes.util.find_library("msvcrt")
else:
    path_libc = ctypes.util.find_library("c")
    
try:
    libc = ctypes.CDLL(path_libc)
except OSError:
    print("Unable to load the system C library")
    sys.exit()
    
print(type(libc.printf(b"%s aaa \n", b"test")))

from c_integration_example import mylib
import ctypes

mylib.test_empty()
mylib.test_add(12.0, 22.2)

numel = 25
data = (ctypes.c_int * numel)(*[x for x in range(numel)])
mylib.test_passing_array(data, numel)

for indx in range(numel):
    print(data[indx], end=" ")
print("")



import SequencerWrapper
import json

prob_fpath = 'prob_nr004-np004-nd010-ca005-dt125-tw001-sn006.json'
prob = None
with open(prob_fpath) as json_file:
    prob = json.load(json_file)

seqSize = len(prob['S'])
seq = (ctypes.c_int * numel)(*prob['S'])
al_i = (ctypes.c_double * len(prob['al_i']))(*prob['al_i'])
be_i = (ctypes.c_double * len(prob['be_i']))(*prob['be_i'])



partialSeq = prob['S']
al_i, be_i, t_ij = [prob[k] for k in ['al_i', 'be_i', 't_ij']]
k = 1
n0 = prob['h_k'][k]
n1 = prob['n_k'][k]




get_travelTime(get_min_tt_seq(partialSeq, n0, n1, al_i, be_i, t_ij), al_i, be_i, t_ij)


import numpy as np

_t_ij = np.array(prob['t_ij'], dtype=np.double)

_t_ij[0]
_t_ij[1]

DOUBLE = ctypes.c_double
PDOUBLE = ctypes.POINTER(DOUBLE)
PPDOUBLE = ctypes.POINTER(PDOUBLE)


def double2ArrayToPointer(arr):
    """ Converts a 2D numpy to ctypes 2D array. 
    
    Arguments:
        arr: [ndarray] 2D numpy float64 array
    Return:
        arr_ptr: [ctypes double pointer]
    """

    # Init needed data types
    ARR_DIMX = DOUBLE * arr.shape[0]
    ARR_DIMY = PDOUBLE * arr.shape[0]

    # Init pointer
    arr_ptr = ARR_DIMY()

    # Fill the 2D ctypes array with values
    for i, row in enumerate(arr):
        arr_ptr[i] = ARR_DIMX()

        for j, val in enumerate(row):
            arr_ptr[i][j] = val


    return arr_ptr


t_ij = double2ArrayToPointer(_t_ij)

SequencerWrapper.get_travelTime(seq, seqSize,
                                al_i, be_i,
                                t_ij)

bu = 0.0
for i in range(len(prob['S']) - 1):
    bu += prob['t_ij'][prob['S'][i]][prob['S'][i + 1]]
    
t_ij[0][0]


n0 = seq[0];
erest_arrvTime = -1.0;
erest_deptTime = al_i[n0];
for i in range(1, len(prob['S'])):
    n1 = seq[i];
    erest_arrvTime = erest_deptTime + prob['t_ij'][n0][n1];
    if be_i[n1] < erest_arrvTime:
        break
    else:
        erest_deptTime = erest_arrvTime if erest_arrvTime > al_i[n1] else al_i[n1]
    n0 = n1;
    
    

prob['bu']

#
#
#t_ij = (PDOUBLE * len(prob['t_ij']))
#t_ij[0]
#type(t_ij)
#
#for i, arr in enumerate(prob['t_ij']):
#    t_ij[i] = DOUBLE * len(prob['t_ij'])
#    
#    
#    (ctypes.c_double * len(prob['t_ij']))
    


