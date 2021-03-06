from numba import unittest_support as unittest

import gc
from os.path import dirname, join
import multiprocessing
import sys
import time
import warnings

from unittest.suite import TestSuite
from numba.testing import load_testsuite
from numba.testing import ddt # for backward compatibility


try:
    import faulthandler
except ImportError:
    faulthandler = None
else:
    try:
        # May fail in IPython Notebook with UnsupportedOperation
        faulthandler.enable()
    except BaseException as e:
        msg = "Failed to enable faulthandler due to:\n{err}"
        warnings.warn(msg.format(err=e))

def load_tests(loader, tests, pattern):
    suite = TestSuite()
    # @@ suite.addTests(load_testsuite(loader, dirname(__file__)))

    # Numba CUDA / OCL / HSA tests are located in a separate directory:
    cuda_dir = join(dirname(dirname(__file__)), 'cuda/tests')
    suite.addTests(loader.discover(cuda_dir))

    ocl_dir = join(dirname(dirname(__file__)), 'ocl/tests')
    suite.addTests(loader.discover(ocl_dir))

    #hsa_dir = join(dirname(dirname(__file__)), 'hsa/tests')
    #suite.addTests(loader.discover(hsa_dir))

    return suite

