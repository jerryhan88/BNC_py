import sys, os
import os.path as opath
import ctypes, ctypes.util

mylibC_path = './mylib.c'
mylibO_path = './mylib.o'
mylibD_path = './mylib.dylib'

def create_dylib():
    os.system('clang -c -fPIC %s -o %s' % (mylibC_path, mylibO_path))
    os.system('clang -shared %s -o %s' % (mylibO_path, mylibD_path))
    os.system('rm %s' % mylibO_path)


if opath.exists(mylibD_path):
    if opath.getctime(mylibD_path) < opath.getmtime(mylibC_path):
        create_dylib()
else:
    create_dylib()

mylib_path = ctypes.util.find_library(mylibD_path[:-len('.dylib')])
if not mylib_path:
    print("Unable to find the specified library.")
    sys.exit()
try:
    mylib = ctypes.CDLL(mylib_path)
except OSError:
    print("Unable to load the system C library")
    sys.exit()

test_empty = mylib.test_empty

test_add = mylib.test_add
test_add.argtypes = [ctypes.c_float, ctypes.c_float]
test_add.restype = ctypes.c_float

test_passing_array = mylib.test_passing_array
test_passing_array.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
test_passing_array.restype = None

print(test_add(1, 2))