import os.path as opath
import os
import sys
import ctypes, ctypes.util
import numpy as np


SequencerC_path = '/Users/ckhan/workspace/BnC_CPLEX/BnC_CPLEX/GH/Sequencer.c'
SequencerO_path = 'Sequencer.o'
SequencerD_path = 'Sequencer.dylib'

if not opath.exists(SequencerC_path):
    print("Unable to find Sequencer.c")
    sys.exit()

def create_dylib():
    os.system('clang -c -fPIC %s -o %s' % (SequencerC_path, SequencerO_path))
    os.system('clang -shared %s -o %s' % (SequencerO_path, SequencerD_path))
    os.system('rm %s' % SequencerO_path)

if opath.exists(SequencerD_path):
    if opath.getctime(SequencerD_path) < opath.getmtime(SequencerC_path):
        create_dylib()
else:
    create_dylib()
        

seqlib_path = ctypes.util.find_library(SequencerD_path[:-len('.dylib')])
if not seqlib_path:
    print("Unable to find the specified library.")
    sys.exit()
try:
    seqlib = ctypes.CDLL(seqlib_path)
except OSError:
    print("Unable to load the system C library")
    sys.exit()    


INTEGER = ctypes.c_int
P_INTEGER = ctypes.POINTER(INTEGER)

DOUBLE = ctypes.c_double
P_DOUBLE = ctypes.POINTER(DOUBLE)
PP_DOUBLE = ctypes.POINTER(P_DOUBLE)


def double2ArrayToPointer(arr):
    """ Converts a 2D numpy to ctypes 2D array.

    Arguments:
        arr: [ndarray] 2D numpy float64 array
    Return:
        arr_ptr: [ctypes double pointer]
    """

    # Init needed data types
    ARR_DIMX = DOUBLE * arr.shape[0]
    ARR_DIMY = P_DOUBLE * arr.shape[0]

    # Init pointer
    arr_ptr = ARR_DIMY()

    # Fill the 2D ctypes array with values
    for i, row in enumerate(arr):
        arr_ptr[i] = ARR_DIMX()

        for j, val in enumerate(row):
            arr_ptr[i][j] = val

    return arr_ptr


'''
double get_erest_arrvTime(int* seq, int seqSize,
                          double* al_i, double* be_i,
                          double** t_ij);
'''
_get_erest_arrvTime = seqlib.get_erest_arrvTime
_get_erest_arrvTime.argtypes = [P_INTEGER, INTEGER,
                                P_DOUBLE, P_DOUBLE,
                                PP_DOUBLE]
_get_erest_arrvTime.restype = DOUBLE

def get_erest_arrvTime(seq, al_i, be_i, t_ij):
    if type(t_ij) != np.ndarray:
        t_ij = np.array(t_ij, dtype=np.double)
    _seqSize = len(seq)
    _seq = (ctypes.c_int * _seqSize)(*seq)
    _al_i = (ctypes.c_double * len(al_i))(*al_i)
    _be_i = (ctypes.c_double * len(be_i))(*be_i)
    _t_ij = double2ArrayToPointer(t_ij)
    return _get_erest_arrvTime(_seq, _seqSize,
                            _al_i, _be_i,
                            _t_ij)


'''
bool valid_TWs(int* seq, int seqSize,
                        double* al_i, double* be_i,
                        double** t_ij);
'''
_valid_TWs = seqlib.valid_TWs
_valid_TWs.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int,
                            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), 
                            ctypes.POINTER(ctypes.POINTER(ctypes.c_double))]
_valid_TWs.restype = ctypes.c_bool

def valid_TWs(seq, al_i, be_i, t_ij):
    if type(t_ij) != np.ndarray:
        t_ij = np.array(t_ij, dtype=np.double)
    _seqSize = len(seq)
    _seq = (ctypes.c_int * _seqSize)(*seq)
    _al_i = (ctypes.c_double * len(al_i))(*al_i)
    _be_i = (ctypes.c_double * len(be_i))(*be_i)
    _t_ij = double2ArrayToPointer(t_ij)
    return _valid_TWs(_seq, _seqSize,
                            _al_i, _be_i,
                            _t_ij)


'''
double get_travelTime(int* seq, int seqSize,
                      double* al_i, double* be_i,
                      double** t_ij);
'''
_get_travelTime = seqlib.get_travelTime
_get_travelTime.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int,
                            ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double), 
                            ctypes.POINTER(ctypes.POINTER(ctypes.c_double))]
_get_travelTime.restype = ctypes.c_double

def get_travelTime(seq, al_i, be_i, t_ij):
    if type(t_ij) != np.ndarray:
        t_ij = np.array(t_ij, dtype=np.double)
    _seqSize = len(seq)
    _seq = (ctypes.c_int * _seqSize)(*seq)
    _al_i = (ctypes.c_double * len(al_i))(*al_i)
    _be_i = (ctypes.c_double * len(be_i))(*be_i)
    _t_ij = double2ArrayToPointer(t_ij)
    return _get_travelTime(_seq, _seqSize,
                            _al_i, _be_i,
                            _t_ij)

'''

void set_min_tt_seq(int* partialSeq, int partialSeqSize,
                     int* minSeq, int* seq,
                     int newSeqSize,
                     int seqBeginIndex4Search,
                     int n0, int n1,
                     double* al_i, double* be_i,
                     double** t_ij);
'''
_set_min_tt_seq = seqlib.set_min_tt_seq
_set_min_tt_seq.argtypes = [P_INTEGER, INTEGER,
                            P_INTEGER, P_INTEGER,
                            INTEGER,
                            INTEGER,
                            INTEGER, INTEGER,
                            P_DOUBLE, P_DOUBLE,
                            PP_DOUBLE]
_set_min_tt_seq.restype = None

def get_min_tt_seq(partialSeq, n0, n1, al_i, be_i, t_ij):
    if type(t_ij) != np.ndarray:
        t_ij = np.array(t_ij, dtype=np.double)
    _partialSeqSize = len(partialSeq)
    _partialSeq = (ctypes.c_int * _partialSeqSize)(*partialSeq)
    _newSeqSize = len(partialSeq) + 2
    _minSeq = (ctypes.c_int * _newSeqSize)(*[-1 for _ in range(_newSeqSize)])
    _seq = (ctypes.c_int * _newSeqSize)(*[-1 for _ in range(_newSeqSize)])
    _seqBeginIndex4Search = 1
    _al_i = (ctypes.c_double * len(al_i))(*al_i)
    _be_i = (ctypes.c_double * len(be_i))(*be_i)
    _t_ij = double2ArrayToPointer(t_ij)
    #
    _set_min_tt_seq(_partialSeq, _partialSeqSize,
                    _minSeq, _seq,
                    _newSeqSize,
                    _seqBeginIndex4Search,
                    n0, n1,
                    _al_i, _be_i,
                    _t_ij)
    if _minSeq[0] == -1:
        return None
    else:
        return [_minSeq[i] for i in range(_newSeqSize)]
