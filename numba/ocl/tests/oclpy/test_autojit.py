from __future__ import print_function, absolute_import

import numpy as np

import numba.unittest_support as unittest
from numba.ocl.testing import OCLTestCase
from numba import ocl


def copy_kernel(out, inp):
    i = ocl.get_global_id(0)
    if i < out.size:
        out[i] = inp[i]


class TestAutoJit(OCLTestCase):
    def test_autojit_kernel(self):
        kernel = ocl.jit(copy_kernel)
        inp = np.arange(10)
        out = np.zeros_like(inp)
        kernel.forall(out.size)(out, inp)
        np.testing.assert_equal(inp, out)

    def test_autojit_device(self):
        @ocl.jit(device=True)
        def inner(a, b):
            return a + b

        @ocl.jit
        def outer(A, B):
            i = ocl.get_global_id(0)
            if i < A.size:
                A[i] = inner(A[i], B[i])

        A = np.arange(10)
        Aorig = A.copy()
        B = np.arange(10)

        outer.forall(A.size)(A, B)
        self.assertFalse(np.all(Aorig == A))
        np.testing.assert_equal(Aorig + B, A)


if __name__ == '__main__':
    unittest.main()

